# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
import constants as const
import automationlib as self.lib

class Car(Hass):
    """Documentation for Car"""

    lib = None
    const = None
    _latitude = -180
    _longitude = -180
    home_since = None
    locked = None

# -----------------------------------------------------------------------------------

    async def initialize(self) -> None:
        """initialise"""

        self.locked = await self.get_state(const.SENSOR_ENTITY_ID) == 'off'

        self.listen_state(self.car_door, const.SENSOR_ENTITY_ID)

        self.run_minutely(self.check_status, datetime(2024, 1, 1))

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def check_status(self, kwargs) -> None:
        """check karoq status"""

        return

        # verbose = self.lib.get_verbose_debug()

        # self.update()

        # state = await self.get_state(const.SENSOR_ENTITY_ID) # binary_sensor.skoda_karoq_vehicle_locked

        # if state == 'unknown' or state == 'unavailable':
        #     return # check again next iteration

        # tracker = await self.get_state(const.DEVICE_TRACKER_ID, attribute='all') # device_tracker.skoda_karoq_position
        # location = tracker['state']
        # latitude = tracker['attributes'].get('latitude', None)
        # longitude = tracker['attributes'].get('longitude', None)
        # home = location == 'home'

        # ts = self.call_service('timestamp/get', name='karoq_home')

        # if home:
        #     if ts is None:
        #         self.call_service('timestamp/set', name='karoq_home')
        # else:
        #     if ts is not None:
        #         self.call_service('timestamp/set', name='karoq_home', value=None, force=True)

        # if (latitude and longitude) and (latitude != self._latitude or longitude != self._longitude):
        #     self.log(f'\tlatitude={latitude} longitude={longitude}')
        #     self.set_state('sensor.karoq_latitude', state=latitude)
        #     self.set_state('sensor.karoq_longitude', state=longitude)
        #     self._latitude = latitude
        #     self._longitude = longitude

        # locked = state == 'off'
        # lock_state = 'locked' if locked else 'unlocked'

        # if verbose:
        #     level = 'ERROR' if (state in ('unavailable', 'unknown')) or (location in ('unavailable', 'unknown')) else 'DEBUG'
        #     self.log(f'\tstate={state} location={location} home={home} locked={locked} lock_state={lock_state} tracker={tracker}', level=level)

        # if not home:
        #     return # not interested if not at home

        # if not locked and not self.locked and self.lib.is_after(16):
        #     ts = self.call_service('timestamp/get', name='karoq_home')

        #     if ts is None:
        #         self.log('\thome but karoq_home timestamp is not set', level='ERROR')
        #         return

        #     diff1 = (datetime.now() - ts).seconds

        #     ts = self.call_service('timestamp/get', name='karoq_notification')
        #     diff2 = (datetime.now() - ts).seconds

        #     message='The car door is unlocked'

        #     if diff2 > self.lib.interval(self, minutes=10):
        #         self.call_service('announcer/notification', message=message, type='desktop', timestamp='karoq_notification')

        #     if diff1 > self.lib.interval(self, minutes=60):
        #         # been at home for more than 1h

        #         # ts = self.call_service('timestamp/get', name='karoq_announce')
        #         # diff = (datetime.now() - ts).seconds

        #         # message='The car door is unlocked. A lock request has been sent'
        #         # self.call_service('lock/lock', entity_id=const.LOCK_ENTITY_ID)
        #         # message='The car door is unlocked'
        #         self.call_service('announcer/announce', message=message, timestamp='karoq_announce')
        # else:
        #     self.locked = locked

# -----------------------------------------------------------------------------------

    async def announce(self) -> None:
        """door announcement"""

        state = await self.get_state(const.SENSOR_ENTITY_ID)
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

    def car_door(self, entity, attribute, old, new, kwargs:dict) -> None:

        self.announce()

# -----------------------------------------------------------------------------------

    def update(self) -> None:

        pass
        # self.call_service('homeassistant/update_entity', entity_id=const.SENSOR_ENTITY_LIST)
        # self.call_service('homeassistant/update_entity', entity_id=const.DEVICE_TRACKER_ID)

# -----------------------------------------------------------------------------------
