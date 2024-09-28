# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import random
import time
from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from appdaemon.plugins.hass.hassapi import Hass  # pylint: disable=E0401 disable=E0611

class Alarms(Hass):
    """Documentation for Alarms"""
    override = False
    default_early_alarm_schedule = 'daily'  # weekday|daily|none
    early_alarm_callback = None
    normal_alarm_callback = None
    test_alarm_callback = None
    rota = None
    lib = None
    night_deliver = [4, 58]
    night_collect = [5, 25]
    default = [8, 0]
    callbacks = [None, None, None]
    STUDY = 'media_player.study'
    BEDROOM = 'media_player.bedroom'

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """."""

        self.log('-'*72)

        self.lib = AutomationLib(self)

        self.rota = self.generate_rota(datetime(2024, 5, 16).date(), 12)

        self.listen_event(self.set_alarm_state_event, 'set_alarm_state')
        self.listen_event(self.status_event, 'status')

        self.listen_state(self.set_early_alarm_callback, 'input_boolean.early_alarm', new='on', action='set')
        self.listen_state(self.set_early_alarm_callback, 'input_boolean.early_alarm', new='off', action='cancel')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='on', action='set')
        self.listen_state(self.set_normal_alarm_callback, 'input_boolean.normal_alarm', new='off', action='cancel')
        self.listen_state(self.reset_alarms, 'input_boolean.reset_alarms', new='on')

        self.run_daily(self.set_alarm_state, '20:30:10') # pre-set - make sure before max retires (to bed)
        self.run_daily(self.set_alarm_state, '00:00:10') # re-set - also can fire event set_alarm_state
        self.run_in(self.set_alarm_state, 0)

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

# -------------------------------------------------------------------------------------------------

    def set_alarm_state_event(self, event, data, kwargs):

        self.set_alarm_state({})

# -------------------------------------------------------------------------------------------------

    def set_alarm_state(self, kwargs):

        self.set_early_alarm()
        self.set_normal_alarm()
        self.show_alarm_time('early')
        self.show_alarm_time('normal')

# -------------------------------------------------------------------------------------------------

    def set_backup_alarm(self, e_id) -> None:

        entity_id = f'switch.sonos_alarm_{e_id}'
        self.set_state(entity_id, state="on")

# -------------------------------------------------------------------------------------------------

    def cancel_backup_alarm(self, e_id) -> None:

        entity_id = f'switch.sonos_alarm_{e_id}'
        self.set_state(entity_id, state="off")

# -------------------------------------------------------------------------------------------------

    def set_early_alarm(self):

        state, alarm_time, hour, minute = self.get_early_alarm_time()
        self.set_early_alarm_time(state, alarm_time, hour, minute)

        if alarm_time == "04:58":
            self.set_backup_alarm('1978') # 05:00
        elif alarm_time == "05:25":
            self.set_backup_alarm('2104') # 05:27

# -------------------------------------------------------------------------------------------------

    def get_early_alarm_time(self):

        day = datetime.now().date()

        a_day = timedelta(days=1)

        if self.now_is_between('03:00:01', '23:59:59'):
            day1 = day + a_day # tomorrow
        else:
            day1 = day

        day0 = day1 - a_day # yesterday

        shift0 = self.check_shift(day0)
        shift1 = self.check_shift(day1)

        self.log(f'\t{day0} is {shift0} shift (day/shift0)')
        self.log(f'\t{day1} is {shift1} shift (day/shift1)')

        override = self.get_state('input_boolean.override') == 'on'

        if override:
            # must be set specifically, don't change
            hour = self.get_state('input_datetime.early_alarm', attribute='hour')
            minute = self.get_state('input_datetime.early_alarm', attribute='minute')
            alarm_time = f'{hour:02d}:{minute:02d}'
        else:
            hour = self.night_deliver[0]
            minute = self.night_deliver[1]
            if shift1 == 'Night' and shift0 == 'Night':
                hour = self.night_collect[0]
                minute = self.night_collect[1]
            alarm_time = f'{hour:02d}:{minute:02d}'

        if not override: # leave if we are overridden, assume set
            if shift0 == 'Off' and shift1 == 'Night':
                # transition shift
                state = 'off'
                hour = self.default[0]
                minute = self.default[1]
                self.log('\tdisabling due to transition shift off->night', level='WARNING')
            elif shift0 == 'Night' and shift1 == 'Off':
                # transition shift
                state = 'on'
                hour = self.night_collect[0]
                minute = self.night_collect[1]
                self.log('\tenabling due to transition shift night->off', level='WARNING')
            elif shift0 == 'Off' and shift1 == 'Off':
                # transition shift
                state = 'off'
                hour = self.default[0]
                minute = self.default[1]
            elif shift1 == shift0 == 'Night' and shift1 == 'Night':
                state = 'on'
                hour = self.night_collect[0]
                minute = self.night_collect[1]
            elif shift0 == 'Day' and shift1 == 'Day':
                state = 'on'
                hour = self.night_deliver[0]
                minute = self.night_deliver[1]
            elif shift0 == 'Day' and shift1 == 'Off':
                state = 'off'
                hour = self.night_deliver[0]
                minute = self.night_deliver[1]
            else:
                # just use tomorrows (or todays) shift
                state = 'off' if shift1 == 'Off' else 'on'
                # hour = self.default[0]
                # minute = self.default[1]
                # alarm_time = f'{hour:02d}:{minute:02d}'

            alarm_time = f'{hour:02d}:{minute:02d}'
        else:
            self.log('\toverride is set', level='WARNING')
            state = 'on'

        # print(f'get_early_alarm state={state} alarm_time={alarm_time} hour={hour} minute={minute}')
        return state, alarm_time, hour, minute

# -------------------------------------------------------------------------------------------------

    def set_early_alarm_time(self, state, alarm_time, hour, minute):

        # self.log(f'set_early_alarm_time state={state} alarm_time={alarm_time} hour={hour} minute={minute}', level="WARNING")
        self.set_state('input_datetime.early_alarm', state=f'{alarm_time}:00', hour=hour, minute=minute, second=0)
        self.set_state('input_boolean.early_alarm', state=state)

        if state == 'on':
            self.set_early_alarm_callback('input_boolean.early_alarm', 'state', 'off', 'on', {'action':'set'})
        else:
            self.set_early_alarm_callback('input_boolean.early_alarm', 'state', 'on', 'off', {'action':'cancel'})

# -------------------------------------------------------------------------------------------------

    def set_normal_alarm(self):

        state, alarm_time, hour, minute = self.get_normal_alarm_time()
        self.set_normal_alarm_time(state, alarm_time, hour, minute)

        if alarm_time == "07:45":
            self.set_backup_alarm('2108') # 07:50

# -------------------------------------------------------------------------------------------------

    def get_normal_alarm_time(self):

        dow = self.lib.dow()

        # (21-00 on tuesday or friday/saturday) or (00-03 on wednesday or saturday/sunday) -> set alarm later
        later = (self.now_is_between('21:00:00', '23:59:59') and ((dow == 2) or (5 <= dow <= 6))) or (self.now_is_between('00:00:00', '03:00:00') and ((dow == 3) or (6 <= dow <= 7)))

        if later:
            hour = 10
            minute = 0
        else:
            hour = 7
            minute = 45

        override = self.get_state('input_boolean.override') == 'on'

        if override:
            state = 'on'
        else:
            state = self.get_state('input_boolean.normal_alarm')

        alarm_time = f"{hour:02d}:{minute:02d}"

        return state, alarm_time, hour, minute

# -------------------------------------------------------------------------------------------------

    def set_normal_alarm_time(self, state, alarm_time, hour, minute):

        # self.log(f'set_normal_alarm_time state={state} alarm_time={alarm_time} hour={hour} minute={minute}', level="WARNING")
        self.set_state('input_datetime.normal_alarm', state=f"{alarm_time}:00", hour=hour, minute=minute, second=0)
        self.set_state('input_boolean.normal_alarm', state=state)

        if state == 'on':
            self.set_normal_alarm_callback('input_boolean.normal_alarm', 'state', 'off', 'on', {'action':'set'})
        else:
            self.set_normal_alarm_callback('input_boolean.normal_alarm', 'state', 'on', 'off', {'action':'cancel'})

# -------------------------------------------------------------------------------------------------

    def show_alarm_time(self, alarm_type):

        time_entity_id = f'input_datetime.{alarm_type}_alarm'
        bool_entity_id = f'input_boolean.{alarm_type}_alarm'

        state = self.get_state(time_entity_id, attribute="attributes")
        d = datetime.now() + timedelta(days=1)
        t = datetime(d.year, d.month, d.day, state['hour'], state['minute'], 0, 0) + timedelta(minutes=-5)
        alarm_time = f"{t.hour:02d}:{t.minute:02d}"
        state = self.get_state(bool_entity_id)
        message = f'The {alarm_type} morning alarm is set to {alarm_time}' if state == 'on' else f'The {alarm_type} morning alarm is cancelled'
        self.call_service("announcer/announce", entity_id=self.STUDY, message=message, snapshot=False)

# -------------------------------------------------------------------------------------------------

    def reset_alarms(self, entity, attribute, old, new, kwargs):

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')
        self._cancel_timer(self.test_alarm_callback, 'test alarm')

        # self.set_state('input_boolean.early_alarm', state=self.get_state('input_boolean.default_early_alarm_state'))
        # self.set_state('input_boolean.normal_alarm', state=self.get_state('input_boolean.default_normal_alarm_state'))

        self.set_state('input_boolean.alarm_testing', state='off')
        self.set_state('input_boolean.testing', state='off')
        self.set_state('input_boolean.reset_alarms', state='off')

        # state, alarm_time, hour, minute = self.get_early_alarm_time()
        # self.set_early_alarm_time(state, alarm_time, hour, minute)

        self.set_alarm_state({})

# ---------------------------------------------------------------------------------------------------------

    def get_alarm_testing(self):

        return self.get_state("input_boolean.alarm_testing") == "on"

# ---------------------------------------------------------------------------------------------------------

    def set_early_alarm_callback(self, entity, attribute, old, new, kwargs):

        self._cancel_timer(self.early_alarm_callback, 'early alarm')
        self.early_alarm_callback = self.set_alarm(alarm_type='early', action=kwargs['action'])

# ---------------------------------------------------------------------------------------------------------

    def set_normal_alarm_callback(self, entity, attribute, old, new, kwargs):

        self._cancel_timer(self.normal_alarm_callback, 'normal alarm')
        self.normal_alarm_callback = self.set_alarm(alarm_type='normal', action=kwargs['action'])

# ---------------------------------------------------------------------------------------------------------

    def set_alarm(self, **kwargs):

        alarm = None
        action = kwargs['action']
        alarm_type = kwargs['alarm_type']
        bool_entity_id = f'input_boolean.{alarm_type}_alarm'
        time_entity_id = f'input_datetime.{alarm_type}_alarm'

        self.log(f"\t{alarm_type} alarm enabled", level='DEBUG')
        self.log(f"\taction={action}", level='DEBUG')

        debug = self.get_alarm_testing()

        if action == 'set':
            state = self.get_state(time_entity_id, attribute="attributes")
            if debug:
                now = datetime.now() + timedelta(minutes=1)
                self.log(f"\t{now}", level='DEBUG')
                alarm_time = f"{now.hour:02d}:{now.minute:02d}"
                self.set_state(time_entity_id, state=f'{alarm_time}:00', hour=now.hour, minute=now.minute, second=0)
                state = self.get_state(time_entity_id, attribute="attributes")
            else:
                d = datetime.now() + timedelta(days=1)
                t = datetime(d.year, d.month, d.day, state['hour'], state['minute'], 0, 0) + timedelta(minutes=-5)
                alarm_time = f"{t.hour:02d}:{t.minute:02d}"
            kwargs.pop('action', None)  # del kwargs['action']
            alarm = self.run_daily(self.alarm, f'{alarm_time}:00', **kwargs)
            self.log(f'\t{alarm_type} alarm set for {alarm_time}:00 using {time_entity_id}', level="WARNING")
        elif action == 'cancel':
            self.set_state(bool_entity_id, state='off')
            alarm_time = 'unset' # can trace in message below

            if alarm_type == 'early':
                alarm = self.early_alarm_callback
                self.cancel_backup_alarm('1978') # 05:00
                self.cancel_backup_alarm('2104') # 05:27
            elif alarm_type == 'normal':
                alarm = self.normal_alarm_callback
                self.cancel_backup_alarm('2108') # 07:50
            elif alarm_type == 'test':
                alarm = self.test_alarm_callback
            self._cancel_timer(alarm, f'{alarm_type} alarm')
        else:
            self.log(f"\tUnexpected alarm action {action}", level='WARNING')

        return alarm

# ---------------------------------------------------------------------------------------------------------

    def alarm(self, kwargs):

        self.run_in(self.lumie_alarm, 0, **kwargs)

        if kwargs['alarm_type'] == 'test' or self.get_alarm_testing():
            s = 10
        else:
            s = 300

        self.run_in(self._alarm, s, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    def is_test(self, kwargs):

        return kwargs['alarm_type'] == 'test' or self.get_alarm_testing()

# ---------------------------------------------------------------------------------------------------------

    def _alarm(self, kwargs):

        alarm_type = kwargs['alarm_type']
        test = self.is_test(kwargs)
        entity_id = self.BEDROOM
        # entity_id = self.STUDY

        if test:
            play = True
            entity_id = self.STUDY
        else:
            play = True # alarm_type == 'early' or alarm_type == 'normal' # (alarm_type == 'normal' and self.play_normal_alarm())

        if play:
            media_content_id = self.select_alarm(alarm_type=alarm_type)
            self.log(f'\talarm_type={alarm_type} test={test} play={play} entity_id={entity_id} media_content_id={media_content_id}')

            # self.run_sequence(
            #     [
            #         {'media_player/volume_mute': {'entity_id': entity_id, 'is_volume_muted': False}},
            #         {'media_player/volume_set': {'entity_id': entity_id, 'volume_level': 0}},
            #         {'media_player/play_media': {'entity_id': entity_id, 'media_content_type': "music", 'media_content_id': media_content_id}},
            #         {'media_player/repeat_set': {'entity_id': entity_id, 'repeat': 'off'}}
            #     ]
            # )

            self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
            self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0)
            self.call_service('media_player/play_media', entity_id=entity_id, media_content_type="music", media_content_id=media_content_id)
            self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')

            divisor = 100
            target_volume = 50  # deal in integers for convenience

            if test:
                span = 2 * divisor # 2s increments
            else:
                span = 5 * divisor # 5s incremnets

            volume = 0
            incr_volume = target_volume * (2.5/100.0)  # 2.5% increase in volume
            sleeptime = span/divisor

            disabled = False

            while volume < target_volume:
                volume += incr_volume
                self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume/100.0)
                if not disabled and volume > 0.15:
                    if alarm_type == 'early':
                        self.cancel_backup_alarm('1978') # 05:00
                        self.cancel_backup_alarm('2104') # 05:27
                    elif alarm_type == 'normal':
                        self.cancel_backup_alarm('2108') # 07:50
                    disabled = True
                time.sleep(sleeptime)

# ---------------------------------------------------------------------------------------------------------

    def select_alarm(self, **kwargs):

        if kwargs['alarm_type'] == 'normal':
            ids = [
                # 'x-rincon-mp3radio://http://prem2.di.fm:80/melodicprogressive_hi?5fba91be81f6da5b573f89c1',
                'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
            ]
        elif kwargs['alarm_type'] == 'test':
            ids = [
                'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
            ]
        else:
            ids = [
                # birdsong spring morning
                'x-sonos-spotify:spotify%3atrack%3a5VFk26TzgwqX18dFhRmbSM?sid=9&flags=8224&sn=1',
                # birdsong garden morning
                'x-sonos-spotify:spotify%3atrack%3a3K3cxx8ntQp8DZbPpltwr4?sid=9&flags=8224&sn=1',
                # a gentle thunderstorm
                'x-sonos-spotify:spotify%3atrack%3a1r4QKeqpv1ov8FkrgKDxQ7?sid=9&flags=8224&sn=1',

                # 'x-sonos-spotify:spotify%3atrack%3a2T5Lipk1QTtvt76Xjcwrxc?sid=9&flags=8224&sn=1', # heavy thunderstorm sounds
                # 'x-sonos-spotify:spotify%3atrack%3a1E0jvxVMYcnZbjvrs03Yay?sid=9&flags=8224&sn=1', # thunderstorm sounds with rain and loud claps of thunder for all isomniacs
                # 'x-sonos-spotify:spotify%3atrack%3a49kbhMUlsVPp0fOdTOCgNM?sid=9&flags=8224&sn=1', # extreme thunderstorm soubnds with torrential rain & very loud thunder claps
                #
                # 'x-sonos-spotify:spotify%3atrack%3a2cwKtKEhPn6ZnJmlzbmpLQ?sid=9&flags=8224&sn=1', # the early morning rain
                #
                # 'x-sonos-spotify:spotify%3atrack%3a4G6Lz9Et6dhLKydPyY4N9a?sid=9&flags=8224&sn=1', # rain drops dancing on a tin roof
                # 'x-sonos-spotify:spotify%3atrack%3a16D3zoIJWuEbXFfkzXSIqs?sid=9&flags=8224&sn=1', # an angry thunderstorm
                # 'x-sonos-spotify:spotify%3atrack%3a6H5aGE9xZEPkpeEAn4f7b8?sid=9&flags=8224&sn=1', # thunderstorm
                # 'x-sonos-spotify:spotify%3atrack%3a3UdClX9rDMiYUOIl6JWaRo?sid=9&flags=8224&sn=1', # heavy thunderstorm
            ]

        return ids[random.randint(0, len(ids) - 1)]  # randomise choice.

# ---------------------------------------------------------------------------------------------------------

    def play_normal_alarm(self, dow=None):

        if dow is None:
            dow = self.lib.dow()

        bank_holiday = self.lib.is_bank_holiday()

        return self.get_state(entity_id='input_boolean.normal_alarm') == 'on' and (not bank_holiday) and dow <= 5 and dow != 3

# ---------------------------------------------------------------------------------------------------------

    def lumie_alarm(self, kwargs):

        # self.lib.log_function_name()
        test = 'test' in kwargs
        timedelta(minutes=5).total_seconds()
        seconds = 5*60 if 'test' not in kwargs else 10
        elev = self.get_state('sun.sun', 'elevation')
        enabled = self.get_state('input_boolean.lumie') == 'on' and elev < 5
        dow = self.lib.dow()
        holiday = self.lib.is_bank_holiday()

        if not holiday and enabled and dow <= 5 and dow != 3 or test:
            # TODO: record handles?
            self.callback[0] = self.run_in_thread(self.lumie_phase1, 0, brightness=100,transition=seconds, rgb_color=[255, 180, 10])  # now
            if self.now_is_between('04:00:00', '08:00:00'):
                self.callback[1] = self.run_in_thread(self.lumie_phase2, seconds, brightness=250, transition=seconds, rgb_color=[250, 250, 250]) # +5m
            self.callback[2] = self.run_in_thread(self.lumie_phase3, 4*seconds)  # +20m
        else:
            self.log(f'\tskipping lumie alarm holiday={holiday} enabled={enabled} dow={dow}', level='INFO')

        # self.lib.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase1(self, kwargs):

        if self.get_state('input_boolean.lumie') == 'off':
            return

        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=brightness, transition=transition, rgb_color=rgb_color)

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase2(self, kwargs):

        if self.get_state('input_boolean.lumie') == 'off':
            return

        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=brightness, transition=transition, rgb_color=rgb_color)

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase3(self, kwargs):

        self.call_service('light/turn_off', entity_id='light.lumie')

# ---------------------------------------------------------------------------------------------------------

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

        self.log(f'{status}')

# ---------------------------------------------------------------------------------

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

        for cycle in range(num_cycles):
            for days, shift in pattern:
                for _ in range(days):
                    rota.append((current_date, shift))
                    current_date += timedelta(days=1)

        return rota

# ---------------------------------------------------------------------------------

    def check_shift(self, date_to_check):

        for date, status in self.rota:
            if date == date_to_check:
                return status

        return "Date out of range"

# ---------------------------------------------------------------------------------

    def _cancel_timer(self, timer, message=None):

        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def add_shift_calendar_events(self, kwargs):

        # print(self.rota)
        for a_date, shift in self.rota:
            # print(f'{date} {shift}')
            if shift != 'Off':
                end_date = a_date + timedelta(days=1)
                self.call_service('calendar/create_event', entity_id='calendar.shifts', summary=shift, description=shift, start_date=str(a_date), end_date=str(end_date))

# -------------------------------------------------------------------------------------------------
