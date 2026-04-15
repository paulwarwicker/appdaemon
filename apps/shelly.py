# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from typing import TYPE_CHECKING, cast

import constants as const
from automationbase import AutomationBase  # type: ignore

class Shelly(AutomationBase):
    """Documentation for Shelly"""

    BUTTON_WINDOW_START = '00:00:00'
    BUTTON_WINDOW_END = '07:30:00'

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.listen_event(self.button_event, 'shelly.click')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def button_event(self, event, data, kwargs) -> None:

        self._log_function_name(start=True, force=True)

        device = data['device']

        if device == const.BEDROOM_BUTTON:
            self.bedroom_button(data, kwargs)
        elif device == const.GARAGE_BUTTON:
            self.garage_button(data, kwargs)

        self._log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def bedroom_button(self, data, kwargs) -> None:

        self._log_function_name(start=True, force=True)

        event_type  = None
        click_type = data['click_type']

        self.log(f'\t{click_type} press on {const.BEDROOM_BUTTON}')

        pt = self.get_state('input_boolean.physical_training') == 'on'

        if click_type == 'single':
            if pt:
                event_type  = 'stop_bedroom'
            else:
                if self.now_is_between(self.BUTTON_WINDOW_START, self.BUTTON_WINDOW_END):
                    event_type  = 'stop_bedroom'
                else:
                    event_type  = 'snooze10'
        elif click_type == 'long':
            if pt:
                event_type  = 'snooze10'
            else:
                if self.now_is_between(self.BUTTON_WINDOW_START, self.BUTTON_WINDOW_END):
                    event_type  = 'stop_bedroom'
                else:
                    event_type  = 'snooze30'
        elif click_type == 'double':
            event_type  = 'all_off'
        elif click_type == 'triple':
            event_type  = 'all_off'

        if event_type is not None:
            self.fire_event(event_type)

        self._log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def _garage_event_from_state(self) -> str | None:
        """Return the garage event based on the current garage sensor state."""

        state = self.get_state(const.GARAGE_ENTITY_ID)

        if state is None:
            return None

        return 'garage_close' if state == 'open' else 'garage_open'

# -----------------------------------------------------------------------------------

    def garage_button(self, data, kwargs) -> None:

        self._log_function_name(start=True, force=True)

        event_type  = None
        click_type = data['click_type']

        self.log(f'\t{click_type} press on {const.GARAGE_BUTTON}')

        if click_type in ('single', 'long', 'double', 'triple'):
            event_type = self._garage_event_from_state()
        # elif click_type == 'triple':
        #     pass

        if event_type is not None:
            self.fire_event(event_type)

        self._log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------
