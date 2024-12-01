# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# import inspect
# import traceback
# import asyncio
from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Vacuum(Hass):
    """Documentation for Vacuum"""

    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.listen_state(self.vacuum_debug, 'vacuum.s7_max_ultra')

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.check_roborock, runtime)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def vacuum_debug(self, entity, attribute, old, new, kwargs) -> None:
        """vacuum debug function"""

        state = self.get_state('vacuum.s7_max_ultra')
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# -----------------------------------------------------------------------------------

    def check_roborock(self, kwargs) -> None:

        state = self.get_state('sensor.s7_max_ultra_dock_error')

        if state in ('ok', 'unavailable'):
            return

        if state == "duct_blockage":
            message = 'Vacuum duct blockage'
        elif state == "water_empty":
            message = 'Vacuum clean water tank empty or not installed'
        elif state == "waste_water_tank_full":
            message = 'Vacuum waste water tank full'
        elif state == "cleaning_tank_full_or_blocked":
            message = 'Vacuum cleaning tank full or blocked'
        elif state == "maintenance_brush_jammed":
            message = 'Vacuum maintenance brush jammed'
        elif state == "dirty_tank_latch_open":
            message = 'Vacuum dirty tank latch open'
        elif state == "no_dustbin":
            message = 'Vacuum has no dustbin'
        else:
            self.desktop_notification(f'Roborock has an unknown error {state}')
            return

        diff = (datetime.now() - self.vacuum_announce_ts).seconds

        if diff > ( 3 * 60 ):
            self.call_service('announcer/broadcast', message=message, timestamp='vacuum')
            self.call_service('announcer/announce', entity_id='media_player.study', message=message)

# -----------------------------------------------------------------------------------
