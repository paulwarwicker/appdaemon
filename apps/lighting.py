# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# import asyncio
import asyncio
import traceback
import json
import time
from datetime import datetime
from enum import Enum

import constants as const
from automationbase import AutomationBase  # type: ignore

class Callback(Enum):
    """
    Docstring for Callback
    """
    KITCHEN = 'kitchen'
    UTILITY_ROOM = 'utility_room'
    CLOAKROOM = 'cloakroom'
    BATHROOM = 'bathroom'

class Lighting(AutomationBase):
    """
    Docstringfor Lighting
    """

    DEFAULT_TIMEOUT = const.LONG_TIMEOUT # can't use constants in class variable initialisation
    callback = None

    timers = {}
    reset_on_off = None
    bathroom_callback_handle = None
    cloakroom_callback_handle = None
    kitchen_callback_handle = None
    utility_callback_handle = None
    fan_light_state = False
    expected_fan_light_state = False
    fan_light_enabled = True
    kitchen_cb = None
    kitchen_callback = None
    kitchen_seconds = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.reset_on_off = self.args.get("reset_on_off", True)  # Default to true

        self.register_service('lighting/garage_on', self.garage_on_service)
        self.register_service('lighting/garage_off', self.garage_off_service)
        self.register_service('lighting/front_door_on', self.front_door_on_service)
        self.register_service('lighting/front_door_off', self.front_door_off_service)
        self.register_service('lighting/lumie_on', self.lumie_on_service)
        self.register_service('lighting/lumie_off', self.lumie_off_service)
        self.register_service('lighting/front_door_ding', self.front_door_ding_service)
        self.register_service('lighting/all_off', self.all_off_service)
        self.register_service('lighting/cancel_timer', self.cancel_timer_service)

        self.register_service('lighting/turn_on_if_off', self.turn_on_if_off_service)
        self.register_service('lighting/welcome_lights', self.welcome_lights_service)
        self.register_service('lighting/upstairs_on', self.upstairs_on_service)
        self.register_service('lighting/bedroom_on', self.bedroom_on_service)
        self.register_service('lighting/landing_on', self.landing_on_service)
        self.register_service('lighting/downstairs_on', self.downstairs_on_service)
        self.register_service('lighting/downstairs_off', self.downstairs_off_service)
        self.register_service('lighting/bannister_on', self.bannister_on_service)
        self.register_service('lighting/cloakroom_on', self.cloakroom_on_service)
        self.register_service('lighting/cloakroom_off', self.cloakroom_off_service)
        self.register_service('lighting/bathroom_on', self.bathroom_on_service)
        self.register_service('lighting/bathroom_off', self.bathroom_off_service)
        self.register_service('lighting/utility_on', self.utility_on_service)
        self.register_service('lighting/utility_off', self.utility_off_service)
        self.register_service('lighting/kitchen_on', self.kitchen_on_service)
        self.register_service('lighting/kitchen_off', self.kitchen_off_service)
        self.register_service('lighting/study_off', self.study_off_service)
        self.register_service('lighting/living_room_on', self.living_room_on_service)
        self.register_service('lighting/living_room_off', self.living_room_off_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timers')
        self.listen_event(self.cancel_timers_event, 'cancel_timers')
        self.listen_event(self.welcome_lights_event, 'welcome_lights') # see location for the real welcome_lights event handler
        self.listen_event(self.front_door_on_event, 'front_door_on')
        self.listen_event(self.front_door_ding_event, 'front_door_ding') # already have front_door_ding
        self.listen_event(self.lights_off_event, "ios.action_fired", actionName='Lights')
        self.listen_event(self.lumie_on_event, 'lumie_on')
        self.listen_event(self.lumie_wake_event, 'lumie_wake')
        self.listen_event(self.all_off_event, 'all_off')
        self.listen_event(self.bathroom_on_event, 'bathroom_on')
        self.listen_event(self.bathroom_off_event, 'bathroom_off')
        self.listen_event(self.test_welcome_lights_event, 'test_welcome_lights')
        self.listen_event(self.test_lights_event, 'test_lights')
        self.listen_event(self.test_landing_event, 'test_landing')
        self.listen_event(self.test_cloakroom_event, 'test_cloakroom')
        self.listen_event(self.test_downstairs_event, 'test_downstairs')
        self.listen_event(self.test_event, 'Test')
        self.listen_event(self.learn_event, 'Learn')
        self.listen_event(self.delete_event, 'Delete')

        self.listen_state(self.bathroom_on_full, 'input_boolean.bathroom_override', new='on')
        self.listen_state(self.bathroom_on_full, 'input_boolean.bathroom_override', new='off')
        self.listen_state(self.cloakroom_on_full, 'input_boolean.cloakroom_override', new='on')
        self.listen_state(self.cloakroom_on_full, 'input_boolean.cloakroom_override', new='off')
        self.listen_state(self.kitchen_on_full, 'input_boolean.kitchen_override', new='on')
        self.listen_state(self.kitchen_on_full, 'input_boolean.kitchen_override', new='off')
        self.listen_state(self.utility_on_full, 'input_boolean.utility_override', new='on')
        self.listen_state(self.utility_on_full, 'input_boolean.utility_override', new='off')
        self.listen_state(self.fan_light, 'input_boolean.fan_light')

        self.run_daily(self.living_room_on, 'sunset - 00:10:00')
        self.run_daily(self.downstairs_all_off, '23:30:00')
        self.run_daily(self.garden_lights_on, 'sunset - 00:10:00')
        self.run_daily(self.garden_lights_off, '21:30:00')
        self.run_daily(self.all_off, '02:00:00')

        self.call_service('light/turn_off', entity_id=const.OUTSIDE_LIGHTS)

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.purge_timers, runtime)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def all_off_service(self, namespace, domain, service, data) -> None:
        """all off service"""

        self._log_function_name(start=True)

        self.show_service(namespace, domain, service, data)

        self.call_service('light/turn_off', entity_id=const.ALL_LIGHTS)
        # TODO: cooker/garden lights?

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def welcome_lights_service(self, namespace, domain, service, data) -> None:
        """turn on welcome lights"""

        self._log_function_name(start=True)

        if not self._is_night():
            self.log('\ttoo early for welcome lights', level='DEBUG')
            return

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.WELCOME_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.call_service('lighting/turn_on_if_off', entity_id=const.WELCOME_LIGHTS, brightness=const.HALF_ON, cb='noop')
        self.call_service('lighting/turn_on_if_off', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, cb='noop')

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_on_service(self, namespace, domain, service, data) -> None:
        """turn on front door lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'front_door_off')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.DING_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.call_service('light/turn_on', entity_id=const.FRONT_DOOR, brightness=self._percent_to_brightness(80), transition=10)
        self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=self._percent_to_brightness(25), transition=10)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_off_service(self, namespace, domain, service, data) -> None:
        """turn off front door lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.set_callback(cb, callback)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def kitchen_on_service(self, namespace, domain, service, data) -> None:
        """turn on kitchen lights"""

        force = data.get('force', False)

        if not force and self.check_override('kitchen'):
            return

        self._log_function_name(start=True)

        # main lights
        brightness = self.get_brightness()
        self.call_service('light/turn_on', entity_id=const.KITCHEN_LIGHTS, brightness=brightness)

        # floor lights
        brightness = const.FULL_ON if self.now_is_between('sunrise', '22:00:00') else const.HALF_ON
        self.call_service('light/turn_on', entity_id=const.KITCHEN_FLOOR_LIGHTS, brightness=brightness)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def kitchen_off_service(self, namespace, domain, service, data) -> None:
        """turn off kitchen lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        if self.check_override('kitchen'):
            self.kitchen_cb = cb
            self.kitchen_callback = callback
            self.kitchen_seconds = seconds
            self.callback = Callback.KITCHEN
            self.log('\tdeferring kitchen off service', level='INFO')
            self.run_in(self.deferred_kitchen_off, const.ONEHOUR)
            self._log_function_name(start=False)
            return

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)
        self.set_callback('kitchen_floor_off', self.get_callback('kitchen_floor_off'), const.KITCHEN_FLOOR_TIMEOUT)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def deferred_kitchen_off(self, kwargs) -> None:
        """deferred kitchen off"""

        self.log('\trunning deferred kitchen off', level='INFO')

        if self.check_override('kitchen'):
            self.log('\t\tignoring deferred_kitchen_off', level='WARNING')
            self.run_in(self.deferred_kitchen_off, const.ONEHOUR)
            return

        cb = self.kitchen_cb if self.kitchen_cb is not None else 'noop'
        callback = self.kitchen_callback if self.kitchen_callback is not None else self.get_callback('noop')
        seconds = self.kitchen_seconds if self.kitchen_seconds is not None else const.LONG_TIMEOUT

        self.set_callback(cb, callback, seconds)
        self.set_callback('kitchen_floor_off', self.get_callback('kitchen_floor_off'), const.KITCHEN_FLOOR_TIMEOUT)

        self.kitchen_cb = None
        self.kitchen_callback = None
        self.kitchen_seconds = None

# -----------------------------------------------------------------------------------

    def living_room_on_service(self, namespace, domain, service, data) -> None:
        """turn on living room lights"""

        force = data.get('force', False)

        if not force and self.check_override('living_room'):
            return

        if not self._is_night():
            return

        self._log_function_name(start=True)

        # main lights
        brightness = self.get_brightness()
        self.call_service('light/turn_on', entity_id=const.STANDARD_LAMP, brightness=brightness)
        self.call_service('light/turn_on', entity_id=const.TABLE_LAMP, brightness=brightness)
        self.call_service('light/turn_on', entity_id=const.RADIATOR, brightness=brightness)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def living_room_off_service(self, namespace, domain, service, data) -> None:
        """turn off living room lights"""

        self._log_function_name(start=True)

        # cb = data.get('cb', 'noop')
        # callback = self.get_callback(cb)
        # seconds = data.get('seconds', const.LONG_TIMEOUT)

        # if self.check_override('kitchen'):
        #     self.kitchen_cb = cb
        #     self.kitchen_callback = callback
        #     self.kitchen_seconds = seconds
        #     self.callback = Callback.KITCHEN
        #     self.log('\tdeferring kitchen off service', level='INFO')
        #     self.run_in(self.deferred_kitchen_off, const.ONEHOUR)
        #     self._log_function_name(start=False)
        #     return

        # self.show_service(namespace, domain, service, data, cb, callback, seconds)

        # self.set_callback(cb, callback, seconds)
        # self.set_callback('kitchen_floor_off', self.get_callback('kitchen_floor_off'), const.KITCHEN_FLOOR_TIMEOUT)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_on_service(self, namespace, domain, service, data) -> None:
        """turn on utility lights"""

        force = data.get('force', False)

        if not force and self.check_override('utility_room'):
            self.log('\t\tignoring utility on service', level='WARNING')
            return

        self._log_function_name(start=True)

        # try:
        #     lux = int(self.get_state(const.UTILITY_SENSOR_ILLUMINANCE))
        # except (TypeError, ValueError):
        #     lux = None

        # if lux is not None and lux < const.UTILITY_LUX_THRESHOLD:
        #     # brightness = const.HALF_ON if self.now_is_between(sunset, f'{sunset}{plus1}') or self.now_is_between(sunrise, f'{sunrise}{plus1}') else const.QUARTER_ON
        #     brightness = const.FULL_ON # const.QUARTER_ON if self._is_summer() else const.HALF_ON

        #     self.show_service(namespace, domain, service, data, cb)

        #     if self._get_verbose_debug():
        #         self.log(f'brightness={brightness}', level='DEBUG')

        if self._is_night():
            brightness = self.get_brightness()
            self.call_service('light/turn_on', entity_id=const.UTILITY_ROOM_LIGHTS, brightness=brightness)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_off_service(self, namespace, domain, service, data) -> None:
        """turn off utility lights"""

        if self.check_override('utility_room'):
            self.log('\t\tdeferring utility off service', level='WARNING')
            return

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on bathroom lights"""

        force = data.get('force', False)

        if not force and self.check_override('bathroom'):
            self.log('\t\tignoring bathroom on service', level='WARNING')
            return

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        ## TODO: why no callback?

        # sunrise = 'sunrise'
        # plus1 = '+ 00:30:00'
        # plus2 = '+ 01:00:00'
        # sunset = 'sunset'
        # late = '23:00:00'

        if self.now_is_between('sunrise + 00:30:00', 'sunset + 01:30:00'):
            brightness = const.FULL_ON_THRESHOLD - 1
            color_temp_kelvin = 5800  # Cool daylight (was 171 mireds)
        # elif self.now_is_between(sunrise, f'{sunrise} {plus1}') or self.now_is_between(f'{sunset} {plus2}', late):
        elif self.now_is_between('sunset + 01:30:00', '23:00:00'):
            brightness = const.HALF_ON # const.QUARTER_ON
            color_temp_kelvin = 2300  # Warm white (was 441 mireds)
        else:
            brightness = 25
            color_temp_kelvin = 2300  # Warm white (was 441 mireds)

        self.show_service(namespace, domain, service, data, cb)

        if self._get_verbose_debug():
            self.log(f'brightness={brightness} color_temp_kelvin={color_temp_kelvin}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=const.BATHROOM_LIGHTS, brightness=brightness, color_temp_kelvin=color_temp_kelvin)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_off_service(self, namespace, domain, service, data) -> None:
        """turn off bathroom lights"""

        if self.check_override('bathroom'):
            self.log('\t\tdeferring bathroom off service', level='WARNING')
            return

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.SHORT_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on cloakroom lights"""

        force = data.get('force', False)

        if not force and self.check_override('cloakroom'):
            self.log('\t\tignoring cloakroom on service', level='WARNING')
            return

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')

        sunset = 'sunset'
        sunrise = 'sunrise'
        plus1 = ' + 01:00:00'

        try:
            lux = int(self.get_state(const.CLOAKROOM_SENSOR_ILLUMINANCE))
        except (TypeError, ValueError):
            lux = None

        print(lux)

        if lux is not None and lux < const.CLOAKROOM_LUX_THRESHOLD:
            # brightness = const.HALF_ON if self.now_is_between(sunset, f'{sunset}{plus1}') or self.now_is_between(sunrise, f'{sunrise}{plus1}') else const.QUARTER_ON
            brightness = const.HALF_ON # const.QUARTER_ON if self._is_summer() else const.HALF_ON

            self.show_service(namespace, domain, service, data, cb)

            if self._get_verbose_debug():
                self.log(f'brightness={brightness}', level='DEBUG')

            self.call_service('light/turn_on', entity_id=const.CLOAKROOM, brightness=brightness)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_off_service(self, namespace, domain, service, data) -> None:
        """turn off cloakroom lights"""

        if self.check_override('cloakroom'):
            self.log('\t\tdeferring cloakroom off service', level='WARNING')
            return

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_on_service(self, namespace, domain, service, data) -> None:
        """turn on garage lights"""

        self._log_function_name(start=True)

        if self._is_below_horizon():
            self.call_service('light/turn_on', entity_id=const.GARAGE_LIGHTS)
            self.call_service('timestamp/set', name='garage_lights_on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_off_service(self, namespace, domain, service, data) -> None:
        """turn off garage lights"""

        self._log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.GARAGE_LIGHTS)
        self.call_service('timestamp/set', name='garage_lights_off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_on_service(self, namespace, domain, service, data) -> None:
        """turn on lumie lights""" # time will be checked in lumie_on_window

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        brightness = int(data.get('brightness', self._percent_to_brightness(1)))
        force = data.get('force', False)

        self.show_service(namespace, domain, service, data, cb, callback)

        if self.lumie_on_window(force):
            self.call_service('light/turn_on', entity_id=const.LUMIE, brightness=brightness)
            self.set_callback(cb, callback)
        else:
            self.log('\toutside time window for lumie', level='INFO')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_off_service(self, namespace, domain, service, data) -> None:
        """turn off lumie lights"""

        self._log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.LUMIE, transition=10)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def upstairs_on_service(self, namespace, domain, service, data) -> None:
        """turn on landing and bedroom lights"""

        if self.get_state('input_boolean.disable_bedroom_lights') == 'on':
            self.log('\tbedroom lights disabled', level='WARNING')
            return

        self._log_function_name(start=True)

        # if self.bedroom_on_window():
        #     self.call_service('lighting/lumie_on', brightness=self._percent_to_brightness(20), force=True) # turn on lumie at 20% if outside time window for bedroom or disabled
        #     self._log_function_name(start=False)
        #     return

        self.set_state('input_boolean.disable_bedroom_lights', state='off')

        self.show_service(namespace, domain, service, data)

        upstairs_ts = self.call_service('timestamp/get', name='upstairs') # we return current as previous here because we will reset current shortly
        downstairs_ts = self.call_service('timestamp/get', name='downstairs') # we return current as previous here because we will reset current shortly
        prev_upstairs_ts = self.call_service('timestamp/get', name='prev_upstairs') # we return current as previous here because we will reset current shortly

        diff1 = (upstairs_ts - downstairs_ts).seconds
        diff2 = (upstairs_ts - prev_upstairs_ts).seconds
        # self.log(f'\tdiff1={diff1} diff2={diff2} test1={diff1 < 1*60} test2={diff2 < const.LONGER_TIMEOUT}')

        if diff1 < 1*60: # light will be on from downstairs motion, we are setting the callback to turn off
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT)

        if diff2 < 2*60: # and not nomotion: # max gone to loo
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=20)

        if self.now_is_between('sunset + 00:30:00', '23:30:00'): # and nomotion:
            self.call_service('lighting/landing_on', cb='landing_off', seconds=const.LONGER_TIMEOUT)
            # self.call_service('lighting/bedroom_on', cb='bedroom_off', seconds=const.THIRTY_SECONDS)
            self.call_service('lighting/lumie_on', brightness=self._percent_to_brightness(20), force=True)
            self.run_in(self.lumie_off, const.THIRTY_SECONDS)
            self.call_service('lighting/downstairs_off', cb='downstairs_off', seconds=0)
        else:
            self.call_service('lighting/lumie_on') # noop callback by default
            self.call_service('lighting/downstairs_off')
            self.call_service('lighting/study_off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def downstairs_on_service(self, namespace, domain, service, data) -> None:
        """turn on bannister and hallway lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', const.LONG_TIMEOUT))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        try:
            lux = int(self.get_state(const.DOWNSTAIRS_SENSOR_ILLUMINANCE))
        except (TypeError, ValueError):
            lux = None

        if lux is not None and lux < const.DOWNSTAIRS_SENSOR_LUX_THRESHOLD:
            self.set_callback(cb, callback, seconds)

            self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON)
            self.call_service('light/turn_on', entity_id=const.BANNISTER, brightness=self._percent_to_brightness(12))

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def downstairs_off_service(self, namespace, domain, service, data) -> None:
        """turn off bannister and hallway lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'downstairs_off')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', 0)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bannister_on_service(self, namespace, domain, service, data) -> None:
        """turn on bannister light"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', 30))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.call_service('light/turn_on', entity_id=const.BANNISTER)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom lights"""

        # force = {}
        # force = {'force': True}

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.SHORT_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        if self.bedroom_on_window():
            # self.call_service('fan/light_on')
            self.call_service('lighting/lumie_on', brightness=self._percent_to_brightness(20), force=True) # turn on lumie at 20% if outside time window for bedroom or disabled
            self.set_callback(cb, callback, seconds)
        else:
            self.log('\toutside time window for bedroom', level='INFO')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def landing_on_service(self, namespace, domain, service, data) -> None:
        """turn on landing lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        if self._is_below_horizon():
            self.show_service(namespace, domain, service, data, cb, callback, seconds)

            self.set_callback(cb, callback, seconds)

            self.call_service('light/turn_on', entity_id=const.LANDING, brightness=const.QUARTER_ON)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def turn_on_if_off_service(self, namespace, domain, service, data) -> None:
        """turn on a light if it off"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', const.LONG_TIMEOUT))
        brightness = int(data.get('brightness', const.QUARTER_ON))
        color_temp_kelvin = int(data.get('color_temp_kelvin', 6500))  # Default to cool white
        entity_id = data.get('entity_id', [])

        if isinstance(entity_id, str):
            entity_id = [entity_id]

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        if self._get_verbose_debug():
            self.log(f'\tentity_id={entity_id} brightness={brightness} color_temp_kelvin={color_temp_kelvin}', level='DEBUG')

        for entity in entity_id:
            prev_state = self.get_state(entity)
            prev_brightness = self.get_state(entity, attribute="brightness")

            if prev_state == 'off':
                self.call_service('light/turn_on', entity_id=entity, brightness=brightness, color_temp_kelvin=color_temp_kelvin)
            else:
                self.log(f'\t{service}: ignored - {entity} already on brightness={prev_brightness}', level='INFO')

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_ding_service(self, namespace, domain, service, data) -> None:
        """turn on front door/hallway lights"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', 0))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.call_service('light/turn_on', entity_id=const.FRONT_DOOR, brightness=const.FULL_ON, transition=10)
        self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, transition=10)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cancel_timer_service(self, namespace, domain, service, data) -> None:
        """cancel a timer"""

        self._log_function_name(start=True)

        name = data.get('name', None)
        cb = data.get('cb', None)
        callback = self.get_callback(cb)

        if self.get_timer(name) is not None:
            self._cancel_timer(name)


        self.show_service(namespace, domain, service, data, cb, callback)

        if callback is not None:
            self.set_callback(cb, callback, 0)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_off_service(self, namespace, domain, service, data) -> None:
        """turn off study light"""

        self._log_function_name(start=True)

        cb = data.get('cb', 'study_off')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', 0)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def all_off_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/all_off')
        self.call_service('sonos/stop', entity_id=const.BEDROOM_SPEAKER)

# -----------------------------------------------------------------------------------

    def lights_off_event(self, event, data, kwargs) -> None:
        """turn off all lights"""

        self.call_service('lighting/all_off')

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.print_timers()

# -----------------------------------------------------------------------------------

    def cancel_timers_event(self, event, data, kwargs) -> None:

        self.cancel_timers()

# -----------------------------------------------------------------------------------

    def welcome_lights_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off', seconds=20)

# -----------------------------------------------------------------------------------

    def front_door_on_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/front_door_on', cb='front_door_off', seconds=10)

# -----------------------------------------------------------------------------------

    def bathroom_on_event(self, event, data, kwargs) -> None:

        brightness = data.get('brightness', 25)
        seconds = data.get('seconds', 10)

        self.call_service('lighting/bathroom_on', seconds=seconds, brightness=brightness, cb='bathroom_off')

# -----------------------------------------------------------------------------------

    def bathroom_off_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/bathroom_off', seconds=0, cb='bathroom_off')

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/front_door_ding', cb='front_door_hallway_off')

# -----------------------------------------------------------------------------------

    def lumie_on_event(self, event, data, kwargs) -> None:

        force = data.get('force', False)
        brightness = data.get('brightness', self._percent_to_brightness(1))

        self.call_service('lighting/lumie_on', brightness=brightness, force=force)

# -----------------------------------------------------------------------------------

    def lumie_wake_event(self, event, data, kwargs) -> None:

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=const.QUARTER_ON, rgb_color=[255, 180, 10])

# -----------------------------------------------------------------------------------

    def test_welcome_lights_event(self, event, data, kwargs):

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off', seconds=10)

# -----------------------------------------------------------------------------------

    async def test_lights_event(self, event, data, kwargs):

        await self.flash(entity_id=const.STUDY)

    async def flash(self, *args, **kwargs) -> None:

        entity_id = kwargs.get('entity_id', const.STUDY)
        times = int(kwargs.get('times', 5))
        interval = float(kwargs.get('interval', 0.1))

        state = self.get_state(entity_id=entity_id, state='state')

        for _ in range(times):
            self.call_service('light/turn_on', entity_id=entity_id, brightness=const.FULL_ON)
            await asyncio.sleep(interval)
            self.call_service('light/turn_off', entity_id=entity_id)
            await asyncio.sleep(interval*2)

        self.call_service('light/turn_on', entity_id=entity_id, state=state)

# -----------------------------------------------------------------------------------

    def test_landing_event(self, event, data, kwargs):

        self.set_state('binary_sensor.downstairs_sensor_motion', state='on')
        time.sleep(10)
        self.set_state('binary_sensor.upstairs_sensor_motion', state='on')

# -----------------------------------------------------------------------------------

    def test_cloakroom_event(self, event, data, kwargs):

        self.set_state('binary_sensor.garage_sensor_motion', state='on')
        time.sleep(5)
        self.set_state('binary_sensor.garage_sensor_motion', state='off')

# -----------------------------------------------------------------------------------

    def test_downstairs_event(self, event, data, kwargs):

        self.set_state('binary_sensor.downstairs_sensor_motion', state='on')
        time.sleep(5)
        self.set_state('binary_sensor.downstair_sensor_motion', state='off')

# -----------------------------------------------------------------------------------

    def learn_event(self, event, data, kwargs):

        command=data.get('name', None)
        print(f'\tlearn {command}')
        self.call_service('remote/learn_command', entity_id='remote.broadlink', device='fan', command=command, command_type='rf')

# -----------------------------------------------------------------------------------

    def test_event(self, event, data, kwargs):

        command=data.get('name', None)
        print(f'\ttest {command}')
        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command=command)

# -----------------------------------------------------------------------------------

    def delete_event(self, event, data, kwargs):

        command=data.get('name', None)
        print(f'\tdelete {command}')
        self.call_service('remote/delete_command', entity_id='remote.broadlink', device='fan', command=command)

# -----------------------------------------------------------------------------------

    def hallway_on(self, kwargs) -> None:

        if self._is_night():  # civil dusk till civil dawn
            if self._get_verbose_debug():
                self.log('\tturn on hallway light', level='DEBUG')

            self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, transition=10)

# -----------------------------------------------------------------------------------

    def hallway_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def bedroom_off(self, kwargs) -> None:

        self._log_function_name(start=True)

        self.call_service('lighting/lumie_off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def landing_off(self, kwargs) -> None:

        self._log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.HALLWAY3, transition=10)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_off(self, kwargs) -> None:

        self._log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.STUDY, transition=10)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def living_room_on(self, kwargs) -> None:
        """turn on living room lights"""

        for entity_id in const.LIVING_ROOM:
            if not self.is_light_on(entity_id):
                self.call_service('light/turn_on', entity_id=entity_id, brightness=self._percent_to_brightness(40), transition=10)

# -----------------------------------------------------------------------------------

    def stairs_on(self, kwargs) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id=const.LANDING, brightness=self._percent_to_brightness(25), transition=10)

# -----------------------------------------------------------------------------------

    def downstairs_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.HALLWAY1, transition=10)
        self.run_in(self.bannister_off, const.BANNISTER_TIMEOUT)

# -----------------------------------------------------------------------------------

    def lumie_off(self, kwargs) -> None:
        """turn off lumie light"""

        self.call_service('light/turn_off', entity_id=const.LUMIE, transition=10)

# -----------------------------------------------------------------------------------

    def cloakroom_off(self, kwargs) -> None:
        """turn off cloakroom light"""

        if self.check_override('cloakroom'):
            return

        self.call_service('light/turn_off', entity_id=const.CLOAKROOM, transition=10)
        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def welcome_lights_off(self, kwargs) -> None:
        """turn off welcome lights excluding standard lamp"""

        self.call_service('light/turn_off', entity_id=const.FRONT_DOOR, transition=10)
        self.call_service('light/turn_off', entity_id=const.HALLWAY1, transition=10)
        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def bathroom_off(self, kwargs) -> None:
        """turn off bathroom lights"""

        if self.check_override('bathroom'):
            return

        self.call_service('light/turn_off', entity_id=const.BATHROOM_LIGHTS, transition=10)
        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def front_door_hallway_off(self, kwargs) -> None:

        key = kwargs.get('key', None)

        hallway_lights = self.light_entities('hallway', const.N_HALLWAY_ENTITIES - 1) # pylint: disable=C0103 disable=W0201

        self.front_door_off(kwargs)

        if key is not None:
            self.log(f'\tturn off hallway - {key}', level='INFO')

        self.call_service('light/turn_off', entity_id=hallway_lights, transition=10)

# -----------------------------------------------------------------------------------

    def garden_lights_on(self, kwargs) -> None:
        """turn on outside lights"""

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn on outside - {key}', level='INFO')

        self.call_service('light/turn_on', entity_id=const.OUTSIDE_LIGHTS)

# -----------------------------------------------------------------------------------

    def garden_lights_off(self, kwargs) -> None:
        """turn off outside lights"""

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off outside - {key}', level='INFO')

        self.call_service('light/turn_off', entity_id=const.OUTSIDE_LIGHTS)

# -----------------------------------------------------------------------------------

    def downstairs_all_off(self, kwargs) -> None:
        """turn off all downstairs lights apart  from study"""

        self.call_service('light/turn_off', entity_id=const.LIVING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=const.STANDARD_LAMP) # try again - wasn't switching off
        self.call_service('light/turn_off', entity_id=const.UTILITY_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=const.DINING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=const.OUTSIDE_LIGHTS)

        self.call_service('switch/turn_off', entity_id=const.COOKER_LIGHTS)

# -----------------------------------------------------------------------------------

    def all_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    def kitchen_off(self, kwargs) -> None: # callback

        if self.check_override('kitchen'):
            return

        entity_ids = self.light_entities('kitchen', const.N_KITCHEN_ENTITIES)

        self.call_service('light/turn_off', entity_id=entity_ids, transition=20)

        cb = 'kitchen_floor_off'
        callback = self.get_callback(cb)

        self.set_callback(cb, callback, 5*60)
        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs) -> None: # callback

        self.call_service('light/turn_off', entity_id=const.KITCHEN_FLOOR_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def utility_off(self, kwargs) -> None:

        if self.check_override('utility_room'):
            return

        self.call_service('light/turn_off', entity_id=const.UTILITY_ROOM_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def front_door_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.FRONT_DOOR, transition=10)
        self.call_service('light/turn_off', entity_id=const.HALLWAY1, transition=10)

# -----------------------------------------------------------------------------------

    def bannister_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.BANNISTER, transition=10)

# -----------------------------------------------------------------------------------

    def set_timer(self, name, timer, callback=None) -> None:
        """set a timer and record callback name"""

        old = self.timers.get(name, None)

        if old is not None:
            if self.check_timer(name, old):
                self.log(f'\treplacing name={name} old={old} with new={timer}', level='DEBUG')
                self._cancel_timer(name)

        self.log(f'\tadding new timer name={name} timer={timer}', level='DEBUG')

        cb_name = None
        try:
            if callable(callback):
                cb_name = getattr(callback, '__name__', str(callback))
            else:
                cb_name = callback
        except Exception:
            cb_name = None

        # store a small dict so we can show which callback will run for this timer
        self.timers[name] = {'handle': timer, 'callback': cb_name}

# -----------------------------------------------------------------------------------

    def get_timer(self, name): # -> str | None:
        """get a timer object (may contain handle and callback)"""

        timer = self.timers.get(name, None)

        if timer is not None and self._get_verbose_debug():
            handle = timer.get('handle') if isinstance(timer, dict) else timer
            cb = timer.get('callback') if isinstance(timer, dict) else None
            self.log(f'\treturning name={name} timer={handle} callback={cb}', level='DEBUG')

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name) -> None:
        """cancel a timer callback"""

        verbose = self._get_verbose_debug()

        timer = self.get_timer(name)

        handle = None
        if isinstance(timer, dict):
            handle = timer.get('handle')
        else:
            handle = timer

        # Validate handle before attempting cancel
        if handle is None:
            self.log(f'\t_cancel_timer: no handle for name={name}', level='WARNING')
            # Ensure stale entry removed
            self.timers.pop(name, None)
            return

        # If available, prefer checking timer existence via info_timer or timer_running
        valid = True
        try:
            if hasattr(self, 'info_timer'):
                info = self.info_timer(handle)
                if info is None:
                    # info_timer returns None for non-existent timers
                    valid = False
            elif hasattr(self, 'timer_running'):
                if not self.timer_running(handle):
                    valid = False
        except Exception as exc:  # defensive: if checking fails, log and continue to attempt cancel
            self.log(f'\t_cancel_timer: error checking handle for name={name} handle={handle} exc={exc}', level='ERROR')

        if not valid:
            self.log(f'\t_cancel_timer: handle not valid or not running for name={name} handle={handle}', level='WARNING')
            self.timers.pop(name, None)
            return

        # Attempt cancel
        self.log(f'\tcancelling running timer name={name} timer={handle}', level='INFO')
        if verbose:
            self.log(f'\tcancelling running timer name={name} timer={handle}', level='DEBUG')

        try:
            self.cancel_timer(handle)
        except Exception as exc:
            self.log(f'\t_cancel_timer: exception cancelling name={name} handle={handle} exc={exc}', level='ERROR')

        # Remove stored reference regardless of cancel outcome
        self.timers.pop(name, None)

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        timer = self.timers.get(name, None)

        if timer is not None:
            handle = timer.get('handle') if isinstance(timer, dict) else timer
            self.log(f'\tremoving timer name={name} timer={handle}', level='INFO')
            self.timers.pop(name, None)
        else:
            self.log(f'\tremove_timer no timer name={name}', level='INFO')

# -----------------------------------------------------------------------------------

    def check_timer(self, name, timer) -> bool:

        verbose = self._get_verbose_debug()

        if not verbose:
            return True

        if timer is None:
            self.log(f'timer is None name={name}', level='ERROR')
            return False

        handle = timer.get('handle') if isinstance(timer, dict) else timer

        extant = self.info_timer(handle)

        if extant is None:
            self.log(f'{name} timer is no longer extant. removing', level='ERROR')
            self.remove_timer(name)
            return False

        end_time, interval, timer_kwargs = self.info_timer(handle)

        return True

# -----------------------------------------------------------------------------------

    def print_timers(self) -> None:
        """print timers"""

        self.purge_timers({})

        status = '\n\n\ttimers:\n\n'

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is None:
                continue

            handle = timer.get('handle') if isinstance(timer, dict) else timer
            cb = timer.get('callback') if isinstance(timer, dict) else None

            if handle is not None and self.timer_running(handle):
                result = self.info_timer(handle)
                if result is None:
                    continue

                end_time, interval, timer_kwargs = result  # Unpack only if result is not None
                remaining = end_time - datetime.now()
                _, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)

                # normalize interval to seconds (int) and build human readable
                try:
                    if isinstance(interval, (int, float)):
                        secs = int(interval)
                    elif hasattr(interval, 'total_seconds'):
                        secs = int(interval.total_seconds())
                    else:
                        secs = int(float(interval))
                except Exception:
                    secs = 0

                if secs:
                    h, rem = divmod(secs, 3600)
                    m, s = divmod(rem, 60)
                    interval_hr = f"{h}h{m}m{s}s" if h else f"{m}m{s}s"
                else:
                    interval_hr = 'one-shot'

                try:
                    kw_str = json.dumps(timer_kwargs, default=str)
                except Exception:
                    kw_str = repr(timer_kwargs)

                status += (
                    f'\tremaining={minutes:02d}:{seconds:02d} handle={handle} end_time={end_time} '
                    f'interval={secs} ({interval_hr}) callback={cb} kwargs={kw_str} '
                    f'isrunning={self.timer_running(handle)}\n'
                )

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    def purge_timers(self, kwargs) -> None:
        """purge timers"""

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is None:
                self.timers.pop(key, None)
                continue

            handle = timer.get('handle') if isinstance(timer, dict) else timer

            if handle is not None and self.timer_running(handle):
                result = self.info_timer(handle)
                if result is None:
                    self.log(f"purging timer {handle}", level="DEBUG")
                    self.timers.pop(key, None) # ignore value
                    continue
            else:
                self.log(f'\t{key} timer is no longer extant or key ({key}) is invalid. pruning', level='DEBUG')
                self.timers.pop(key, None) # ignore value

# -----------------------------------------------------------------------------------

    def cancel_timers(self) -> None:
        """cancel timers"""

        self.log('\ttimers:')

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key)
            if timer is None:
                self.timers.pop(key, None)
                continue

            handle = timer.get('handle') if isinstance(timer, dict) else timer

            if handle is not None and self.timer_running(handle):
                end_time, interval, timer_kwargs = self.info_timer(handle)
                cb = timer.get('callback') if isinstance(timer, dict) else None

                try:
                    if isinstance(interval, (int, float)):
                        secs = int(interval)
                    elif hasattr(interval, 'total_seconds'):
                        secs = int(interval.total_seconds())
                    else:
                        secs = int(float(interval))
                except Exception:
                    secs = 0

                if secs:
                    h, rem = divmod(secs, 3600)
                    m, s = divmod(rem, 60)
                    interval_hr = f"{h}h{m}m{s}s" if h else f"{m}m{s}s"
                else:
                    interval_hr = 'one-shot'

                try:
                    kw_str = json.dumps(timer_kwargs, default=str)
                except Exception:
                    kw_str = repr(timer_kwargs)

                self.log(
                    f"\tname={key} timer={handle} callback={cb} end_time={end_time} "
                    f"interval={secs} ({interval_hr}) kwargs={kw_str} isrunning={self.timer_running(handle)}"
                )
            else:
                self.log(f'\t{key} timer is no longer extant or key ({key}) is invalid. pruning', level='INFO')
                self.timers.pop(key, None) # ignore value

# -----------------------------------------------------------------------------------

    def light_entities(self, name, count=1):
        """generate a list of light entity names"""

        entities = []

        for entity in range(1, count+1):
            entities.append(f'light.{name}_{entity}')

        return entities

# -----------------------------------------------------------------------------------

    def any_light_on_full(self, area)  -> bool:
        """is any light on full"""

        entity_ids = self.light_entities_for_area(area)

        result=False

        for entity_id in entity_ids:
            brightness = self.get_state(entity_id=entity_id, attribute="brightness")
            self.log(f'entity_id={entity_id} brightness={brightness}', level='DEBUG')
            if brightness is not None and brightness > const.FULL_ON_THRESHOLD:
                result=True
                break

        self.log(f'any_light_on_full returning {result} for {area}', level='DEBUG')

        return result

# -----------------------------------------------------------------------------------

    def light_entities_for_area(self, area):
        """light entities for area"""

        entity_ids = []

        if area == 'kitchen':
            entity_ids = self.light_entities(area, const.N_KITCHEN_ENTITIES)
        elif area == 'utility_room':
            entity_ids = [ const.UTILITY ] # self.light_entities(area, const.N_UTILITY_ROOM_ENTITIES)
        elif area == 'bathroom':
            entity_ids = self.light_entities(area, const.N_BATHROOM_ENTITIES)
        elif area == 'cloakroom':
            entity_ids = [ const.CLOAKROOM ] # self.light_entities(area, const.N_CLOAKROOM_ENTITIES)

        return entity_ids

# -----------------------------------------------------------------------------------

    def any_light_on(self, area)  -> bool:
        """is any light on"""

        entity_ids = self.light_entities_for_area(area)

        for entity_id in entity_ids:
            if self.is_light_on(entity_id):
                return True

        return False

# -----------------------------------------------------------------------------------

    def is_light_on(self, entity_id)  -> bool:
        """is light on"""

        brightness = self.get_state(entity_id=entity_id, attribute="brightness")

        return brightness is not None and brightness >= 5

# -----------------------------------------------------------------------------------

    def toggle_bedroom_light(self) -> None:
        """toggle bedroom light"""

        self._log_function_name(start=True)

        state = self.fan_light_state
        self.fan_light_state = not self.fan_light_state

        message=f'toggle_bedroom_light fan_light_state={self.fan_light_state} was {state}'

        if self.fan_light_enabled:
            self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')
        self.call_service('announcer/notification', message=message, type='desktop')

        self.log(f'\t{message}', level='INFO')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_callback(self, cb=None, callback=None, seconds=DEFAULT_TIMEOUT) -> None:

        if cb is not None:
            self._cancel_timer(cb)

        if callback is None:
            self.log('no callback specified', 'ERROR')
            traceback.print_stack()
        else:
            if cb != 'noop' and cb is not None:
                timer = self.run_in(callback, seconds, key=cb, seconds=seconds)
                self.set_timer(cb, timer, callback)
                self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def get_callback(self, cb):

        callback = None

        if cb is not None:
            callback = getattr(self, cb)

        return callback

# -----------------------------------------------------------------------------------

    def show_service(self,namespace, domain, service, data, cb=None, callback=None, seconds=None) -> None:

        if self._get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} callback={callback} seconds={seconds}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def lumie_on_window(self, force):

        if force:
            self.log(f'lumie_on_window returning True because force={force}', level='DEBUG')

        return self.now_is_between('23:30:00', '04:00:00') or force

# -----------------------------------------------------------------------------------

    def noop(self, kwargs) -> None:

        pass

# -----------------------------------------------------------------------------------

    def bathroom_on_full(self, entity, attribute, old, new, kwargs) -> None:
        """bathroom on full"""

        if new == 'on':
            self.call_service('lighting/bathroom_on', entity_id=const.BATHROOM_LIGHTS, cb='noop', seconds=const.SHORT_TIMEOUT, force=True)
            self.bathroom_callback_handle = self.run_in(self.bathroom_off, const.ONEHOUR, force=True)
        else:
            self.call_service('lighting/bathroom_off', entity_id=const.BATHROOM_LIGHTS, cb='bathroom_off', seconds=0, force=True)
            if self.bathroom_callback_handle is not None:
                self.cancel_timer(self.bathroom_callback_handle)
            self.bathroom_callback_handle = None

# -----------------------------------------------------------------------------------

    def cloakroom_on_full(self, entity, attribute, old, new, kwargs) -> None:
        """cloakroom on full"""

        if new == 'on':
            self.call_service('lighting/cloakroom_on', entity_id=const.CLOAKROOM, cb='noop', seconds=const.SHORT_TIMEOUT, force=True)
            self.cloakroom_callback_handle = self.run_in(self.cloakroom_off, const.HALFHOUR, force=True)
        else:
            self.call_service('lighting/cloakroom_off', entity_id=const.CLOAKROOM, cb='cloakroom_off', seconds=0, force=True)
            if self.cloakroom_callback_handle is not None:
                self.cancel_timer(self.cloakroom_callback_handle)
            self.cloakroom_callback_handle = None

# -----------------------------------------------------------------------------------

    def kitchen_on_full(self, entity, attribute, old, new, kwargs) -> None:
        """kitchen on full"""

        if new == 'on':
            self.call_service('lighting/kitchen_on', entity_id=const.KITCHEN_LIGHTS, cb='noop', seconds=const.SHORT_TIMEOUT, force=True)
            self.kitchen_callback_handle = self.run_in(self.kitchen_off, const.ONEHOUR, force=True)
        else:
            self.call_service('lighting/kitchen_off', entity_id=const.KITCHEN_LIGHTS, cb='kitchen_off', seconds=0, force=True)
            self.call_service('lighting/kitchen_off', entity_id=const.KITCHEN_LIGHTS, cb='kitchen_off', seconds=0, force=True) # just in case
            self.kitchen_floor_off({})
            if self.kitchen_callback_handle is not None:
                self.cancel_timer(self.kitchen_callback_handle)
            self.kitchen_callback_handle = None

# -----------------------------------------------------------------------------------

    def utility_on_full(self, entity, attribute, old, new, kwargs) -> None:
        """utility room on full"""

        if new == 'on':
            self.call_service('lighting/utility_on', entity_id=const.UTILITY, cb='noop', seconds=const.SHORT_TIMEOUT, force=True)
            self.utility_callback_handle = self.run_in(self.utility_off, const.ONEHOUR, force=True)
        else:
            self.call_service('lighting/utility_off', entity_id=const.UTILITY, cb='utility_off', seconds=0, force=True)
            if self.utility_callback_handle is not None:
                self.cancel_timer(self.utility_callback_handle)
            self.utility_callback_handle = None

# -----------------------------------------------------------------------------------

    def fan_light(self, entity, attribute, old, new, kwargs) -> None:
        """toggle ceiling fan light"""

        # state = self.get_state('input_boolean.fan_light')

        # input_boolean.fan_light will reflect the state of the ceiling fan light
        # if new == 'on' and state != 'on' or new == 'off' and state != 'off':

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')

# -----------------------------------------------------------------------------------

    def bedroom_on_window(self) -> bool:
        """bedroom on window"""

        return self.now_is_between('sunset', f'{const.BEDROOM_WINDOW_ON_HOUR}:00:00')

# -----------------------------------------------------------------------------------

    def get_brightness(self) -> int:
        """get brightness"""

        # if self._is_summer():
        #     brightness = const.HALF_ON if self.now_is_between('sunrise', 'sunset') else const.QUARTER_ON
        # else:
        #     brightness = (const.FULL_ON_THRESHOLD - 1) if self.now_is_between('sunrise', 'sunset') else const.HALF_ON

        # if self._is_summer():
        #     brightness = (const.FULL_ON_THRESHOLD - 1) if self.now_is_between('sunrise', '22:00:00') else const.HALF_ON # was 'sunset + 02:30:00'
        # else:
        #     brightness = const.HALF_ON if self.now_is_between('sunrise', 'sunset + 02:30:00') else const.QUARTER_ON

        brightness = (const.FULL_ON_THRESHOLD - 1) if self.now_is_between('sunrise', '22:00:00') else const.HALF_ON # was 'sunset + 02:30:00'

        return brightness

# -----------------------------------------------------------------------------------

    def check_override(self, name) -> bool:
        """check override"""

        bool_entity_id = f'input_boolean.{name}_override'

        override = self.get_state(bool_entity_id) == 'on' or self.any_light_on_full(name)

        if override:
            self.log(f'\tignoring {name} off service', level='INFO')

        return override

# -----------------------------------------------------------------------------------
