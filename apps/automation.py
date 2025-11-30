# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
import pprint
import textwrap
import traceback # pylint: disable=unused-import
from io import StringIO

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Automation(Hass):
    """Documentation for Automation"""

    debug = False
    testing = False
    verbose = False
    trace = False
    override = False

    lib: "AutomationLib" = _helpers  # type: ignore
    state = 'Not Driving'
    log_level = None

    handlers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.lib.initialize()

        self.debug = self.get_state('input_boolean.debug') == 'on'
        self.verbose = self.get_state('input_boolean.verbose') == 'on'
        self.testing = self.get_state('input_boolean.testing') == 'on'
        self.trace = self.get_state('input_boolean.trace') == 'on'
        self.log(f"\tautomation state: debug={self.debug} verbose={self.verbose} testing={self.testing} trace={self.trace}", level='INFO')

        self.call_service('scene/reload')

        self.listen_event(self.set_all_state_event, 'set_all_state')
        self.listen_event(self.status_event, 'status')
        self.listen_event(self.test_event, 'test')

        self.listen_state(self.set_console_log_level, 'input_boolean.debug')
        self.listen_state(self.set_console_log_level, 'input_boolean.verbose')
        self.listen_state(self.set_console_log_level, 'input_boolean.trace')
        self.listen_state(self.set_debug_flag, 'input_boolean.debug')
        self.listen_state(self.set_verbose_flag, 'input_boolean.verbose')
        self.listen_state(self.set_testing_flag, 'input_boolean.testing')
        self.listen_state(self.set_trace_flag, 'input_boolean.trace')

        self.listen_state(self.reset_test1, 'input_boolean.test_1', new='on')
        self.listen_state(self.reset_test2, 'input_boolean.test_2', new='on')

        self.listen_state(self.fire_status_event, 'input_boolean.status', new='on')

        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='on', action='set')
        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='off', action='cancel')

        self.run_daily(self.reset, '04:00:00') # daily reset including booleans

        self.run_daily(self.set_all_state, '20:00:00') # set state - make sure before max retires (to bed)

        self.run_daily(self.backup, '23:30:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.maxine_travel_time_to_home, runtime)
        # self.run_minutely(self.fix_audio_delay, runtime)
        self.run_minutely(self.test, runtime)

        # runtime = datetime(2024, 1, 1, 0, 0, 0)
        # self.run_hourly(...)

        self.test({})

        self.set_all_state({})
        self._set_console_log_level()

        # self.log('initialising timestamps HACK', level='WARNING')
        # self.call_service('timestamp/init')
        self.log('timestamp status', level='INFO')
        self.call_service('timestamp/status')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def test(self, kwargs) -> None:
        """test method"""

        # self.lib.log_function_name(start=True)

        # print(self.lib.dow())
        # traceback.print_stack() # leave

        # self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def dummy(self) -> None:
        """dummy"""

        self.lib.log_function_name(start=True)
        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_all_state(self, kwargs) -> None:
        """set all state - reset to false and then set_default_state"""

        self.lib.log_function_name(start=True)

        booleans = {
            'override', 'sonos', 'lumie', 'test_1', 'test_2', 'test_3',
            'water_garden_1', 'water_garden_15', 'water_garden_20', 'water_garden_30', 'bedtime',
            'reset_alarms', 'test_utility_motion', 'test_kitchen_motion', 'test_bins_announce',
            'test_frost_warning', 'test_notification', 'test_announcement', 'test_maxine_home',
            'test_reset', 'test_front_door_ding', 'test_front_door_light_on', 'test_test',
            'test_early_alarm', 'mock_run', 'alarm_debug'
        }

        # ensure certain booleans are not reset whether defined or not
        booleans -= {'debug', 'verbose', 'early_alarm', 'normal_alarm', 'test_alarm'}

        for boolean in booleans:
            self.set_state(f'input_boolean.{boolean}', state='off')

        self.set_default_state()

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_console_log_level(self, entity, attribute, old, new, kwargs) -> None:
        """set console log level depending on the debug or verboseflag"""

        # separate method required because we are listening to the state of the input_boolean.debug and input_boolean.verbose and needs a specific signature
        self._set_console_log_level()

# -----------------------------------------------------------------------------------

    def _set_console_log_level(self) -> None:
        """internal method to set console level using the debug flag. set the property log_level and report a change"""

        level = "DEBUG" if self.get_state('input_boolean.debug') == 'on' else "INFO"
        level = "DEBUG"
        prefix = "VERBOSE " if self.get_state('input_boolean.verbose') == 'on' else ""
        log_level = level+prefix

        if self.log_level != log_level:
            self.log(f'\tchanging log level to {prefix}{level} (now {log_level} was {self.log_level})', level='INFO')
            self.log_level = level+prefix

            for module in const.MODULES:
                app = self.get_app(module)
                if app is not None:
                    self.log(f'setting log level {prefix}{level} on app {module} (app={app})', level='INFO')
                    app.set_log_level(level)

# -----------------------------------------------------------------------------------

    def set_debug_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set debug flag"""

        self.debug = new == 'on'
        self.log(f'\tautomation debug now {self.debug}', level='INFO')
        self._set_console_log_level()
        self.lib.set_debug(self.debug)

# -----------------------------------------------------------------------------------

    def set_verbose_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set verbose flag"""

        self.verbose = new == 'on'
        self.log(f'\tautomation verbose now {self.verbose}', level='INFO')
        self._set_console_log_level()
        self.lib.set_verbose(self.verbose)

# -----------------------------------------------------------------------------------

    def set_testing_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set testing flag"""

        self.testing = new == 'on'
        self.log(f'\tautomation testing now {self.testing}', level='INFO')
        self._set_console_log_level()
        self.lib.set_testing(self.testing)

# -----------------------------------------------------------------------------------

    def set_trace_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set trace flag"""

        self.trace = new == 'on'
        self.log(f'\tautomation trace now {self.trace}', level='INFO')
        self._set_console_log_level()
        self.lib.set_trace(self.trace)

# -----------------------------------------------------------------------------------

    def reset_test1(self, entity, attribute, old, new, kwargs) -> None:
        """reset test_1 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_1', state='off')

# -----------------------------------------------------------------------------------

    def reset_test2(self, entity, attribute, old, new, kwargs) -> None:
        """reset test_2 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_2', state='off')

# -----------------------------------------------------------------------------------

    def reset_test3(self, entity, attribute, old, new, kwargs) -> None:
        """reset test_3 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_3', state='off')

# -----------------------------------------------------------------------------------

    def set_default_state(self) -> None:
        """set default values from backstop default values"""

        # self.set_state('input_boolean.early_alarm', state=self.get_state('input_boolean.default_early_alarm_state'))
        self.set_state('input_boolean.normal_alarm', state=self.get_state('input_boolean.default_normal_alarm_state'))
        self.set_state('input_boolean.lumie', state=self.get_state('input_boolean.default_lumie_state'))
        self.set_state('input_boolean.debug', state=self.get_state('input_boolean.default_debug_state'))
        self.set_state('input_boolean.verbose', state=self.get_state('input_boolean.default_verbose_state'))
        self.set_state('input_boolean.testing', state=self.get_state('input_boolean.default_testing_state'))
        self.set_state('input_boolean.trace', state=self.get_state('input_boolean.default_trace_state'))

# -----------------------------------------------------------------------------------

    def register_test(self, callback, entity_id='input_boolean.test_1', **kwargs) -> None:
        """register test"""

        handler = self.listen_state(callback, entity_id, **kwargs)
        self.log(f'\tcallback {callback.__name__} registered on {entity_id}', level='WARNING')
        self.handlers[entity_id] = handler

# -----------------------------------------------------------------------------------

    def deregister_test(self, entity_id, **kwargs) -> None:
        """deregister test"""

        handler = self.handlers[entity_id] if entity_id in self.handlers else None
        if handler is not None:
            self.log(f'\tcallback {handler} deregistered on {entity_id}', level='WARNING')
            self.cancel_listen_state(handler, **kwargs)

# -----------------------------------------------------------------------------------

    def register_test_1(self, callback, entity_id='input_boolean.test_1', **kwargs) -> None:
        """register test 1"""

        self.register_test(callback, entity_id, **kwargs)

# -----------------------------------------------------------------------------------

    def register_test_2(self, callback, entity_id='input_boolean.test_2', **kwargs) -> None:
        """register test 2"""

        self.register_test(callback, entity_id, **kwargs)

# -----------------------------------------------------------------------------------

    def register_test_3(self, callback, entity_id='input_boolean.test_3', **kwargs) -> None:
        """register test 3"""

        self.register_test(callback, entity_id, **kwargs)

# -----------------------------------------------------------------------------------

    def deregister_test_1(self, **kwargs) -> None:
        """deregister test 1"""

        self.deregister_test('input_boolean.test_1', **kwargs)

# -----------------------------------------------------------------------------------

    def deregister_test_2(self, **kwargs) -> None:
        """deregister test 2"""

        self.deregister_test('input_boolean.test_2', **kwargs)

# -----------------------------------------------------------------------------------

    def deregister_test_3(self, **kwargs) -> None:
        """deregister test 3 and unset test_3 flag"""

        self.deregister_test('input_boolean.test_3', **kwargs)
        self.set_state('input_boolean.test_3', state='off')

# -----------------------------------------------------------------------------------

    def test_test(self, entity, attribute, old, new, kwargs) -> None:
        """test test"""

        self.lib.log_function_name(start=True)
        self.run_in(self.test, 0)
        self.lib.log_function_name(start=False)

        self.lib.log_function_name(start=True, force=True)
        self.run_in(self.test, 0)
        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def reset(self, kwargs) -> None:
        """reset dowstairs motion flag and set default sonos configuration"""

        if self.lib.get_alarm_testing():
            self.call_service('alarm/reset')

        # self.call_service('motion/reset_motion_flag')
        self.call_service('sonos/unjoin_all')

        self.set_state('input_boolean.override', state='off')
        self.set_state('input_boolean.sonos', state='off')
        self.set_state('input_boolean.test_1', state='off')
        self.set_state('input_boolean.test_2', state='off')
        self.set_state('input_boolean.test_3', state='off')
        self.log('\treset', level='WARNING')

# -----------------------------------------------------------------------------------

    def notification(self, message, log=False, title='') -> None:
        """send notification to log, tv and discord"""

        if log or self.get_state('input_boolean.debug') == 'on':
            self.log(f'\tmessage="{message}" title="{title}"')

        self.call_service('notify/lg_webos_tv_oled65c7v', message=message)
        self.call_service('notify/disc0rd', service_data={
            'target': '1250932196613685313',
            'title': title,
            'message': message
        })

# -----------------------------------------------------------------------------------

    def desktop_notification(self, message) -> None:
        """send desktop notification to discord using announcer"""

        self.call_service('announcer/notification', message=message, type='desktop')

# -----------------------------------------------------------------------------------

    def announce(self, message, entity_id, kwargs) -> None:
        """announce to a single device using announcer"""

        self.call_service("announcer/announce", entity_id=entity_id, message=message)

# -----------------------------------------------------------------------------------

    def fix_audio_delay(self, kwargs) -> None:

        delay = self.get_state('number.living_room_audio_delay')
        if delay != 3:
            self.set_state('number.living_room_audio_delay', state=3)

# -----------------------------------------------------------------------------------

    def maxine_travel_time_to_home(self, kwargs) -> None:
        """set travel time to home for maxine. set maxine_driving_status sensor"""

        # self.lib.log_function_name(start=True)
        # self.lib.log_function_name(start=True, force=True)

        home = self.get_state('person.maxine') == 'home'

        if not home:
            # fetch raw values
            result = self.get_state('sensor.google_travel_time')
            direction = self.get_state('sensor.home_maxine_direction_of_travel')
            state = self.get_state('sensor.maxine_iphone_activity')

            for name, val in (('result', result), ('direction', direction), ('state', state)):
                if name == 'result':
                    result = val
                elif name == 'direction':
                    direction = val
                else:
                    state = val

            # debug types
            if self.lib.get_debug():
                self.log(f'\ttypes: result={type(result)} direction={type(direction)} state={type(state)}', level='DEBUG')
                self.log(f'\ttypes: result={result} direction={direction} state={state}', level='DEBUG')

            if result == 'unknown' or result is None:
                self.log('\tmaxine travel time is unknown', level='ERROR')
                # self.lib.log_function_name(start=False)
                return

            try:
                minutes = int(result)
            except (TypeError, ValueError):
                self.log(f'\tUnable to parse travel time: {result!r}', level='ERROR')
                # self.lib.log_function_name(start=False)
                self.lib.log_function_name(start=False, force=True)
                return

            message = f'Max is {minutes} minutes away'

            direction = '' if direction is None else str(direction)
            state = '' if state is None else str(state)

            if state == "Automotive":
                if self.state != 'Driving':
                    self.state = 'Driving'
                    self.set_state('sensor.maxine_driving_status', state=self.state)
            else:
                if self.state != 'Not Driving':
                    self.state = 'Not Driving'
                    self.set_state('sensor.maxine_driving_status', state=self.state)

            ts = self.call_service('timestamp/get', name='travel')

            # compute diff safely
            if ts is None:
                diff = 0
            else:
                try:
                    diff = int((datetime.now() - ts).total_seconds())
                except Exception: # pylint: disable=broad-exception-caught
                    diff = 0

            # ensure direction is compared correctly (avoid using "in" on strings)
            announce = (direction == 'towards') and self.now_is_between('08:00:00', '02:00:00') and (10 <= minutes <= 15) and (diff >= 4 * 60)

            if announce:
                try:
                    ts_str = ts.ctime() if hasattr(ts, 'ctime') else str(ts)
                    ts_ts = ts.timestamp() if hasattr(ts, 'timestamp') else float(diff)
                except Exception: # pylint: disable=broad-exception-caught
                    ts_str = str(ts)
                    ts_ts = float(diff)
                self.log(f'\tmessage={message} ts={ts_str} ({ts_ts:6.3f})', level='DEBUG')
                self.call_service('announcer/announce', entity_id='media_player.study', message=message, timestamp='travel')
        else:
            if self.state != 'Not Driving':
                self.set_state('sensor.maxine_driving_status', state=self.state)

        # self.lib.log_function_name(start=False)
        # self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def set_all_state_event(self, event, data, kwargs) -> None:
        """listener for set_all_state event"""

        self.set_all_state({})

# -----------------------------------------------------------------------------------

    def set_bins_test(self, entity, attribute, old, new, kwargs) -> None:
        """set bins test"""

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.bins_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_notification_test(self, entity, attribute, old, new, kwargs) -> None:
        """set notification test"""

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.notification_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_announcement_test(self, entity, attribute, old, new, kwargs) -> None:
        """set announcement test"""

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.announce_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_front_door_ding_test(self, entity, attribute, old, new, kwargs) -> None:
        """set front door ding test"""

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_ding_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_front_door_light_on_test(self, entity, attribute, old, new, kwargs) -> None:
        """set front door light on test"""

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_light_on_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_test_test(self, entity, attribute, old, new, kwargs) -> None:
        """set test test"""

        action = kwargs['action']

        if action == 'set':
            print('set test test')
            pass # pylint: disable=unnecessary-pass
            # self.register_test_3(self.test_test)
        elif action == 'cancel':
            print('cancel test test')
            pass # pylint: disable=unnecessary-pass
            # self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def backup(self, kwargs) -> None:
        """backup"""

        self.call_service('hassio/backup_full', compressed=True, homeassistant_exclude_database=True)

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:
        """status"""

        status = '\n\n'
        state = self.get_state('input_boolean.default_debug_state')
        status += f'\tdefault_debug_state={state}\n'
        state = self.get_state('input_boolean.default_verbose_state')
        status += f'\tdefault_verbose_state={state}\n'
        state = self.get_state('input_boolean.default_testing_state')
        status += f'\tdefault_testing_state={state}\n\n'
        status += f'\tdebug={self.debug}\n'
        status += f'\tverbose={self.verbose}\n'
        status += f'\ttesting={self.testing}\n\n'

        scheduler = self.get_scheduler_entries()

        # https://stackoverflow.com/questions/521532/how-do-i-get-pythons-pprint-to-return-a-string-instead-of-printing
        s = StringIO()
        pprint.pprint(scheduler['alarms'], s, indent=2, width=1, compact=True)
        status += textwrap.indent(s.getvalue(), '        ')

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:
        """status event"""

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def test_event(self, event, data, kwargs) -> None:
        """test event"""

        print(self.lib.is_playing(self, 'media_player.study'))

# -----------------------------------------------------------------------------------

    def fire_status_event(self, entity, attribute, old, new, kwargs) -> None:
        """fire status event"""

        self.fire_event("status")

# -----------------------------------------------------------------------------------

    # def _call_lib(self, name: str, *args, **kwargs):
    #     """Call a function on self.lib (app instance) or a module function.

    #     - If the attribute is a bound method on the app instance, call it.
    #     - If it's a module-level function expecting (app, ...), call with self first.
    #     - Await if the result is a coroutine/Task.
    #     """
    #     fn = getattr(self.lib, name, None)
    #     if fn is None:
    #         return None

    #     try:
    #         result = fn(*args, **kwargs)
    #     except TypeError:
    #         # probably module function that expects app first
    #         result = fn(self, *args, **kwargs)

    #     if asyncio.iscoroutine(result) or isinstance(result, asyncio.Task):
    #         return await result

    #     return result

# -----------------------------------------------------------------------------------
