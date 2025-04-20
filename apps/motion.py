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
    upstairs_motion_flag = False
    upstairs_motion_active = False
    downstairs_motion_flag = False
    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

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

        self.listen_state(self.front_door_motion, 'binary_sensor.front_door_motion',          new='on',  cb='front_door_off')
        self.listen_state(self.front_door_motion, 'binary_sensor.front_door_motion',          new='off', cb='front_door_off')
        self.listen_state(self.kitchen_motion,    'binary_sensor.kitchen_sensor_motion',      new='on',  cb='kitchen_off')
        self.listen_state(self.kitchen_motion,    'binary_sensor.kitchen_sensor_motion',      new='off', cb='kitchen_off')
        self.listen_state(self.utility_motion,    'binary_sensor.utility_room_sensor_motion', new='on',  cb='utility_off')
        self.listen_state(self.utility_motion,    'binary_sensor.utility_room_sensor_motion', new='off', cb='utility_off')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='on',  cb='bathroom_off')
        self.listen_state(self.bathroom_motion,   'binary_sensor.bathroom_sensor_motion',     new='off', cb='bathroom_off')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.garage_sensor_motion',       new='on',  cb='cloakroom_off')
        self.listen_state(self.cloakroom_motion,  'binary_sensor.garage_sensor_motion',       new='off', cb='cloakroom_off')

        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion',   new='on') #,  cb='downstairs_off', seconds=5*60)
        self.listen_state(self.upstairs_motion,   'binary_sensor.upstairs_sensor_motion',     new='on') #,  cb='upstairs_off', seconds=10*60)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

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

        ts = self.call_service('timestamp/get', name='garage', return_result=True)
        diff = (datetime.now() - ts).seconds

        if diff > self.lib.interval(seconds=10):
            self.call_service('light/turn_on', entity_id=self.const.GARAGE2)

# -----------------------------------------------------------------------------------

    def status_event(self, event:str, data:dict, kwargs) -> None:

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def front_door_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.front_door_motion('', '', '', 'on', {'seconds': 5, 'key': 'front door', 'cb': 'front_door_off'})

# -----------------------------------------------------------------------------------

    def downstairs_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def upstairs_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.upstairs_motion('', '', '', '', {'seconds': 5, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def stairs_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.downstairs_motion('', '', '', '', {'seconds': 5, 'key': 'downstairs', 'cb': 'bannister_off'})
        self.lib.delay(15)
        self.upstairs_motion('', '', '', '', {'seconds': 10, 'key': 'upstairs', 'cb': 'bannister_off'})

# -----------------------------------------------------------------------------------

    def kitchen_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.kitchen_motion('', '', '', '', {'seconds': 5})

# -----------------------------------------------------------------------------------

    def utility_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.utility_motion('', '', '', '', {'seconds': 5, 'key': 'utility', 'cb': 'utility_off'})

# -----------------------------------------------------------------------------------

    def garage_motion_event(self, event:str, data:dict, kwargs) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'\tevent={event} data={data} kwargs={kwargs}', level='DEBUG')

        self.garage_motion('', '', 'off', 'on', {})
        self.lib.delay(15)
        self.garage_motion('', '', 'on', 'off', {'test': True})

# -----------------------------------------------------------------------------------

    def motion_motion_event(self, event:str, data:dict, kwargs) -> None:

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

    def upstairs_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name(True, True)

        if self.upstairs_motion_active:
            self.log('upstairs_motion_active is active', level='WARNING')
            self.lib.log_function_name(False, True)
            return

        self.upstairs_motion_active = True
        self.run_in(self.reset_upstairs_motion_active, 10*60)

        ts = self.call_service('timestamp/get', name='upstairs_motion', return_result=True)
        # nomotion = (datetime.now() - ts).seconds > 1*60*60

        self.call_service('timestamp/set', name='upstairs_motion', value=datetime.now())

        ts = self.call_service('timestamp/get', name='upstairs', return_result=True)
        self.call_service('timestamp/set', name='prev_upstairs', value=ts)
        self.call_service('timestamp/set', name='upstairs', value=datetime.now())

        if self.lib.is_below_horizon(): # and not self.upstairs_motion_active:
            # self.upstairs_motion_active = True
            self.call_service('lighting/upstairs_on')
            # self.call_service('lighting/upstairs_on', cb='upstairs_off', seconds=seconds, nomotion=nomotion)
            # self.run_in(self.reset_upstairs_motion_active, 10*60)

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def downstairs_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name(True, True)

        self.downstairs_motion_flag = True
        self.call_service('timestamp/set', name='downstairs')

        # self.check_downstairs_motion()
        # self.stairs_motion(**kwargs)

        if self.lib.is_below_horizon(): # or self.lib.get_testing():
            self.call_service('lighting/downstairs_on', seconds=3*60, cb='downstairs_off')

        # if self.now_is_between('05:00:00', '06:30:00'):
        #     self.call_service('media_player/volume_mute', entity_id='media_player.bedroom', is_volume_muted=True)
        #     self.call_service('light/turn_off', entity_id=self.const.LUMIE)

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def check_downstairs_motion(self) -> None:

        downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_result=True)
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion', return_result=True)

        if (downstairs_ts - front_door_ts).seconds < 60:
            self.call_service('lighting/front_door_off')
            # self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP)

# -----------------------------------------------------------------------------------

    def check_upstairs_motion(self) -> None:

        upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_result=True)
        front_door_ts = self.call_service('timestamp/get', name='front_door_motion', return_result=True)

        if (upstairs_ts - front_door_ts).seconds < 120:
            self.run_in(self.all_off, 60)

# -----------------------------------------------------------------------------------

    def kitchen_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name()

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', 5*60)

        self.call_service(f'lighting/kitchen_{new}', cb=cb, seconds=seconds)

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def utility_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name()

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', 2*60)
        brightness = kwargs.get('brightness', 64)

        if new == 'off':
            self.call_service('lighting/utility_off', cb=cb)
        elif new == 'on':
            if self.now_is_between('sunset + 00:15:00', 'sunrise'):
                self.call_service('lighting/turn_on_if_off', entity_id=self.const.UTILITY, brightness=brightness, seconds=seconds, cb=cb)

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def bathroom_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name()

        cb = kwargs.get('cb', None)

        self.call_service(f'lighting/bathroom_{new}', entity_id=self.const.BATHROOM_LIGHTS, cb=cb)

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def cloakroom_motion(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

        self.lib.log_function_name()

        cb = kwargs.get('cb', None)
        seconds = kwargs.get('seconds', 1*60)
        brightness = kwargs.get('brightness', 128)

        if new == 'on':
            early = 'sunrise + 01:00:00'
            evening = 'sunset + 00:00:00'
            brightness = 255 if self.now_is_between(early, evening) else 128

        self.call_service(f'lighting/cloakroom_{new}', entity_id=self.const.CLOAKROOM, brightness=brightness, seconds=seconds, cb=cb)

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def garage_motion(self, entity_id:str, attribute:str, old:str, new:str, kwargs) -> None:

        # self.lib.log_function_name()

        if self.lib.get_verbose_debug():
            self.log(f'\tentity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if old == 'off' and new == 'on':
            self.call_service('lighting/garage_on')
        elif old == 'on' and new == 'off' and kwargs.get('test', False):
            self.call_service('lighting/garage_off')

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    # def stairs_motion(self, **kwargs) -> None:

    #     cb = kwargs['cb']
    #     seconds = kwargs['seconds']
    #     key = kwargs['key']
    #     verbose = self.lib.get_verbose_debug()

    #     downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_result=True)
    #     upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_result=True)

    #     if verbose:
    #         self.log(
    #             f'\tcb={cb} seconds={seconds} key={key} ' +
    #             f'downstairs_ts={downstairs_ts.ctime()} ({downstairs_ts.timestamp():6.3f}) ' +
    #             f'upstairs_ts={upstairs_ts.ctime()} ({upstairs_ts.timestamp():6.3f})', level='DEBUG')

    #     if self.lib.is_below_horizon() or self.lib.get_testing():
    #         self.call_service('lighting/bannister_on', seconds=seconds, cb=cb, key=key)

# -----------------------------------------------------------------------------------

    def front_door_motion(self, entity_id:str, attribute:str, old:str, new:str, kwargs) -> None:

        cb = kwargs.get('cb', None)

        if self.now_is_between('sunset', 'sunrise'):
            self.call_service(f'lighting/front_door_{new}', entity_id=self.const.FRONT_DOOR_LIGHTS, cb=cb)

# -----------------------------------------------------------------------------------

    def status(self, entity:str, attribute:str, old:str, new:str, kwargs) -> None:

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
