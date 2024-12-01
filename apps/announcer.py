# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import threading
import time
import json
import re
import uuid
import traceback
from queue import Queue
import yaml
import arrow  # pylint: disable=E0401
import requests  # type: ignore # pylint: disable=E0401

from ics import Calendar # type: ignore # pylint: disable=E0401

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611
# app_lock decorator
import adbase as ad # type: ignore pylint: disable=E0401 disable=W0611
# import myconstants as const # type: ignore # pylint: disable=E0401

class Announcer(Hass): # pylint: disable=W0212 disable=W0621
    """This is the documentation for Announcer"""

    lib = None
    const = None
    queue = None
    announce_queue = None
    notify_queue = None
    announce_lock = None
    cache = True

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """Documentation for Announcer"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.queue = Queue(maxsize = 0)
        self.notify_queue = Queue(maxsize = 0)
        self.announce_queue = Queue(maxsize = 0)

        self.register_service('announcer/announce', self.announce_service)
        self.register_service('announcer/broadcast', self.broadcast_service)
        self.register_service('announcer/notification', self.notification_service)
        self.register_service('announcer/initialised', self.initialised_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.vouchers_event, 'vouchers')
        self.listen_event(self.bins_event, 'bins1')
        self.listen_event(self.bins_event, 'bins2')
        self.listen_event(self.bins_event, 'bins3')
        self.listen_event(self.announce_event, 'announce')
        self.listen_event(self.announce_event, 'announcement')
        self.listen_event(self.broadcast_event, 'broadcast')

        self.run_daily(self.bins, '19:30:00', event='preannounce')
        self.run_daily(self.bins, '17:30:00', event='announce')
        self.run_daily(self.bins, '19:30:00', event='followup')
        self.run_daily(self.vouchers_announce, '19:30:30')

        self.announce_lock = threading.Lock()
        announce_thread = threading.Thread(target=self.announce_worker)
        announce_thread.daemon = True
        announce_thread.start()
        notify_thread = threading.Thread(target=self.notify_worker)
        notify_thread.daemon = True
        notify_thread.start()

        print(self.const.ANNOUNCE_VOLUME)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def announce_service(self, namespace, domain, service, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, kwargs={kwargs}', level='DEBUG')

        entity_id = kwargs['entity_id']
        other_id = list(set(self.const.ALL_ENTITY_ID) - set([entity_id]))
        message = kwargs['message']
        volume = kwargs.get('volume', self.const.ANNOUNCE_VOLUME)
        announce = kwargs.get('announce', True)
        timestamp = kwargs.get('timestamp', None)

        entry = self.prepare('announce_service', entity_id, other_id, volume, message, announce, timestamp, False) # force=False
        with self.announce_lock:
            self.announce(entry)

# -----------------------------------------------------------------------------------

    def broadcast_service(self, namespace, domain, service, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, kwargs={kwargs}', level='DEBUG')

        entity_id = kwargs.get('broadcast_entity_id', self.const.BROADCAST_ENTITY_ID)
        other_id = kwargs.get('other_entity_id', self.const.OTHER_ENTITY_ID)
        volume = kwargs.get('volume', 0.5)
        message = kwargs['message']
        announce = kwargs.get('announce', True)
        timestamp = kwargs.get('timestamp', None)

        if self.lib.get_testing():
            entity_id = 'media_player.study'
            other_id = []
            volume = self.const.ANNOUNCE_VOLUME

        entry = self.prepare('broadcast_service', entity_id, other_id, volume, message, announce, timestamp, True) # force=True
        with self.announce_lock:
            self.announce(entry)

# -----------------------------------------------------------------------------------

    def notification_service(self, namespace, domain, service, data) -> None:

        notify_type = data.get('type', 'desktop')
        message = data.get('message', 'default message')

        self.notification(notify_type, message)

# -----------------------------------------------------------------------------------

    def initialised_service(self, namespace, domain, service, data) -> None:

        name = data.get('name', 'unknown')
        message = f'{name} initialised'

        self.notification('desktop', message)

# -----------------------------------------------------------------------------------

    def announce_event(self, event, data, kwargs) -> None:

        message = 'first announce message'

        for attempt in range(3):
            if attempt == 1:
                message = 'second announce message'
            elif attempt == 2:
                message = 'third announce message'

            self.call_service('announcer/announce',
                              entity_id='media_player.study',
                              message=message,
                            #   volume=self.const.ANNOUNCE_VOLUME,
                              announce=True,
                              timestamp=None)
            time.sleep(2.0)

# -----------------------------------------------------------------------------------

    def broadcast_event(self, event, data, kwargs) -> None:

        entity_id = self.const.BROADCAST_ENTITY_ID
        other_id = self.const.OTHER_ENTITY_ID
        volume = 0.5

        message = 'first broadcast message'

        for attempt in range(3):
            if attempt == 1:
                message = 'second broadcast message'
            elif attempt == 2:
                message = 'third broadcast message'

            self.call_service('announcer/broadcast',
                              entity_id=entity_id,
                              other_id=other_id,
                              message=message,
                              volume=volume,
                              timestamp=None)
            time.sleep(2.0)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status()

# -----------------------------------------------------------------------------------

    def vouchers_event(self, event, data, kwargs) -> None:

        self.vouchers_announce({})

# -----------------------------------------------------------------------------------

    def bins_event(self, event, data, kwargs) -> None:

        self.bins({'event': event})

# -----------------------------------------------------------------------------------

    @ad.app_lock
    def announce(self, entry) -> None: # pylint: disable=R0914

        (uu_id, method_id, entity_list, other_id, volume, message, announce, timestamp, force) = entry

        verbose = self.lib.get_verbose_debug()

        if entity_list is None:
            self.log('entity_list is unspecified', level='ERROR')
            traceback.print_stack()
            return

        entity_list = [entity_list] if isinstance(entity_list, str) else entity_list

        if self.lib.get_testing():
            entity_list = [self.const.STUDY]

        if self.announceable(announce) or force:
            if verbose:
                status = f'\n\n\tin announce\t{uu_id} entity_id={entity_list} volume={volume} message="{message}" announce={announce} force={force}\n'
                status += f'\t\t\t{uu_id} other_id={other_id}\n'
                status += self.print_queue(True)
                self.log(status, level='DEBUG')

            media_content_id = f'media-source://tts/cloud?message="{message}"'

            # entity_id = entity_list[0]

            # self.call_service('sonos/snapshot', entity_id='all', with_group=True)

            # if len(entity_list) > 1:
            #     for entity in entity_list:
            #         self.call_service('media_player/unjoin', entity_id=entity)
            #         self.call_service('media_player/repeat_set', entity_id=entity, repeat='off')
            #         self.call_service('media_player/volume_set', entity_id=entity, volume_level=volume)
            #         self.call_service('media_player/volume_mute', entity_id=entity, is_volume_muted=False)

            #     self.call_service('media_player/join', entity_id=entity_id, group_members=entity_list[1:])

            #     for entity in other_id:
            #         self.call_service('media_player/volume_mute', entity_id=entity, is_volume_muted=True)

            #     for entity in entity_list:
            #         self.call_service('media_player/volume_mute', entity_id=entity, is_volume_muted=False)

            entity_id = entity_list if method_id == "announce_service" else self.const.ALL_ENTITY_ID

            self.call_service('media_player/play_media',
                            entity_id=entity_id,
                            media_content_type="music",
                            media_content_id=media_content_id,
                            announce=True)

            time.sleep(max(len(message) * self.const.SECONDS_PER_CHARACTER, self.const.MINIMUM_MESSAGE_LENGTH))

            # if method_id == "broadcast_service":
            #     time.sleep(5)

            # self.call_service('sonos/restore', entity_id='all', with_group=True)

            # time.sleep(0 if method_id == "announce_service" else 10)

            if timestamp:
                self.call_service('timestamp/set', name=timestamp)

        self.notification('desktop', message)

# -----------------------------------------------------------------------------------

    def notification(self, notify_type, message) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\t{notify_type} notification message={message}', level="DEBUG")

        self.call_service('notify/disc0rd', title='Desktop notification', message=message, target='1250932196613685313')

# -----------------------------------------------------------------------------------

    def bins(self, kwargs) -> None:

        event = kwargs.get('event', None)

        if event in ('preannounce','bins1') :
            self.bins_announce('preannounce', self.lib.get_testing())
        elif event in ('announce', 'bins2'):
            self.bins_announce('announce', self.lib.get_testing())
        elif event in ('followup', 'bins3'):
            self.bins_announce('followup', self.lib.get_testing())

# -----------------------------------------------------------------------------------

    def bins_announce(self, event, force=False):

        # https://www.scambs.gov.uk/recycling-and-bins/find-your-household-bin-collection-day#id=100091416947
        # baseurl = 'https://refusecalendarapi.azurewebsites.net/calendar/ical/'
        baseurl = 'https://servicelayer3c.azure-api.net/wastecalendar/calendar/ical/'
        url = baseurl+'100091416947'
        bins = []

        # 6am day after tomorrow or 6am tomorrow
        dow = self.now().floor('day').shift(hours=6).shift(days=2) if event == 'preannounce' else self.now().floor('day').shift(hours=6).shift(days=1)

        loop = True

        while loop:
            # r = requests.get(url) # FIXME: remove?
            # t = r.text
            t = requests.get(url).text
            if t[0] == '{':
                y = json.loads(t)
                a = re.search(r'^Rate limit is exceeded. Try again in (\d+) seconds.$', y['message'])
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

            phrase = ''

            if event == 'preannounce':
                phrase = ' '.join(['It', 'is', 'the', ' '.join(bins), 'this', 'week'])
            elif event == 'announce':
                phrase = ' '.join(['Can', 'you', 'put', 'the', ' '.join(bins), 'out', 'please'])
            elif event == 'followup':
                phrase = ' '.join(['Have', 'you', 'put', 'the', ' '.join(bins), 'out'])
            else:
                phrase = 'An error has occured in bins announce'

            entry = self.prepare('broadcast_service', self.const.BROADCAST_ENTITY_ID, self.const.OTHER_ENTITY_ID, 0.5, phrase, True, f'bins_{event}', True) # force=True
            with self.announce_lock:
                self.announce(entry)

# -----------------------------------------------------------------------------------

    def vouchers_announce(self, kwargs) -> None:

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

        if self.lib.is_mock_run():
            value = 1
            expiry = 'whenever'

        if dow in (2,5) or force:
            if value > 0:
                message = ' '.join([str(value), 'pounds', 'of', 'vouchers', 'expiring', 'end', 'of', expiry])
                entry = self.prepare('broadcast_service', self.const.BROADCAST_ENTITY_ID, self.const.OTHER_ENTITY_ID, 0.5, message, True, 'vouchers', True) # force=True
                with self.announce_lock:
                    self.announce(entry)
            else:
                self.log('\tno expiring vouchers', level='WARNING')

# -----------------------------------------------------------------------------------

    def announce_worker(self, *args, **kwargs) -> None:

        self.log('\tannounce_worker listening')

        while True:
            entry = self.get_entry(self.announce_queue)
            with self.announce_lock:
                self.announce(entry)

# -----------------------------------------------------------------------------------

    def notify_worker(self, *args, **kwargs) -> None:

        self.log('\tnotify_worker listening')

        while True:
            entry = self.get_entry(self.notify_queue)
            with self.announce_lock:
                self.announce(entry)

# -----------------------------------------------------------------------------------

    def prepare(self, method_id, entity_id, other_id, volume, message, announce, timestamp, delay) -> list: # pylint: disable=R0913

        uu_id = uuid.uuid4()

        if self.lib.get_testing():
            volume = self.const.ANNOUNCE_VOLUME
            entity_id = ['media_player.study']
            other_id = list(set(self.const.ALL_ENTITY_ID) - set(entity_id))

        if self.lib.get_verbose_debug():
            status = f'\n\n\tin {method_id} put {uu_id} entity_id={entity_id} volume={volume} message="{message}" announce={announce} timestamp={timestamp} delay={delay}\n'
            status += f'\t\t\t{uu_id} other_id={other_id}\n'

        return [uu_id, method_id, entity_id, other_id, volume, message, announce, timestamp, delay]

# -----------------------------------------------------------------------------------

    def now(self):

        return arrow.now() # pylint: disable=E1101

# -----------------------------------------------------------------------------------

    # @ad.app_lock
    def get_entry(self, queue) -> list:

        # with self._lock:
        # result = self.announce_queue.get()
        result = queue.get()

        return result

# -----------------------------------------------------------------------------------

    # @ad.app_lock
    def put_entry(self, queue, entry) -> None:

        # with self._lock:
        # self.announce_queue.put(entry)
        queue.put(entry)

# -----------------------------------------------------------------------------------

    # @ad.app_lock
    def print_queue(self, return_result=False) -> None:

        status = '\n\tremaining queue:\n'

        for item in self.queue.queue:
            status += f'\t\t{item}\n'

        if return_result:
            return status

        self.log(f'\n{status}')

# -----------------------------------------------------------------------------------

    def announceable(self, hint) -> bool:

        # force_announcement has precendence over both mute_announcement and hint
        if self.get_state('input_boolean.force_announcement') == 'on' and hint is True:
            return True # only return true if forced and hint is true

        # mute_announcement has precendence over hint
        if self.get_state('input_boolean.mute_announcement') == 'on' or hint is False:
            return False # is muted or hint is false

        dow = self.lib.dow()

        announceable1 = self.now_is_between(f'{self.const.START_HOUR:02d}:30:00', f'{self.const.END_HOUR:02d}:30:00')
        announceable2 = (dow in (2,4) and self.now_is_between('09:27:00', '09:58:00')) or (dow in (1,5) and self.now_is_between('16:27:00', '16:58:00'))

        if self.lib.get_verbose_debug():
            self.log(f'\tannounceable1={announceable1} announceable2={announceable2}, announceable1 and not announceable2={announceable1 and not announceable2}', level='DEBUG')

        return announceable1 and not announceable2

# -----------------------------------------------------------------------------------

    def status(self) -> None:

        # status = '\n\n'
        # self.log(f'{status}')

        self.print_queue()

# -----------------------------------------------------------------------------------
