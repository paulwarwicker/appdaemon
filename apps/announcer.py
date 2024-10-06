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
import json
import re
import yaml
import arrow  # pylint: disable=E0401
import requests  # pylint: disable=E0401

from queue import Queue
from ics import Calendar

from appdaemon.plugins.hass.hassapi import Hass  # pylint: disable=E0401 disable=E0611
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611

class Announcer(Hass): # pylint: disable=W0212 disable=W0621
    """This is the documentation for Announcer"""

    queue = None
    cache = True
    START = 8
    END = 21
    lib = None
    BROADCAST_ENTITY_ID = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
    OTHER_ENTITY_ID = ['media_player.study', 'media_player.bedroom_2']

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """Documentation for Announcer"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        self.queue = Queue(maxsize = 0)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.vouchers_announce_event, 'vouchers_announce')
        self.listen_event(self.bins_announce_event, 'bins_announce')

        self.listen_event(self.test_announce_event, 'test_announce')
        self.listen_event(self.test_broadcast_event, 'test_broadcast')
        # self.listen_event(self.test_bins_announcement_event, 'test_bins_announcement')
        # self.listen_event(self.test_vouchers_announcement_event, 'test_vouchers_announcement')

        self.register_service('announcer/announce', self.announce)
        self.register_service('announcer/broadcast', self.broadcast)
        self.register_service('announcer/notification', self.notification)
        self.register_service('announcer/desktop_notification', self.desktop_notification)
        self.register_service('announcer/initialised', self.initialised)

        self.run_daily(self.bins_preannounce, '19:30:00')
        self.run_daily(self.bins_announce1, '17:30:00')
        self.run_daily(self.bins_announce2, '19:30:00')
        self.run_daily(self.vouchers_announce, '17:29:00')

        # self.submit_to_executor(self.announce_worker)
        t = threading.Thread(target=self.announce_worker)
        t.daemon = True
        t.start()

        self.log('initialised')

# -------------------------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs={}) -> None:

        self._status()

# -------------------------------------------------------------------------------------------------

    def vouchers_announce_event(self, event, data, kwargs={}) -> None:

        self.vouchers_announce()

# -------------------------------------------------------------------------------------------------

    def bins_announce_event(self, event, data, kwargs={}) -> None:

        self.bins_announce1()

# -------------------------------------------------------------------------------------------------

    def announce_worker(self, *args, **kwargs) -> None:

        self.log('\tannounce_worker listening')

        if self.lib.get_verbose_debug():
            print(self.queue.queue)

        while True:
            (entity_id, message, snapshot, announce) = self.queue.get()
            if self.lib.get_verbose_debug():
                print(f'\tworker got entity_id={entity_id} message={message} snapshot={snapshot} announce={announce}')
                print(f'\tremaining queue: {self.queue.queue}')
            self._announce(entity_id, message, snapshot, announce)

# -------------------------------------------------------------------------------------------------

    def announce(self, namespace, domain, service, kwargs) -> None:

        # if self.lib.get_verbose_debug():
        #     print(f'namespace={namespace}, domain={domain}, service={service}, kwargs={kwargs}')

        entity_id = kwargs['entity_id']
        message = kwargs['message']
        snapshot = kwargs.get('snapshot', False)
        announce = kwargs.get('announce', True)

        self.queue.put([entity_id, message, snapshot, announce])

        if self.lib.get_verbose_debug():
            print(f'\tput entity_id={entity_id} message={message} snapshot={snapshot} announce={announce}')

# ---------------------------------------------------------------------------------------------------------

    def _announce(self, entity_id=None, message='', snapshot=False, announce=True) -> None:

        e = entity_id if isinstance(entity_id, str) else entity_id[0]
        (entity_id, volume) = self.lib.get_entity_id(e)
        s = snapshot
        snapshot = self.lib.is_playing(e)

        if self.lib.get_verbose_debug():
            print(f'\tin _announce entity_id={entity_id} message={message} snapshot={snapshot}, announce={announce}, e={e}, volume={volume}, s={s} (was {snapshot})')

        if self._announceable(announce):
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

            # self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume)
            # self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
            # # print(f'delay={len(message) * 0.35}, message={message}')
            # self.call_service('tts/speak', entity_id='tts.google_en_co_uk', cache=False, message=message, media_player_entity_id=entity_id) # https://www.home-assistant.io/integrations/google_translate/
            # self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')

            time.sleep(len(message) * 0.35) # was 0.25

            if snapshot:
                self.call_service('sonos/restore', entity_id=entity_id, with_group=True)

            # self._desktop_notification(message) # caused issues with announcement (??) logged anyway
        else:
            self._desktop_notification(message)

# ---------------------------------------------------------------------------------

    def broadcast(self, namespace, domain, service, kwargs) -> None:

        broadcast_entity_id = kwargs.get('broadcast_entity_id', self.BROADCAST_ENTITY_ID)
        other_entity_id = kwargs.get('other_entity_id', self.OTHER_ENTITY_ID)
        volume = kwargs.get('volume', 0.4)
        message = kwargs['message']
        snapshot = kwargs.get('snapshot', True)
        timestamp = kwargs.get('timestamp', None)

        if self.lib.get_testing():
            volume = 0.2
            broadcast_entity_id = ['media_player.study']
            other_entity_id = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room', 'media_player.bedroom_2']

        if self.lib.get_verbose_debug():
            print(f'\tin broadcast broadcast_entity_id={broadcast_entity_id}, other_entity_id={other_entity_id}, volume={volume}, message={message}, snapshot={snapshot}')

        self._broadcast(broadcast_entity_id, other_entity_id, volume, message, snapshot)

        if timestamp:
            self.call_service('timestamp/set', name=timestamp)

# ---------------------------------------------------------------------------------------------------------

    def _broadcast(self, broadcast_entity_id, other_entity_id, volume, message, snapshot) -> None:

        self.call_service('sonos/snapshot', entity_id='all')

        self.call_service('media_player/join', entity_id=broadcast_entity_id[0], group_members=broadcast_entity_id[1:])

        for e in broadcast_entity_id:
            self.call_service('media_player/volume_set', entity_id=e, volume_level=volume)

        for e in other_entity_id:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=True)

        self._announce(broadcast_entity_id, message, False)

        self.call_service('sonos/restore', entity_id='all')

        for e in broadcast_entity_id + other_entity_id:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=False)

        self._desktop_notification(message)

# ---------------------------------------------------------------------------------

    def desktop_notification(self, namespace, domain, service, data) -> None:

        self._desktop_notification(data['message'])

# ---------------------------------------------------------------------------------------------------------

    def _desktop_notification(self, message) -> None:

        self.log(f'\t{message}', level="INFO")

        self.run_sequence(
            [
                {'notify/disc0rd': {'title': 'Deferred notification', 'message': message, 'target': "1250932196613685313"}},
                # {'notify/pushbullet': {'title': 'Deferred notification', 'message': message}}
            ]
        )

# ---------------------------------------------------------------------------------------------------------

    def notification(self, namespace, domain, service, data) -> None:

        self._notification(data['message'])

# ---------------------------------------------------------------------------------------------------------

    def _notification(self, message) -> None:

        self.log(f'\t{message}', level="INFO")

        self.run_sequence(
            [
                {'notify/disc0rd': {'title': 'FIXME: Notification', 'message': 'FIXME: ' + message, 'target': "1250932196613685313"}},
                # {'notify/pushbullet': {'title': 'Deferred notification', 'message': message}}
            ]
        )

# ---------------------------------------------------------------------------------------------------------

    def initialised(self, namespace, domain, service, data) -> None:

        name = data.get('name', 'unknown')
        entity_id = 'media_player.study'
        message = f'{name} initialised'
        snapshot = False
        announce = data.get('announce', False)

        self.queue.put([entity_id, message, snapshot, announce])
        if self.lib.get_verbose_debug():
            print(f'\tinitialised put queue entity_id={entity_id} message={message} snapshot={snapshot} announce={announce}')

# ---------------------------------------------------------------------------------------------------------

    def _announceable(self, hint) -> bool:

        if self.get_state('input_boolean.force_announcement') == 'on':
            return True

        # mute_announcement has precendence over hint
        if self.get_state('input_boolean.mute_announcement') == 'on':
            return False

        if hint is False:
            return False

        dow = self.lib.dow()

        announceable1 = self.now_is_between(f'{self.START:02d}:00:00', f'{self.END:02d}:30:00')
        announceable2 = (dow in (2,4) and self.now_is_between('09:27:00', '09:58:00')) or (dow in (1,5) and self.now_is_between('16:27:00', '16:58:00'))

        if self.lib.get_verbose_debug():
            print(f'\tannouncable1={announceable1} announcable2={announceable2}, announceable1 and not announceable2={announceable1 and not announceable2}')

        return announceable1 and not announceable2

# -------------------------------------------------------------------------------------------------

    def _status(self) -> None:

        status = '\n\n\t--\n'

        self.log(f'{status}')

        print(self.queue)

# ---------------------------------------------------------------------------------

    def bins_announce(self, announce_type, force=False):

        # https://www.scambs.gov.uk/recycling-and-bins/find-your-household-bin-collection-day#id=100091416947
        # baseurl = 'https://refusecalendarapi.azurewebsites.net/calendar/ical/'
        baseurl = 'https://servicelayer3c.azure-api.net/wastecalendar/calendar/ical/'
        url = baseurl+'100091416947'  # was '100091416948'
        bins = []
        dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow     # pylint: disable=E0401

        if announce_type == 'preannounce':
            dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow     # pylint: disable=E0401
        else:
            dow = arrow.now().floor('day').shift(hours=6).shift(days=1)  # 6am tomorrow       # pylint: disable=E0401

        loop = True
        pattern = r'^Rate limit is exceeded. Try again in (\d+) seconds.$'

        while loop:
            r = requests.get(url)  # pylint: disable=E0401
            t = r.text
            if t[0] == '{':
                y = json.loads(t)
                a = re.search(pattern, y['message'])
                s = a.groups(1)[0]
                self.lib.delay(int(s))
            else:
                loop = False

        c = Calendar(t)  # pylint: disable=E0401

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

            self._announce(message=phrase)

# ---------------------------------------------------------------------------------------------------------

    def bins_preannounce(self, kwargs={}) -> None:

        self.bins_announce('preannounce', self.lib.get_testing())

# ---------------------------------------------------------------------------------------------------------

    def bins_announce1(self, kwargs={}) -> None:

        self.bins_announce('announce1')

# ---------------------------------------------------------------------------------------------------------

    def bins_announce2(self, kwargs={}) -> None:

        self.bins_announce('announce2')

# ---------------------------------------------------------------------------------------------------------

    def vouchers_announce(self, kwargs={}) -> None:

        dow = self.lib.dow()

        with open('/homeassistant/data.yaml', 'r', encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                self.log(e, level="ERROR")

        vouchers = data['vouchers']
        force = vouchers['force']
        value = vouchers['value']
        expiry = vouchers['expiry']
        force = True

        if self.lib.is_mock_run():
            value = 1
            expiry = 'whenever'

        if dow == 2 or force:
            if value > 0:
                phrase = ' '.join([str(value), 'pounds', 'of', 'vouchers', 'expiring', 'end', 'of', expiry])
                self.log(f'\tphrase={phrase}')
                self._announce(message=phrase)
            else:
                self.log('\tno expiring vouchers', level='WARNING')

# -------------------------------------------------------------------------------------------------

    def test_announce_event(self, event, data, kwargs) -> None:

        kwargs = {'entity_id': 'media_player.study', 'message': 'This is the first test message', 'snapshot': False, 'announce': True}
        # await
        self.announce('default', 'announcer', 'announce', kwargs)
        kwargs['message'] = 'This is the second'
        # await
        self.announce('default', 'announcer', 'announce', kwargs)
        kwargs['message'] = 'And this is the third'
        # await
        self.announce('default', 'announcer', 'announce', kwargs)

# -------------------------------------------------------------------------------------------------

    def test_broadcast_event(self, event, data, kwargs) -> None:

        kwargs = {'broadcast_entity_id': self.BROADCAST_ENTITY_ID, 'other_entity_id': self.OTHER_ENTITY_ID,'message': 'This is the first test message', 'snapshot': True, 'announce': True, 'volume': 0.3}
        # await
        self.broadcast('default', 'announcer', 'broadcast', kwargs)
        kwargs['message'] = 'This is the second'
        # await
        self.broadcast('default', 'announcer', 'broadcast', kwargs)
        kwargs['message'] = 'And this is the third'
        # await
        self.broadcast('default', 'announcer', 'broadcast', kwargs)

# ---------------------------------------------------------------------------------------------------------
