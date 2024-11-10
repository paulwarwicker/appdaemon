# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

class FrontDoor(Hass):
    """Documentation for Front Door"""

    lib = None

# ---------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.register_service('front_door/battery', self.front_door_battery_service)

        self.listen_event(self.test_front_door_battery_event, 'test_front_door_battery')

        self.run_daily(self.front_door_battery, '19:30:00')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised')

# ---------------------------------------------------------------------------------

    def front_door_battery_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        # minutes = kwargs.get('minutes', None)

        self.front_door_battery({})

# ---------------------------------------------------------------------------------

    def test_front_door_battery_event(self, event:str, data:dict, kwargs) -> None:

        self.front_door_battery({})

# ----------------------------------------------------------------------------------------------

    def front_door_battery(self, kwargs) -> None:

        level = int(self.get_state('sensor.front_door_battery'))

        message = None

        if level <= 50:
            battery = ''
            if level <= 20:
                battery = ' - CRITICAL'
                message = 'Please replace the front door battery immediately'
            elif level <= 25:
                battery = ' - dangerously low'
                message = 'Please replace the front door battery as soon as possible'
            elif level <= 30:
                battery = ' - low'
                message = 'Please charge the second front door battery'
            if message:
                self.call_service('announcer/broadcast', message=message)

            message=f'Recharge front door battery ({level:d}%{battery})'
            self.call_service('announcer/notification', message=message, type='desktop')

# ---------------------------------------------------------------------------------
