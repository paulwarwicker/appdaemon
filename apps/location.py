# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Location(Hass):
    """This is the documentation for Location"""

    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.register_service('location/max_home', self.max_home_service)
        self.register_service('location/paul_home', self.paul_home_service)

        # arrive
        self.listen_state(self.paul_location_detect, self.const.PAUL_ENTITY_ID, new='home')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Home', location='proximity.home')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Village', location='proximity.village')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Pilates', location='proximity.pilates')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Pilates2', location='proximity.pilates2')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Pilates3', location='proximity.pilates3')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Pilates4', location='proximity.pilates4')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Indian_Ocean', location='proximity.indian_ocean', duration=10)
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Karen_Wax', location='proximity.karen_wax', duration=10)
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Karen_Smith', location='proximity.karen_smith')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        # self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Bar_Hill', location='proximity.bar_hill')
        # self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, new='Newmarket', location='proximity.newmarket')

        # leave
        self.listen_state(self.paul_location_detect, self.const.PAUL_ENTITY_ID, new='not_home')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='DS_Smith_Fordham', location='proximity.ds_smith_fordham')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='DS_Smith_Warboys', location='proximity.ds_smith_warboys')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Pilates', location='proximity.pilates')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Pilates2', location='proximity.pilates2')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Pilates3', location='proximity.pilates3')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Pilates4', location='proximity.pilates4')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Indian_Ocean', location='proximity.indian_ocean', duration=10)
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Karen_Wax', location='proximity.karen_wax', duration=10)
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Karen_Nails', location='proximity.karen_nails')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Karen_Smith', location='proximity.karen_smith')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Martyn_Tracey', location='proximity.martyn_tracey')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Papworth', location='proximity.papworth')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Morrisons_StIves', location='proximity.morrisons_stives')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Sainsburys_Eddington', location='proximity.sainsburys_eddington')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Waitrose_Trumpington', location='proximity.waitrose_trumpington')
        self.listen_state(self.max_location_detect, self.const.MAX_ENTITY_ID, old='Jollop_Place', location='proximity.jollop_place')

        self.listen_event(self.test_max_home_event, 'max_home')
        self.listen_event(self.test_paul_home_event, 'paul_home')
        self.listen_event(self.test_welcome_lights_event, 'welcome_lights')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def max_home_service(self, namespace, domain, service, kwargs) -> None:
        """max home"""

        self.lib.log_function_name(True, True)

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off', seconds=5*60, key='welcome_lights')

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def paul_home_service(self, namespace, domain, service, kwargs) -> None:
        """paul home"""

        self.lib.log_function_name(True, True)

        self.call_service('garage/open')

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def max_location_announce(self, entity_id, state, kwargs):

        announce = True
        village = entity_id == 'proximity.village'
        home = entity_id == 'proximity.home'
        direction = self.get_state('sensor.home_maxine_direction_of_travel')
        name = self.const.LOCATIONS[entity_id][1]

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'\tentity_id={entity_id} state={state} name={name} direction={direction} village={village} home={home}', level='DEBUG')

        if village:
            message = "Max is in the village"
            if direction != 'towards':
                announce = False
        elif home:
            message = "Max is home"
        else:
            if state == 'arrive':
                message = f'Max has arrived at {name}'
            else:
                message = f'Max has left {name}'

        if announce:
            self.call_service('announcer/announce', entity_id='media_player.study', message=message, force=True)

        if village:
            self.call_service('location/max_home')

# -----------------------------------------------------------------------------------

    def max_location_detect(self, entity_id, attribute, old, new, kwargs):

        self.lib.log_function_name(True, True)

        location = kwargs['location']
        location_entity_id = (self.const.LOCATIONS[location][0]).lower()

        verbose = self.lib.get_verbose_debug()

        if verbose:
            # 2024-11-29 17:59:07.465115 INFO location:       entity=device_tracker.maxine_iphone attribute=state old=DS_Smith_Fordham new=not_home location=proximity.ds_smith_fordham
            self.log(f'\tmax location location={location} location_entity_id={location_entity_id} attribute={attribute} old={old} new={new}', level='INFO')

        if new.lower() == location_entity_id:
            self.max_location_announce(location, 'arrive', kwargs)
        elif old.lower() == location_entity_id:
            self.max_location_announce(location, 'leave', kwargs)

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def paul_location_detect(self, entity_id, attribute, old, new, kwargs):

        self.lib.log_function_name(True, True)

        if self.lib.get_verbose_debug():
            self.log(f'\tpaul location entity_id={entity_id} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        if new == 'home':
            self.call_service('garage/open')

        if new == 'not_home':
            self.call_service('garage/close')

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs):

        pass

# -----------------------------------------------------------------------------------

    def test_max_home_event(self, event, data, kwargs):

        self.call_service('location/max_home')

# -----------------------------------------------------------------------------------

    def test_paul_home_event(self, event, data, kwargs):

        self.call_service('location/paul_home')

# -----------------------------------------------------------------------------------

    def test_welcome_lights_event(self, event, data, kwargs):

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off', seconds=10, key='welcome_lights')

# -----------------------------------------------------------------------------------
