# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught disable=line-too-long

"""Montion detection and lighting control"""

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
# from dataclasses import dataclass

# from typing import TYPE_CHECKING, cast

import constants as const
from automationbase import AutomationBase  # type: ignore

# @dataclass
class Motion(AutomationBase):
    """Class documentation for Motion"""

    override = False
    upstairs_motion_flag = False
    upstairs_motion_active = False
    downstairs_motion_flag = False

    # override: bool = False
    # upstairs_motion_flag: bool = False
    # upstairs_motion_active: bool = False
    # downstairs_motion_flag: bool = False

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise location class"""

        super().initialize()

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
        self.listen_state(self.utility_motion,    'binary_sensor.utility_sensor_motion',      new='on')
        self.listen_state(self.utility_motion,    'binary_sensor.utility_sensor_motion',      new='off', cb='utility_off')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='on')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='off', cb='bathroom_off')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.cloakroom_sensor_motion',    new='on')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.cloakroom_sensor_motion',    new='off', cb='cloakroom_off')
        self.listen_state(self.garage_motion,     'binary_sensor.garage_sensor_motion',       new='on')
        self.listen_state(self.garage_motion,     'binary_sensor.garage_sensor_motion',       new='off', cb='garage_off')

        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion',   new='on')
        self.listen_state(self.upstairs_motion,   'binary_sensor.upstairs_sensor_motion',     new='on')
        self.listen_state(self.bedroom_motion,    'binary_sensor.bedroom_sensor_motion',      new='on')

        self.listen_state(self.ignore_sensors,    'input_boolean.ignore_sensors',             old='off', new='on')
        self.listen_state(self.ignore_sensors,    'input_boolean.ignore_sensors',             old='off', new='on')

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

        # if self.check_ignore_sensors():
        #     return

        ts = self.call_service('timestamp/get', name='garage')
        diff = (datetime.now() - ts).seconds

        if diff > self._interval(seconds=10):
            self.call_service('light/turn_on', entity_id=const.GARAGE2)

# -----------------------------------------------------------------------------------

    def status_event(self, event:str, data:dict, kwargs) -> None:
        """status event"""

        self.status('', '', '', '', {})

# -----------------------------------------------------------------------------------

    def front_door_motion_event(self, event:str, data:dict, kwargs) -> None:
        """front door motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.front_door_motion(None, None, None, 'on', {'seconds': 5, 'cb': 'front_door_off'})

# -----------------------------------------------------------------------------------

    def downstairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """downstairs motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def upstairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """upstairs motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.upstairs_motion('', '', '', '', {'seconds': 5, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def stairs_motion_event(self, event:str, data:dict, kwargs) -> None:
        """stairs motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})
        self._delay(15)
        self.upstairs_motion('', '', '', '', {'seconds': 10, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def kitchen_motion_event(self, event:str, data:dict, kwargs) -> None:
        """kitchen motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.kitchen_motion('', '', '', '', {'seconds': 5})

# -----------------------------------------------------------------------------------

    async def utility_motion_event(self, event:str, data:dict, kwargs) -> None:
        """utility motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        # await self.set_state('binary_sensor.utility_room_sensor_motion', state='on')
        # await self.set_state('binary_sensor.utility_room_sensor_motion', state='off', cb='utility_off', seconds=5) # doesn't work

        self.utility_motion('', '', '', 'on', {'seconds': 5, 'cb': 'utility_off'})

        await self.sleep(10.0)

        await self.set_state('binary_sensor.utility_room_sensor_motion', state='on')
        await self.sleep(5.0)
        self.utility_motion('', '', '', 'off', {'seconds': 0, 'cb': 'utility_off'})

# -----------------------------------------------------------------------------------

    def garage_motion_event(self, event:str, data:dict, kwargs) -> None:
        """garage motion event"""

        if self._get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.garage_motion('', '', 'off', 'on', {})
        self._delay(15)
        self.garage_motion('', '', 'on', 'off', {'test': True})

# -----------------------------------------------------------------------------------

    def motion_motion_event(self, event:str, data:dict, kwargs) -> None:
        """motion motion event"""

    #     if self._get_verbose_debug():
    #         self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

    #     entity_id = 'light.hallway_1'
    #     self.downstairs_motion_event('',{},{})

    #     self._delay(15)
    #     self.upstairs_motion_event('',{},{})
    #     self._delay(15)
    #     self.garage_motion_event('',{},{})
    #     self._delay(15)
    #     self.front_door_motion_event('',{},{})
    #     self._delay(15)
    #     self.call_service('light/turn_off', entity_id=entity_id)
    #     self.kitchen_motion_event('',{},{})
    #     self._delay(15)
    #     self.utility_motion_event('',{},{})

# -----------------------------------------------------------------------------------

    def upstairs_motion(self, entity, attribute, old, new, kwargs) -> None:
        """upstairs motion"""

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True) #, force=True)

        if self.upstairs_motion_active:
            self.log('upstairs_motion_active is active', level='WARNING')
        else:
            self.upstairs_motion_active = True
            self.run_in(self.reset_upstairs_motion_active, 10*60)

            ts = self.call_service('timestamp/get', name='upstairs_motion')
            # nomotion = (datetime.now() - ts).seconds > 1*const.ONEHOUR

            self.call_service('timestamp/set', name='upstairs_motion')

            ts = self.call_service('timestamp/get', name='upstairs')
            self.call_service('timestamp/set', name='prev_upstairs', value=ts)
            self.call_service('timestamp/set', name='upstairs')

            if self._is_below_horizon():
                self.call_service('lighting/upstairs_on')

        self._log_function_name(start=False) #, force=True)

# -----------------------------------------------------------------------------------

    def downstairs_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        force = {'force': False} if True else {} # pylint: disable=using-constant-test
        self._log_function_name(**force)

        self.downstairs_motion_flag = True
        self.call_service('timestamp/set', name='downstairs')

        if self._is_below_horizon():
            self.call_service('lighting/downstairs_on', cb='downstairs_off', seconds=const.LONGER_TIMEOUT)
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT)

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def check_downstairs_motion(self) -> None:

        if self.check_ignore_sensors():
            return

        downstairs_ts = self.call_service('timestamp/get', name='downstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (downstairs_ts - front_door_ts).seconds < 60:
            self.call_service('lighting/front_door_off')
            # self.call_service('light/turn_off', entity_id=const.STANDARD_LAMP)

# -----------------------------------------------------------------------------------

    def check_upstairs_motion(self) -> None:

        if self.check_ignore_sensors():
            return

        upstairs_ts = self.call_service('timestamp/get', name='upstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (upstairs_ts - front_door_ts).seconds < 120:
            self.run_in(self.all_off, 60)

# -----------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/kitchen_{new}', cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        # if self.now_is_between('sunset + 00:15:00', 'sunrise'):
        #     if new == 'off':
        #         self.call_service('lighting/utility_off', cb=cb, seconds=seconds)
        #     elif new == 'on':
        #         self.call_service('lighting/turn_on_if_off', entity_id=const.UTILITY, cb=cb, seconds=seconds, brightness=const.QUARTER_ON)

        self.call_service(f'lighting/utility_{new}', cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/bathroom_{new}', entity_id=const.BATHROOM_LIGHTS, cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        force = {}
        # force = {'force': True}

        self._log_function_name(**force)

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.DEFAULT_TIMEOUT)

        self.call_service(f'lighting/cloakroom_{new}', entity_id=const.CLOAKROOM, seconds=seconds, cb=cb)

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def bedroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        force = {}
        # force = {'force': True}

        self._log_function_name(**force)

        # cb = kwargs.get('cb', None)
        # seconds = kwargs.get('seconds', const.DEFAULT_TIMEOUT)

        # just set timestamp
        ts = self.call_service('timestamp/get', name='bedroom')
        self.call_service('timestamp/set', name='bedroom')
        self.call_service('timestamp/set', name='prev_bedroom', value=ts)

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def garage_motion(self, entity_id, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True)

        if self._get_verbose_debug():
            self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if old == 'off' and new == 'on':
            self.call_service('lighting/garage_on')
        elif old == 'on' and new == 'off' and kwargs.get('test', False):
            self.call_service('lighting/garage_off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def front_door_motion(self, entity_id, attribute, old, new, kwargs) -> None:

        if self.check_ignore_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', None)

        if self.now_is_between('sunset', 'sunrise'):
            self.call_service(f'lighting/front_door_{new}', entity_id=const.FRONT_DOOR_LIGHTS, cb=cb)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:

        status = f'\n\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n\tupstairs_motion_active={self.upstairs_motion_active}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------

    def ignore_sensors(self, entity, attribute, old, new, kwargs) -> None:

        if new == 'on':
            self.run_in(self.ignore_sensors, 3 * 60 * 60, new='off')
        else:
            self.log('Resuming motion sensors')

# -----------------------------------------------------------------------------------

    def all_off(self, kwargs) -> None:

        self.call_service('lighting/all_off')

# -----------------------------------------------------------------------------------

    def reset_upstairs_motion_active(self, kwargs) -> None:

        self.upstairs_motion_active = False

# -----------------------------------------------------------------------------------

    def check_ignore_sensors(self) -> bool:

        ignore = self.get_state('input_boolean.ignore_sensors') == 'on'

        if ignore:
            self.log('Ignoring motion due to ignore_sensors', level='WARNING')

        return ignore

# -----------------------------------------------------------------------------------
