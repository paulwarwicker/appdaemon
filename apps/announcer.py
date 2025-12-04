# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import threading
import json
import re
import uuid
# from datetime import datetime, time, timedelta # pylint: disable=unused-import

from typing import Optional
from typing import TYPE_CHECKING, cast

from ics import Calendar # type: ignore # pylint: disable=E0401

import yaml
import requests  # type: ignore # pylint: disable=E0401
import arrow  # type: ignore # pylint: disable=E0401
import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
# app_lock decorator
import adbase as ad # type: ignore pylint: disable=E0401 disable=W0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Announcer(Hass): # pylint: disable=W0212 disable=W0621
    """This is the documentation for Announcer"""

    announce_lock: Optional[threading.Lock] = None
    cache = True
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """Documentation for Announcer"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

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

        self.log('announcer initialised -----------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def announce_service(self, namespace, domain, service, kwargs) -> None:

        self.log(f'namespace={namespace}, domain={domain}, service={service}, kwargs={kwargs}', level='DEBUG')

        entity_id = kwargs.get('entity_id', const.STUDY_SPEAKER)
        message = kwargs.get('message', 'Default message')
        announce = kwargs.get('announce', True)
        timestamp = kwargs.get('timestamp', None)
        force = kwargs.get('force', False)
        volume = kwargs.get('volume', const.STUDY_ANNOUNCE_VOLUME_LOW if self.lib.is_night() else const.STUDY_ANNOUNCE_VOLUME)

        entry = self.prepare(entity_id, message, timestamp, announce, force, volume)

        with self._ensure_announce_lock():
            self.announce(entry)

# -----------------------------------------------------------------------------------

    def broadcast_service(self, namespace, domain, service, kwargs) -> None:

        self.log(f'namespace={namespace}, domain={domain}, service={service}, kwargs={kwargs}', level='DEBUG')

        message = kwargs.get('message', 'Default message')
        announce = kwargs.get('announce', True)
        timestamp = kwargs.get('timestamp', None)
        force = kwargs.get('force', False)
        volume = kwargs.get('volume', const.ANNOUNCE_VOLUME_LOW if self.lib.is_night() else const.ANNOUNCE_VOLUME)

        entry = self.prepare(None, message, timestamp, announce, force, volume)

        with self._ensure_announce_lock():
            self.announce(entry)

# -----------------------------------------------------------------------------------

    def notification_service(self, namespace, domain, service, data) -> None:

        notify_type = data.get('type', 'desktop')
        message = data.get('message', 'default message')
        timestamp = data.get('timestamp', None)

        self.notification(notify_type, message)

        if timestamp is not None:
            self.call_service('timestamp/set', name=timestamp)

# -----------------------------------------------------------------------------------

    def initialised_service(self, namespace, domain, service, data) -> None:

        name = data.get('name', 'unknown')

        message = f'{name} initialised'
        spacer = (80 - len(name) - 11) * '-'

        self.log(f'{message} {spacer}', level='INFO')
        self.notification('desktop', message)

# -----------------------------------------------------------------------------------

    def announce_event(self, event, data, kwargs) -> None:

        messages = ['first announce message', 'second announce message', 'third announce message']

        for i, message in enumerate(messages):
            self.run_in(self._announce, i * 2, entity_id=const.STUDY_SPEAKER, message=message)

# -----------------------------------------------------------------------------------

    def broadcast_event(self, event, data, kwargs) -> None:

        messages = ['first broadcast message', 'second broadcast message', 'third broadcast message']

        for i, message in enumerate(messages):
            self.run_in(self._announce, i * 2, entity_id=const.KITCHEN_SPEAKER, message=message)

# -----------------------------------------------------------------------------------

    def _announce(self, kwargs) -> None:
        """Helper scheduled via run_in to perform a single announce call."""

        entity_id = kwargs.get('entity_id', const.STUDY_SPEAKER)
        message = kwargs.get('message', 'Default message')
        volume = kwargs.get('volume', None)

        if volume is None:
            if entity_id == const.STUDY_SPEAKER:
                volume = const.STUDY_ANNOUNCE_VOLUME_LOW if self.lib.is_night() else const.STUDY_ANNOUNCE_VOLUME
            else:
                volume = const.ANNOUNCE_VOLUME_LOW if self.lib.is_night() else const.ANNOUNCE_VOLUME

        entry = self.prepare(entity_id, message, 'general', True, True, volume)

        with self._ensure_announce_lock():
            self.announce(entry)

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

        (uu_id, entity_id, message, timestamp, announce, force, volume) = entry

        entity_ids = [const.STUDY_SPEAKER, const.HALLWAY_SPEAKER] if self.lib.get_testing() else [const.KITCHEN_SPEAKER]
        # entity_ids = const.BROADCAST_ENTITY_ID if entity_id is None else [entity_id]

        if self.announceable(announce) or force:

            self.call_service('media_player/play_media',
                              entity_id=entity_ids,
                              media_content_type='music',
                              media_content_id='http://homeassistant.local:8123/local/bing.mp3',
                              announce=True,
                              extra={'volume': volume})

            self.lib.delay(1.0) # give it time to play

            self.call_service('media_player/play_media',
                              entity_id=entity_ids,
                              media_content_type='music',
                              media_content_id=f'media-source://tts/cloud?message="{message}"',
                              announce=True,
                              extra={'volume': volume})

            self.lib.delay(max(len(message) * const.SECONDS_PER_CHARACTER, const.MINIMUM_MESSAGE_LENGTH))

            if timestamp:
                self.call_service('timestamp/set', name=timestamp)

        self.notification('desktop', message)

# -----------------------------------------------------------------------------------

    def notification(self, notify_type, message) -> None:

        # self.call_service('notify/disc0rd', title='Desktop notification', message=message, target='1250932196613685313')
        # self.call_service('notify/disc0rd', title='Desktop notification', message=message, service_data={'target': '1250932196613685313'})
        self.call_service('notify/disc0rd', service_data={
            'target': '1250932196613685313',
            'title': 'Desktop notification',
            'message': message
        })

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

    def fetch_calendar(self, url) -> Calendar:

        try:
            resp = requests.get(url=url, timeout=5.0)
            resp.raise_for_status()
        except requests.RequestException as exc:
            self.log(f"Failed to fetch bin calendar: {exc}", level="ERROR")
            return False

        while True:
            text = resp.text

            # JSON error message?
            if text.startswith("{"):
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    break

                # Rate limit check
                m = re.match(r"^Rate limit is exceeded\. Try again in (\d+) seconds\.$",
                            data.get("message", ""))

                if m:
                    delay_seconds = int(m.group(1))
                    self.lib.delay(self, delay_seconds)

                    # retry request after delay
                    try:
                        resp = requests.get(url=url, timeout=5.0)
                        resp.raise_for_status()
                    except requests.RequestException as exc:
                        self.log(f"Failed to fetch bin calendar: {exc}", level="ERROR")
                        return False

                    continue  # re-check response
            break

        return Calendar(text)

# -----------------------------------------------------------------------------------

    def bins_announce(self, event, test=False):

        # https://www.scambs.gov.uk/recycling-and-bins/find-your-household-bin-collection-day#id=100091416947
        baseurl = 'https://servicelayer3c.azure-api.net/wastecalendar/calendar/ical/'
        url = baseurl+'100091416947'
        bins = []

        # 6am day after tomorrow or 6am tomorrow
        # day of week ??
        dow = arrow.now().floor('day').shift(hours=6).shift(days=2) if event == 'preannounce' else arrow.now().floor('day').shift(hours=6).shift(days=1)

        # dt = datetime.now()
        # # floor to day
        # start_of_day = datetime.combine(dt.date(), time())
        # # shift 6 hours and 2 days
        # result = start_of_day + timedelta(hours=6, days=2)

        c = self.fetch_calendar(url)

        for e in iter(c.timeline.overlapping(dow, dow)):
            bins.append(e.name.split()[0].lower())

        if test:
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

            entry = self.prepare(None, phrase, f'bins_{event}', announce=True, force=False)
            with self._ensure_announce_lock():
                self.announce(entry)

# -----------------------------------------------------------------------------------

    def vouchers_announce(self, kwargs) -> None:

        dow = self.lib.dow()

        data = {}

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
                entry = self.prepare(None, message, 'vouchers', announce=True, force=force)
                with self._ensure_announce_lock():
                    self.announce(entry)
            else:
                self.log('\tno expiring vouchers', level='WARNING')

# -----------------------------------------------------------------------------------

    def prepare(self, entity_id, message, timestamp, announce, force=False, volume=50) -> list: # pylint: disable=R0913

        uu_id = uuid.uuid4()

        if self.lib.get_testing():
            entity_id = const.STUDY_SPEAKER
            volume = const.STUDY_ANNOUNCE_VOLUME_LOW if self.lib.is_night() else const.STUDY_ANNOUNCE_VOLUME

        return [uu_id, entity_id, message, timestamp, announce, force, volume]

# -----------------------------------------------------------------------------------

    def announceable(self, hint) -> bool:

        # force_announcement has precendence over both mute_announcement and hint
        if self.get_state('input_boolean.force_announcement') == 'on' and hint is True:
            return True # only return true if forced and hint is true

        # mute_announcement has precendence over hint
        if self.get_state('input_boolean.mute_announcement') == 'on' or hint is False:
            return False # is muted or hint is false

        dow = self.lib.dow()

        announceable1 = self.now_is_between(f'{const.START_HOUR:02d}:30:00', f'{const.END_HOUR:02d}:30:00')
        announceable2 = (dow in (2,4) and self.now_is_between('09:27:00', '09:58:00')) or (dow in (1,5) and self.now_is_between('16:27:00', '16:58:00'))

        if self.lib.get_verbose_debug():
            self.log(f'\tannounceable1={announceable1} announceable2={announceable2}, announceable1 and not announceable2={announceable1 and not announceable2}', level='DEBUG')

        return announceable1 and not announceable2

# -----------------------------------------------------------------------------------

    def status(self):

        self.log('\n\n')

        return

# -----------------------------------------------------------------------------------

    def _ensure_announce_lock(self) -> threading.Lock:
        """Ensure announce_lock exists and return it."""

        if self.announce_lock is None:
            self.announce_lock = threading.Lock()
        return self.announce_lock

# -----------------------------------------------------------------------------------
