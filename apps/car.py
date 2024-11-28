# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
# import myconstants as const

class Car(Hass):
    """Documentation for Car"""

    lib = None
    _latitude = -180
    _longitude = -180
    LOCK_ENTITY_ID = 'lock.skoda_karoq_door_lock'
    SENSOR_ENTITY_ID = 'binary_sensor.skoda_karoq_vehicle_locked'
    SENSOR_ENTITY_LIST = [
        'binary_sensor.skoda_karoq_doors_locked','binary_sensor.skoda_karoq_bonnet',
        'binary_sensor.skoda_karoq_vehicle_locked','binary_sensor.skoda_karoq_doors_open',
        'binary_sensor.skoda_karoq_windows','binary_sensor.skoda_karoq_trunk'
        ]
    DEVICE_TRACKER_ID = 'device_tracker.skoda_karoq_position'


# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.listen_state(self.car_door, self.SENSOR_ENTITY_ID)

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_status, runtime)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def check_status(self, kwargs) -> None:
        """check karoq status"""

        self.call_service('homeassistant/update_entity', entity_id=self.DEVICE_TRACKER_ID)

        state = self.get_state(self.SENSOR_ENTITY_ID)
        tracker = self.get_state(self.DEVICE_TRACKER_ID, attribute='all')
        location = tracker['state']

        # self.log(f'\nstate={state}\nlocation={location}\nattributes={attributes}')

        if not location in ('unavailable','unknown'):
            latitude = tracker['attributes']['latitude']
            longitude = tracker['attributes']['longitude']
            # self.log(f'\tlatitude={latitude} longitude={longitude}')
            if latitude != self._latitude or longitude != self._longitude:
                self.set_state('sensor.karoq_latitude', state=latitude)
                self.set_state('sensor.karoq_longitude', state=longitude)
                self._latitude = latitude
                self._longitude = longitude

        if location != "home":
            return

        if state in ('unavailable','unknown'):
            self.log(f'\tupdate entities {self.SENSOR_ENTITY_LIST}')
            self.call_service('homeassistant/update_entity', entity_id=self.SENSOR_ENTITY_LIST)
            return

        verbose = self.lib.get_verbose_debug()
        locked = state == 'off'
        lock_state = 'locked' if locked else 'unlocked'

        if verbose:
            ts = self.call_service('timestamp/get', name='karoq', return_result=True)
            self.log(f'\tstate={state} locked={locked} lock_state={lock_state} ts={ts}', level='DEBUG')

        if state != 'off':
            if self.lib.is_after(16):
                message='The car door is unlocked. A lock request has been sent'
                self.call_service('lock/lock', entity_id=self.LOCK_ENTITY_ID)

                ts = self.call_service('timestamp/get', name='karoq', return_result=True)
                diff = (datetime.now() - ts).seconds

                if diff > self.lib.interval(minutes=10):
                    self.call_service('announcer/broadcast', message=message, timestamp='karoq')

                return

            ts = self.call_service('timestamp/get', name='karoq', return_result=True)
            diff = (datetime.now() - ts).seconds
            if diff > self.lib.interval(minutes=60):
                self.announce()

# -----------------------------------------------------------------------------------

    def announce(self) -> None:
        """door announcement"""

        state = self.get_state(self.SENSOR_ENTITY_ID)
        self.log(f'\tstate={state}', level='DEBUG')
        message = None

        if state == 'off':
            message = 'The car door is locked'
        elif state == 'on':
            message = 'The car door is unlocked'
        else:
            self.call_service('homeassistant/update_entity', entity_id=self.SENSOR_ENTITY_LIST)
            # message = 'The car door state is unknown'
            # self.call_service('announcer/notification', message=message, type='desktop')
            # message = None

        if message:
            self.call_service('announcer/broadcast', message=message, timestamp='karoq')

# -----------------------------------------------------------------------------------

    def car_door(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        self.announce()

# -----------------------------------------------------------------------------------
