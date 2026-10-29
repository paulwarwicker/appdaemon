# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from datetime import datetime, timedelta

from datetime import datetime

# from typing import TYPE_CHECKING, cast

import constants as const
from automationbase import AutomationBase  # type: ignore

class Heating(AutomationBase):
    """documentation for Heating"""

    boosted = False
    bedroom_boosted = False
    living_room_boosted = False
    LOW_TEMPERATURE_THRESHOLD = 2.5
    BEDROOM_THRESHOLD = 23.0

# -----------------------------------------------------------------------------------

    def initialize(self):
        """initialise"""

        super().initialize()

        runtime = datetime(2024, 1, 1, 0, 0, 0)

        self.run_every(
            self.set_living_room_temperature,
            runtime,
            const.TENMINUTES
        )

        self.run_every(
            self.set_bedroom_temperature,
            runtime,
            const.TENMINUTES
        )

        self.set_bedroom_temperature({})
        self.set_living_room_temperature({})

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def set_living_room_temperature(self, kwargs):
        """set living room temperature"""

        if self._summer_heating():
            return

        attributes = self.get_state(entity_id=const.HEATING, attribute="all")
        # self.log(f'Heating attributes: {attributes}')
        # current_temperature = attributes['attributes']['current_temperature']
        # temperature = attributes['attributes']['temperature']

        forecast = self.get_state('sensor.weather_tomorrowio_forecast_low_12h')

        if forecast is None:
            self.log('Forecast low is None', level='ERROR')
            return

        current = self.get_state('sensor.weather_tomorrowio_temperature')

        if current is None:
            self.log('Current temperature is None', level='ERROR')
            return

        entity_id = const.HEATING
        temperature = self.get_state(entity_id, attribute="current_temperature")
        temperature = float(temperature) if temperature is not None else None
        # entity_id = 'sensor.heating_temperature'
        # temperature = self.get_state(entity_id)

        if temperature is None:
            self.log('Heating temperature is None', level='ERROR')
            return
        else:
            if self._get_verbose():
                self.log(f'Heating temperature is {temperature}', level='INFO')

        current = float(current)
        forecast = float(forecast)
        temperature = float(temperature)

        if current <= self.LOW_TEMPERATURE_THRESHOLD:
            target = temperature + 1.0
            # temperature will already be in 0.5 degree increments
            if temperature >= target:
                pass
            else:
                # attributes={'target_temp_high': target, "hvac_action": "heat"}
                # self.call_service('climate/set_temperature', entity_id=const.HEATING, **attributes)
                if not self.boosted:
                    self.call_service('climate/set_temperature', entity_id=entity_id, temperature=target, hvac_mode='heat')
                    self.boosted = True
        else:
            if self.boosted:
                target = temperature - 1.0
                # reset to previous temperature
                self.call_service('climate/set_temperature', entity_id=entity_id, temperature=target, hvac_mode='heat')
                self.boosted = False

# -----------------------------------------------------------------------------------

    def set_bedroom_temperature(self, kwargs):
        """set room temperature"""

        if self._summer_heating() or not self.now_is_between("20:00:00", "07:00:00"):
            return

        entity_id = const.BEDROOM_RADIATOR
        current = self.get_state(entity_id, attribute="temperature")

        if current is None:
            # self.log('Radiator temperature is None', level='ERROR') # FIXME: handle this case properly
            return

        current = float(current)

        if current <= self.BEDROOM_THRESHOLD:
            target = self.BEDROOM_THRESHOLD + 1.0
            if not self.bedroom_boosted:
                self.call_service('climate/set_temperature', entity_id=entity_id, temperature=target, hvac_mode='heat')
                self.bedroom_boosted = True
        else:
            if self.bedroom_boosted:
                self.call_service('climate/set_temperature', entity_id=entity_id, temperature=self.BEDROOM_THRESHOLD, hvac_mode='heat')
            self.bedroom_boosted = False

# -----------------------------------------------------------------------------------
