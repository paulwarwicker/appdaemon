# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Car(Hass):
    """Documentation for Car"""

    lib = None
    const = None
    _latitude = -180
    _longitude = -180
    locked = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)
        self.locked = self.get_state(self.const.SENSOR_ENTITY_ID) == 'off'

        self.listen_state(self.car_door, self.const.SENSOR_ENTITY_ID)

        self.run_minutely(self.check_status, datetime(2024, 1, 1))

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def check_status(self, kwargs) -> None:
        """check karoq status"""

        verbose = self.lib.get_verbose_debug()

        state = self.get_state(self.const.SENSOR_ENTITY_ID) # binary_sensor.skoda_karoq_vehicle_locked

        if state == 'unknown':
            self.log(f'\tupdate entities {self.const.SENSOR_ENTITY_LIST}')
            self.update()
            return # check again next iteration

        tracker = self.get_state(self.const.DEVICE_TRACKER_ID, attribute='all') # device_tracker.skoda_karoq_position
        location = tracker['state']
        home = location == 'home'

        if location in ('unknown', 'available'):
            self.log(f'\tupdate tracker {self.const.DEVICE_TRACKER_ID}')
            self.update()

        # if location != "home":
        #     return

        latitude = tracker['attributes'].get('latitude', None)
        longitude = tracker['attributes'].get('longitude', None)

        if (latitude and longitude) and (latitude != self._latitude or longitude != self._longitude):
            if verbose:
                self.log(f'\tlatitude={latitude} longitude={longitude}')
            self.set_state('sensor.karoq_latitude', state=latitude)
            self.set_state('sensor.karoq_longitude', state=longitude)
            self._latitude = latitude
            self._longitude = longitude

        locked = state == 'off'
        lock_state = 'locked' if locked else 'unlocked'

        if not locked and not self.locked:
            if verbose and not home:
                ts = self.call_service('timestamp/get', name='karoq_announce', return_result=True)
                level = 'ERROR' if (state in ('unavailable', 'unknown')) or (location in ('unavailable', 'unknown')) else 'DEBUG'
                self.log(f'\tstate={state} location={location} locked={locked} lock_state={lock_state} tracker={tracker} ts={ts} (karoq_announce)', level=level)

            if self.lib.is_after(16):
                # message='The car door is unlocked'
                message='The car door is unlocked. A lock request has been sent'
                self.call_service('lock/lock', entity_id=self.const.LOCK_ENTITY_ID)

                ts = self.call_service('timestamp/get', name='karoq_notification', return_result=True)
                diff = (datetime.now() - ts).seconds

                if diff > self.lib.interval(minutes=10):
                    self.call_service('announcer/notification', message=message, type='desktop', timestamp='karoq_notification')
                    return

                ts = self.call_service('timestamp/get', name='karoq_announce', return_result=True)
                diff = (datetime.now() - ts).seconds

                if diff > self.lib.interval(minutes=30):
                    self.call_service('announcer/announce', message=message, timestamp='karoq_announce')

                # ts = self.call_service('timestamp/get', name='karoq', return_result=True)
                # diff = (datetime.now() - ts).seconds

                # self.call_service('announcer/broadcast', message=message, timestamp='karoq')

                # if diff > self.lib.interval(minutes=30):
                #     self.call_service('announcer/notification', message=message, type='desktop')
                #     self.call_service('timestamp/set', name='karoq')

                # # return


                # ts = self.call_service('timestamp/get', name='karoq', return_result=True)
                # diff = (datetime.now() - ts).seconds

                # if diff > self.lib.interval(minutes=20):
                #     self.call_service('announcer/broadcast', message=message, timestamp='karoq')
                # return

            # ts = self.call_service('timestamp/get', name='karoq', return_result=True)
            # diff = (datetime.now() - ts).seconds
            # if diff > self.lib.interval(minutes=60):
            #     self.announce()
        else:
            self.locked = locked

# -----------------------------------------------------------------------------------

    def announce(self) -> None:
        """door announcement"""

        state = self.get_state(self.const.SENSOR_ENTITY_ID)
        self.log(f'\tstate={state}', level='DEBUG')
        message = None

        if state == 'off':
            message = 'The car door is locked'
        elif state == 'on':
            message = 'The car door is unlocked'
        else:
            self.update()

        if message is not None:
            self.call_service('announcer/broadcast', message=message, timestamp='karoq_announce')

# -----------------------------------------------------------------------------------

    def car_door(self, entity:str, attribute:str, old:str, new:str, kwargs:dict) -> None:

        self.announce()

# -----------------------------------------------------------------------------------

    def update(self) -> None:

        self.call_service('homeassistant/update_entity', entity_id=self.const.SENSOR_ENTITY_LIST)
        self.call_service('homeassistant/update_entity', entity_id=self.const.DEVICE_TRACKER_ID)

# -----------------------------------------------------------------------------------
