# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught disable=line-too-long

"""Montion detection and lighting control"""

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Motion(Hass):
    """Class documentation for Location"""

    override = False
    upstairs_motion_flag = False
    upstairs_motion_active = False
    downstairs_motion_flag = False
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise location class"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        # self.register_service('motion/set_motion_flag', self.set_motion_flag_service)
        # self.register_service('motion/reset_motion_flag', self.reset_motion_flag_service)
        self.register_service('motion/garage', self.garage_motion_service)

        self.listen_event(self.stairs_motion_event,     'stairs_motion')
        self.listen_event(self.upstairs_motion_event,   'upstairs_motion')
        self.listen_event(self.downstairs_motion_event, 'downstairs_motion')
        self.listen_event(self.front_door_motion_event, 'front_door_motion')
        self.listen_event(self.kitchen_motion_event,    'kitchen_motion')
        self.listen_event(self.utility_motion_event,    'utility_motion')
        self.listen_event(self.garage_motion_event,     'garage_motion')
        self.listen_event(self.motion_motion_event,     'motion_motion')
        self.listen_event(self.status_event,            'status')

        self.listen_state(self.front_door_motion, 'binary_sensor.front_door_motion',          new='on')
        self.listen_state(self.front_door_motion, 'binary_sensor.front_door_motion',          new='off', cb='front_door_off')
        self.listen_state(self.kitchen_motion,    'binary_sensor.kitchen_sensor_motion',      new='on')
        self.listen_state(self.kitchen_motion,    'binary_sensor.kitchen_sensor_motion',      new='off', cb='kitchen_off')
        self.listen_state(self.utility_motion,    'binary_sensor.utility_room_sensor_motion', new='on')
        self.listen_state(self.utility_motion,    'binary_sensor.utility_room_sensor_motion', new='off', cb='utility_off')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='on')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='off', cb='bathroom_off')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.garage_sensor_motion',       new='on')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.garage_sensor_motion',       new='off', cb='cloakroom_off')

        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion',   new='on')
        self.listen_state(self.upstairs_motion,   'binary_sensor.upstairs_sensor_motion',     new='on')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    # def set_motion_flag_service(self, namespace:str, domain:str, service:str, kwargs) -> None:
    #     """set downstairs motion flag"""

    #     name = kwargs.get('name', None)
    #     value = kwargs.get('value', None)

    #     if name == 'upstairs':
    #         self.upstairs_motion_flag = value
    #     elif name == 'downstairs':
    #         self.downstairs_motion_flag = value

# -----------------------------------------------------------------------------------

    # def reset_motion_flag_service(self, namespace:str, domain:str, service:str, kwargs) -> None:
    #     """reset motion flags"""

    #     self.upstairs_motion_flag = False
    #     self.downstairs_motion_flag = False

# -----------------------------------------------------------------------------------

    def garage_motion_service(self, namespace:str, domain:str, service:str, kwargs) -> None:
        """garage motion detected"""

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring garage motion due to ignore_sensors', level='WARNING')
            return

        ts = self.call_service('timestamp/get', name='garage')
        diff = (datetime.now() - ts).seconds

        if diff > self.lib.interval(self, seconds=10):
            self.call_service('light/turn_on', entity_id=const.GARAGE2)

# -----------------------------------------------------------------------------------

    def status_event(self, event:str, data:dict, kwargs) -> None:
        """status event"""

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def front_door_motion_event(self, event:str, data:dict, kwargs) -> None:
        """front door motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.front_door_motion('', '', '', 'on', {'seconds': 5, 'key': 'front door', 'cb': 'front_door_off'})

# -----------------------------------------------------------------------------------

    def downstairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """downstairs motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def upstairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """upstairs motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.upstairs_motion('', '', '', '', {'seconds': 5, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def stairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """stairs motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})
        self.lib.delay(self, 15)
        self.upstairs_motion('', '', '', '', {'seconds': 10, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def kitchen_motion_event(self, event:str, data:dict, kwargs) -> None:
        """kitchen motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.kitchen_motion('', '', '', '', {'seconds': 5})

# -----------------------------------------------------------------------------------

    def utility_motion_event(self, event:str, data:dict, kwargs) -> None:
        """utility motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.utility_motion('', '', '', '', {'seconds': 5, 'key': 'utility', 'cb': 'utility_off'})

# -----------------------------------------------------------------------------------

    def garage_motion_event(self, event:str, data:dict, kwargs) -> None:
        """garage motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.garage_motion('', '', 'off', 'on', {})
        self.lib.delay(self, 15)
        self.garage_motion('', '', 'on', 'off', {'test': True})

# -----------------------------------------------------------------------------------

    def motion_motion_event(self, event:str, data:dict, kwargs) -> None:
        """motion motion event"""

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        entity_id = 'light.hallway_1'
        self.downstairs_motion_event('',{},{})

        self.lib.delay(self, 15)
        self.upstairs_motion_event('',{},{})
        self.lib.delay(self, 15)
        self.garage_motion_event('',{},{})
        self.lib.delay(self, 15)
        self.front_door_motion_event('',{},{})
        self.lib.delay(self, 15)
        self.call_service('light/turn_off', entity_id=entity_id)
        self.kitchen_motion_event('',{},{})
        self.lib.delay(self, 15)
        self.utility_motion_event('',{},{})

# -----------------------------------------------------------------------------------

    def upstairs_motion(self, entity, attribute, old, new, kwargs) -> None:
        """upstairs motion"""

        self.lib.log_function_name(start=True)
        # self.lib.log_function_name(force=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring upstairs motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        if self.upstairs_motion_active:
            self.log('upstairs_motion_active is active', level='WARNING')
        else:
            self.upstairs_motion_active = True
            self.run_in(self.reset_upstairs_motion_active, 10*60)

            ts = self.call_service('timestamp/get', name='upstairs_motion')
            # nomotion = (datetime.now() - ts).seconds > 1*60*60

            self.call_service('timestamp/set', name='upstairs_motion', value=datetime.now())

            ts = self.call_service('timestamp/get', name='upstairs')
            self.call_service('timestamp/set', name='prev_upstairs', value=ts)
            self.call_service('timestamp/set', name='upstairs', value=datetime.now())

            if self.lib.is_below_horizon():
                self.call_service('lighting/upstairs_on')

        self.lib.log_function_name(start=False)
        # self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def downstairs_motion(self, entity, attribute, old, new, kwargs) -> None:

        force = {}
        # force = {'force': True}

        self.lib.log_function_name(**force)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring upstairs motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        self.downstairs_motion_flag = True
        self.call_service('timestamp/set', name='downstairs')

        if self.lib.is_below_horizon():
            self.call_service('lighting/downstairs_on', cb='downstairs_off', seconds=const.LONGER_TIMEOUT)
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT)

        self.lib.log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def check_downstairs_motion(self) -> None:

        downstairs_ts = self.call_service('timestamp/get', name='downstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (downstairs_ts - front_door_ts).seconds < 60:
            self.call_service('lighting/front_door_off')
            # self.call_service('light/turn_off', entity_id=const.STANDARD_LAMP)

# -----------------------------------------------------------------------------------

    def check_upstairs_motion(self) -> None:
        upstairs_ts = self.call_service('timestamp/get', name='upstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (upstairs_ts - front_door_ts).seconds < 120:
            self.run_in(self.all_off, 60)

# -----------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring kitchen motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/kitchen_{new}', cb=cb, seconds=seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring upstairs motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.DEFAULT_TIMEOUT)

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            if new == 'off':
                self.call_service('lighting/utility_off', cb=cb, seconds=seconds)
            elif new == 'on':
                self.call_service('lighting/turn_on_if_off', entity_id=const.UTILITY, cb=cb, seconds=seconds, brightness=const.QUARTER_ON)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring bathroom motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/bathroom_{new}', entity_id=const.BATHROOM_LIGHTS, cb=cb, seconds=seconds)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        force = {}
        # force = {'force': True}

        self.lib.log_function_name(**force)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring cloakroom motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.DEFAULT_TIMEOUT)

        self.call_service(f'lighting/cloakroom_{new}', entity_id=const.CLOAKROOM, seconds=seconds, cb=cb)

        self.lib.log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def garage_motion(self, entity_id, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring garage motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        if self.lib.get_verbose_debug():
            self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if old == 'off' and new == 'on':
            self.call_service('lighting/garage_on')
        elif old == 'on' and new == 'off' and kwargs.get('test', False):
            self.call_service('lighting/garage_off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_motion(self, entity_id, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        if self.get_state('input_boolean.ignore_sensors') == 'on':
            self.log('Ignoring front door motion due to ignore_sensors', level='WARNING')
            self.lib.log_function_name(start=False)
            return

        cb = kwargs.get('cb', None)

        if self.now_is_between('sunset', 'sunrise'):
            self.call_service(f'lighting/front_door_{new}', entity_id=const.FRONT_DOOR_LIGHTS, cb=cb)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:

        status = f'\n\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n\tupstairs_motion_active={self.upstairs_motion_active}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------

    def all_off(self, kwargs) -> None:

        self.call_service('lighting/all_off')

# -----------------------------------------------------------------------------------

    def reset_upstairs_motion_active(self, kwargs) -> None:

        self.upstairs_motion_active = False

# -----------------------------------------------------------------------------------
