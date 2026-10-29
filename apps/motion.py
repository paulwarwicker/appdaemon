# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught disable=line-too-long

"""Motion detection and lighting control"""

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import constants as const
import requests
import json
import os
import time

from automationbase import AutomationBase  # type: ignore
from datetime import datetime, timedelta

# @dataclass
class Motion(AutomationBase):
    """Class documentation for Motion"""

    override = False
    upstairs_motion_flag = False
    upstairs_motion_active = False
    downstairs_motion_flag = False

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise location class"""

        super().initialize()

        self.register_service('motion/garage', self.garage_motion_service)
        self.register_service('motion/reset_active', self.reset_service)

        self.listen_event(self.stairs_motion_event,     'stairs_motion')
        self.listen_event(self.upstairs_motion_event,   'upstairs_motion')
        self.listen_event(self.downstairs_motion_event, 'downstairs_motion')
        self.listen_event(self.kitchen_motion_event,    'kitchen_motion')
        self.listen_event(self.utility_motion_event,    'utility_motion')
        self.listen_event(self.garage_motion_event,     'garage_motion')
        self.listen_event(self.status_event,            'status')
        self.listen_event(self.front_door_live_event,   'front_door_live')
        self.listen_event(self.reset_event,             'reset_active')

        self.listen_state(self.front_door_motion,       'event.front_door_motion',                  cb='front_door_hallway_off')
        self.listen_state(self.kitchen_motion,          'binary_sensor.kitchen_sensor_motion',      new='on')
        self.listen_state(self.kitchen_motion,          'binary_sensor.kitchen_sensor_motion',      new='off', cb='kitchen_off')
        self.listen_state(self.utility_motion,          'binary_sensor.utility_sensor_motion',      new='on')
        self.listen_state(self.utility_motion,          'binary_sensor.utility_sensor_motion',      new='off', cb='utility_off')
        self.listen_state(self.bathroom_motion,         'binary_sensor.bathroom_sensor_motion',     new='on')
        self.listen_state(self.bathroom_motion,         'binary_sensor.bathroom_sensor_motion',     new='off', cb='bathroom_off')
        self.listen_state(self.cloakroom_motion,        'binary_sensor.cloakroom_sensor_motion',    new='on')
        self.listen_state(self.cloakroom_motion,        'binary_sensor.cloakroom_sensor_motion',    new='off', cb='cloakroom_off')
        self.listen_state(self.living_room_motion,      'binary_sensor.living_room_sensor_motion',  new='on')
        # self.listen_state(self.living_room_motion,      'binary_sensor.living_room_sensor_motion',  new='off', cb='living_room_off')
        self.listen_state(self.garage_motion,           'binary_sensor.garage_sensor_motion',       new='on')
        self.listen_state(self.garage_motion,           'binary_sensor.garage_sensor_motion',       new='off', cb='garage_off')

        self.listen_state(self.downstairs_motion,       'binary_sensor.downstairs_sensor_motion',   new='on')
        self.listen_state(self.upstairs_motion,         'binary_sensor.upstairs_sensor_motion',     new='on')
        self.listen_state(self.bedroom_motion,          'binary_sensor.bedroom_sensor_motion',      new='on')

        self.listen_state(self.ignore_sensors,          'input_boolean.ignore_sensors',             old='off', new='on')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def garage_motion_service(self, namespace, domain, service, kwargs) -> None:
        """garage motion detected"""

        if self.check_sensors():
            return

        ts = self.call_service('timestamp/get', name='garage')
        diff = (datetime.now() - ts).seconds

        if diff > self._interval(seconds=10):
            self.call_service('light/turn_on', entity_id=const.GARAGE2)

# -----------------------------------------------------------------------------------

    def reset_service(self, namespace, domain, service, data) -> None:
        """reset"""

        self._log_function_name(start=True)

        self.upstairs_motion_active = False

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:
        """status event"""

        self.status('', '', '', '', {})

# -----------------------------------------------------------------------------------

    def front_door_motion_event(self, event, data, kwargs) -> None:
        """front door motion event"""

        self.front_door_motion('', '', '', '', {'cb': 'front_door_hallway_off'})

# -----------------------------------------------------------------------------------

    def front_door_live_event(self, event, data, kwargs) -> None:
        """front door live event"""

        if self.check_sensors():
            return

        self._log_function_name(start=True)

        self.download_live_view({})

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def downstairs_motion_event(self, event, data, kwargs) -> None:
        """downstairs motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def upstairs_motion_event(self, event, data, kwargs) -> None:
        """upstairs motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.upstairs_motion('', '', '', '', {'seconds': 5, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def stairs_motion_event(self, event, data, kwargs) -> None:
        """stairs motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})
        self._delay(15)
        self.upstairs_motion('', '', '', '', {'seconds': 10, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def kitchen_motion_event(self, event, data, kwargs) -> None:
        """kitchen motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.kitchen_motion('', '', '', '', {'seconds': 5})

# -----------------------------------------------------------------------------------

    async def utility_motion_event(self, event, data, kwargs) -> None:
        """utility motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.utility_motion('', '', '', 'on', {'seconds': 5, 'cb': 'utility_off'})

        await self.sleep(10.0)

        await self.set_state('binary_sensor.utility_room_sensor_motion', state='on')
        await self.sleep(5.0)
        self.utility_motion('', '', '', 'off', {'seconds': 0, 'cb': 'utility_off'})

# -----------------------------------------------------------------------------------

    def garage_motion_event(self, event, data, kwargs) -> None:
        """garage motion event"""

        self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.garage_motion('', '', 'off', 'on', {})
        self._delay(15)
        self.garage_motion('', '', 'on', 'off', {'test': True})

# -----------------------------------------------------------------------------------

    def reset_event(self, event, data, kwargs):

        self.call_service('motion/reset_active')

# -----------------------------------------------------------------------------------

    def front_door_motion(self, entity, attribute, old, new, kwargs) -> None:
        """front door motion"""

        if self.check_sensors() or new not in ('on', 'off'):
            return

        self._log_function_name(start=True)

        self.log(f'\tfront_door_motion: entity={entity} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='DEBUG')

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.DING_TIMEOUT)

        if self.now_is_between('sunset', 'sunrise'):
            self.call_service(f'lighting/front_door_{new}', entity_id=const.FRONT_DOOR_LIGHTS, cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def upstairs_motion(self, entity, attribute, old, new, kwargs) -> None:
        """upstairs motion"""

        if self.check_sensors():
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

        if self.check_sensors():
            return

        force = {'force': False} if True else {} # pylint: disable=using-constant-test
        self._log_function_name(**force)

        self.downstairs_motion_flag = True
        self.call_service('timestamp/set', name='downstairs')

        if self._is_below_horizon():
            self.call_service('lighting/downstairs_on', cb='downstairs_off', seconds=const.LONGER_TIMEOUT)
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT)

        if self._get_cleaning():
            self.call_service('lighting/bannister_on', cb='bannister_off', seconds=const.BANNISTER_TIMEOUT, brightness=255)

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def check_downstairs_motion(self) -> None:

        if self.check_sensors():
            return

        downstairs_ts = self.call_service('timestamp/get', name='downstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (downstairs_ts - front_door_ts).seconds < 60:
            self.call_service('lighting/front_door_off')
            # self.call_service('light/turn_off', entity_id=const.STANDARD_LAMP)

# -----------------------------------------------------------------------------------

    def check_upstairs_motion(self) -> None:

        if self.check_sensors():
            return

        upstairs_ts = self.call_service('timestamp/get', name='upstairs')
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion')

        if (upstairs_ts - front_door_ts).seconds < 120:
            self.run_in(self.all_off, 60)

# -----------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/kitchen_{new}', cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', 'noop')
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            self.call_service(f'lighting/utility_{new}', cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bathroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
            return

        self._log_function_name(start=True)

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.LONG_TIMEOUT)

        self.call_service(f'lighting/bathroom_{new}', entity_id=const.BATHROOM_LIGHTS, cb=cb, seconds=seconds)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def cloakroom_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
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

        if self.check_sensors():
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

    def living_room_motion(self, entity, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
            return

        # if self.get_state('light.standard_lamp', attribute="state") == 'on':
        #     self.log('living_room_motion: standard_lamp on, skipping', level='DEBUG')
        #     return

        force = {}
        # force = {'force': True}

        self._log_function_name(**force)

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', const.HALFHOUR)

        # # just set timestamp
        # ts = self.call_service('timestamp/get', name='living_room')
        # self.call_service('timestamp/set', name='living_room')
        # self.call_service('timestamp/set', name='prev_living_room', value=ts)

        self.call_service(f'lighting/living_room_{new}', entity_id=const.LIVING_ROOM, seconds=seconds, cb=cb)

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def motion_debug(self, entity, attribute, old, new, kwargs) -> None:

        force = {}
        # force = {'force': True}

        self._log_function_name(**force)

        print(f'\tentity={entity} attribute={attribute} old={old} new={new} kwargs={kwargs}')

        self._log_function_name(start=False, **force)

# -----------------------------------------------------------------------------------

    def garage_motion(self, entity_id, attribute, old, new, kwargs) -> None:

        if self.check_sensors():
            return

        self._log_function_name(start=True)

        self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='DEBUG')

        if old == 'off' and new == 'on':
            self.call_service('lighting/garage_on')
            self.call_service('garage/open_if_closed')
        elif old == 'on' and new == 'off' and kwargs.get('test', False):
            self.call_service('lighting/garage_off')

        self.call_service('timestamp/set', name='garage_motion')

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

    def check_sensors(self) -> bool:

        ignore = self.get_state('input_boolean.ignore_sensors') == 'on'

        if ignore:
            self.log('Ignoring motion due to ignore_sensors', level='WARNING')
            return ignore

        # cleaning = self._get_cleaning()

        # if cleaning:
        #     self.log('Detecting motion due to cleaning', level='WARNING')
        #     return False

        return False

# -----------------------------------------------------------------------------------

