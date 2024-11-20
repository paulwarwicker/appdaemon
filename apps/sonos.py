# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

class Sonos(Hass):
    """Documentation for Sonos"""

    lib = None
    ALL_ENTITIES = ['media_player.kitchen', 'media_player.bathroom', 'media_player.bedroom', 'media_player.study', 'media_player.dining_room']

# -----------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.lib = AutomationLib(self)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.join_test_event, 'join_test')

        self.register_service('sonos/mute_all', self.mute_all)
        self.register_service('sonos/unjoin_all', self.unjoin_all)
        self.register_service('sonos/unjoin_entity', self.unjoin_entity)
        self.register_service('sonos/set_configuration', self.set_configuration)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def mute_all(self, kwargs):

        self._configure(self.ALL_ENTITIES, {}, 0, True, False, True, False)

# -----------------------------------------------------------------------------------

    def _configure(self, speakers: list, volume: list, delay: int, unjoin: bool, join: bool, mute: bool, check_downstairs_motion: bool):


        # is_not_bank_holiday = not self.lib.is_bank_holiday()
        is_bank_holiday = self.lib.is_bank_holiday()

        if self.lib.get_verbose_debug():
            self.log(f"\tis_bank_holiday={is_bank_holiday}", level='DEBUG')

        if unjoin:
            self.log(f"\tunjoin {speakers}", level='DEBUG')
            self.call_service('media_player/unjoin', entity_id=speakers)

        if join:
            self.log(f"\tjoin {speakers}", level='DEBUG')
            self.call_service('media_player/join', entity_id=speakers[0], group_members=speakers[1:])

        if mute:
            self.log(f"\tmute {speakers}", level='DEBUG')

        # assume bank holiday and mute
        self.call_service('media_player/volume_mute', entity_id=speakers, is_volume_muted=True)

        if mute or is_bank_holiday:
            return

        if not is_bank_holiday:
            for speaker in speakers:
                self.log(f'\tsetting speaker volume to {volume[speaker]} for {speaker}', level='DEBUG')
                self.call_service('media_player/volume_set', entity_id=speaker, volume_level=volume[speaker])
                self.call_service('media_player/volume_mute', entity_id=speaker, is_volume_muted=False)

# -----------------------------------------------------------------------------------

    def configuration_1(self, kwargs):

        speakers = ['media_player.bedroom', 'media_player.bathroom']
        volume = {
            'media_player.bedroom': 0.01,
            'media_player.bathroom': 0.3,
        }

        self._configure(speakers, volume, 7, True, True, False, False)

# -----------------------------------------------------------------------------------

    def configuration_2(self, kwargs):
        # bedroom with join

        speakers = ['media_player.bedroom']
        volume = { 'media_player.bedroom': 0.01 }

        self._configure(speakers, volume, 7, True, True, False, False)

# -----------------------------------------------------------------------------------

    def configuration_3(self, kwargs):

        speakers = ['media_player.kitchen', 'media_player.bedroom']
        volume = {'media_player.kitchen': 0.05, 'media_player.bedroom': 0.05}

        self._configure(speakers, volume, 7, True, True, False, False)

# -----------------------------------------------------------------------------------

    def configuration_4(self, kwargs):
        # bedroom no join

        speakers = ['media_player.bedroom']
        volume = { 'media_player.bedroom': 0.01 }

        self._configure(speakers, volume, 7, True, False, False, False)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs):

        status = '\n\n'

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    async def join_test_event(self, event, data, kwargs):

        print(100)
        await self.unjoin_all('','','',{})
        self.lib.delay(2)
        self.configuration_1({})
        self.lib.delay(2)
        await self.unjoin_all('','','',{})
        self.lib.delay(2)
        self.configuration_2({})
        self.lib.delay(2)
        await self.unjoin_all('','','',{})
        self.lib.delay(2)
        self.configuration_3({})
        self.lib.delay(2)
        await self.unjoin_all('','','',{})
        self.lib.delay(2)
        self.configuration_4({})
        self.lib.delay(2)
        await self.unjoin_all('','','',{})
        print(200)

# -----------------------------------------------------------------------------------

    async def unjoin_all(self, namespace, domain, service, kwargs) -> None:

        self._configure(self.ALL_ENTITIES, {}, 0, True, False, True, False)

# -----------------------------------------------------------------------------------

    async def unjoin_entity(self, namespace, domain, service, kwargs) -> None:

        entity_id = kwargs['entity_id']
        self.call_service('media_player/unjoin', entity_id=entity_id)

# -----------------------------------------------------------------------------------

    async def set_configuration(self, namespace, domain, service, kwargs) -> None:

        config = kwargs['config']

        if config == '1':
            self.configuration_1({})
        elif config == '2':
            self.configuration_2({})
        elif config == '3':
            self.configuration_3({})
        elif config == '4':
            self.configuration_4({})

# -----------------------------------------------------------------------------------
