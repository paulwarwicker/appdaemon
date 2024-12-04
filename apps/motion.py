# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# import typing
from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Motion(Hass):
    """Documentation for Motion"""

    override = False
    downstairs_motion_flag = False
    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.register_service('motion/set_downstairs_motion_flag', self.set_downstairs_motion_flag)
        self.register_service('motion/reset_downstairs_motion_flag', self.reset_downstairs_motion_flag)

        self.listen_event(self.stairs_motion_event, 'stairs_motion')
        self.listen_event(self.upstairs_motion_event, 'upstairs_motion')
        self.listen_event(self.downstairs_motion_event, 'downstairs_motion')
        self.listen_event(self.front_door_motion_event, 'front_door_motion')
        self.listen_event(self.kitchen_motion_event, 'kitchen_motion')
        self.listen_event(self.utility_motion_event, 'utility_motion')
        self.listen_event(self.garage_motion_event, 'utility_motion')
        self.listen_event(self.motion_motion_event, 'motion_motion')

        self.listen_state(self.kitchen_motion, 'binary_sensor.kitchen_sensor_motion', old='off', new='on', seconds=5*60, key='kitchen', cb='kitchen_off')
        self.listen_state(self.utility_motion, 'binary_sensor.utility_room_motion_sensor_motion', old='off', new='on', seconds=5*60, key='utility', cb='utility_off')
        self.listen_state(self.garage_motion, 'binary_sensor.garage_sensor_motion', old='off', new='on', seconds=10*60, key='garage', cb='garage_off')
        self.listen_state(self.garage_motion, 'binary_sensor.garage_sensor_motion', old='on', new='off', seconds=5*60, key='garage', cb='garage_off')
        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion', old='off', new='on', seconds=5*60, key='downstairs', cb='bannister_off')
        self.listen_state(self.upstairs_motion, 'binary_sensor.upstairs_sensor_motion', old='off', new='on', seconds=10*60, key='upstairs', cb='bannister_off')
        self.listen_state(self.front_door_motion, 'binary_sensor.front_door_motion')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def set_downstairs_motion_flag(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """set downstairs motion flag"""

        value = kwargs.get('value', None)

        if value:
            self.downstairs_motion_flag = value

# -----------------------------------------------------------------------------------

    def reset_downstairs_motion_flag(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """reset downstairs motion flag"""

        self.downstairs_motion_flag = False

# -----------------------------------------------------------------------------------

    def upstairs_motion(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        upstairs_ts = datetime.now()
        prev_upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_result=True) # we return current as previous here because we will reset current shortly
        downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_result=True)

        self.call_service('timestamp/set', name='prev_upstairs', value=prev_upstairs_ts)
        self.call_service('timestamp/set', name='upstairs', value=upstairs_ts)

        diff1 = (upstairs_ts - downstairs_ts).seconds
        diff2 = (upstairs_ts - prev_upstairs_ts).seconds

        if self.lib.get_verbose_debug():
            self.log(f'\tu={upstairs_ts} d={downstairs_ts} p={prev_upstairs_ts}', level='DEBUG')
            self.log(f'\tdiff1={diff1} diff2={diff2}', level='DEBUG')

        if diff1 <= 300:
            timer = 600 # 10m timer for bannister if less than 300 seconds difference
            self.call_service('lighting/lumie_on') # lumie_on will check time of day
        elif diff1 > 300 and diff2 <= 120:
            timer = 10 # but if max has gone to the loo, only 10 seconds
        else:
            timer = 60

        if self.now_is_between('22:00:00', 'sunrise') or self.lib.get_testing():
            kwargs = {**kwargs, 'timer': timer, 'key': 'upstairs'} #  'check_override': False,

        self.stairs_motion(**kwargs)

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def downstairs_motion(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        verbose = self.lib.get_verbose_debug()
        self.downstairs_motion_flag = True

        if verbose:
            self.log(f'\tdownstairs_motion_flag={self.downstairs_motion_flag}', level='DEBUG')

        self.call_service('timestamp/set', name='downstairs')
        self.stairs_motion(**kwargs)

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('media_player/volume_mute', entity_id='media_player.bedroom', is_volume_muted=True)
            self.call_service('light/turn_off', entity_id=self.const.LUMIE)

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def kitchen_motion(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        seconds = kwargs.get('seconds', 5*60)

        self.call_service('lighting/kitchen_on', seconds=seconds, cb='kitchen_off', key='kitchen')
        self.call_service('lighting/kitchen_floor_on', seconds=seconds*2, cb='kitchen_floor_off', key='kitchen_floor')

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def utility_motion(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', 5*60)
        key = kwargs.get('key', 'utility')
        brightness = kwargs.get('brightness', 64)

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            self.call_service('lighting/turn_on_if_off', entity_id=self.const.UTILITY, brightness=brightness, seconds=seconds, cb=cb, key=key)

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def status(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        status = f'\n\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------

    def status_event(self, event:str, data:dict, kwargs:dict) -> None:

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def garage_motion(self, entity_id:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        if self.lib.get_verbose_debug():
            self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if old == 'off' and new == 'on':
            self.call_service('lighting/garage_on')
        elif old == 'on' and new == 'off' and kwargs.get('test', False):
            self.call_service('lighting/garage_off')

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def stairs_motion(self, **kwargs) -> None:

        cb = kwargs['cb']
        seconds = kwargs['seconds']
        key = kwargs['key']
        verbose = self.lib.get_verbose_debug()

        downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_result=True)
        upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_result=True)

        if verbose:
            self.log(
                f'\tcb={cb} seconds={seconds} key={key} ' +
                f'downstairs_ts={downstairs_ts.ctime()} ({downstairs_ts.timestamp():6.3f}) ' +
                f'upstairs_ts={upstairs_ts.ctime()} ({upstairs_ts.timestamp():6.3f})', level='DEBUG')

        if self.lib.is_below_horizon() or self.lib.get_testing():
            self.call_service('lighting/bannister_on', seconds=seconds, cb=cb, key=key)

# -----------------------------------------------------------------------------------

    def front_door_motion(self, entity_id:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        # self.lib.log_function_name()

        seconds = kwargs.get('seconds', 5*60)

        if self.lib.get_verbose_debug():
            self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if (self.now_is_between('05:00:00', '06:00:00') and new == 'on'):
            self.call_service('scene/turn_on', entity_id='scene.all_off')

        if (self.now_is_between('sunset', 'sunrise') and new == 'on'):
            self.call_service('lighting/front_door_on', seconds=seconds, cb='front_door_off', key='front_door')

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def front_door_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.front_door_motion('', '', '', 'on', {'seconds': 5, 'key': 'front door', 'cb': 'front_door_off'})

# -----------------------------------------------------------------------------------

    def downstairs_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def upstairs_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.upstairs_motion('', '', '', '', {'seconds': 5, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def stairs_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})
        self.lib.delay(15)
        self.upstairs_motion('', '', '', '', {'seconds': 10, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def kitchen_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.kitchen_motion('', '', '', '', {'seconds': 5})

# -----------------------------------------------------------------------------------

    def utility_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.utility_motion('', '', '', '', {'seconds': 5, 'key': 'utility', 'cb': 'utility_off'})

# -----------------------------------------------------------------------------------

    def garage_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.garage_motion('', '', 'off', 'on', {}) # {'seconds': 5, 'key': 'garage', 'cb': 'garage_off'})
        self.lib.delay(15)
        self.garage_motion('', '', 'on', 'off', {'test': True})

# -----------------------------------------------------------------------------------

    def motion_motion_event(self, event:str, data:dict, kwargs:dict) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        entity_id = 'light.hallway_1'
        self.downstairs_motion_event('',{},{})

        self.lib.delay(15)
        self.upstairs_motion_event('',{},{})
        self.lib.delay(15)
        self.garage_motion_event('',{},{})
        self.lib.delay(15)
        self.front_door_motion_event('',{},{})
        self.lib.delay(15)
        self.call_service('light/turn_off', entity_id=entity_id)
        self.kitchen_motion_event('',{},{})
        self.lib.delay(15)
        self.utility_motion_event('',{},{})

# -----------------------------------------------------------------------------------
