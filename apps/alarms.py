# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# Lemon & Einar K - Tenacity (Solarsoul Chill Breaks Remix)

# import traceback
import random
# import re
from datetime import datetime, timedelta

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Alarms(Hass):
    """Documentation for Alarms"""

    rota = None
    early_alarm_callback = None
    normal_alarm_callback = None
    override = False
    default_early_alarm_schedule = 'daily'  # weekday|daily|none
    callbacks = [None, None, None]
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise alarms"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.rota = self.generate_rota(datetime(2024, 5, 16).date(), 12)

        self.register_service('alarms/reset', self.reset_service)

        self.listen_event(self.set_alarm_state_event, 'set_alarm_state')
        self.listen_event(self.status_event, 'status')

        self.listen_state(self.set_early_alarm_callback, 'input_boolean.early_alarm', new='on', action='set')
        self.listen_state(self.set_early_alarm_callback, 'input_boolean.early_alarm', new='off', action='cancel')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='on', action='set')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='off', action='cancel')
        self.listen_state(self.reset_alarms, 'input_boolean.reset_alarms', new='on')
        # self.listen_state(self.reset_alarms, 'input_boolean.alarm_testing', new='on')
        # self.listen_state(self.reset_alarms, 'input_boolean.alarm_testing', new='off')

        # also can fire event set_alarm_state
        self.run_daily(self.set_alarm_state, '20:30:00') # make sure before max goes to bed

        self.run_in(self.set_alarm_state, 0)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def reset_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """reset alarms"""

        self.reset_alarms('','','','',{})

# -----------------------------------------------------------------------------------

    def set_alarm_state_event(self, event, data, kwargs):

        self.set_alarm_state({})

# -----------------------------------------------------------------------------------

    # def set_alarm_state_async(self, kwargs):

    #     # self.set_early_alarm()
    #     # self.set_normal_alarm()
    #     # self.show_alarm_time('early')
    #     self.show_alarm_time('normal')

# -----------------------------------------------------------------------------------

    def set_alarm_state(self, kwargs):

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.alarms_disabled') == 'on':
            self.cancel_alarms()
            self.set_state('input_boolean.early_alarm', state='off')
        else:
            self.set_early_alarm()

        self.set_normal_alarm()

        if self.get_state('input_boolean.alarms_disabled') == 'off':
            self.show_alarm_time('early')

        self.show_alarm_time('normal')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_early_alarm(self):

        self.lib.log_function_name(start=True)

        state, alarm_time, hour, timestamp = self.get_early_alarm_time()
        self.set_early_alarm_time(state, alarm_time, hour, timestamp)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def get_early_alarm_time(self, backup=False):

        self.lib.log_function_name(start=True)

        # day = datetime.now().date()

        # a_day = timedelta(days=1)

        # if self.now_is_between('03:00:00', '23:59:59'):
        #     day1 = day + a_day # tomorrow
        # else:
        #     day1 = day

        # day0 = day1 - a_day # yesterday

        # shift0 = self.check_shift(day0)
        # shift1 = self.check_shift(day1)

        # if self.lib.get_verbose_debug():
        #     self.log(f'\t{day0} is {shift0} shift (day/shift0)')
        #     self.log(f'\t{day1} is {shift1} shift (day/shift1)')

        # override = self.get_state('input_boolean.override') == 'on'

        # if override:
        #     # must be set specifically, don't change
        #     hour = self.get_state('input_datetime.early_alarm', attribute='hour')
        #     minute = self.get_state('input_datetime.early_alarm', attribute='minute')
        #     alarm_time = f'{hour:02d}:{minute:02d}'
        # else:
        #     hour = const.NIGHT_DELIVER[0]
        #     minute = const.NIGHT_DELIVER[1]
        #     if shift1 == 'Night' and shift0 == 'Night':
        #         hour = const.NIGHT_COLLECT[0]
        #         minute = const.NIGHT_COLLECT[1]
        #     if backup:
        #         minute += 1
        #     alarm_time = f'{hour:02d}:{minute:02d}'

        # if override:
        #     self.log('\toverride is set', level='WARNING')
        #     state = 'on'
        # else:
        #     if shift0 == 'Off' and shift1 == 'Night':
        #         # transition shift
        #         state = 'off'
        #         hour = const.DEFAULT[0]
        #         minute = const.DEFAULT[1]
        #         self.log('\tdisabling due to transition shift off->night', level='WARNING')
        #     elif shift0 == 'Night' and shift1 == 'Off':
        #         # transition shift
        #         state = 'on'
        #         hour = const.NIGHT_COLLECT[0]
        #         minute = const.NIGHT_COLLECT[1]
        #         self.log('\tenabling due to transition shift night->off', level='WARNING')
        #     elif shift0 == 'Off' and shift1 == 'Off':
        #         # transition shift
        #         state = 'off'
        #         hour = const.DEFAULT[0]
        #         minute = constULT[1]
        #     elif shift1 == shift0 == 'Night':
        #         state = 'on'
        #         hour = const.NIGHT_COLLECT[0]
        #         minute = const.NIGHT_COLLECT[1]
        #     elif shift1 == shift0 == 'Day': # elif shift0 == 'Day' and shift1 == 'Day':
        #         state = 'on'
        #         hour = const.NIGHT_DELIVER[0]
        #         minute = const.NIGHT_DELIVER[1]
        #     elif shift0 == 'Off' and shift1 == 'Day':
        #         state = 'on'
        #         hour = const.NIGHT_DELIVER[0]
        #         minute = const.NIGHT_DELIVER[1]
        #     elif shift0 == 'Day' and shift1 == 'Off':
        #         state = 'off'
        #         hour = const.NIGHT_DELIVER[0]
        #         minute = const.NIGHT_DELIVER[1]
        #     else:
        #         # just use tomorrows shift
        #         state = 'off' if shift1 == 'Off' else 'on'
        #         self.log(f'defaukt time would be wrong if shift was \'on\'. shift={state}')
        #         hour = const.DEFAULT[0]
        #         minute = const.DEFAULT[1]

        #     if backup:
        #         minute += 1

        #     alarm_time = f'{hour:02d}:{minute:02d}'

        # return state, alarm_time, hour, minute

        hour = minute = second = None
        parts = const.EARLY_ALARM_TIME.split(':')

        if len(parts) >= 2:
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2]) if len(parts) > 2 else 0

        alarm_time = f'{hour:02d}:{minute:02d}'
        timestamp = hour * 3600 + minute * 60 + second

        self.lib.log_function_name(start=False)

        return 'off', alarm_time, hour, timestamp

# -----------------------------------------------------------------------------------

    def set_early_alarm_time(self, state, alarm_time, hour, timestamp):

        self.lib.log_function_name(start=True)

        if self.lib.get_verbose_debug():
            self.log(f'set_early_alarm_time state={state} alarm_time={alarm_time} hour={hour} timestamp={timestamp}', level="WARNING")

        self.set_state('input_datetime.early_alarm', state=f'{alarm_time}:00', attributes={"hour": hour, "timestamp": timestamp})
        self.set_state('input_boolean.early_alarm', state=state)

        if state == 'on':
            self.set_early_alarm_callback('input_boolean.early_alarm', 'state', 'off', 'on', {'action':'set'})
        else:
            self.set_early_alarm_callback('input_boolean.early_alarm', 'state', 'on', 'off', {'action':'cancel'})

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_normal_alarm(self):

        self.lib.log_function_name(start=True)

        state, alarm_time, hour, timestamp = self.get_normal_alarm_time()
        self.set_normal_alarm_time(state, alarm_time, hour, timestamp)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def get_normal_alarm_time(self):

        self.lib.log_function_name(start=True)

        dow = self.lib.dow()

        # (06-00 on tuesday or friday/saturday) or (00-06 on wednesday or saturday/sunday) -> set alarm later
        # later = (self.now_is_between('06:00:00', '23:59:59') and ((dow == 2) or (5 <= dow <= 6))) or (self.now_is_between('00:00:00', '05:59:59') and ((dow == 3) or (6 <= dow <= 7)))
        # dow: 1 - mon, 2 - tue, 3 - wed, 4 - thu, 5 - fri, 6 - sat, 7 - sun
        later = not (self.now_is_between('06:00:00', '23:59:59') and (dow in (1,2))) or (self.now_is_between('00:00:00', '05:59:59') and (dow in (2,3)))

        if later:
            parts = const.LATE_ALARM_TIME.split(':')
        else:
            parts = const.NORMAL_ALARM_TIME.split(':')

        hour = minute = second = None

        if len(parts) >= 2:
            hour = int(parts[0])
            minute = int(parts[1])
            second = int(parts[2]) if len(parts) > 2 else 0

        alarm_time = f'{hour:02d}:{minute:02d}'
        timestamp = hour * 3600 + minute * 60 + second

        state = 'on'

        override = self.get_state('input_boolean.override') == 'on'

        if override:
            state = 'on'

        self.lib.log_function_name(start=False)

        return state, alarm_time, hour, timestamp

# -----------------------------------------------------------------------------------

    def set_normal_alarm_time(self, state, alarm_time, hour, timestamp):

        self.lib.log_function_name(start=True)

        if self.lib.get_verbose_debug():
            self.log(f'set_normal_alarm_time state={state} alarm_time={alarm_time} hour={hour} timestamp={timestamp}', level="WARNING")

        self.set_state('input_datetime.normal_alarm', state=f"{alarm_time}:00", attributes={"hour": hour, "timestamp": timestamp})
        self.set_state('input_boolean.normal_alarm', state=state)

        if state == 'on':
            self.set_normal_alarm_callback('input_boolean.normal_alarm', 'state', 'off', 'on', {'action':'set'})
        else:
            self.set_normal_alarm_callback('input_boolean.normal_alarm', 'state', 'on', 'off', {'action':'cancel'})

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def show_alarm_time(self, alarm_type):

        self.lib.log_function_name(start=True)

        _alarm_type = alarm_type

        time_entity_id = f'input_datetime.{alarm_type}_alarm'
        bool_entity_id = f'input_boolean.{alarm_type}_alarm'

        tm = self._read_time_attrs(time_entity_id)
        if tm is None:
            self.log(f'Unable to read time attributes for {time_entity_id}', level='WARNING')
            alarm_time = None
        else:
            hour, minute = tm
            d = datetime.now() + timedelta(days=1)
            t = datetime(d.year, d.month, d.day, hour, minute, 0, 0)
            alarm_time = f"{t.hour:02d}:{t.minute:02d}"

        state = self.get_state(bool_entity_id)
        if alarm_time is None:
            message = f'The {_alarm_type} morning alarm time is unknown'
        else:
            message = f'The {_alarm_type} morning alarm is set to {alarm_time}' if state == 'on' else f'The {_alarm_type} morning alarm is cancelled'

        self.call_service("announcer/announce", entity_id=const.STUDY_SPEAKER, message=message)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cancel_alarms(self):

        self.lib.log_function_name(start=True)

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')

        # self.set_state('input_boolean.testing', state='off')
        self.set_state('input_boolean.reset_alarms', state='off')
        self.set_state('input_boolean.alarm_testing', state='off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def reset_alarms(self, entity, attribute, old, new, kwargs):

        self.lib.log_function_name(start=True)

        self.cancel_alarms()
        self.set_alarm_state({})
        self.set_state('input_boolean.reset_alarms', state='off')
        self.set_state('input_boolean.alarm_testing', state='off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_early_alarm_callback(self, entity, attribute, old, new, kwargs):

        self.lib.log_function_name(start=True)

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self.early_alarm_callback = self.set_alarm(alarm_type='early', action=kwargs['action'])

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_normal_alarm_callback(self, entity, attribute, old, new, kwargs):

        self.lib.log_function_name(start=True)

        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')
        self.normal_alarm_callback = self.set_alarm(alarm_type='normal', action=kwargs['action'])

        self.lib.log_function_name(start=False)

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

        self.lib.log_function_name(start=True)

        alarm = None
        action = kwargs['action']
        alarm_type = kwargs['alarm_type']
        _alarm_type = alarm_type

        if self.lib.get_verbose_debug():
            self.log(f"\t{alarm_type} alarm enabled", level='DEBUG')
            self.log(f"\taction={action}", level='DEBUG')

        bool_entity_id = f'input_boolean.{alarm_type}_alarm'
        time_entity_id = f'input_datetime.{alarm_type}_alarm'

        debug = self.lib.get_alarm_testing()

        if action == 'set':
            # state = self.get_state(time_entity_id, attribute="attributes")
            tm = self._read_time_attrs(time_entity_id)
            if tm is None:
                # cannot determine time; abort setting alarm
                self.log(f'Aborting set_alarm: cannot read time from {time_entity_id}', level='ERROR')
                self.lib.log_function_name(start=False)
                return None

            hour, minute = tm

            if debug:
                d = datetime.now() + timedelta(minutes=1)

                if self.lib.get_verbose_debug():
                    self.log(f"\t{d}", level='DEBUG')

                alarm_time = f"{d.hour:02d}:{d.minute:02d}"
                self.set_state(time_entity_id, state=f'{alarm_time}:00', hour=d.hour, minute=d.minute, second=0)
                hour = d.hour
                minute = d.minute

            alarm_time = f"{hour:02d}:{minute:02d}"

            kwargs.pop('action', None)
            alarm = self.run_daily(self.alarm, f'{alarm_time}:00', **kwargs)
            self.log(f'\t{_alarm_type} alarm set for {alarm_time}:00 using {time_entity_id}', level="INFO")
        elif action == 'cancel':
            self.set_state(bool_entity_id, state='off')
            alarm_time = 'unset' # can trace in message below

            if _alarm_type == 'early':
                alarm = self.early_alarm_callback
            elif alarm_type == 'normal':
                alarm = self.normal_alarm_callback
            self._cancel_timer(alarm, f'{_alarm_type} alarm')
            alarm = None
        else:
            self.log(f"\tUnexpected alarm action {action}", level='WARNING')

        self.lib.log_function_name(start=False)

        return alarm

# -----------------------------------------------------------------------------------

    def alarm(self, kwargs):

        self.run_in(self._alarm, 0, **kwargs)

# -----------------------------------------------------------------------------------

    def is_test(self, kwargs):

        return kwargs['alarm_type'] == 'test' or self.lib.get_alarm_testing()

# -----------------------------------------------------------------------------------

    def _alarm(self, kwargs):

        self.lib.log_function_name(start=True)

        alarm_type = kwargs['alarm_type']
        entity_id = const.STUDY_SPEAKER if self.is_test(kwargs) else const.BEDROOM_SPEAKER

        media_content_id = self.select_alarm(alarm_type=alarm_type)

        self.call_service('sonos/play_thing', entity_id=entity_id, media_content_id=media_content_id, volume_level=const.ALARM_VOLUME, delayed=True)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def select_alarm(self, **kwargs):
        """select alarm sound"""

        self.lib.log_function_name(start=True)

        alarm_type = kwargs['alarm_type']

        if alarm_type == 'normal':
            ids = const.NORMAL_ALARM
        elif alarm_type == 'test':
            ids = const.NORMAL_ALARM
        else:
            # ids = const.EARLY_ALARM
            ids = const.NORMAL_ALARM

        self.lib.log_function_name(start=False)

        return ids[random.randint(0, len(ids) - 1)]  # randomise choice.

# -----------------------------------------------------------------------------------

    def play_normal_alarm(self, dow=None):
        """play normal alarm if enabled"""

        self.lib.log_function_name(start=True)

        if dow is None:
            dow = self.lib.dow()

        bank_holiday = self.lib.is_bank_holiday()

        self.lib.log_function_name(start=False)

        return self.get_state(entity_id='input_boolean.normal_alarm') == 'on' and (not bank_holiday) and dow <= 5 and dow != 3

# -----------------------------------------------------------------------------------

    def lumie_alarm(self, kwargs):
        """lumie alarm"""

        self.lib.log_function_name(start=True)

        test = 'test' in kwargs
        timedelta(minutes=5).total_seconds()
        seconds = 5*60 if 'test' not in kwargs else 10
        elev = self.get_state('sun.sun', 'elevation')
        enabled = self.get_state('input_boolean.lumie') == 'on' and elev < 5
        dow = self.lib.dow()
        holiday = self.lib.is_bank_holiday()

        if not holiday and enabled and dow <= 5 and dow != 3 or test:
            self.callback[0] = self.run_in_thread(self.lumie_phase, 0, brightness=100,transition=seconds, rgb_color=[255, 180, 10])  # now
            if self.now_is_between('04:00:00', '08:00:00'):
                self.callback[1] = self.run_in_thread(self.lumie_phase, seconds, brightness=250, transition=seconds, rgb_color=[250, 250, 250]) # +5m
            self.callback[2] = self.run_in_thread(self.lumie_phase3, 4*seconds)  # +20m
        else:
            self.log(f'\tskipping lumie alarm holiday={holiday} enabled={enabled} dow={dow}', level='INFO')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_phase(self, kwargs):

        if self.get_state('input_boolean.lumie') == 'off':
            return

        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']

        self.call_service('lighting/lumie_on', brightness=brightness)

# # -----------------------------------------------------------------------------------

#     def lumie_phase2(self, kwargs):

#         if self.get_state('input_boolean.lumie') == 'off':
#             return

#         brightness = kwargs['brightness']
#         transition = kwargs['transition']
#         rgb_color = kwargs['rgb_color']

#         self.call_service('light/turn_on', entity_id='light.lumie', brightness=brightness, transition=transition, rgb_color=rgb_color)

# -----------------------------------------------------------------------------------

    def lumie_phase3(self, kwargs):

        self.call_service('light/turn_off', entity_id='light.lumie')

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

    def check_shift(self, date_to_check):

        for date, status in self.rota:
            if date == date_to_check:
                return status

        return "Date out of range"

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, timer, message=None):

        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='DEBUG')

# -----------------------------------------------------------------------------------
