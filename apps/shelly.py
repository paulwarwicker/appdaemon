# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611

class Shelly(Hass):
    """Documentation for Shelly"""

    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.listen_event(self.button_event, 'shelly.click')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def button_event(self, event, data, kwargs) -> None:

        device = data['device']

        if self.lib.get_verbose_debug():
            self.log(f'\tbutton press on {device}')

        if device == self.const.BEDROOM_BUTTON:
            self.bedroom_button(data, kwargs)
        elif device == self.const.GARAGE_BUTTON:
            self.garage_button(data, kwargs)


# -----------------------------------------------------------------------------------

    def bedroom_button(self, data, kwargs) -> None:

        event_type  = None
        click_type = data['click_type']

        if self.lib.get_verbose_debug():
            self.log(f'\t{click_type} press on {self.const.BEDROOM_BUTTON}')
            # self.log(f'\t{data}')

        if click_type == 'single':
            event_type  = 'all_off'
        elif click_type == 'long':
            event_type  = 'snooze'
        elif click_type == 'double':
            event_type  = 'lumie_on'
        elif click_type == 'triple':
            pass

        if event_type is not None:
            self.fire_event(event_type)

# -----------------------------------------------------------------------------------

    def garage_button(self, data, kwargs) -> None:

        event_type  = None
        click_type = data['click_type']

        if self.lib.get_verbose_debug():
            self.log(f'\t{click_type} press on {self.const.GARAGE_BUTTON}')
            # self.log(f'\t{data}')

        if click_type == 'single':
            event_type  = 'garage_close'
        elif click_type == 'long':
            event_type  = 'garage_open'
        elif click_type == 'double':
            state = self.get_state(self.const.GARAGE_ENTITY_ID)
            if state == 'open':
                event_type = 'garage_close'
            else:
                event_type = 'garage_open'
        elif click_type == 'triple':
            pass

        if event_type is not None:
            self.fire_event(event_type)

# -----------------------------------------------------------------------------------
