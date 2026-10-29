# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# Lemon & Einar K - Tenacity (Solarsoul Chill Breaks Remix)

import random
from datetime import datetime, timedelta

from dateutil import parser # pylint: disable=import-error

import constants as const
from automationbase import AutomationBase  # type: ignore

class Alarms(AutomationBase):
    """Documentation for Alarms"""

    rota = None
    early_alarm_callback = None
    normal_alarm_callback = None
    override = False
    default_early_alarm_schedule = 'daily'  # weekday|daily|none
    callbacks = [None, None, None]

    NUM_WORDS = {
        0: "twelve", 1: "one", 2: "two", 3: "three", 4: "four",
        5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
        10: "ten", 11: "eleven", 12: "twelve",
        13: "thirteen", 14: "fourteen", 15: "fifteen",
        16: "sixteen", 17: "seventeen", 18: "eighteen",
        19: "nineteen", 20: "twenty", 21: "twenty one",
        22: "twenty two", 23: "twenty three", 24: "twenty four",
        25: "twenty five", 26: "twenty six", 27: "twenty seven",
        28: "twenty eight", 29: "twenty nine"
    }

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise alarms"""

        super().initialize()

        self.rota = self.generate_rota(datetime(2024, 5, 16).date(), 12)

        self.register_service('alarms/reset', self.reset_service)

        self.listen_event(self.set_alarm_state_event, 'set_alarm_state')
        self.listen_event(self.status_event, 'status')

        self.listen_state(self.set_early_alarm_callback,  'input_boolean.early_alarm', new='on', action='set')
        self.listen_state(self.set_early_alarm_callback,  'input_boolean.early_alarm', new='off', action='cancel')
        self.listen_state(self.disable_physical_training, 'input_boolean.early_alarm', new='off')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='on', action='set')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='off', action='cancel')
        self.listen_state(self.reset_alarms, 'input_boolean.reset_alarms', new='on')

        self.run_daily(self.set_alarm_state, '20:30:00') # make sure before max goes to bed

        # alarms will be set daily as above. can also set manually by firing event set_alarm_state
        # enabling/disabling alarms in UI will announce if set, but announce here if we have reloaded code
        self.show_alarm_time('early')
        self.show_alarm_time('normal')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def reset_service(self, namespace, domain, service, kwargs) -> None:
        """reset alarms"""

        self.reset_alarms('', '', '', '', {})

# -----------------------------------------------------------------------------------

    def set_alarm_state_event(self, event, data, kwargs):

        self.set_alarm_state({})

# -----------------------------------------------------------------------------------

    def set_alarm_state(self, kwargs):

        self._log_function_name(start=True)

        self.cancel_alarms()
        self.set_early_alarm()
        self.set_normal_alarm()

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_early_alarm(self):

        self._log_function_name(start=True)

        state, alarm_time, timestamp, ids = self.get_early_alarm_time()
        self.set_early_alarm_time(state, alarm_time, timestamp, ids)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_normal_alarm(self):

        self._log_function_name(start=True)

        state, alarm_time, timestamp, ids = self.get_normal_alarm_time()
        self.set_normal_alarm_time(state, alarm_time, timestamp, ids)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def get_early_alarm_time(self, backup=False):

        self._log_function_name(start=True)

        hour = minute = second = 12
        parts = const.EARLY_ALARM_TIME.split(':')

        try:
            if len(parts) >= 1:
                hour = int(parts[0])
            if len(parts) >= 2:
                minute = int(parts[1])
            if len(parts) >= 3:
                second = int(parts[2])
        except (ValueError, TypeError) as exc:
            self.log(f'Invalid EARLY_ALARM_TIME "{const.EARLY_ALARM_TIME}" - using {hour:02d}:{minute:02d}:{second:02d}: {exc}', level='WARNING')

        alarm_time = f'{hour:02d}:{minute:02d}:{second:02d}'
        timestamp = hour * 3600 + minute * 60 + second

        state = 'on' if self.get_state('input_boolean.override') == 'on' else 'off'

        self._log_function_name(start=False)

        return state, alarm_time, timestamp, const.SUNSETS_ALARM

# -----------------------------------------------------------------------------------

    def get_normal_alarm_time(self):

        self._log_function_name(start=True)

        dow = self._dow()

        # setting alarm for tomorrow. usually set at 20:30 the previous evening. if mon or tue evening or tues wed morning -> setup for early alarms
        # dow: 1 - mon, 2 - tue, 3 - wed, 4 - thu, 5 - fri, 6 - sat, 7 - sun
        later = not (self.now_is_between('06:00:00', '23:59:59') and (dow in (1,2))) or (self.now_is_between('00:00:00', '05:59:59') and (dow in (2,3))) # (1 <= dow <= 2)

        hour = minute = second = 12

        if later:
            parts = const.LATE_ALARM_TIME.split(':')
            alarm_time = const.LATE_ALARM_TIME
            desc = 'LATE_ALARM_TIME'
            ids = const.PROGRESSIVE_ALARM # always progress if later
        else:
            parts = const.NORMAL_ALARM_TIME.split(':')
            alarm_time = const.NORMAL_ALARM_TIME
            desc = 'NORMAL_ALARM_TIME'
            ids = const.NORMAL_ALARM # varied if earlier

        try:
            if len(parts) >= 1:
                hour = int(parts[0])
            if len(parts) >= 2:
                minute = int(parts[1])
            if len(parts) >= 3:
                second = int(parts[2])
        except (ValueError, TypeError) as exc:
            self.log(f'Invalid {desc} "{alarm_time}" - using {hour:02d}:{minute:02d}:{second:02d}: {exc}', level='WARNING')

        alarm_time = f'{hour:02d}:{minute:02d}:{second:02d}'
        timestamp = hour * 3600 + minute * 60 + second

        state = 'on'

        self._log_function_name(start=False)

        return state, alarm_time, timestamp, ids

# -----------------------------------------------------------------------------------

    def set_early_alarm_time(self, state, alarm_time, timestamp, ids):

        self._log_function_name(start=True)

        time_entity_id = 'input_datetime.early_alarm'
        bool_entity_id = 'input_boolean.early_alarm'

        parts = alarm_time.split(':')

        hour = parts[0]
        minute = parts[1]
        seconds = parts[2] if len(parts) >=3 else 0

        if ids is None:
            ids = const.EARLY_ALARM

        self.log(f'set_early_alarm_time {state=} {alarm_time=} {timestamp=} {hour=} {minute=} {seconds=} {ids=}', level="DEBUG")

        self.set_state(time_entity_id, state=f"{alarm_time}", attributes={"timestamp": timestamp, "hour": hour, "minute": minute, "seconds": seconds})
        self.set_state(bool_entity_id, state=state)

        if state == 'on':
            self.set_early_alarm_callback(bool_entity_id, 'state', 'off', 'on', {'action': 'set', 'ids': ids})
        else:
            self.set_early_alarm_callback(bool_entity_id, 'state', 'on', 'off', {'action':'cancel'})

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_normal_alarm_time(self, state, alarm_time, timestamp, ids):

        self._log_function_name(start=True)

        time_entity_id = 'input_datetime.normal_alarm'
        bool_entity_id = 'input_boolean.normal_alarm'

        parts = alarm_time.split(':')

        hour = parts[0]
        minute = parts[1]
        seconds = parts[2] if len(parts) >=3 else 0

        if ids is None:
            ids = const.NORMAL_ALARM

        self.log(f'set_normal_alarm_time {state=} {alarm_time=} {timestamp=} {hour=} {minute=} {seconds=} {ids=}', level="DEBUG")

        self.set_state(time_entity_id, state=f"{alarm_time}", attributes={"timestamp": timestamp, "hour": hour, "minute": minute, "seconds": seconds})
        self.set_state(bool_entity_id, state=state)

        if state == 'on':
            self.set_normal_alarm_callback(bool_entity_id, 'state', 'off', 'on', {'action': 'set', 'ids': ids})
        else:
            self.set_normal_alarm_callback(bool_entity_id, 'state', 'on', 'off', {'action':'cancel'})

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def show_alarm_time(self, alarm_type, override=None):

        self._log_function_name(start=True)

        _alarm_type = alarm_type

        time_entity_id = f'input_datetime.{alarm_type}_alarm'
        bool_entity_id = f'input_boolean.{alarm_type}_alarm'

        if override is None:
            tm = self._read_time_attrs(time_entity_id)
            if tm is None:
                self.log(f'Unable to read time attributes for {time_entity_id}', level='WARNING')
                alarm_time = None
            else:
                hour, minute = tm
                d = datetime.now() + timedelta(days=1)
                t = datetime(d.year, d.month, d.day, hour, minute, 0, 0)
                alarm_time = f"{t.hour:02d}:{t.minute:02d}"
        else:
            hour = override.hour
            minute = override.minute
            second = override.second
            alarm_time = f"{hour:02d}:{minute:02d}:{second:02d}"

        state = self.get_state(bool_entity_id)

        alarm_words = self.time_to_words(alarm_time) if alarm_time is not None else 'unknown time'

        message = f'The {_alarm_type} morning alarm is set to {alarm_words}' if state == 'on' else f'The {_alarm_type} morning alarm is cancelled'
        volume = const.ANNOUNCE_VOLUME_LOW if self._is_night() else const.STUDY_ANNOUNCE_VOLUME
        self.call_service("announcer/announce", entity_id=const.STUDY_SPEAKER, message=message, volume=volume, announce=True) #, force=True)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cancel_alarms(self):

        self._log_function_name(start=True)

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')

        self.set_state('input_boolean.reset_alarms', state='off')
        self.set_state('input_boolean.alarm_testing', state='off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def reset_alarms(self, entity, attribute, old, new, kwargs):

        self._log_function_name(start=True)

        self.cancel_alarms()
        self.set_state('input_boolean.physical_training', state='off')
        self.set_state('input_boolean.wake_up_boo', state='off')
        self.set_alarm_state({})

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_early_alarm_callback(self, entity, attribute, old, new, kwargs):

        self._log_function_name(start=True)

        action = kwargs['action']
        ids = kwargs.get('ids', None)

        if ids is None:
            ids = const.EARLY_ALARM

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self.early_alarm_callback = self.set_alarm(alarm_type='early', action=action, ids=ids)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def disable_physical_training(self, entity, attribute, old, new, kwargs):

        self._log_function_name(start=True)

        self.set_state('input_boolean.physical_training', state='off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_normal_alarm_callback(self, entity, attribute, old, new, kwargs):

        self._log_function_name(start=True)

        action = kwargs['action']
        ids = kwargs.get('ids', None)

        if ids is None:
            ids = const.NORMAL_ALARM

        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')
        self.normal_alarm_callback = self.set_alarm(alarm_type='normal', action=action, ids=ids)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def _read_time_attrs(self, entity_id: str):
        """Return (hour, minute) from an input_datetime entity or None on failure.

        Handles cases where HA exposes 'hour' but not 'minute' and provides a 'timestamp'
        instead, or where the state string contains the time.
        """

        attrs = self.get_state(entity_id, attribute="attributes")

        if not isinstance(attrs, dict):
            self.log(f'{entity_id} attributes not available or not a dict: {attrs!r}', level='WARNING')
            return None

        hour = attrs.get('hour')
        minute = attrs.get('minute')

        # If minute is missing, try to derive from 'timestamp' (seconds since midnight)
        if minute is None:
            ts = attrs.get('timestamp')
            if isinstance(ts, (int, float)):
                try:
                    total_seconds = int(ts)
                    minute = (total_seconds // 60) % 60
                    if hour is None:
                        hour = (total_seconds // 3600) % 24
                except Exception:
                    minute = None

        # If still missing, try parsing the entity state (e.g. "10:00:00" or "10:00")
        if minute is None:
            state = self.get_state(entity_id)
            if isinstance(state, str):
                try:
                    parts = state.split(':')
                    if len(parts) >= 2:
                        hour = int(parts[0])
                        minute = int(parts[1])
                except Exception:
                    pass

        if hour is None or minute is None:
            self.log(f'{entity_id} missing hour/minute in attributes: {attrs!r}', level='WARNING')
            return None

        try:
            return int(hour), int(minute)
        except (TypeError, ValueError):
            self.log(f'{entity_id} hour/minute not integers: {attrs!r}', level='WARNING')
            return None

# -----------------------------------------------------------------------------------

    def set_alarm(self, **kwargs):

        self._log_function_name(start=True)

        alarm = None
        action = kwargs['action']
        alarm_type = kwargs['alarm_type']
        ids = kwargs.get('ids', None)
        _alarm_type = alarm_type

        if action == 'set' and ids is None:
            if alarm_type == 'early':
                ids = kwargs['ids'] = const.EARLY_ALARM
            else:  # normal
                ids = kwargs['ids'] = const.NORMAL_ALARM
            self.log(f'No ids provided for {alarm_type} alarm; using {ids=}', level='WARNING')

        self.log(f"\t{alarm_type} alarm enabled", level='DEBUG')
        self.log(f"\taction={action}", level='DEBUG')

        bool_entity_id = f'input_boolean.{alarm_type}_alarm'
        time_entity_id = f'input_datetime.{alarm_type}_alarm'

        debug = self._get_alarm_testing()

        if action == 'set':
            # state = self.get_state(time_entity_id, attribute="attributes")
            hm = self._read_time_attrs(time_entity_id)
            if hm is None:
                # cannot determine time; abort setting alarm
                self.log(f'Aborting set_alarm: cannot read time from {time_entity_id=}', level='ERROR')
                self._log_function_name(start=False)
                return None

            hour, minute = hm

            if debug:
                d = (datetime.now() + timedelta(minutes=1)).replace(second=0, microsecond=0)
                hour = d.hour
                minute = d.minute
                second = d.second
                timestamp = hour * 3600 + minute * 60 + second
                alarm_time = f"{hour:02d}:{minute:02d}:{second:02d}"

                self.log(f"\t\tdebug_time={d}", level='DEBUG')

                self.set_state(time_entity_id, state=f"{alarm_time}", attributes={"timestamp": timestamp, "hour": hour, "minute": minute, "seconds": second})
                alarm = self.run_once(self.alarm, alarm_time, **kwargs)
                self.show_alarm_time(_alarm_type, d)
                self._log_function_name(start=False)
                return
            else:
                alarm_time = f"{hour:02d}:{minute:02d}:{0:02d}"

            kwargs.pop('action', None)
            kwargs['ids'] = ids
            # https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_daily
            alarm = self.run_daily(self.alarm, alarm_time, **kwargs)
            # alarm = self.run_daily(self.alarm, alarm_time, ids=ids, alarm_type=_alarm_type)
            self.log(f'\t{_alarm_type} alarm set for {alarm_time=} using {time_entity_id=}. {kwargs=}', level="INFO")
        elif action == 'cancel':
            self.set_state(bool_entity_id, state='off')
            alarm_time = 'unset' # can trace in message below

            alarm = {'early': self.early_alarm_callback, 'normal': self.normal_alarm_callback}.get(_alarm_type)
            self._cancel_timer(alarm, f'{_alarm_type} alarm')
            alarm = None
        else:
            self.log(f"\tUnexpected alarm action {action}", level='WARNING')

        # if _alarm_type == 'normal' or (self.get_state('input_boolean.alarms_disabled') == 'off' and _alarm_type == 'early'):
        self.show_alarm_time(_alarm_type)

        self._log_function_name(start=False)

        return alarm

# -----------------------------------------------------------------------------------

    def alarm(self, kwargs):
        """play alarm"""

        self._log_function_name(start=True)

        alarm_type = kwargs['alarm_type']
        ids = kwargs['ids']
        entity_id = const.STUDY_SPEAKER if self.is_test(kwargs) else const.BEDROOM_SPEAKER

        # media_content_id = self.select_alarm(alarm_type=alarm_type)
        media_content_id = ids[random.randint(0, len(ids) - 1)]  # randomise choice

        if alarm_type == 'early' and self.get_state('input_boolean.wake_up_boo') == 'on':
            media_content_id = const.WAKE_UP_BOO_STREAM # override

        self.log(f'\tPlaying {alarm_type} alarm on {entity_id} with {media_content_id=}', level='INFO')
        self.call_service('sonos/play_thing', entity_id=entity_id, media_content_id=media_content_id, volume_level=const.ALARM_VOLUME, delayed=True)
        self.run_in(self.stop_bedroom_alarm, 60*60)

        if alarm_type == 'early' and self.get_state('input_boolean.physical_training') == 'on':
            self.call_service('lighting/wardrobe_on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def select_alarm(self, **kwargs):
        """select alarm sound"""

        self._log_function_name(start=True)

        alarm_type = kwargs['alarm_type']

        if alarm_type == 'normal':
            ids = const.NORMAL_ALARM
        # elif alarm_type == 'test':
        #     ids = const.PROGRESSIVE_ALARM
        else:
            ids = const.SUNSETS_ALARM

        self._log_function_name(start=False)

        return ids[random.randint(0, len(ids) - 1)]  # randomise choice.

# -----------------------------------------------------------------------------------

    def play_normal_alarm(self, dow=None):
        """play normal alarm if enabled"""

        self._log_function_name(start=True)

        if dow is None:
            dow = self._dow()

        bank_holiday = self._is_bank_holiday()

        self._log_function_name(start=False)

        return self.get_state(entity_id='input_boolean.normal_alarm') == 'on' and (not bank_holiday) and dow <= 5 and dow != 3

# -----------------------------------------------------------------------------------

    def lumie_alarm(self, kwargs):
        """lumie alarm"""

        self._log_function_name(start=True)

        test = 'test' in kwargs
        timedelta(minutes=5).total_seconds()
        seconds = 5*60 if 'test' not in kwargs else 10
        elev = self.get_state('sun.sun', 'elevation')
        enabled = self.get_state('input_boolean.lumie') == 'on' and elev < 5
        dow = self._dow()
        holiday = self._is_bank_holiday()

        if not holiday and enabled and dow <= 5 and dow != 3 or test:
            self.callback[0] = self.run_in_thread(self.lumie_phase, 0, brightness=100,transition=seconds, rgb_color=[255, 180, 10])  # now
            if self.now_is_between('04:00:00', '08:00:00'):
                self.callback[1] = self.run_in_thread(self.lumie_phase, seconds, brightness=250, transition=seconds, rgb_color=[250, 250, 250]) # +5m
            self.callback[2] = self.run_in_thread(self.lumie_off, 4*seconds)  # +20m
        else:
            self.log(f'\tskipping lumie alarm {holiday=}, {enabled=}, {dow=}', level='INFO')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_phase(self, kwargs):

        if self.get_state('input_boolean.lumie') == 'off':
            return

        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']

        self.call_service('lighting/lumie_on', brightness=brightness)

# -----------------------------------------------------------------------------------

    def lumie_off(self, kwargs):

        self.call_service('light/turn_off', entity_id='light.lumie')

# -----------------------------------------------------------------------------------

    def lumie_on(self, kwargs):

        self.fire_event('lumie_wake')

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs):

        status = f'\n\n\tearly_alarm_callback={self.early_alarm_callback}\n'
        status += f'\tnormal_alarm_callback={self.normal_alarm_callback}\n'
        state = self.get_state('input_boolean.default_early_alarm_state')
        status += f'\tdefault_early_alarm_state={state}\n'
        state = self.get_state('input_boolean.default_normal_alarm_state')
        status += f'\tdefault_normal_alarm_state={state}\n'
        state = self.get_state('input_boolean.default_lumie_state')
        status += f'\tdefault_lumie_state={state}\n'
        status += f'\tdefault_early_alarm_schedule={self.default_early_alarm_schedule}\n'

        day = datetime.now().date()
        a_day = timedelta(days=1)

        if self.now_is_between('03:00:01', '23:59:59'):
            day1 = day + a_day # tomorrow
        else:
            day1 = day

        day0 = day1 - a_day # yesterday

        shift0 = self.check_shift(day0)
        shift1 = self.check_shift(day1)

        status += f'\n\t{day0} is {shift0} shift (day0)\n'
        status += f'\t{day1} is {shift1} shift (day1)\n'

        status += '\n'

        day = datetime.now().date()

        if self.now_is_between('03:00:01', '23:59:59'):
            day += a_day # tomorrow

        for _ in range(7):
            shift = self.check_shift(day)
            status += f'\t{day} is {shift} shift\n'
            day += a_day

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    def generate_rota(self, start_date, num_cycles):

        # Shift pattern: 3 days on, 1 day off, 3 days on, 3 days off, 4 days on (night shift), 7 days off, 3 days on, 4 days off
        pattern = [
            (3, 'Day'),
            (1, 'Off'),
            (3, 'Day'),
            (3, 'Off'),
            (4, 'Night'),
            (7, 'Off'),
            (3, 'Night'),
            (4, 'Off')
        ]

        rota = []
        current_date = start_date

        for _ in range(num_cycles):
            for days, shift in pattern:
                for _ in range(days):
                    rota.append((current_date, shift))
                    current_date += timedelta(days=1)

        return rota

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, timer, message=None):

        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='INFO')

# -----------------------------------------------------------------------------------

    def is_test(self, kwargs):

        return kwargs['alarm_type'] == 'test' or self._get_alarm_testing()

# -----------------------------------------------------------------------------------

    def time_to_words(self, time_str, style="british"):
        """
        Convert a time string into natural language.
        style = "british" or "american"
        """
        t = parser.parse(time_str)
        hour = t.hour
        minute = t.minute

        # Special cases
        if hour == 0 and minute == 0:
            return "midnight"
        if hour == 12 and minute == 0:
            if style == 'british':
                return "midday"
            return "noon"

        # 12?hour conversion
        hour_12 = hour % 12 or 12
        next_hour_12 = (hour_12 % 12) + 1

        if style.lower() == "american":
            if minute == 0:
                return f"{self.NUM_WORDS[hour_12]} o'clock"
            else:
                return f"{self.NUM_WORDS[hour_12]} {self.NUM_WORDS[minute]}"

        snapped = (minute // 5) * 5

        # Recompute hour/minute phrasing based on snapped value
        if snapped == 0:
            phrase = f"{self.NUM_WORDS[hour_12]} o'clock"
        elif snapped == 15:
            phrase = f"quarter past {self.NUM_WORDS[hour_12]}"
        elif snapped == 30:
            phrase = f"half past {self.NUM_WORDS[hour_12]}"
        elif snapped == 45:
            phrase = f"quarter to {self.NUM_WORDS[next_hour_12]}"
        elif snapped < 30:
            phrase = f"{self.NUM_WORDS[snapped]} past {self.NUM_WORDS[hour_12]}"
        else:
            phrase = f"{self.NUM_WORDS[60 - snapped]} to {self.NUM_WORDS[next_hour_12]}"

        if snapped == minute:
            return phrase
        return f"just gone {phrase}"

# -----------------------------------------------------------------------------------

    def stop_bedroom_alarm(self, kwargs) -> None:
        """stop bedroom alarm"""

        self.fire_event('stop_bedroom')

# -----------------------------------------------------------------------------------
