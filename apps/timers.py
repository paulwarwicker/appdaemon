# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Timers(Hass):
    """Documentation for Timers"""

    lib = None
    timers = {}
    # groups = {}

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        # self.lib = AutomationLib(self)

        self.register_service('timers/set', self.set_timer_service)
        self.register_service('timers/get', self.get_timer_service)
        self.register_service('timers/cancel', self.cancel_timer_service)
        self.register_service('timers/status', self.timer_status_service)
        self.register_service('timers/cancel_kitchen_timers', self.cancel_kitchen_timers_service)
        self.register_service('timers/cancel_utility_timers', self.cancel_utility_timers_service)

        # self.listen_state(self.set_console_log_level, 'input_boolean.debug', new='on')
        # self.listen_state(self.set_console_log_level, 'input_boolean.debug', new='off')

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def set_timer_service(self, namespace, domain, service, kwargs) -> None:
        """store a timer callback"""

        name = kwargs.get('name', None)
        cb = kwargs.get('cb', None)
        # group = kwargs.get('group', 'general')

        if name is not None:
            self._cancel_timer(name)
            self.timers[name] = cb
            self.log(f'\t{name} timer started', level='INFO')

            # group = self.groups.get(group, None)

            # if group is None:
            #     group = groups[group] = {}

            # group[name] = cb

# ---------------------------------------------------------------------------------------------------------

    def get_timer_service(self, namespace, domain, service, kwargs) -> None:
        """get a timer callback"""

        name = kwargs.get('name', None)

        return self.get_timer(name)

# ---------------------------------------------------------------------------------------------------------

    def cancel_timer_service(self, namespace, domain, service, kwargs) -> None:
        """get a timer callback"""

        name = kwargs.get('name', None)

        self._cancel_timer(name)

# ---------------------------------------------------------------------------------------------------------

    def cancel_kitchen_timers_service(self, namespace, domain, service, kwargs) -> None:
        """get a timer callback"""

        self._cancel_timer('kitchen_timer')
        self._cancel_timer('kitchen_long_timer')
        self._cancel_timer('kitchen_floor_timer')

# ---------------------------------------------------------------------------------------------------------

    def cancel_utility_timers_service(self, namespace, domain, service, kwargs) -> None:
        """get a timer callback"""

        self._cancel_timer('utility_timer')
        self._cancel_timer('utility_long_timer')

# ---------------------------------------------------------------------------------------------------------

    def get_timer(self, name):
        """get a timer callback"""

        return self.timers.get(name, None)


# ---------------------------------------------------------------------------------------------------------

    def _cancel_timer(self, name) -> None:
        """get a timer callback"""

        name = self.kwargs.get('name', None)
        cb = self.timers.get(name, None)

        if cb:
            self.cancel_timer(existing, True)
            self.log(f'\t{name} timer cancelled', level='WARNING')

# ---------------------------------------------------------------------------------------------------------

    def timer_status_service(self, namespace, domain, service, kwargs) -> None:
        """."""

        pass

# ---------------------------------------------------------------------------------------------------------
