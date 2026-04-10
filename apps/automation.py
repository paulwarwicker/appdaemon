# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import pprint
import textwrap
import traceback # pylint: disable=unused-import
from io import StringIO

# from typing import TYPE_CHECKING, cast

import constants as const # pylint: disable=unused-import

# import automationlib as _helpers  # type: ignore

# from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

# if TYPE_CHECKING:
#     from automationlib import AutomationLib  # type: ignore

from automationbase import AutomationBase  # type: ignore

class Automation(AutomationBase):
    """Documentation for Automation"""

    # debug = False
    # testing = False
    # verbose = False
    # trace = False
    # override = False

    # lib: "AutomationLib" = _helpers  # type: ignore
    # log_level = None

    handlers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # # runtime: get the running AutomationLib app instance (do not instantiate directly)
        # self.lib = cast("AutomationLib", self.get_app('automationlib'))
        # if self.lib is None:
        #     # defensive fallback to module if app not present (optional)
        #     self.lib = _helpers  # type: ignore

        super().initialize()

        self.call_service('scene/reload')

        self.listen_event(self.set_all_state_event, 'set_all_state')
        self.listen_event(self.reset_trace, 'reset')

        self.listen_event(self.status_event, 'status')

        # self.listen_state(self.set_console_log_level, 'input_boolean.debug')
        # self.listen_state(self.set_console_log_level, 'input_boolean.verbose')
        # self.listen_state(self.set_console_log_level, 'input_boolean.trace')
        self.listen_state(self.set_debug_flag, 'input_boolean.debug')
        self.listen_state(self.set_verbose_flag, 'input_boolean.verbose')
        self.listen_state(self.set_testing_flag, 'input_boolean.testing')
        self.listen_state(self.set_trace_flag, 'input_boolean.trace')
        self.listen_state(self.physical_training, 'input_boolean.physical_training')

        self.listen_state(self.reset_test1, 'input_boolean.test_1', new='on')
        self.listen_state(self.reset_test2, 'input_boolean.test_2', new='on')

        self.listen_state(self.fire_status_event, 'input_boolean.status', new='on')

        self.run_daily(self.reset, '04:00:00') # daily reset including booleans

        self.run_daily(self.set_all_state, '20:30:00') # set state - make sure before max retires (to bed)

        self.run_daily(self.backup, '23:30:00')

        self.set_all_state({})
        self._set_console_log_level()

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

        # self.test({})

# -----------------------------------------------------------------------------------

    def test(self, kwargs) -> None:
        """test method"""

        self._log_function_name(start=True)

        # print(self._dow())
        # traceback.print_stack() # leave

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_all_state(self, kwargs) -> None:
        """set all state - reset to false and then set_default_state"""

        self._log_function_name(start=True)

        booleans = {
            'override', 'sonos', 'lumie', 'test_1', 'test_2', 'test_3',
            'water_garden_1', 'water_garden_15', 'water_garden_20', 'water_garden_30', 'bedtime',
            'reset_alarms', 'mock_run', 'alarm_debug',
            'ignore_sensors', 'power_off_media', 'wake_up_boo', 'physical_training',
            # 'test_utility_motion', 'test_kitchen_motion', 'test_bins_announce',
            # 'test_frost_warning', 'test_notification', 'test_announcement', 'test_maxine_home',
            # 'test_reset', 'test_front_door_ding', 'test_front_door_light_on', 'test_early_alarm',
        }

        # ensure certain booleans are not reset whether defined or not
        booleans -= {'debug', 'verbose', 'early_alarm', 'normal_alarm', 'test_alarm'}

        # print(booleans)

        for boolean in booleans:
            self.set_state(f'input_boolean.{boolean}', state='off')

        # self.set_default_state()

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_console_log_level(self, entity, attribute, old, new, kwargs) -> None:
        """set console log level depending on the debug or verboseflag"""

        # separate method required because we are listening to the state of the input_boolean.debug and input_boolean.verbose and needs a specific signature
        self._set_console_log_level()

# -----------------------------------------------------------------------------------

    def set_debug_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set debug flag"""

        self.shared.debug = new == 'on'
        self._set_console_log_level()
        self._set_flag_value('debug', self.shared.debug)
        self.log(f'\tverbose={self.shared.verbose} debug={self.shared.debug} trace={self.shared.trace} testing={self.shared.testing}', level='INFO')

# -----------------------------------------------------------------------------------

    def set_verbose_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set verbose flag"""

        self.shared.verbose = new == 'on'
        self._set_console_log_level()
        self._set_flag_value('verbose', self.shared.verbose)
        self.log(f'\tverbose={self.shared.verbose} debug={self.shared.debug} trace={self.shared.trace} testing={self.shared.testing}', level='INFO')

# -----------------------------------------------------------------------------------

    def set_testing_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set testing flag"""

        self.shared.testing = new == 'on'
        self._set_console_log_level()
        self._set_flag_value('testing', self.shared.testing)
        self.log(f'\tverbose={self.shared.verbose} debug={self.shared.debug} trace={self.shared.trace} testing={self.shared.testing}', level='INFO')

# -----------------------------------------------------------------------------------

    def set_trace_flag(self, entity, attribute, old, new, kwargs) -> None:
        """set trace flag"""

        self.shared.trace = new == 'on' # self.shared.debug = self.shared.verbose =
        self.set_state('input_boolean.debug', state='on' if self.shared.trace else 'off')
        self.set_state('input_boolean.verbose', state='on' if self.shared.trace else 'off')
        self._set_console_log_level()
        self._set_flag_value('trace', self.shared.trace)
        self.log(f'\tverbose={self.shared.verbose} debug={self.shared.debug} trace={self.shared.trace} testing={self.shared.testing}', level='INFO')

# -----------------------------------------------------------------------------------

    def physical_training(self, entity, attribute, old, new, kwargs) -> None:
        """enable physical training setup"""

        if new == 'on':
            self.set_state('input_boolean.wake_up_boo', state='on')
            self.set_state('input_boolean.early_alarm', state='on')
        else:
            self.set_state('input_boolean.wake_up_boo', state='off')
            self.set_state('input_boolean.early_alarm', state='off')

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

    def reset(self, kwargs) -> None:
        """reset dowstairs motion flag and set default sonos configuration"""

        if self._get_alarm_testing():
            self.call_service('alarm/reset')

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
        status += f'\tdebug={self.shared.debug}\n'
        status += f'\tverbose={self.shared.verbose}\n'
        status += f'\ttesting={self.shared.testing}\n\n'

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

        self.status('', '', '', '', {})

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

    def reset_trace(self, kwargs) -> None:
        """reset tracing flag from input_boolean"""

        self.shared.trace = self.shared.verbose = self.shared.debug = self.shared.testing = False

# -----------------------------------------------------------------------------------
