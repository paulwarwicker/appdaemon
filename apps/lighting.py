# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# import asyncio
import traceback
import time
from datetime import datetime

# from typing import TYPE_CHECKING, Optional, cast # , Any
from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Lighting(Hass):
    """Documentation for Lighting"""

    DEFAULT_TIMEOUT = const.LONG_TIMEOUT # can't use constants in class variable initialisation

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

    # Expose lib as AutomationLib for the type checker; default to the helper module so
    # pylint/mypy see the attributes without requiring per-file casts. initialise()
    # will replace this with the running AppDaemon app instance.
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))  # type: ignore
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # fallback
        assert self.lib is not None

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

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timers')
        self.listen_event(self.cancel_timers_event, 'cancel_timers')
        self.listen_event(self.welcome_lights_event, 'welcome_lights') # see location for the real welcome_lights event handler
        self.listen_event(self.front_door_on_event, 'front_door_on')
        self.listen_event(self.front_door_ding_event, 'front_door_ding_lights')
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

        self.run_daily(self.living_room_on, 'sunset - 00:10:00')
        self.run_daily(self.downstairs_all_off, '23:30:00')
        self.run_daily(self.outside_off, '21:30:00')
        self.run_daily(self.all_off, '02:00:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.purge_timers, runtime)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def all_off_service(self, namespace, domain, service, data) -> None:
        """all off service"""

        self.lib.log_function_name(start=True)

        self.show_service(namespace, domain, service, data)

        self.call_service('light/turn_off', entity_id=const.ALL_LIGHTS)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def welcome_lights_service(self, namespace, domain, service, data) -> None:
        """turn on welcome lights"""

        self.lib.log_function_name(start=True)

        if not self.lib.is_night():
            self.log('\ttoo early for welcome lights', level='DEBUG')
            return

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.WELCOME_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.call_service('lighting/turn_on_if_off', entity_id=const.WELCOME_LIGHTS, brightness=const.HALF_ON, cb='noop')
        self.call_service('lighting/turn_on_if_off', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, cb='noop')

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_on_service(self, namespace, domain, service, data) -> None:
        """turn on front door lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        ## TODO: why no callback?

        # self.show_service(namespace, domain, service, data, cb, callback)

        self.call_service('light/turn_on', entity_id=const.FRONT_DOOR, brightness=self.lib.percent_to_brightness(80), transition=10)
        self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=self.lib.percent_to_brightness(25), transition=10)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_off_service(self, namespace, domain, service, data) -> None:
        """turn off front door lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.set_callback(cb, callback)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def kitchen_on_service(self, namespace, domain, service, data) -> None:
        """turn on kitchen lights"""

        self.lib.log_function_name(start=True)

        force = data.get('force', False)

        if not force and (self.get_state('input_boolean.kitchen_override') == 'on' or self.any_light_on_full('kitchen')):
            self.log('\tignoring kitchen on service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        brightness = self.get_brightness()

        self.call_service('light/turn_on', entity_id=const.KITCHEN_LIGHTS, brightness=brightness)
        brightness = const.FULL_ON if self.now_is_between('sunrise', 'sunset') else const.HALF_ON
        self.call_service('light/turn_on', entity_id=const.KITCHEN_FLOOR_LIGHTS, brightness=brightness)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def kitchen_off_service(self, namespace, domain, service, data) -> None:
        """turn off kitchen lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        if self.get_state('input_boolean.kitchen_override') == 'on' or self.any_light_on_full('kitchen'):
            self.kitchen_cb = cb
            self.kitchen_callback = callback
            self.kitchen_seconds = seconds
            self.log('\tdeferring kitchen off service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)
        self.set_callback('kitchen_floor_off', self.get_callback('kitchen_floor_off'), const.KITCHEN_FLOOR_TIMEOUT)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_on_service(self, namespace, domain, service, data) -> None:
        """turn on utility lights"""

        self.lib.log_function_name(start=True)

        force = data.get('force', False)

        if not force and (self.get_state('input_boolean.utility_override') == 'on' or self.any_light_on_full('utility_room')):
            self.log('\tignoring utility on service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        brightness = self.get_brightness()

        self.call_service('light/turn_on', entity_id=const.UTILITY_ROOM_LIGHTS, brightness=brightness)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_off_service(self, namespace, domain, service, data) -> None:
        """turn off utility lights"""

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.utility_override') == 'on' or self.any_light_on_full('utility_room'):
            self.log('\tdeferring utility off service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on bathroom lights"""

        self.lib.log_function_name(start=True)

        force = data.get('force', False)

        if not force and (self.get_state('input_boolean.bathroom_override') == 'on' or self.any_light_on_full('bathroom')):
            self.log('\tignoring bathroom on service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        cb = data.get('cb', 'noop')
        ## TODO: why no callback?

        sunrise = 'sunrise'
        plus1 = '+ 01:00:00'
        sunset = 'sunset'
        late = '23:00:00'

        if self.now_is_between(f'{sunrise} {plus1}', f'{sunset} {plus1}'):
            brightness = const.FULL_ON_THRESHOLD - 1
            color_temp = 171
        elif self.now_is_between(sunrise, f'{sunrise} {plus1}') or self.now_is_between(f'{sunset} {plus1}', late):
            brightness = const.QUARTER_ON
            color_temp = 441
        else:
            brightness = 25
            color_temp = 441

        self.show_service(namespace, domain, service, data, cb)

        if self.lib.get_verbose_debug():
            self.log(f'brightness={brightness} color_temp={color_temp}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=const.BATHROOM_LIGHTS, brightness=brightness, color_temp=color_temp)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_off_service(self, namespace, domain, service, data) -> None:
        """turn off bathroom lights"""

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.bathroom_override') == 'on' or self.any_light_on_full('bathroom'):
            self.log('\tdeferring bathroom off service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.SHORT_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on cloakroom lights"""

        self.lib.log_function_name(start=True)

        force = data.get('force', False)

        if not force and (self.get_state('input_boolean.cloakroom_override') == 'on' or self.any_light_on_full('cloakroom')):
            self.log('\tignoring cloakroom on service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        cb = data.get('cb', 'noop')

        sunset = 'sunset'
        sunrise = 'sunrise'
        plus1 = ' + 01:00:00'

        if self.now_is_between(sunset, f'{sunrise}{plus1}'):
            brightness = const.HALF_ON if self.now_is_between(sunset, f'{sunset}{plus1}') or self.now_is_between(sunrise, f'{sunrise}{plus1}') else const.QUARTER_ON

            self.show_service(namespace, domain, service, data, cb)

            if self.lib.get_verbose_debug():
                self.log(f'brightness={brightness}', level='DEBUG')

            self.call_service('light/turn_on', entity_id=const.CLOAKROOM, brightness=brightness)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_off_service(self, namespace, domain, service, data) -> None:
        """turn off cloakroom lights"""

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.cloakroom_override') == 'on' or self.any_light_on_full('cloakroom'):
            self.log('\tdeferring cloakroom off service', level='INFO')
            self.lib.log_function_name(start=False)
            return

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_on_service(self, namespace, domain, service, data) -> None:
        """turn on garage lights"""

        self.lib.log_function_name(start=True)

        if self.lib.is_below_horizon():
            self.call_service('light/turn_on', entity_id=const.GARAGE_LIGHTS)
            self.call_service('timestamp/set', name='garage_lights_on')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_off_service(self, namespace, domain, service, data) -> None:
        """turn off garage lights"""

        self.lib.log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.GARAGE_LIGHTS)
        self.call_service('timestamp/set', name='garage_lights_off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_on_service(self, namespace, domain, service, data) -> None:
        """turn on lumie lights""" # time will be checked in lumie_on_window

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        brightness = int(data.get('brightness', self.lib.percent_to_brightness(1)))
        force = data.get('force', False)

        self.show_service(namespace, domain, service, data, cb, callback)

        if self.lumie_on_window() or force:
            self.call_service('light/turn_on', entity_id=const.LUMIE, brightness=brightness)
            self.set_callback(cb, callback)
        else:
            self.log('\toutside time window for lumie', level='INFO')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def lumie_off_service(self, namespace, domain, service, data) -> None:
        """turn off lumie lights"""

        self.lib.log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.LUMIE)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def upstairs_on_service(self, namespace, domain, service, data) -> None:
        """turn on landing and bedroom lights"""

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.landing_disabled') == 'on' or not self.bedroom_on_window():
            self.call_service('lighting/lumie_on')
            self.lib.log_function_name(start=False)
            return

        self.set_state('input_boolean.landing_disabled', state='off')

        self.show_service(namespace, domain, service, data)

        upstairs_ts = self.call_service('timestamp/get', name='upstairs') # we return current as previous here because we will reset current shortly
        downstairs_ts = self.call_service('timestamp/get', name='downstairs') # we return current as previous here because we will reset current shortly
        prev_upstairs_ts = self.call_service('timestamp/get', name='prev_upstairs') # we return current as previous here because we will reset current shortly

        diff1 = (upstairs_ts - downstairs_ts).seconds
        diff2 = (upstairs_ts - prev_upstairs_ts).seconds
        self.log(f'\tdiff1={diff1} diff2={diff2} test1={diff1 < 1*60} test2={diff2 < const.LONGER_TIMEOUT}')

        if diff1 < 1*60: # light will be on from downstairs motion, we are setting the callback to turn off
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT)

        if diff2 < 2*60: # and not nomotion: # max gone to loo
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=20)

        if self.now_is_between('sunset + 00:30:00', '23:30:00'): # and nomotion:
            self.call_service('lighting/landing_on', cb='landing_off', seconds=const.LONGER_TIMEOUT)
            self.call_service('lighting/bedroom_on', cb='bedroom_off', seconds=const.TWOMINUTES)
            self.call_service('lighting/downstairs_off', cb='downstairs_off', seconds=0)
        else:
            self.call_service('lighting/lumie_on')
            self.call_service('lighting/study_off')
            self.call_service('lighting/downstairs_off', cb='downstairs_off', seconds=0)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def downstairs_on_service(self, namespace, domain, service, data) -> None:
        """turn on bannister and hallway lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', const.LONG_TIMEOUT))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON)
        self.call_service('light/turn_on', entity_id=const.BANNISTER, brightness=self.lib.percent_to_brightness(12))

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def downstairs_off_service(self, namespace, domain, service, data) -> None:
        """turn off bannister and hallway lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'downstairs_off')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', 0)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bannister_on_service(self, namespace, domain, service, data) -> None:
        """turn on bannister light"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', 30))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.call_service('light/turn_on', entity_id=const.BANNISTER)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom lights"""

        # force = {}
        # force = {'force': True}

        self.lib.log_function_name(start=True)#force=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.SHORT_TIMEOUT)

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        if self.bedroom_on_window():
            self.toggle_bedroom_light()
            self.set_callback(cb, callback, seconds)
        else:
            self.log('\toutside time window for bedroom', level='INFO')

        self.lib.log_function_name(start=False)#, force=True)

# -----------------------------------------------------------------------------------

    def landing_on_service(self, namespace, domain, service, data) -> None:
        """turn on landing lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = data.get('seconds', const.LONG_TIMEOUT)

        if self.lib.is_below_horizon():
            self.show_service(namespace, domain, service, data, cb, callback, seconds)

            self.set_callback(cb, callback, seconds)

            self.call_service('light/turn_on', entity_id=const.LANDING, brightness=const.QUARTER_ON)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def turn_on_if_off_service(self, namespace, domain, service, data) -> None:
        """turn on a light if it off"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', const.LONG_TIMEOUT))
        brightness = int(data.get('brightness', const.QUARTER_ON))
        color_temp = int(data.get('color_temp', 152))
        entity_id = data.get('entity_id', [])

        if isinstance(entity_id, str):
            entity_id = [entity_id]

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        if self.lib.get_verbose_debug():
            self.log(f'\tentity_id={entity_id} brightness={brightness} color_temp{color_temp}', level='DEBUG')

        for entity in entity_id:
            prev_state = self.get_state(entity)
            prev_brightness = self.get_state(entity, attribute="brightness")

            if prev_state == 'off':
                self.call_service('light/turn_on', entity_id=entity, brightness=brightness, color_temp=color_temp)
            else:
                self.log(f'\t{service}: ignored - {entity} already on brightness={prev_brightness}', level='INFO')

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_ding_service(self, namespace, domain, service, data) -> None:
        """turn on front door/hallway lights"""

        self.lib.log_function_name(start=True)

        cb = data.get('cb', 'noop')
        callback = self.get_callback(cb)
        seconds = int(data.get('seconds', 0))

        self.show_service(namespace, domain, service, data, cb, callback, seconds)

        self.set_callback(cb, callback, seconds)

        self.call_service('light/turn_on', entity_id=const.FRONT_DOOR, brightness=const.FULL_ON, transition=10)
        self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, transition=10)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cancel_timer_service(self, namespace, domain, service, data) -> None:
        """cancel a timer"""

        self.lib.log_function_name(start=True)

        name = data.get('name', None)
        cb = data.get('cb', None)
        callback = self.get_callback(cb)

        if self.get_timer(name) is not None:
            self._cancel_timer(name)


        self.show_service(namespace, domain, service, data, cb, callback)

        if callback is not None:
            self.set_callback(cb, callback, 0)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_off_service(self, namespace, domain, service, data) -> None:
        """turn off study light"""

        self.lib.log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.STUDY)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def all_off_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/all_off')
        self.call_service('sonos/stop_bedroom')

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

        self.call_service('lighting/front_door_ding', cb='front_door_hallway_off', seconds=20)

# -----------------------------------------------------------------------------------

    def lumie_on_event(self, event, data, kwargs) -> None:

        force = data.get('force', False)
        brightness = data.get('brightness', self.lib.percent_to_brightness(1))

        self.call_service('lighting/lumie_on', brightness=brightness, force=force)

# -----------------------------------------------------------------------------------

    def lumie_wake_event(self, event, data, kwargs) -> None:

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=const.QUARTER_ON, rgb_color=[255, 180, 10])

# -----------------------------------------------------------------------------------

    def test_welcome_lights_event(self, event, data, kwargs):

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off', seconds=10)

# -----------------------------------------------------------------------------------

    def test_lights_event(self, event, data, kwargs):

        self.living_room_on({})

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

        if self.lib.is_night():  # civil dusk till civil dawn
            if self.lib.get_verbose_debug():
                self.log('\tturn on hallway light', level='DEBUG')

            self.call_service('light/turn_on', entity_id=const.HALLWAY1, brightness=const.QUARTER_ON, transition=10)

# -----------------------------------------------------------------------------------

    def hallway_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=const.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def bedroom_off(self, kwargs) -> None:

        self.lib.log_function_name(start=True)

        self.toggle_bedroom_light()

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def landing_off(self, kwargs) -> None:

        self.lib.log_function_name(start=True)

        self.call_service('light/turn_off', entity_id=const.HALLWAY3, transition=10)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def living_room_on(self, kwargs) -> None:
        """turn on living room lights"""

        for entity_id in const.LIVING_ROOM:
            if not self.is_light_on(entity_id):
                self.call_service('light/turn_on', entity_id=entity_id, brightness=self.lib.percent_to_brightness(40), transition=10)

# -----------------------------------------------------------------------------------

    def stairs_on(self, kwargs) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id=const.LANDING, brightness=self.lib.percent_to_brightness(25), transition=10)

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

        if self.get_state('input_boolean.cloakroom_override') == 'on' or self.any_light_on_full('cloakroom'):
            self.log('\tignoring cloakroom off service', level='INFO')
            self.lib.log_function_name(start=False)
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

        if self.get_state('input_boolean.bathroom_override') == 'on' or self.any_light_on_full('bathroom'):
            self.log('\tignoring bathroom off service', level='INFO')
            self.lib.log_function_name(start=False)
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

    def outside_off(self, kwargs) -> None:
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

        entity_ids = self.light_entities('kitchen', const.N_KITCHEN_ENTITIES)

        if self.get_state('input_boolean.kitchen_override') == 'on' or self.any_light_on_full('kitchen'):
            self.log('\tdeferring kitchen off', level='INFO')
            return

        self.call_service('light/turn_off', entity_id=entity_ids, transition=10) # was entity_id=const.KITCHEN_LIGHTS


        cb = 'kitchen_floor_off'
        callback = self.get_callback(cb)

        self.set_callback(cb, callback, 5*60)
        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs) -> None: # callback

        self.call_service('light/turn_off', entity_id=const.KITCHEN_FLOOR_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def utility_off(self, kwargs) -> None:

        if self.get_state('input_boolean.utility_override') == 'on' or self.any_light_on_full('utility_room'):
            self.log('\tdeferring utility off', level='INFO')
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

    def set_timer(self, name:str, timer:str) -> None:
        """set a timer"""

        old = self.timers.get(name, None)

        if old is not None:
            if self.check_timer(name, old):
                self.log(f'\treplacing name={name} old={old} with new={timer}', level='DEBUG')
                self._cancel_timer(name)

        self.log(f'\tadding new timer name={name} timer={timer}', level='DEBUG')

        self.timers[name] = timer

# -----------------------------------------------------------------------------------

    def get_timer(self, name:str): # -> str | None:
        """get a timer"""

        timer = self.timers.get(name, None)

        if timer is not None and self.lib.get_verbose_debug():
            self.log(f'\treturning name={name} timer={timer}', level='DEBUG')

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name:str) -> None:
        """cancel a timer callback"""

        verbose = self.lib.get_verbose_debug()

        timer = self.get_timer(name)
        self.log(f'\tcancelling running timer name={name} timer={timer}', level='INFO')
        # self.call_service('announcer/notification', message=f'_cancel_timer name={name}', type='desktop') # keep for debugging

        if timer is not None:
            if verbose:
                self.log(f'\tcancelling running timer name={name} timer={timer}', level='DEBUG')

            self.cancel_timer(timer)
            self.timers.pop(name)

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        timer = self.timers.get(name, None)

        if timer is not None:
            self.log(f'\tremoving timer name={name} timer={timer}', level='INFO')
            self.timers.pop(name)
        else:
            self.log(f'\tremove_timer no timer name={name}', level='INFO')

# -----------------------------------------------------------------------------------

    def check_timer(self, name, timer) -> bool:

        verbose = self.lib.get_verbose_debug()

        if not verbose:
            return True

        if timer is None:
            self.log(f'timer is None name={name}', level='ERROR')
            return False

        extant = self.info_timer(timer)

        if extant is None:
            self.log(f'{name} timer is no longer extant. removing', level='ERROR')
            self.remove_timer(name)
            return False

        end_time, interval, kwargs = self.info_timer(timer)

        return True

# -----------------------------------------------------------------------------------

    def print_timers(self) -> None:
        """print timers"""

        self.purge_timers({})

        status = '\n\n\ttimers:\n\n'

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is not None and self.timer_running(timer):
                result = self.info_timer(timer)
                if result is None:
                    continue

                end_time, interval, kwargs = result  # Unpack only if result is not None
                remaining = end_time - datetime.now()
                _, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                status += f'\tremaining={minutes:02d}:{seconds:02d} end_time={end_time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}\n'

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    def purge_timers(self, kwargs) -> None:
        """purge timers"""

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is not None and self.timer_running(timer):
                result = self.info_timer(timer)
                if result is None:
                    self.log(f"purging timer {timer}", level="DEBUG")
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
            if self.timer_running(timer):
                end_time, interval, kwargs = self.info_timer(timer)
                self.log(f'\tname={key} timer={timer} end_time={end_time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}')
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
            entity_ids = self.light_entities(area, const.N_UTILITY_ROOM_ENTITIES)
        elif area == 'bathroom':
            entity_ids = self.light_entities(area, const.N_BATHROOM_ENTITIES)
        elif area == 'cloakroom':
            entity_ids = self.light_entities(area, const.N_CLOAKROOM_ENTITIES)

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

        self.lib.log_function_name(start=True)

        state = self.fan_light_state
        self.fan_light_state = not self.fan_light_state

        message=f'toggle_bedroom_light fan_light_state={self.fan_light_state} was {state}'

        if self.fan_light_enabled:
            self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')
        self.call_service('announcer/notification', message=message, type='desktop')

        self.log(f'\t{message}', level='INFO')

        self.lib.log_function_name(start=False)

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
                self.set_timer(cb, timer)
                self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def get_callback(self, cb):

        callback = None

        if cb is not None:
            callback = getattr(self, cb)

        return callback

# -----------------------------------------------------------------------------------

    def show_service(self,namespace, domain, service, data, cb=None, callback=None, seconds=None) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} callback={callback} seconds={seconds}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def lumie_on_window(self):

        return self.now_is_between('23:30:00', '04:00:00')

# -----------------------------------------------------------------------------------

    def noop(self, kwargs) -> None:

        pass

# -----------------------------------------------------------------------------------

    def bathroom_on_full(self, entity, attribute, old, new, kwargs) -> None:
        """bathroom on full"""

        if new == 'on':
            self.call_service('lighting/bathroom_on', entity_id=const.BATHROOM_LIGHTS, cb='noop', seconds=const.SHORT_TIMEOUT, force=True)
            self.bathroom_callback_handle = self.run_in(self.bathroom_off, 60 * 60, force=True)
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
            self.cloakroom_callback_handle = self.run_in(self.cloakroom_off, 45 * 60, force=True)
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
            self.kitchen_callback_handle = self.run_in(self.kitchen_off, 60 * 60, force=True)
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
            self.utility_callback_handle = self.run_in(self.utility_off, 60 * 60, force=True)
        else:
            self.call_service('lighting/utility_off', entity_id=const.UTILITY, cb='utility_off', seconds=0, force=True)
            if self.utility_callback_handle is not None:
                self.cancel_timer(self.utility_callback_handle)
            self.utility_callback_handle = None

# -----------------------------------------------------------------------------------

    def bedroom_on_window(self) -> bool:
        """bedroom on window"""

        return self.now_is_between('sunset', f'{const.BEDROOM_WINDOW_ON_HOUR}:00:00')


# -----------------------------------------------------------------------------------

    def get_brightness(self) -> bool:
        """get brightness"""

        if self.lib.is_summer():
            brightness = const.HALF_ON if self.now_is_between('sunrise', 'sunset') else const.QUARTER_ON
        else:
            brightness = (const.FULL_ON_THRESHOLD - 1) if self.now_is_between('sunrise', 'sunset') else const.HALF_ON

        return brightness
