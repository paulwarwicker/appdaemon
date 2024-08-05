# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import threading
import time

from queue import Queue

import arrow  # pylint: disable=E0401

import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611 disable=W0212 disable=W0621
# import appdaemon.adbase as ad  # pylint: disable=E0401,E0611
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611

class Announcer(hass.Hass): # pylint: disable=W0212 disable=W0621
    """This is the documentation for Announcer"""

    # _lock = None
    queue = None
    cache = True
    START = 8
    END = 21
    lib = None


# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.log('-'*72)

        self.lib = AutomationLib(self) # .get_ad_api()
        self.queue = Queue(maxsize = 0)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.test_message_event, 'test_message')

        self.register_service('announcer/announce', self.announce)
        self.register_service('announcer/broadcast', self.broadcast)
        self.register_service('announcer/notification', self.notification)
        self.register_service('announcer/desktop_notification', self.desktop_notification)
        self.register_service('announcer/initialised', self.initialised)

        self.run_daily(self.bins_preannounce, '19:30:00')
        self.run_daily(self.bins_announce1, '17:30:00')
        self.run_daily(self.bins_announce2, '19:30:00')
        self.run_daily(self.vouchers_announce, '17:29:00')
        self.log('\t*announce* registered')

        # self._lock = threading.RLock()

        # self.submit_to_executor(self.announce_worker)

        t = threading.Thread(target=self.announce_worker)
        t.daemon = True
        t.start()

        self.log('\tregistration end')

        self._announce('media_player.study', f'{self.name.capitalize()} initialised', False)

# -------------------------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs={}):

        self._status()

# -------------------------------------------------------------------------------------------------

    def test_message_event(self, event, data, kwargs={}):

        self._announce('media_player.study', 'Test message', False)

# -------------------------------------------------------------------------------------------------

    def announce_worker(self, *args, **kwargs):

        self.log('\tannounce_worker listening')

        while True:
            (entity_id, message, snapshot) = self.queue.get()

            # with self._lock:
            #     # self.log(f'got entity_id={entity_id}, message={message}, snapshot={snapshot}')
            #     self._announce(entity_id, message, snapshot)

            self._announce(entity_id, message, snapshot)

# -------------------------------------------------------------------------------------------------

    async def announce(self, namespace, domain, service, kwargs):

        self.queue.put([kwargs['entity_id'], kwargs['message'], kwargs.get('snapshot', False)])

# ---------------------------------------------------------------------------------

    async def broadcast(self, namespace, domain, service, kwargs):

        # self.log(f'\t\tin announce entity_id={entity_id}, message={message}, snapshot={snapshot}')

        self._broadcast(kwargs['broadcast_entity_id'],
                        kwargs['other_entity_id'],
                        kwargs['volume'],
                        kwargs['message'],
                        kwargs['snapshot'])

# ---------------------------------------------------------------------------------

    async def desktop_notification(self, namespace, domain, service, data):

        self._desktop_notification(data['message'])

# ---------------------------------------------------------------------------------------------------------

    async def notification(self, namespace, domain, service, data):

        self._notification(data['message'])

# ---------------------------------------------------------------------------------------------------------

    async def initialised(self, namespace, domain, service, data):

        name = data.get('name', 'unknown')
        self._announce('media_player.study', f'{name} initialised', False)

# ---------------------------------------------------------------------------------------------------------

    def _announceable(self):

        if self.get_state('input_boolean.force_announcement') == 'on':
            return True

        if self.get_state('input_boolean.mute_announcement') == 'on':
            return False

        dow = self.lib.dow()

        announceable1 = self.now_is_between(f'{self.START:02d}:00:00', f'{self.END:02d}:30:00')
        announceable2 = (dow in (2,4) and self.now_is_between('09:27:00', '09:58:00')) or (dow in (1,5) and self.now_is_between('16:27:00', '16:58:00'))

        # self.log(f'announcable1={announceable1} announcable2={announceable2}, announceable1 and not announceable2={announceable1 and not announceable2}', level="WARNING")

        # return announceable1
        return announceable1 and not announceable2

# ---------------------------------------------------------------------------------------------------------

    def _announce(self, entity_id, message, snapshot):

        # self.log(f'\t\tin _announce entity_id={entity_id} message={message} snapshot={snapshot}', level='WARNING')

        (entity_id, volume) = self._set_entity_id_volume(entity_id)

        if self._announceable():
            if snapshot:
                self.call_service('sonos/snapshot', entity_id=entity_id, with_group=True)

            self.run_sequence(
                [
                    {'media_player/volume_set': {'entity_id': entity_id, 'volume_level': volume}},
                    {'media_player/volume_mute': {'entity_id': entity_id, 'is_volume_muted': False}},
                    # https://www.home-assistant.io/integrations/google_translate/
                    {'tts/speak': {'entity_id': 'tts.google_en_co_uk', 'cache': self.cache, 'message': message, 'media_player_entity_id': entity_id}},
                    {'media_player/repeat_set': {'entity_id': entity_id, 'repeat': 'off'}}
                ]
            )

            time.sleep(len(message) * 0.25)

            self._desktop_notification(message)

            if snapshot:
                self.call_service('sonos/restore', entity_id=entity_id, with_group=True)
        else:
            self._desktop_notification(message)

# ---------------------------------------------------------------------------------------------------------

    def _broadcast(self, broadcast_entity_id, other_entity_id, volume, message, snapshot):

        self.call_service('sonos/snapshot', entity_id='all')

        self.call_service('media_player/join', entity_id=broadcast[0], group_members=broadcast[1:])

        for e in broadcast_entity_id:
            self.call_service('media_player/volume_set', entity_id=e, volume_level=volume)

        for e in other_entity_id:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=True)

        self._announce(broadcast_entity_id, message, False)

        self.call_service('sonos/restore', entity_id='all')

        for e in broadcast_entity_id + other_entity_id:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=False)

# ---------------------------------------------------------------------------------------------------------

    def _desktop_notification(self, message):

        self.log(f'\t{message}', level="WARNING")

        self.run_sequence(
            [
                {'notify/disc0rd': {'title': 'Deferred notification', 'message': message, 'target': "1250932196613685313"}},
                # {'notify/pushbullet': {'title': 'Deferred notification', 'message': message}}
            ]
        )

# ---------------------------------------------------------------------------------------------------------

    def _notification(self, message):

        self.log(f'\t{message}', level="WARNING")

        self.run_sequence(
            [
                {'notify/disc0rd': {'title': 'FIXME: Notification', 'message': 'FIXME: ' + message, 'target': "1250932196613685313"}},
                # {'notify/pushbullet': {'title': 'Deferred notification', 'message': message}}
            ]
        )

# -------------------------------------------------------------------------------------------------

    def _set_entity_id_volume(self, entity_id):

        if entity_id is not None:
            if self.now_is_between('08:00:00', '21:30:00'):
                volume = 0.25
            elif self.now_is_between('21:30:00', '08:00:00'):
                volume = 0.1
        else:
            entity_id, volume = self.lib.get_entity_id()

        return entity_id, volume

# ---------------------------------------------------------------------------------------------------------

    def _status(self):

        status = f'\n\n\t--\n'
        status += f'\t--\n'

        self.log(f'{status}')

        print(self.queue)

# ---------------------------------------------------------------------------------

    # def announce_listener(self, *args, **kwargs):

    #     self.log('\tannounce_listener listening')

    #     # lock = threading.Lock()

    #     while True:
    #         (entity_id, message, snapshot) = self.queue.get(block=True)

    #         self.log(f'got entity_id={entity_id}, message={message}, snapshot={snapshot}')
    #         self._announce(entity_id, message, snapshot)

    #         # lock.acquire()

    #         # try:
    #         #     self._announce(entity_id, message, snapshot)
    #         # except BaseException:
    #         #     lock.release()

    #         # with lock:
    #         #     self._announce(entity_id, message, snapshot)

# ---------------------------------------------------------------------------------

    def bins_announce(self, announce_type, force=False):

        # https://www.scambs.gov.uk/recycling-and-bins/find-your-household-bin-collection-day#id=100091416947
        # baseurl = 'https://refusecalendarapi.azurewebsites.net/calendar/ical/'
        baseurl = 'https://servicelayer3c.azure-api.net/wastecalendar/calendar/ical/'
        url = baseurl+'100091416947'  # was '100091416948'
        bins = []
        dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow

        if announce_type == 'preannounce':
            dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow
        else:
            dow = arrow.now().floor('day').shift(hours=6).shift(days=1)  # 6am tomorrow

        loop = True
        pattern = r'^Rate limit is exceeded. Try again in (\d+) seconds.$'

        while loop:
            r = requests.get(url)
            t = r.text
            if t[0] == '{':
                y = json.loads(t)
                a = re.search(pattern, y['message'])
                s = a.groups(1)[0]
                self.lib.delay(int(s))
            else:
                loop = False

        c = Calendar(t)

        for e in iter(c.timeline.overlapping(dow, dow)):
            bins.append(e.name.split()[0].lower())

        if force:
            bins = ['orange']

        if len(bins) > 0:
            if len(bins) > 1:
                bins.insert(1, 'and')
                bins.append('bins')
            else:
                bins.append('bin')

            if announce_type == 'preannounce':
                phrase = ' '.join(['It', 'is', 'the', ' '.join(bins), 'this', 'week'])
            elif announce_type == 'announce1':
                phrase = ' '.join(['Can', 'you', 'put', 'the', ' '.join(bins), 'out', 'please'])
            elif announce_type == 'announce2':
                phrase = ' '.join(['Have', 'you', 'put', 'the', ' '.join(bins), 'out'])

            self.announce(message=phrase)

# ---------------------------------------------------------------------------------------------------------

    def bins_preannounce(self, kwargs={}):

        if self.get_testing():
            self.bins_announce('preannounce', True)
        else:
            self.bins_announce('preannounce')

# ---------------------------------------------------------------------------------------------------------

    def bins_announce1(self, kwargs={}):

        self.bins_announce('announce1')

# ---------------------------------------------------------------------------------------------------------

    def bins_announce2(self, kwargs={}):

        self.bins_announce('announce2')

# ---------------------------------------------------------------------------------------------------------

    def vouchers_announce(self, kwargs={}):

        dow = arrow.now().isoweekday()

        with open('/homeassistant/data.yaml', 'r', encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        vouchers = data['vouchers']
        force = vouchers['force']
        value = vouchers['value']
        expiry = vouchers['expiry']

        mock_run = self.lib.is_mock_run()

        if mock_run:
            value = 1
            expiry = 'whenever'

        if dow == 2 or force or mock_run:
            if value > 0:
                phrase = ' '.join([str(value), 'pounds', 'of', 'vouchers', 'expiring', 'end', 'of', expiry])
                self.log(f'\tphrase={phrase}')
                self._announce(message=phrase)
            else:
                self.log('\tno expiring vouchers', level='WARNING')

# ---------------------------------------------------------------------------------------------------------

