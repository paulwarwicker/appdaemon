# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from datetime import datetime, timedelta

from datetime import datetime

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore
class Heating(Hass):
    """This is the documentation for Heating"""

    lib: "AutomationLib" = _helpers  # type: ignore
    LOW_TEMPERATURE_THRESHOLD = 5.0

# -----------------------------------------------------------------------------------

    def initialize(self):
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        # self.register_service('location/max_home', self.max_home_service)

        # self.listen_state(self.max_location_detect, const.MAX_ENTITY_ID, old='Jan_Jim', location='proximity.jan_jim')

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.set_room_temperature, runtime)

        # runtime = datetime(2024, 1, 1)
        # self.run_minutely(self.test, runtime)

        # self.run_daily(self.set_all_state, '20:00:00') # set state - make sure before max retires (to bed)

        # self.listen_event(self.test_max_home_event, 'max_home')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    # def max_home_service(self, namespace, domain, service, kwargs) -> None:
#         """max home"""

#         self.lib.log_function_name(start=True)

#         self.call_service('lighting/welcome_lights', cb='welcome_lights_off')

#         self.lib.log_function_name(start=False)

# # -----------------------------------------------------------------------------------

#     def test_paul_home_event(self, event, data, kwargs):

#         self.call_service('location/paul_home')

# -----------------------------------------------------------------------------------

    def set_room_temperature(self, kwargs):
        """set room temperature"""

        if self.lib.summer_heating():
            return

        attributes = self.get_state(entity_id=const.HEATING, attribute="all")
        # self.log(f'Heating attributes: {attributes}')
        # current_temperature = attributes['attributes']['current_temperature']
        # temperature = attributes['attributes']['temperature']

        forecast = self.get_state('sensor.weather_tomorrowio_forecast_low_12h')

        if forecast is None:
            self.log('Forecast low is None', level='ERROR')
            return

        forecast = float(forecast)
        # self.log(f'Forecast low: {forecast}')
        current_temperature = self.get_state(const.HEATING, attribute="current_temperature")
        temperature = self.get_state(const.HEATING, attribute="temperature")
        # self.log(f'Heating: current={current_temperature} target={temperature}')

        # if forecast <= 21.5: # self.LOW_TEMPERATURE_THRESHOLD:
        #     # temperature will already be in 0.5 degree increments
        #     target = temperature + 1.0
        #     if temperature < target:
        #         attributes={'target_temp_high': target, "hvac_action": "heat"}
        #         # self.call_service('climate/set_temperature', entity_id=const.HEATING, **attributes)
        #         self.call_service('climate/set_temperature', entity_id=const.HEATING, temperature=target, hvac_mode='heat')


# -----------------------------------------------------------------------------------
