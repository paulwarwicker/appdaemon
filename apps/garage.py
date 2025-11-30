# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import time
from datetime import datetime

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Garage(Hass):
    """Documentation for Garage"""

    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.register_service('garage/open', self.garage_open_service)
        self.register_service('garage/close', self.garage_close_service)

        self.listen_state(self.garage_door_announce_open, const.GARAGE_ENTITY_ID, new='open')
        self.listen_state(self.garage_door_announce_opening, const.GARAGE_ENTITY_ID, new='opening')
        self.listen_state(self.garage_door_announce_closing, const.GARAGE_ENTITY_ID, new='closing')
        self.listen_state(self.garage_door_announce_closed, const.GARAGE_ENTITY_ID, new='closed')
        self.listen_state(self.garage_door_debug, const.GARAGE_ENTITY_ID)

        self.listen_event(self.garage_open_event, 'garage_open')
        self.listen_event(self.garage_close_event, 'garage_close')
        self.listen_event(self.garage_open_close_event, 'garage_open_close')

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.close_garage_door, runtime)

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garage_door, runtime)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def garage_open_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        self.lib.log_function_name(start=True)

        self.call_service('timestamp/set', name='garage')
        self.garage_door_open('','','','',{})

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_close_service(self, namespace, domain, service, kwargs) -> None:
        """close the garage"""

        self.lib.log_function_name(start=True)

        self.call_service('timestamp/set', name='garage')
        self.garage_door_close('','','','',{})

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def garage_open_event(self, event, data, kwargs:dict) -> None:

        self.call_service('garage/open')

# -----------------------------------------------------------------------------------

    def garage_close_event(self, event, data, kwargs:dict) -> None:

        self.call_service('garage/close')

# -----------------------------------------------------------------------------------

    def garage_open_close_event(self, event, data, kwargs:dict) -> None:

        self.lib.log_function_name(start=True)

        self.call_service('garage/open')
        time.sleep(30)
        self.call_service('garage/close')

# -----------------------------------------------------------------------------------

    def garage_door_open(self, entity, attribute, old, new, kwargs) -> None:
        """open garage door"""

        self.call_service('cover/open_cover', entity_id=const.GARAGE_ENTITY_ID)
        self.call_service('lighting/garage_on')

# -----------------------------------------------------------------------------------

    def garage_door_close(self, entity, attribute, old, new, kwargs) -> None:
        """close garage door"""

        self.call_service('cover/close_cover', entity_id=const.GARAGE_ENTITY_ID)
        self.call_service('lighting/garage_off')

# -----------------------------------------------------------------------------------

    def garage_door(self, entity, attribute, old, new, kwargs) -> None:
        """listener for garage door"""

        below = self.lib.is_below_horizon()

        if new == 'opening':
            if below:
                self.call_service('lighting/garage_on', seconds=self.lib.interval(self, minutes=30), cb='garage_off')
        elif new == 'closed':
            if below:
                self.call_service('lighting/garage_off', seconds=self.lib.interval(self, minutes=1), cb='garage_off')

        self.garage_door_announce(state=new)

# -----------------------------------------------------------------------------------

    def garage_door_announce_opening(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door opening"""

        self.garage_door(const.GARAGE_ENTITY_ID, 'state', 'closed', 'opening', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_closing(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door closing"""

        self.garage_door(const.GARAGE_ENTITY_ID, 'state', 'open', 'closing', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_open(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now open"""

        self.garage_door(const.GARAGE_ENTITY_ID, 'state', 'opening', 'open', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_closed(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now closed"""

        self.garage_door(const.GARAGE_ENTITY_ID, 'state', 'closing', 'closed', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce(self, **kwargs) -> None:
        """garage door announcement"""

        state = kwargs['state']

        if state == 'opening':
            message = 'The garage door is opening'
        elif state == 'closing':
            message = 'The garage door is closing'
        elif state == 'closed':
            message = 'The garage door is closed'
        elif state == 'open':
            message = 'The garage door is open'
            time.sleep(4.0) # just delay open announcement because this will be triggered immediately after opening
        elif state == 'unavailable':
            return
        else:
            state = self.get_state(const.GARAGE_ENTITY_ID)
            message = f'The garage door is {state}'

        self.call_service('announcer/broadcast', message=message, timestamp='garage')

# -----------------------------------------------------------------------------------

    def is_garage_door_closed(self) -> bool:
        """is garage door closed"""

        state = self.get_state(const.GARAGE_ENTITY_ID)

        return state == 'closed'

# -----------------------------------------------------------------------------------

    def is_garage_door_open(self) -> bool:
        """is garage door open"""

        state = self.get_state(const.GARAGE_ENTITY_ID)

        return state == 'open'

# -----------------------------------------------------------------------------------

    def check_garage_door(self, kwargs) -> None:
        """check garage door state"""

        if self.is_garage_door_open():
            (state, ts) = self.garage_door_debug()
            diff = (datetime.now() - ts).seconds

            if diff >= self.lib.interval(self, minutes=60):
                self.garage_door_announce(state=state)

# -----------------------------------------------------------------------------------

    def close_garage_door(self, kwargs) -> None:
        """close garage door automatically"""

        if self.is_garage_door_open() and self.now_is_between('21:00:00', '06:30:00'):
            self.garage_door_close('','','','',{})

# -----------------------------------------------------------------------------------

    def garage_door_debug(self, entity='', attribute='', old='', new='', kwarg=None) -> tuple:

        state = self.get_state(const.GARAGE_ENTITY_ID)
        ts = self.call_service('timestamp/get', name='garage')
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} kwargs={kwarg} state={state} ts={ts}', level='INFO')

        return state,ts

# -----------------------------------------------------------------------------------
