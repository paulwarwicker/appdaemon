# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Garage(Hass):
    """Documentation for Garage"""

    lib = None
    PAUL_ENTITY_ID = 'device_tracker.paulw_iphone'
    GARAGE_ENTITY_ID = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'
    BROADCAST_ENTITY_ID = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
    OTHER_ENTITY_ID = ['media_player.study', 'media_player.bedroom_2']

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # self.log('-'*72)

        self.lib = AutomationLib(self)

        self.register_service('garage/open', self.garage_open_service)
        self.register_service('garage/close', self.garage_close_service)

        # self.register_service('garage/status', self.garage_status_service)
        # self.listen_event(self.status_event, 'status')

        self.listen_state(self.garage_door_open, self.PAUL_ENTITY_ID, old='not_home', new='home')
        self.listen_state(self.garage_door_close, self.PAUL_ENTITY_ID, old='home', new='not_home')
        self.listen_state(self.garage_door_announce_open, self.GARAGE_ENTITY_ID, new='open')
        self.listen_state(self.garage_door_announce_opening, self.GARAGE_ENTITY_ID, new='opening')
        self.listen_state(self.garage_door_announce_closing, self.GARAGE_ENTITY_ID, new='closing')
        self.listen_state(self.garage_door_announce_closed, self.GARAGE_ENTITY_ID, new='closed')
        self.listen_state(self.garage_door_debug, self.GARAGE_ENTITY_ID)

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garage_door, runtime)

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        self.log('initialised')


# ---------------------------------------------------------------------------------------------------------

    def garage_open_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        self.garage_door_open()

# ---------------------------------------------------------------------------------------------------------

    def garage_close_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        self.garage_door_close()

# ---------------------------------------------------------------------------------------------------------

    def garage_door_open(self, entity='', attribute='', old='', new='', kwargs={}) -> None:
        """open garage door"""

        self.call_service('cover/open_cover', entity_id=self.GARAGE_ENTITY_ID)

        if self.lib.is_below_horizon(): # FIXME: call lighting service
            # self.garage_door_lights(on=True)
            self.call_service('scene/activate', entity_id='scene.garage_open')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_close(self, entity='', attribute='', old='', new='', kwargs={}) -> None:
        """close garage door"""

        self.call_service('cover/close_cover', entity_id=self.GARAGE_ENTITY_ID)

        if self.lib.is_below_horizon(): # FIXME: call lighting service
        #     self.garage_door_lights(on=False)
            self.call_service('scene/activate', entity_id='scene.garage_close')

# ---------------------------------------------------------------------------------------------------------

    def garage_door(self, entity, attribute, old, new, kwargs={}) -> None:
        """listener for garage door"""

        below = self.lib.is_below_horizon()

        if new == 'opening':
            if below:
                pass # FIXME: call lighting service
                # self.garage_door_lights(on=True)
        elif new == 'closed':
            if below:
                pass # FIXME: call timer service
                # seconds = self.lib.interval(minutes=2)
                # self.log(f'\tstart garage_door_light timer for {seconds:d}s', level='DEBUG')
                # self.run_in(self.garage_door_lights_off, seconds)

        self.garage_door_announce(state=new)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_opening(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door opening"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closed', 'opening')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closing(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door closing"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'open', 'closing')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_open(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now open"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'opening', 'open')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closed(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now closed"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closing', 'closed')

# ---------------------------------------------------------------------------------------------------------

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

        self.call_service("announcer/broadcast", broadcast_entity_id=self.BROADCAST_ENTITY_ID, other_entity_id=self.OTHER_ENTITY_ID, message=message, volume=0.5, snapshot=True)
        # self.call_service('announcer/desktop_notification', message=message)
        self.call_service('timestamp/set', name='garage')

# ---------------------------------------------------------------------------------------------------------

    # def is_garage_door_closed(self) -> bool:
    #     """is garage door closed"""

    #     state = self.get_state(self.GARAGE_ENTITY_ID)

    #     return state == 'closed'

# ---------------------------------------------------------------------------------------------------------

    def check_garage_door(self, kwargs={}) -> None:
        """check garage door state"""

        state = self.get_state(self.GARAGE_ENTITY_ID)

        if state != 'closed':
            ts = self.call_service('timestamp/get_timestamp', name='garage', return_result=True)
            self.log(f'\tGarage door is {state} ts={ts}', level='WARNING')
            diff = (datetime.now() - ts).seconds
            if diff >= self.lib.interval(minutes=60):
                self.garage_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_debug(self, entity, attribute, old, new, kwarg) -> None:

        state = self.get_state(self.GARAGE_ENTITY_ID)
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# -------------------------------------------------------------------------------------------------
