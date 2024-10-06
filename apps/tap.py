# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import math
# import traceback
# import asyncio
from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Tap(Hass):
    """Documentation for Tap"""

    lib = None
    # tap_ts = None
    tap_ts = datetime.now()

    DAILY_WATERING_MINUTES = 30

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        self.register_service('tap/water_for', self.water_garden_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.water_garden_event, 'water_garden')
        self.listen_event(self.water_garden_for_action, "ios.action_fired", actionName='Water15', minutes=15)

        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_1', new='on', minutes=1)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_1', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_15', new='on', minutes=15)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_15', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_20', new='on', minutes=20)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_20', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_30', new='on', minutes=30)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_30', new='off')

        self.run_daily(self.water_garden_daily, '19:30:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garden_tap, runtime)

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def water_garden_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        minutes = kwargs.get('minutes', None)

        if minutes:
            self.water_garden_for('','','','', {'minutes': minutes})

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for(self, entity, attribute, old, new, kwargs={}) -> None:
        """water garden for <minutes> minutes. different switches will set 1, 15, 20, 30 minutes"""

        minutes = kwargs['minutes']

        if minutes:
            self.tap_on(minutes=minutes)
        else:
            self.error('no timer set')

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_action(self, event, data, kwargs={}) -> None:
        """water garden for 15 minutes as an iOS action"""

        minutes = kwargs['minutes']

        self.log(f'\twater_garden_for_action for {minutes:d} minutes')
        self.water_garden_for_n_minutes({minutes: minutes})  # was minutes=minutes

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_n_minutes(self, kwargs={}) -> None:
        """water garden for <minutes> minutes"""

        self.water_garden_for('', '', '', '', kwargs)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_stop(self, entity, attribute, old, new, kwargs={}) -> None:
        """stop watering garden"""

        self.tap_off() # TODO: stop running thread

# ---------------------------------------------------------------------------------------------------------

    def water_garden_daily(self, kwargs={}) -> None:
        """water garden daily"""

        if self.lib.is_summer():
            if self.lib.no_rain():
                kwargs = {**kwargs, 'minutes': self.DAILY_WATERING_MINUTES}
                self.water_garden_for_n_minutes(kwargs)
                self.announce(message=f'Watering garden for {self.DAILY_WATERING_MINUTES} minutes')

# ---------------------------------------------------------------------------------------------------------

    def tap_on(self, **kwargs) -> None:
        """turn garden tap on for <minutes> minutes"""

        minutes = kwargs['minutes']

        if minutes:
            self.log(f'\ttap_on for {minutes:d} minutes')
            self.call_service('switch/turn_on', entity_id='switch.garden_tap')
            self.call_service('timsestamp/set', name='tap')
            seconds = self.lib.interval(minutes=minutes)
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.tap_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def tap_off(self, kwargs={}) -> None:
        """turn garden tap off"""

        self.call_service('switch/turn_off', entity_id='switch.garden_tap')
        self.announce(message='The garden tap is now off')
        self.call_service('timsestamp/set', name='tap', value=None)
        self.set_state('input_boolean.water_garden_1', state='off')
        self.set_state('input_boolean.water_garden_15', state='off')
        self.set_state('input_boolean.water_garden_20', state='off')
        self.set_state('input_boolean.water_garden_30', state='off')

# ---------------------------------------------------------------------------------------------------------

    def check_garden_tap(self, kwargs) -> None:
        """check garden tap state"""

        state = self.get_state('switch.garden_tap')

        if state == 'on':
            self.log(f'\tGarden tap is {state}', level='WARNING')
            seconds = (datetime.now() - self.tap_ts).seconds
            n = math.ceil(seconds / 60)
            diff1,diff2 = divmod(seconds, 60)
            self.log(f'\t\t{diff1} {diff2}')
            if diff1 > 0 and ((diff1 + 1) % 10) == 0:
                self.announce(message=f'The garden tap has been on for {n} minutes', entity_id=['media_player.kitchen','media_player.study'])

# ---------------------------------------------------------------------------------

    def water_garden_event(self, event, data, kwargs) -> None:

        minutes = data['minutes']
        self.water_garden_for_n_minutes({'minutes': minutes})
        self.announce(message=f'Watering garden for {minutes} minutes')

# ---------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status('','','','')

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

