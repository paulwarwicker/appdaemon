# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

class Location(Hass):
    """This is the documentation for Location"""

    lib = None
    max_entity_id = 'device_tracker.maxine_iphone'
    paul_entity_id = 'device_tracker.paulw_iphone'

    locations = {
        'proximity.ds_smith_fordham': 'DS Smith Fordham',
        'proximity.ds_smith_warboys': 'DS Smith Warboys',
        'proximity.pilates': 'Pilates',
        'proximity.pilates2': 'Pilates Bar Hill',
        'proximity.pilates3': 'Pilates Nothstowe',
        'proximity.karen_wax': 'Karen waxing',
        'proximity.karen_smith': 'Karen Smith',
        'proximity.karen_nail': 'Karen nails',
        'proximity.indian_ocean': 'Indian Ocean',
        'proximity.newmarket': 'Newmarket junction',
        'proximity.bar_hill': 'Bar Hill junction',
        'proximity.village': 'Max is in the village',
        'proximity.sainsbury_eddington': 'Sainsburys Eddington',
        'proximity.waitrose_trumpington': 'Waitrose Trumpington',
        'proximity.morrisons_stives': 'Morrisons St Ives',
        'proximity.gay_kellaway_racing': 'Gay Kellaway Racing',
        'proximity.martyn_tracey': 'Martyn and Tracey',
        'proximity.papworth': 'Papworh',
    }

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        # self.log('-'*72)

        # self.lib = AutomationLib(self)

        # self.listen_event(self.status_event, 'status') # TODO: maybe

        # arrive
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Village', name='Village', location='proximity.village')
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Pilates', name='Pilates', location='proximity.pilates')
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Indian_Ocean', name='Indian_Ocean', location='proximity.indian_ocean', duration=10)
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Karen_Wax', name='Karen_Wax', location='proximity.karen_wax', duration=10)
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Karen_Smith', name='Karen_Smith', location='proximity.karen_smith')
        self.listen_state(self.max_location_detect, self.max_entity_id, new='Gay_Kellaway_Racing', name='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='DS_Smith_Fordham', name='DS_Smith_Fordham', location='proximity.ds_smith_fordham')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='DS_Smith_Warboys', name='DS_Smith_Warboys', location='proximity.ds_smith_warboys')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='Pilates_Class', name='Pilates_Class', location='proximity.pilates_class')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='Bar_Hill', name='Bar_Hill', location='proximity.bar_hill')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='Sainsburys_Eddington', name='Sainsburys_Eddington', location='proximity.sainsburys_eddington')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='Waitrose_Trumpington', name='Waitrose_Trumpington', location='proximity.waitrose_trumpington')
        # self.listen_state(self.max_location_detect, self.max_entity_id, new='Morrisons_StIves', name='Morrisons_StIves', location='proximity.morrisons_stives')

        # leave
        self.listen_state(self.max_location_detect, self.max_entity_id, old='DS_Smith_Fordham', name='DS_Smith_Fordham', location='proximity.ds_smith_fordham')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='DS_Smith_Warboys', name='DS_Smith_Warboys', location='proximity.ds_smith_warboys')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Pilates', name='Pilates', location='proximity.pilates')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Pilates_Class', name='Pilates_Class', location='proximity.pilates_class')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Indian_Ocean', name='Indian_Ocean', location='proximity.indian_ocean', duration=10)
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Karen_Wax', name='Karen_Wax', location='proximity.karen_wax', duration=10)
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Karen_Nails', name='Karen_Nails', location='proximity.karen_nails')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Karen_Smith', name='Karen_Smith', location='proximity.karen_smith')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Martyn_Tracey', name='Martyn_Tracey', location='proximity.martyn_tracey')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Papworth', name='Papworth', location='proximity.papworth')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Gay_Kellaway_Racing', name='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Morrisons_StIves', name='Morrisons_StIves', location='proximity.morrisons_stives')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Sainsburys_Eddington', name='Sainsburys_Eddington', location='proximity.sainsburys_eddington')
        self.listen_state(self.max_location_detect, self.max_entity_id, old='Waitrose_Trumpington', name='Waitrose_Trumpington', location='proximity.waitrose_trumpington')
        # self.listen_state(self.max_location_detect, self.max_entity_id, old='Newmarket', name='Newmarket', location='proximity.newmarket')

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        self.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def max_location_announce(self, entity_id, state, kwargs):

        announce = True
        village = entity_id == 'proximity.village'

        direction = self.get_state("proximity.home", attribute="dir_of_travel")
        self.log(f'\tdirection={direction}', level='DEBUG')

        name = self.locations[entity_id]
        self.log(f'\tentity_id={entity_id} state={state} name={name}')

        if village:
            message = "Max is in the village"
            if direction != 'towards':
                announce = False
        else:
            if state == 'arrive':
                message = f'Max has arrived at {name}'
            else:
                message = f'Max has left {name}'

        if announce:
            self.call_service('announcer/announce', entity_id='media_player.study', message=message)

        if village:
            self.call_service('automation/max_home')

# ---------------------------------------------------------------------------------------------------------

    def max_location_detect(self, entity, attribute, old, new, kwargs):

        name = kwargs['name']
        location = kwargs['location']

        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} name={name} location={location}', level='INFO')

        if new == name:
            self.max_location_announce(location, 'arrive', kwargs)
        elif old == name:
            self.max_location_announce(location, 'leave', kwargs)

# ---------------------------------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs):

        pass

# ---------------------------------------------------------------------------------
