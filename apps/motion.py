# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Motion(Hass):
    """Documentation for Motion"""

    downstairs_motion_flag = False
    lib = None
    UTILITY_ENTITY_ID = 'light.utility_room_1'

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        self.register_service('motion/set_downstairs_motion_flag', self.set_downstairs_motion_flag)
        self.register_service('motion/reset_downstairs_motion_flag', self.reset_downstairs_motion_flag)

        self.listen_state(self.kitchen_motion, 'binary_sensor.kitchen_sensor_motion', old='off', new='on', timer=300, location='kitchen')
        self.listen_state(self.utility_motion, 'binary_sensor.utility_room_motion_sensor_motion', old='off', new='on', timer=300, location='utility')
        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion', old='off', new='on', timer=300, check_override=True, location='downstairs')
        self.listen_state(self.upstairs_motion, 'binary_sensor.upstairs_sensor_motion', old='off', new='on', timer=600, check_override=False, location='upstairs')

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def set_downstairs_motion_flag(self, namespace, domain, service, kwargs) -> None:
        """store a timer callback"""

        value = kwargs.get('value', None)

        if value:
            self.downstairs_motion_flag = value

# ---------------------------------------------------------------------------------------------------------

    def reset_downstairs_motion_flag(self, namespace, domain, service, kwargs) -> None:
        """store a timer callback"""

        self.downstairs_motion_flag = False

# ---------------------------------------------------------------------------------------------------------

    def upstairs_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        ts = datetime.now()

        downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_value=True)
        prev_upstairs_ts = self.call_service('timestamp/get', name='prev_upstairs', return_value=True)
        upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_value=True)

        self.call_service('timestamp/set', name='prev_upstairs', value=upstairs_ts)
        self.call_service('timestamp/set', name='upstairs', value=ts)

        diff1 = (upstairs_ts - downstairs_ts).seconds
        diff2 = (upstairs_ts - prev_upstairs_ts).seconds
        self.log(f'\tdiff1={diff1} diff2={diff2}', level='DEBUG')

        if diff1 <= 300:
            timer = 600 # 5m timer for bannister
            if self.now_is_between('00:00:00', '03:00:00'):
                self.call_service('lighting/turn_on', entity_id='light.lumie', brightness=10)
        elif diff1 > 300 and diff2 <= 120:
            timer = 10
        else:
            timer = 120

        if self.now_is_between('22:00:00', 'sunrise') or self.get_state(entity_id='input_boolean.test_2'):
            kwargs = {**kwargs, 'timer': timer, 'check_override': False, 'location': 'upstairs'}
        self.stairs_motion(**kwargs)

# ---------------------------------------------------------------------------------------------------------

    def downstairs_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.downstairs_motion_flag = True
        self.log(f'\tdownstairs_motion_flag={self.downstairs_motion_flag}', level='DEBUG')

        self.call_service('timestamp/set', name='downstairs')

        self.stairs_motion(**kwargs)

        if self.lib.is_night():
            self.call_service('sonos/unjoin_all')
            self.call_service('lighting/turn_off', entity_id='light.lumie')

        # self.cancel_alarm_if_set('switch.sonos_alarm_1392', '07:00:00')  # 07:00 alarm
        # self.cancel_alarm_if_set('input_boolean.early_alarm', '07:00:00', '06:00:00')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.call_service('timers/cancel_kitchen_timers')
        self.call_service('lighting/kitchen_floor_on')
        self.call_service('lighting/kitchen_floor_off', seconds=5 * 60)
        # seconds = 5 * 60
        # self.log(f'\tstart kitchen floor timer for {seconds:d}s', level='INFO')
        # self.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)

        # if self.sun_down():
        # if self.now_is_between('sunset + 00:15:00', 'sunrise + 00:30:00'):
        if self.lib.is_night():
            self.log('\tsun down - turn_on_if_off kitchen_1/4/5/6', level='INFO')
            self.call_service('lighting/kitchen_low', seconds=5 * 60)
            self.call_service('lighting/kitchen_off', seconds=10 * 60)
            # self.turn_on_if_off('light.kitchen_1')
            # self.turn_on_if_off('light.kitchen_4')
            # self.turn_on_if_off('light.kitchen_5')
            # self.turn_on_if_off('light.kitchen_6')
            # seconds = 5 * 60
            # self.log(f'\tstart short kitchen timer for {seconds:d}s', level='INFO')
            # self.kitchen_timer = self.run_in(self.kitchen_off, seconds, **kwargs)
            # seconds = 10 * 60
            # self.log(f'\tstart long kitchen timer for {seconds:d}s', level='INFO')
            # self.kitchen_long_timer = self.run_in(self.kitchen_all_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.call_service('timers/cancel_utility_timers')
        self.call_service('lighting/utility_on')

        # entity_id = 'light.utility_room_1'
        # # state = self.get_state(entity_id=entity_id)
        # brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        # self.log(f'\tbrightness={brightness} st={self.utility_timer} lt={self.utility_long_timer}', level='DEBUG')

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            prev_state = self.call_service('lighting/turn_on_if_off', entity_id=self.UTILITY_ENTITY_ID, brightness=64, return_value=True)
            self.log(f'\tprev_state={prev_state}', level='DEBUG')
            self.call_service('lighting/utility_on', seconds=5 * 60)
            self.call_service('lighting/utility_off', seconds=10 * 60)
            # seconds = 5 * 60
            # self.log(f'\tstart short utility timer for {seconds:d}s', level='DEBUG')
            # self.utility_timer = self.run_in(self.utility_off, seconds, timer_type='short')
            # seconds = 10 * 60
            # self.log(f'\tstart long utility timer for {seconds:d}s', level='DEBUG')
            # self.utility_long_timer = self.run_in(self.utility_off, seconds, timer_type='long')

# ---------------------------------------------------------------------------------------------------------

    def stairs_motion(self, **kwargs) -> None:

        downstairs_ts = self.call_service('timestamp/get', name='downstairs', return_value=True)
        upstairs_ts = self.call_service('timestamp/get', name='upstairs', return_value=True)

        self.log(f'\tts1={downstairs_ts.ctime()} ({downstairs_ts.timestamp():6.3f})', level='DEBUG')
        self.log(f'\tts2={upstairs_ts.ctime()} ({upstairs_ts.timestamp():6.3f})', level='DEBUG')

        if self.lib.is_below_horizon():
            seconds = kwargs['timer']
            override = not kwargs['check_override']
            self.call_service('timers/cancel', name='stairs')
            self.call_service('lighting/bannister_on', seconds=5 * 60, cb=self.bannister_off)
            # self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            # self.stairs_timer = self.run_in(self.bannister_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------

    def status(self, entity='', attribute='', old='', new='', kwargs={}) -> None:

        status = f'\n\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# ---------------------------------------------------------------------------------

    def set_downstairs_motion_flag(self, namespace, domain, service, data) -> None:

        self.downstairs_motion_flag = data['state']

# ---------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status()

# ---------------------------------------------------------------------------------
