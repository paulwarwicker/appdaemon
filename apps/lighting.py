# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import inspect
# import traceback
# import asyncio
from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Lighting(Hass):
    """Documentation for Lighting"""

    lib = None
    stairs_timer = None
    utility_timer = None
    kitchen_timer = None
    kitchen_long_timer = None
    kitchen_floor_timer = None
    utility_long_timer = None

    handlers = {}

    upstairs_ts = datetime.now()
    downstairs_ts = datetime.now()
    initialise_ts = datetime.now()
    prev_upstairs_ts = datetime.now()

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        # self.register_service('automation/set_downstairs_motion_flag', self.set_downstairs_motion_flag)
        # self.register_service('automation/log_function_name', self._log_function_name)
        # self.register_service('automation/max_home', self._max_home)

        self.listen_event(self.lights_off, "ios.action_fired", actionName='Lights')
        self.listen_event(self.status_event, 'status')

        self.listen_state(self.front_door_ding, 'binary_sensor.front_door_ding', old='off', new='on')

        self.listen_state(self.kitchen_motion, 'binary_sensor.kitchen_sensor_motion', old='off', new='on', timer=300, location='kitchen')
        self.listen_state(self.utility_motion, 'binary_sensor.utility_room_motion_sensor_motion', old='off', new='on', timer=300, location='utility')
        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion', old='off', new='on', timer=300, check_override=True, location='downstairs')
        self.listen_state(self.upstairs_motion, 'binary_sensor.upstairs_sensor_motion', old='off', new='on', timer=600, check_override=False, location='upstairs')

        self.run_daily(self.stairs_on, "sunset + 00:00:00")
        self.run_daily(self.radiator_on, "sunset + 00:10:00")
        self.run_daily(self.living_room_lights_off, "23:30:00")
        self.run_daily(self.outside_lights_off, "21:30:00")
        # self.run_daily(self.wardrobe_on, '07:00:00')

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def turn_on_if_off(self, entity_id, brightness=64): # -> Any
        """turn on a light if it off"""

        prev_state = self.get_state(entity_id)
        prev_brightness = self.get_state(entity_id, attribute="brightness")
        debug = self.debug

        if prev_state == 'off':
            if debug:
                self.log(f'\tturn on {entity_id} brightness={brightness}', level='DEBUG')
            self.call_service('light/turn_on', entity_id=entity_id, brightness=brightness)
        else:
            if debug:
                self.log(f'\tignored - {entity_id} already on brightness={prev_brightness}', level='DEBUG')
        return prev_state

# ---------------------------------------------------------------------------------------------------------

    def any_light_on_full(self, entity_ids)  -> bool:
        """is any light on full"""

        for entity_id in entity_ids:
            brightness = self.get_state(entity_id=entity_id, attribute="brightness")
            if brightness is not None and brightness >= 250:
                return True

        return False

# ---------------------------------------------------------------------------------------------------------

    def light_entities(self, name, count=1): # -> Any # FIXME
        """generate a list of light entity names"""

        entities = []

        for entity in range(1, count+1):
            entities.append(f'light.{name}_{entity}')

        return entities

# ---------------------------------------------------------------------------------------------------------

    def _cancel_timer(self, timer, message=None) -> None:
        """cancel a timer if set"""

        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def set_timestamp(self, timestamp) -> None:
        """set a named timestamo"""

        if timestamp is not None:
            ts = datetime.now()
            if timestamp == "travel":
                self.travel_announce_ts = ts
            elif timestamp == "garage":
                self.garage_announce_ts = ts
            elif timestamp == "karoq":
                self.karoq_announce_ts = ts
            elif timestamp == "tap":
                self.tap_ts = ts
            elif timestamp == "general":
                self.general_announce_ts = ts

# ---------------------------------------------------------------------------------------------------------

    def activate_scene(self, entity, attribute, old, new, kwargs={}) -> None:
        """activate a scene <scene> and set <entity_id> off"""

        scene = kwargs['scene']
        entity_id = kwargs['entity_id']

        if scene:
            scene = 'scene.'+scene
            if new == 'on':
                self.turn_on(scene)
            else:
                self.turn_off(scene)

        if entity_id:
            self.delay(1)
            self.set_state(entity_id, state='off')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights(self, **kwargs) -> None:
        """turn on garage door lights"""

        entities = {'light.garage_2', 'light.garage_1'}

        if kwargs['on'] is True:
            self.call_service('light/turn_on', entity_id=entities)
        else:
            s = self.lib.interval(minutes=5)
            self.run_in(self.garage_door_lights_off, s)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights_on(self, kwargs={}) -> None:
        """turn off garage door lights"""

        self.garage_door_lights(on=True)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights_off(self, kwargs={}) -> None:
        """turn off garage door lights"""

        self.garage_door_lights(on=False)

# ---------------------------------------------------------------------------------------------------------

    def lights_off(self, event, data, kwargs={}) -> None:
        """turn off hallway, garage and front door lights"""

        self.call_service('light/turn_off', entity_id=['light.hallway_1', 'light.hallway_2', 'light.front_door_1', 'light.garage_1', 'light.garage_2']) # not light.standard_lamp_1 !!

# ---------------------------------------------------------------------------------------------------------

    def stairs_on(self, kwargs={}) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id='light.hallway_3', brightness=5)

# ---------------------------------------------------------------------------------------------------------

    def radiator_on(self, kwargs={}) -> None:
        """turn on radiator light"""

        self.call_service('light/turn_on', entity_id='light.radiator')

# ---------------------------------------------------------------------------------------------------------

    def living_room_lights_off(self, kwargs={}) -> None:
        """turn living room lights"""

        self.run_sequence(
            [
                {'light/turn_off': {'entity_id': ['light.radiator', 'light.standard_lamp_1', 'light.table_lamp_1']}},
                {'light/turn_off': {'entity_id': ['light.standard_lamp_1']}},
            ]
        )

        # self.call_service('light/turn_off', entity_id='light.radiator')
        # self.call_service('light/turn_off', entity_id='light.standard_lamp_1')
        # self.call_service('light/turn_off', entity_id='light.table_lamp_1')
        # # try again - wasn't switching off
        # self.call_service('light/turn_off', entity_id='light.standard_lamp_1')

# ---------------------------------------------------------------------------------------------------------

    def outside_lights_off(self, kwargs={}) -> None:
        """turn off outside lights"""

        self.run_sequence(
            [
                {'light/turn_off': {'entity_id': ['light.front_door_1', 'light.garage_1', 'light.garage_2']}},
            ]
        )

        # self.call_service('light/turn_off', entity_id='light.front_door_1')
        # self.call_service('light/turn_off', entity_id='light.garage_1')
        self.log('\toutside lights off')

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_on(self, kwargs={}) -> None:
        """turn on wardrobe light"""

        if 'dow' in kwargs:
            dow = kwargs['dow']
        else:
            dow = self.lib.dow()

        turn_on = (not (dow == 3 or dow >= 6)) and self.sun_down()

        if turn_on:
            self.log('\tturn on wardrobe')
            self.call_service('switch/turn_on', entity_id='switch.wardrobe')
            s = self.lib.interval(minutes=15)
            self.log(f'\tstart wardrobe timer for {s:d}s')
            self.run_in(self.wardrobe_off, s)

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_off(self, kwargs={}) -> None:
        """turn off wardrobe light"""

        self.call_service('switch/turn_off', entity_id='switch.wardrobe')

# ---------------------------------------------------------------------------------------------------------

    def hallway_on(self, kwargs={}) -> None:

        if self.sun_down(): # Turn on hallway lights when dark after 6am
            self.log('\tsun down - turn on hallway light', level='DEBUG')
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)
            self.log('\thallway off')
            self.log('\tset timer for hallway light', level='DEBUG')
            self.run_at(self.hallway_off, 'sunrise + 00:10:00')

# ---------------------------------------------------------------------------------------------------------

    def hallway_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.hallway_1')
        self.call_service('light/turn_off', entity_id='light.hallway_2')
        self.log('\thallway off')

# ---------------------------------------------------------------------------------------------------------

    def utility_off(self, kwargs={}) -> None:

        entity_id = 'light.utility_room_1'
        timer_type = kwargs['timer_type']
        brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        state = self.get_state(entity_id=entity_id, attribute="state")
        self.log(f'\ttimer_type={timer_type} brightness={brightness} state={state} st={self.utility_timer} lt={self.utility_long_timer}', level='DEBUG')
        self.cancel_utility_timers(timer_type='short')
        # (timer_type == 'long' or (brightness is not None and brightness <= 130)):
        if state == 'on' and timer_type == 'long':
            self.call_service('light/turn_off', entity_id=entity_id)
        else:
            self.log('\tlong timer running or brightness >= 130', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def bannister_on(self, kwargs={}) -> None:

        self.call_service('light/turn_on', entity_id='light.bannister', brightness=77)
        elev = self.get_state('sun.sun', 'elevation')
        if elev < 5: # and not self.now_is_between('01:30:00', 'sunrise'):
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)

# ---------------------------------------------------------------------------------------------------------

    def bannister_off(self, kwargs={}) -> None:

        check = kwargs['check_override']
        location = kwargs['location']
        if (check and not self.override) or not check:
            self.log(f'\tturn off bannister - {location}')
            self.call_service('light/turn_off', entity_id='light.bannister')
            self.call_service('light/turn_off', entity_id='light.hallway_1')
            self.override = False
            self.stairs_timer = None
        else:
            self.log(f'\tskip turn off bannister - {location}')

# ---------------------------------------------------------------------------------------------------------

    def downstairs_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.upstairs')
        self.call_service('light/turn_off', entity_id='light.downstairs')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.kitchen_floor')
        self.kitchen_floor_timer = None

# ---------------------------------------------------------------------------------------------------------

    def kitchen_off(self, kwargs={}) -> None:

        entity_ids = self.light_entities('kitchen', 6)
        if not self.any_light_on_full(entity_ids):
            self.kitchen_all_off(kwargs)
        else:
            self.log('\tdeferring - kitchen lights high', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_all_off(self, kwargs={}) -> None:

        self.cancel_kitchen_timers()
        self.kitchen_floor_on()
        seconds = 60
        self.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)
        self.log(f'\tstart {seconds}s timer floor lights', level='DEBUG')
        for e in [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]:
            self.call_service('light/turn_off', entity_id=f'light.kitchen_{e}')

# ---------------------------------------------------------------------------------------------------------

    def ding_front_door_light(self, kwargs={}) -> None:
        """Turn on front door light when dark when someone calls. see also front_door_light_on/off"""

        if self.now_is_between('sunset', 'sunrise'):
            # TODO: return to previous level if was previously on
            brightness = self.get_state('light.front_door_1', attribute='brightness')
            state = self.get_state('light.front_door_1')
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=192, transition=10)
            # self.turn_on('scene.front_door_ding_2') # FIXME: not working - scenes dont allow transitiona
            seconds = 12*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            # FIXME:, brightness=brightness) # state=state??
            self.run_in(self.front_door_light_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def ding_hallway_light(self, kwargs={}) -> None:
        """Turn on hallway light when dark"""

        if self.lib.is_night():  # civil dusk till civil dawn
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64, transition=5)
            seconds = 10*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.hallway_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_on(self, kwargs={}) -> None:

        self.run_in(self._front_door_light_on, 0)

# ---------------------------------------------------------------------------------------------------------

    def _front_door_light_on(self, kwargs={}) -> None:

        if self.now_is_between('sunset', 'sunrise + 1:00:00'):
            if self.lib.is_below_horizon():
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=128, transition=10)
                self.call_service('light/turn_on', entity_id='light.garage_1', brightness=128, transition=10)
            else:
                self.run_in(self.int_front_door_light_on, 60)  # respawn self in 60s

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_off(self, kwargs={}) -> None:

        # scene = 'scene.front_door_ding_2'
        # self.log(f'\tscene={scene}', level='DEBUG')
        # self.turn_off(scene) # TODO: not working
        self.call_service('light/turn_off', entity_id='light.hallway_1', transition=10)
        self.call_service('light/turn_off', entity_id='light.front_door_1', transition=10)

# ---------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs={}) -> None:

        status = f'\n\n\tkitchen_timer={self.kitchen_timer}\n'
        status += f'\tkitchen_long_timer={self.kitchen_long_timer}\n'
        status += f'\tkitchen_floor_timer={self.kitchen_floor_timer}\n'
        status += f'\tutility_timer={self.utility_timer}\n'
        status += f'\tutility_timer={self.utility_long_timer}\n'
        status += f'\tstairs_timer={self.stairs_timer}\n'
        status += f'\n\tupstairs_ts={self.upstairs_ts}\n'
        status += f'\tdownstairs_ts={self.downstairs_ts}\n'
        status += f'\tprev_upstairs_ts={self.prev_upstairs_ts}\n'
        status += f'\tgeneral_announce_ts={self.general_announce_ts}\n'
        status += f'\ttravel_announce_ts={self.travel_announce_ts}\n'
        status += f'\tgarage_announce_ts={self.garage_announce_ts}\n'
        status += f'\ttap_ts={self.tap_ts}\n'
        status += f'\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n'
        state = self.get_state('input_boolean.default_debug_state')
        status += f'\tdefault_debug_state={state}\n'
        state = self.get_state('input_boolean.default_verbose_state')
        status += f'\tdefault_verbose_state={state}\n'
        state = self.get_state('input_boolean.default_testing_state')
        status += f'\tdefault_testing_state={state}\n'
        status += f'\n\tdebug={self.debug}\n'
        status += f'\tverbose={self.verbose}\n'
        status += f'\ttesting={self.testing}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# ---------------------------------------------------------------------------------

    def _log_function_name(self, namespace, domain, service, data) -> None:

        type_ = data.get('start', True)
        self.log(f'\ttype={type_}')
        self.log_function_name() # FIXME

# ---------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status('','','','')

# ---------------------------------------------------------------------------------------------------------

    def log_function_name(self, start=True) -> None:

        name = inspect.currentframe().f_back.f_code.co_name
        # print(inspect.currentframe())

        if self.verbose or self.debug:
            self.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------
