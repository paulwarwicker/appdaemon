# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Shelly(Hass):
    """Documentation for Shelly"""

    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.listen_event(self.button_event, 'shelly.click')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def button_event(self, event, data, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        device = data['device']

        if device == const.BEDROOM_BUTTON:
            self.bedroom_button(data, kwargs)
        elif device == const.GARAGE_BUTTON:
            self.garage_button(data, kwargs)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def bedroom_button(self, data, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        event_type  = None
        click_type = data['click_type']

        if self.lib.get_verbose_debug():
            self.log(f'\t{click_type} press on {const.BEDROOM_BUTTON}')

        if click_type == 'single':
            event_type  = 'snooze'
        elif click_type == 'long':
            event_type  = 'stop_bedroom'
        elif click_type == 'double':
            event_type  = 'all_off'
        elif click_type == 'triple':
            event_type  = 'stop_bedroom'

        if event_type is not None:
            self.fire_event(event_type)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def _garage_event_from_state(self) -> str | None:
        """Return the garage event based on the current garage sensor state."""

        state = self.get_state(const.GARAGE_ENTITY_ID)

        if state is None:
            return None

        return 'garage_close' if state == 'open' else 'garage_open'

# -----------------------------------------------------------------------------------

    def garage_button(self, data, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        event_type  = None
        click_type = data['click_type']

        if self.lib.get_verbose_debug():
            self.log(f'\t{click_type} press on {const.GARAGE_BUTTON}')

        if click_type in ('single', 'long', 'double'):
            event_type = self._garage_event_from_state()
        elif click_type == 'triple':
            pass

        if event_type is not None:
            self.fire_event(event_type)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------
