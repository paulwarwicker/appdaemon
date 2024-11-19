# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

class Garage(Hass):
    """Documentation for Garage"""

    lib = None
    PAUL_ENTITY_ID = 'device_tracker.paulw_iphone'
    GARAGE_ENTITY_ID = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'
    BROADCAST_ENTITY_ID = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
    OTHER_ENTITY_ID = ['media_player.study', 'media_player.bedroom_2']

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.register_service('garage/open', self.garage_open_service)
        self.register_service('garage/close', self.garage_close_service)

        self.listen_state(self.garage_door_open, self.PAUL_ENTITY_ID, old='not_home', new='home')
        self.listen_state(self.garage_door_close, self.PAUL_ENTITY_ID, old='home', new='not_home')
        self.listen_state(self.garage_door_announce_open, self.GARAGE_ENTITY_ID, new='open')
        self.listen_state(self.garage_door_announce_opening, self.GARAGE_ENTITY_ID, new='opening')
        self.listen_state(self.garage_door_announce_closing, self.GARAGE_ENTITY_ID, new='closing')
        self.listen_state(self.garage_door_announce_closed, self.GARAGE_ENTITY_ID, new='closed')
        self.listen_state(self.garage_door_debug, self.GARAGE_ENTITY_ID)

        self.listen_event(self.test_garage_open_event, 'test_garage_open')
        self.listen_event(self.test_garage_close_event, 'test_garage_close')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garage_door, runtime)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def garage_open_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        self.garage_door_open('','','','',{})

# -----------------------------------------------------------------------------------

    def garage_close_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        self.garage_door_close('','','','',{})

# -----------------------------------------------------------------------------------

    def garage_door_open(self, entity, attribute, old, new, kwargs) -> None:
        """open garage door"""

        self.call_service('cover/open_cover', entity_id=self.GARAGE_ENTITY_ID)

        if self.lib.is_below_horizon():
            self.call_service('lighting/garage_on')

# -----------------------------------------------------------------------------------

    def garage_door_close(self, entity, attribute, old, new, kwargs) -> None:
        """close garage door"""

        self.call_service('cover/close_cover', entity_id=self.GARAGE_ENTITY_ID)

        if self.lib.is_below_horizon():
            self.call_service('lighting/garage_off')

# -----------------------------------------------------------------------------------

    def garage_door(self, entity, attribute, old, new, kwargs) -> None:
        """listener for garage door"""

        below = self.lib.is_below_horizon()

        if new == 'opening':
            if below:
                self.call_service('lighting/garage_on', seconds=self.lib.interval(minutes=30), cb='garage_off', key='garage')
        elif new == 'closed':
            if below:
                self.call_service('lighting/garage_off', seconds=self.lib.interval(minutes=1), cb='garage_off', key='garage')

        self.garage_door_announce(state=new)

# -----------------------------------------------------------------------------------

    def garage_door_announce_opening(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door opening"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closed', 'opening', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_closing(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door closing"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'open', 'closing', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_open(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now open"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'opening', 'open', {})

# -----------------------------------------------------------------------------------

    def garage_door_announce_closed(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now closed"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closing', 'closed', {})

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
        elif state == 'unavailable':
            return
        else:
            state = self.get_state(self.GARAGE_ENTITY_ID)
            message = f'The garage door is {state}'

        self.call_service('announcer/broadcast', message=message, timestamp='garage')

# -----------------------------------------------------------------------------------

    def is_garage_door_closed(self) -> bool:
        """is garage door closed"""

        state = self.get_state(self.GARAGE_ENTITY_ID)

        return state == 'closed'

# -----------------------------------------------------------------------------------

    def is_garage_door_open(self) -> bool:
        """is garage door open"""

        state = self.get_state(self.GARAGE_ENTITY_ID)

        return state == 'open'

# -----------------------------------------------------------------------------------

    def check_garage_door(self, kwargs) -> None:
        """check garage door state"""

        if self.is_garage_door_open():
            (state, ts) = self.garage_door_debug()
            diff = (datetime.now() - ts).seconds
            if diff >= self.lib.interval(minutes=60):
                self.garage_door_announce(state=state)

# -----------------------------------------------------------------------------------

    def garage_door_debug(self, entity='', attribute='', old='', new='', kwarg={}) -> tuple:

        state = self.get_state(self.GARAGE_ENTITY_ID)
        ts = self.call_service('timestamp/get', name='garage', return_result=True)
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} kwargs={kwarg} state={state} ts={ts}', level='INFO')

        return state,ts

# -----------------------------------------------------------------------------------

    def test_garage_open_event(self, event, data, kwargs:dict) -> None:

        self.call_service('garage/open')

# -----------------------------------------------------------------------------------

    def test_garage_close_event(self, event, data, kwargs:dict) -> None:

        self.call_service('garage/close')

# -----------------------------------------------------------------------------------
