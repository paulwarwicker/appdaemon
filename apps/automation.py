# -*- coding: utf-8 -*-

# Dave55
# mDqF3fGKGm9Z
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime, timedelta
import pprint
import textwrap
from io import StringIO
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611

class Automation(Hass):
    """Documentation for Automation"""

    debug = False
    testing = False
    verbose = False
    override = False

    lib = None
    const = None
    state = 'Not Driving'
    log_level = None

    handlers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.call_service('scene/reload')

        self.debug = self.get_state('input_boolean.default_debug_state') == 'on'
        self.verbose = self.get_state('input_boolean.default_verbose_state') == 'on'
        self.testing = self.get_state('input_boolean.default_testing_state') == 'on'

        self.listen_event(self.set_all_state_event, 'set_all_state')
        self.listen_event(self.status_event, 'status')
        self.listen_event(self.test_event, 'test')

        self.listen_state(self.set_console_log_level, 'input_boolean.debug')
        self.listen_state(self.set_console_log_level, 'input_boolean.verbose')

        self.listen_state(self.reset_test1, 'input_boolean.test_1', new='on')
        self.listen_state(self.reset_test2, 'input_boolean.test_2', new='on')

        self.listen_state(self.fire_status_event, 'input_boolean.status', new='on')
        self.listen_state(self.set_debug_flag, 'input_boolean.debug')
        self.listen_state(self.set_verbose_flag, 'input_boolean.verbose')

        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='on', action='set')
        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='off', action='cancel')

        self.run_daily(self.reset, '04:00:00') # daily reset including booleans

        self.run_daily(self.set_all_state, '20:00:00') # set state - make sure before max retires (to bed)

        self.run_daily(self.backup, '23:30:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.maxine_travel_time_to_home, runtime)
        self.run_minutely(self.fix_audio_delay, runtime)

        # runtime = datetime(2024, 1, 1, 0, 0, 0)
        # self.run_hourly(...)

        self.set_all_state({})
        self._set_console_log_level()

        self.call_service('timestamp/init')
        # self.fire_event('timestamps')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

        self.test({})

# -----------------------------------------------------------------------------------

    def test(self, kwargs) -> None:
        """test method"""

        self.lib.log_function_name(True, True)

        # traceback.print_stack() # leave

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def dummy(self) -> None:
        """dummy"""

        self.lib.log_function_name()
        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def set_all_state(self, kwargs) -> None:
        """set all state - reset to false and then set_default_state"""

        self.lib.log_function_name()

        booleans = {
            # !!! do NOT include debug/verbose/testing !!!
            # 'early_alarm', 'normal_alarm', 'test_alarm',
            'lumie', 'test_1', 'test_2', 'test_3', 'sonos',
            'water_garden_1', 'water_garden_15', 'water_garden_20', 'water_garden_30', 'bedtime',
            'reset_alarms', 'test_utility_motion', 'test_kitchen_motion', 'test_bins_announce', 'test_frost_warning', 'test_notification',
            'test_announcement', 'test_maxine_home', 'test_reset', 'test_front_door_ding', 'test_front_door_light_on', 'test_test',
            'test_early_alarm', 'mock_run', 'alarm_debug'
        }

        for boolean in booleans:
            self.set_state(f'input_boolean.{boolean}', state='off')

        self.set_default_state()

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def set_console_log_level(self, entity, attribute, old, new, kwargs) -> None:
        """set console log level depending on the debug flag"""

        self._set_console_log_level()

# -----------------------------------------------------------------------------------

    def _set_console_log_level(self) -> None:
        """internal method to set console level using the debug flag. set the property log_level and report a change"""

        level = "DEBUG" if self.get_state('input_boolean.debug') == 'on' else "INFO"
        prefix = "VERBOSE " if self.get_state('input_boolean.verbose') == 'on' else ""

        if self.log_level != level:
            self.log(f'\tchanging log level to {prefix}{level}')
            self.set_log_level(level)
            self.log_level = level

            for module in self.const.MODULES:
                self.log(f'setting log level {prefix}{level} on app {module}')
                app = self.get_app(module)
                if app is not None:
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

        self.lib.log_function_name()
        self.run_in(self.test, 0)
        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def reset(self, kwargs) -> None:
        """reset dowstairs motion flag and set default sonos configuration"""

        if self.lib.get_alarm_testing():
            self.call_service('alarm/reset')

        self.call_service('motion/reset_motion_flag')
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
        self.call_service('notify/disc0rd', title=title, message=message, target="1250932196613685313")

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

        home = self.get_state('person.maxine') == 'home'

        if not home:
            minutes = int(self.get_state('sensor.google_travel_time'))
            message = f'Max is {minutes} minutes away'
            direction = self.get_state('sensor.home_maxine_direction_of_travel')
            state = self.get_state('sensor.maxine_iphone_activity')

            if state == "Automotive":
                if self.state != 'Driving':
                    self.state = 'Driving'
                    self.set_state('sensor.maxine_driving_status', state=self.state)
            else:
                if self.state != 'Not Driving':
                    self.state = 'Not Driving'
                    self.set_state('sensor.maxine_driving_status', state=self.state)

            ts = self.call_service('timestamp/get', name='travel', return_result=True)
            diff = (datetime.now() - ts).seconds
            announce = direction in ('towards') and self.now_is_between('10:00:00', '02:00:00') and (10 <= minutes <= 15) and (diff >= 4 * 60)

            if announce:
                self.log(f'\tmessage={message} ts={ts.ctime()} ({ts.timestamp():6.3f})', level='DEBUG')
                self.call_service('announcer/announce', entity_id='media_player.study', message=message, timestamp='travel')
        else:
            if self.state != 'Not Driving':
                self.set_state('sensor.maxine_driving_status', state=self.state)

# -----------------------------------------------------------------------------------

    def set_all_state_event(self, event, data, kwargs) -> None:
        """listener for set_all_state event"""

        self.set_all_state({})

# -----------------------------------------------------------------------------------

    def set_bins_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.bins_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_notification_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.notification_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_announcement_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.announce_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_front_door_ding_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_ding_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_front_door_light_on_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_light_on_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def set_test_test(self, entity, attribute, old, new, kwargs) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.test_test)
        elif action == 'cancel':
            self.deregister_test_3()

# -----------------------------------------------------------------------------------

    def backup(self, kwargs) -> None:

        self.call_service('hassio/backup_full', compressed=True, homeassistant_exclude_database=True)

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:

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

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def test_event(self, event, data, kwargs) -> None:

        print(self.lib.is_playing('media_player.study'))

# -----------------------------------------------------------------------------------

    def fire_status_event(self, entity, attribute, old, new, kwargs) -> None:

        self.fire_event("status")

# -----------------------------------------------------------------------------------
