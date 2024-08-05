# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611

class Sonos(hass.Hass):
    """This is the documentation for Automation"""

    broadcast_entity_id = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
    other_entity_id = ['media_player.study', 'media_player.bedroom_2']
    main_entity_id = ['media_player.bathroom', 'media_player.study', 'media_player.bedroom', 'media_player.bedroom_2']
    study_entity_id = 'media_player.study'
    lib = None
    automation = None

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.log('-'*72)

        self.lib = AutomationLib(self)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.join_test_event, 'join_test')

        # set for 07:00
        # self.run_daily(self.sonos_configure1a, '06:59:55') # kitchen, bedroom, bedroom2
        self.run_daily(self.sonos_configuration_2, '06:59:55')
        # set for 07:45
        # bedroom, bedroom2, bathroom
        self.run_daily(self.sonos_configuration_2, '07:44:55')
        # set for 09:00
        self.run_daily(self.sonos_configuration_1, '08:59:55')
        # set for 10:00
        self.run_daily(self.sonos_configuration_1, '09:59:55')
        self.log('\tsonos_configure* registered')

        self.call_service('announcer/initialised', name=self.name.capitalize())

# -------------------------------------------------------------------------------------------------

    # def sonos_unjoin(self, kwargs={}):

    #     self.call_service('media_player/unjoin', entity_id=self.main_entity_id)

    #     # if self.utils.is_weekend():
    #     #     self.log('\tis weekend - ignored', level='DEBUG')
    #     # else:
    #     #     self.call_service('media_player/unjoin', entity_id=self.main_entity_id)

# ---------------------------------------------------------------------------------------------------------

    def sonos_unjoin_all(self, kwargs={}):

        speakers = ['media_player.kitchen', 'media_player.bathroom', 'media_player.bedroom', 'media_player.bedroom_2', 'media_player.study', 'media_player.dining_room']
        volume = {
            'media_player.kitchen': 0.0,
            'media_player.bathroom': 0.0,
            'media_player.bedroom': 0.0,
            'media_player.bedroom_2': 0.0,
            'media_player.study': 0.0,
            'media_player.dining_room': 0.0
        }

        self._sonos_configure(speakers, volume, True, 0, False, False)
        self.call_service('automation/set_downstairs_motion_flag', state=False)

# ---------------------------------------------------------------------------------------------------------

    def _sonos_configure(self, speakers, volume, unjoin, delay, join, check_downstairs_motion):

        if unjoin:
            self.log(f"\tunjoin {speakers}", level='DEBUG')
            self.call_service('media_player/unjoin', entity_id=speakers)

        if join:
            self.log(f"\tjoin {speakers}", level='DEBUG')
            self.call_service('media_player/join', entity_id=speakers[0], group_members=speakers[1:])

        # assume bank holiday and mute
        for speaker in speakers:
            self.call_service('media_player/volume_mute', entity_id=speaker, is_volume_muted=True)

        if not self.utils.is_mock_run():
            self.utils.delay(delay)

        is_not_bank_holiday = not self.utils.is_bank_holiday()
        no_downstairs_motion = True
        if check_downstairs_motion:
            no_downstairs_motion = not self.downstairs_motion_flag
        self.utils.log_debug(f"\tis_not_bank_holiday={is_not_bank_holiday} no_downstairs_motion={no_downstairs_motion}")

        if is_not_bank_holiday and no_downstairs_motion:
            for speaker in speakers:
                self.utils.log_debug(f'\tsetting speaker volume to {volume[speaker]} for {speaker}')
                self.call_service('media_player/volume_set', entity_id=speaker, volume_level=volume[speaker])
                self.call_service('media_player/volume_mute', entity_id=speaker, is_volume_muted=False)

# ---------------------------------------------------------------------------------------------------------

#     def sonos_configure1(self, kwargs={}):

#         speakers = ['media_player.kitchen', 'media_player.bedroom', 'media_player.bedroom_2']
#         volume = {'media_player.kitchen': 0.05, 'media_player.bedroom': 0.05, 'media_player.bedroom_2': 0.3}

#         sonos = self.get_state(entity_id='input_boolean.sonos')
#         state = self.get_state(entity_id='input_boolean.test_1')

#         if sonos == 'off':
#             self._sonos_configure(speakers, volume, True, 0, True, True)
#         else:
#             self.log(f'\t{state}', level='DEBUG')
#             if state == 'on':
#                 self._sonos_configure(speakers, volume, True, 0, True, True)
#             else:
#                 self.call_service('media_player/unjoin', entity_id=speakers)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configuration_1(self, kwargs={}):

        speakers = [
            'media_player.bedroom', 'media_player.bathroom', 'media_player.bedroom_2', ]
        volume = {
            'media_player.bedroom': 0.01, 'media_player.bathroom': 0.3, 'media_player.bedroom_2': 0.3
        }

        # don't bother to check downstairs_motion_flag but mute for bank holiday - checked in sonos_configure
        self._sonos_configure(speakers, volume, True, 7, True, False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configuration_2(self, kwargs={}):

        speakers = ['media_player.bedroom']
        volume = { 'media_player.bedroom': 0.01 }

        # don't bother to check downstairs_motion_flag but mute for bank holiday - checked in sonos_configure
        self._sonos_configure(speakers, volume, True, 7, True, False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configuration_3(self, kwargs={}):

        speakers = ['media_player.kitchen', 'media_player.bedroom', 'media_player.bedroom_2']
        volume = {'media_player.kitchen': 0.05, 'media_player.bedroom': 0.05, 'media_player.bedroom_2': 0.3}

        # don't bother to check downstairs_motion_flag but mute for bank holiday - checked in sonos_configure
        self._sonos_configure(speakers, volume, True, 7, True, False)

# ---------------------------------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs={}):

        status = '\n\n'

        self.log(f'{status}')

# ---------------------------------------------------------------------------------------------------------

    def join_test_event(self, event, data, kwargs={}):

        status = 'join_test'

        self.log(f'{status}')

        # self.sonos_configure1()
        # self.sonos_configure1a()

        # self.utils.delay(5)
        self.sonos_configuration_1()
        self.utils.delay(5)
        self.sonos_unjoin_all()
        self.sonos_configuration_2()
        self.utils.delay(5)
        self.sonos_unjoin_all()
        self.sonos_configuration_3()
        self.utils.delay(5)
        self.sonos_unjoin_all()

# ---------------------------------------------------------------------------------------------------------

    def is_playing(self, entity_id=None):

        if entity_id is None:
            entity_id, volume = self.utils.get_entity_id()

        state = self.get_state(entity_id=entity_id, attribute="state")
        return state == 'playing'

# ---------------------------------------------------------------------------------------------------------
