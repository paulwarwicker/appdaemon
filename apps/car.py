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

class Car(Hass):
    """Documentation for Car"""

    lib = None
    count = 0
    KAROQ_ENTITY_ID = 'binary_sensor.tmbkr7nu5p5079987_doors_locked'

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_karoq_door, runtime)

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def check_karoq_door(self, kwargs={}) -> None:
        """check karoq door state"""

        state = self.get_state(self.KAROQ_ENTITY_ID)

        if state == 'unavailable':
            count += 1
            if count > 10:
                  self.log(f'\tkaroq_door_state={state}', level='WARNING')
                  count = 0
            return

        locked = state == 'off'
        lock_state = 'locked' if locked else 'unlocked'
        ts = self.call_service('timestamp/get', name='karoq', return_value=True)

        if self.lib.get_verbose_debug():
            self.log(f'\tstate={state} locked={locked} lock_state={lock_state} ts={ts}', level='WARNING')
            self.log(f'\tThe car door is {lock_state} ts={ts}', level='WARNING')

        if state != 'off':
            if self.lib.is_after(18):
                self.call_service('lock/lock', entity_id='lock.tmbkr7nu5p5079987_door_locked')
                state = self.get_state(self.KAROQ_ENTITY_ID)
                message='The car door is unlocked. A lock request has been sent'
                self.call_service('announcer/broadcast', message=message)
                return

            diff = (datetime.now() - ts).seconds
            if diff > self.lib.interval(minutes=60):
                self.karoq_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    def karoq_door_announce(self, **kwargs) -> None:
        """karoq door announcement"""

        state = kwargs['state']

        if state == 'off':
            message = 'The car door is locked'
        elif state == 'on':
            message = 'The car door is unlocked'

        self.call_service('announcer/broadcast', message=message, timestamp='karoq')
        # self.call_service('timestamp/set', name='karoq')

# ---------------------------------------------------------------------------------------------------------
