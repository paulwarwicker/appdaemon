# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# Lemon & Einar K - Tenacity (Solarsoul Chill Breaks Remix)

# import traceback
# import random
# import time
from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Alarms2(Hass):
    """Documentation for Alarms"""
    override = False
    default_early_alarm_schedule = 'daily'  # weekday|daily|none
    early_alarm_callback = None
    normal_alarm_callback = None
    test_alarm_callback = None
    rota = None
    lib = None
    const = None
    callbacks = [None, None, None]

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """."""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        # self.rota = self.generate_rota(datetime(2024, 5, 16).date(), 12)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    async def get_alarm_state(self):

        disabled = await self.get_state('input_boolean.alarms_disabled') == 'on'

# -----------------------------------------------------------------------------------
