# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import time
import pprint
import textwrap
from io import StringIO
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611

class Sonos(Hass):
    """Documentation for Sonos"""

    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.snooze_event, 'snooze')
        self.listen_event(self.play_thing_event, 'play_thing')
        self.listen_event(self.join_test_event, 'join_test')

        self.register_service('sonos/snooze', self.snooze_service)
        self.register_service('sonos/mute_all', self.mute_all_service)
        self.register_service('sonos/unjoin_all', self.unjoin_all_service)
        self.register_service('sonos/play_media2', self.play_media2_service)
        self.register_service('sonos/unjoin_entity', self.unjoin_entity_service)
        self.register_service('sonos/mute_unjoin_all', self.mute_unjoin_all_service)
        self.register_service('sonos/set_configuration', self.set_configuration_service)

        self.listen_event(self.test_event, 'test')
        self.listen_event(self.test_sonos_event, 'sonos')
        self.listen_event(self.mute_all_event, 'mute_all')
        self.listen_event(self.unjoin_all_event, 'unjoin_all')
        self.listen_event(self.play_hallway_event, 'play_hallway')
        self.listen_event(self.stop_hallway_event, 'stop_hallway')

        self.run_daily(self.play_hallway, '07:45:00')
        self.run_daily(self.stop_hallway, '21:00:00')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    async def mute_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(self.const.BROADCAST_ENTITY_ID, {}, unjoin=False, join=False, mute=True)

# -----------------------------------------------------------------------------------

    async def unjoin_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(self.const.BROADCAST_ENTITY_ID, {}, unjoin=True, join=False, mute=False)

# -----------------------------------------------------------------------------------

    async def mute_unjoin_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(self.const.BROADCAST_ENTITY_ID, {}, unjoin=True, join=False, mute=True)

# -----------------------------------------------------------------------------------

    async def unjoin_entity_service(self, namespace, domain, service, kwargs) -> None:

        entity_id = kwargs['entity_id']

        self.call_service('media_player/unjoin', entity_id=entity_id)

# -----------------------------------------------------------------------------------

    async def snooze_service(self, namespace, domain, service, kwargs) -> None:

        self.lib.log_function_name(True, True)

        entity_id = kwargs.get('entity_id', None)

        if entity_id is None:
            return

        # playing = self.lib.is_playing(entity_id)
        all_attributes = await self.get_state(entity_id=entity_id, attribute="all")

        self.log(f'{entity_id} {all_attributes}')

        attributes = all_attributes.get('attributes', None)

        # if attributes is None:
        #     return

        volume_level = attributes.get('volume_level', None)
        media_content_id = attributes.get('media_content_id', None)

        self.log(f'{entity_id} {volume_level} {media_content_id}')

        self.call_service('media_player/media_stop', entity_id=entity_id)

        self.run_in(self.play_thing, 30, entity_id=entity_id, volume_level=0.5, media_content_id=media_content_id)

# -----------------------------------------------------------------------------------

    async def play_media2_service(self, namespace, domain, service, kwargs) -> None:

        entity_id = kwargs.get('entity_id', None)
        volume_level = kwargs.get('volume_level', None)
        media_content_id = kwargs.get('media_content_id', None)

# -----------------------------------------------------------------------------------

    async def set_configuration_service(self, namespace, domain, service, kwargs) -> None:

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

    def status_event(self, event, data, kwargs):

        status = '\n'

        for entity_id in self.const.BROADCAST_ENTITY_ID:
            playing = self.lib.is_playing(entity_id)
            status += f'\n\tentity_id={entity_id} is_playing={playing}\n\n'
            attributes = self.get_state(entity_id=entity_id, attribute="all")
            s = StringIO()
            pprint.pprint(attributes, s, indent=3, width=1, compact=True)
            status += textwrap.indent(s.getvalue(), '        ')

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    def play_hallway_event(self, event, data, kwargs):

        self.play_hallway({})

# -----------------------------------------------------------------------------------

    def stop_hallway_event(self, event, data, kwargs):

        self.lib.log_function_name(True, True)
        self.stop_hallway({})

# -----------------------------------------------------------------------------------

    async def snooze_event(self, event, data, kwargs):

        await self.snooze_service('', '', '', {'entity_id':self.const.STUDY_SPEAKER})

# -----------------------------------------------------------------------------------

    async def mute_all_event(self, event, data, kwargs):

        await self.mute_all_service('', '', '', {})

# -----------------------------------------------------------------------------------

    async def unjoin_all_event(self, event, data, kwargs):

        await self.unjoin_all_service('', '', '', {})

# -----------------------------------------------------------------------------------

    async def join_test_event(self, event, data, kwargs):

        s=5
        print(100)
        await self.unjoin_all_service('', '', '', {})
        await self.sleep(s)
        await self.configuration_1({})
        await self.sleep(s)
        await self.unjoin_all_service('', '', '', {})
        await self.sleep(s)
        await self.configuration_2({})
        await self.sleep(s)
        await self.unjoin_all_service('', '', '', {})
        await self.sleep(s)
        await self.configuration_3({})
        await self.sleep(s)
        await self.unjoin_all_service('', '', '', {})
        await self.sleep(s)
        await self.configuration_4({})
        await self.sleep(s)
        await self.unjoin_all_service('', '', '', {})
        print(200)

# -----------------------------------------------------------------------------------

    def test_sonos_event(self, event, data, kwargs):

        entity_id = self.const.BEDROOM_SPEAKER

        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
        self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0.01)
        self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')
        self.call_service('media_player/play_media',
                            entity_id=entity_id,
                            media_content_type='music',
                            # media_content_id='aac://http://prem2.radiotunes.com:80/popchristmas?5fba91be81f6da5b573f89c1',
                            media_content_id='aac://http://prem2.zenradio.com:80/zrsoundsofrain_aac?5fba91be81f6da5b573f89c1',
                        )

# -----------------------------------------------------------------------------------

    def test_event(self, event, data, kwargs):

        self.log(f'study_playing={self.lib.is_playing(self.const.STUDY_SPEAKER)}')
        self.log(f'bedroom_playing={self.lib.is_playing(self.const.BEDROOM_SPEAKER)}')
        self.log(f'bedroom2_playing={self.lib.is_playing(self.const.HALLWAY_SPEAKER)}')

# -----------------------------------------------------------------------------------

    def play_thing_event(self, event, data, kwargs):

        self.play_thing({'entity_id': self.const.STUDY_SPEAKER, 'volume_level': 0.5, 'media_content_id': self.const.NORMAL_ALARM[0]})

# -----------------------------------------------------------------------------------

    def play_thing_sync(self, kwargs):

        entity_id = kwargs['entity_id']
        volume_level = kwargs['volume_level']
        media_content_id = kwargs['media_content_id']

        for _ in range(5):
            self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
            self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume_level)
            self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')
            self.call_service('media_player/play_media',
                            entity_id=entity_id,
                            media_content_type='music',
                            media_content_id=media_content_id)

# -----------------------------------------------------------------------------------

    def play_hallway(self, kwargs):

        self.play_thing({'entity_id': self.const.HALLWAY_SPEAKER, 'volume_level': 0.02, 'media_content_id': self.const.BOSSANOVA_STREAM, 'delay': False})

# -----------------------------------------------------------------------------------

    def stop_hallway(self, kwargs):

        self.call_service('media_player/media_stop', entity_id=self.const.HALLWAY_SPEAKER)

# -----------------------------------------------------------------------------------

    def _configure(self, speakers: list, volumes: list, unjoin: bool, join: bool, mute: bool):

        default_volume = 0.01
        xmute = not True
        is_bank_holiday = self.lib.is_bank_holiday()

        if self.lib.get_verbose_debug():
            self.log(f"\tis_bank_holiday={is_bank_holiday}", level='DEBUG')

        if unjoin:
            self.log(f"\tunjoin {speakers}", level='DEBUG')
            self.call_service('media_player/unjoin', entity_id=speakers)

        if join:
            self.log(f"\tjoin {speakers}", level='DEBUG')
            self.call_service('media_player/join', entity_id=speakers[0], group_members=speakers[1:])

        if mute or is_bank_holiday:
            self.log(f"\tmute {speakers}", level='DEBUG')
            if xmute:
                self.call_service('media_player/volume_mute', entity_id=speakers, is_volume_muted=True)
            else:
                self.call_service('media_player/volume_mute', entity_id=speakers, is_volume_muted=False)
                self.call_service('media_player/volume_set', entity_id=speakers, volume_level=default_volume)
            return

        for speaker in speakers:
            volume =  volumes.get(speaker, None if xmute else default_volume)
            if volume is not None:
                self.log(f'\tsetting speaker volume to {volume} for {speaker}', level='DEBUG')
                self.call_service('media_player/volume_set', entity_id=speaker, volume_level=volume)

# -----------------------------------------------------------------------------------

    async def configuration_1(self, kwargs):
        # bedroom/bathroom

        speakers = [self.const.BEDROOM_SPEAKER, self.const.BATHROOM_SPEAKER]
        volume = {
            'media_player.bedroom': 0.01,
            'media_player.bathroom': 0.3,
        }

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    async def configuration_2(self, kwargs):
        # bedroom with join

        speakers = [self.const.BEDROOM_SPEAKER]
        volume = {self.const.BEDROOM_SPEAKER: 0.01}

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    async def configuration_3(self, kwargs):
        # bedroom no join

        speakers = [self.const.BEDROOM_SPEAKER]
        volume = {self.const.BEDROOM_SPEAKER: 0.01}

        self._configure(speakers, volume, unjoin=True, join=False, mute=False)

# -----------------------------------------------------------------------------------

    async def configuration_4(self, kwargs):
        # bedroom/kitchen

        speakers = [self.const.KITCHEN_SPEAKER, self.const.BEDROOM_SPEAKER]
        volume = {self.const.KITCHEN_SPEAKER: 0.05, self.const.BEDROOM_SPEAKER: 0.05}

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    def play_thing(self, kwargs):

        self.lib.log_function_name(True, True)

        entity_id = kwargs['entity_id']
        volume_level = kwargs.get('volume_level', 0.15)
        media_content_id = kwargs['media_content_id']
        delay = kwargs.get('delay', True)

        self.call_service('sonos/unjoin_entity', entity_id=entity_id)
        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
        self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0)
        self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'\tentity_id={entity_id} media_content_id={media_content_id}', level='DEBUG')

        for attempt in range(self.const.ATTEMPTS):
            state = self.get_state(entity_id, attribute="state")
            if not state == 'playing':
                if verbose:
                    self.log(f'state={state} attempt={attempt} media={media_content_id} entity_id={entity_id}', level='DEBUG')
                self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
                self.call_service('media_player/play_media', entity_id=entity_id, media_content_type="music", media_content_id=media_content_id)
                time.sleep(1.0)
            else:
                break

        divisor = 100
        target_volume = int(volume_level * 100)  # deal in integers for convenience
        span = 4 * divisor # 4s incremnets

        volume = 0
        incr_volume = target_volume * (2.5/100.0)  # 2.5% increase in volume
        sleeptime = span/divisor

        if delay:
            while volume < target_volume:
                volume += incr_volume
                self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume/100.0)
                time.sleep(sleeptime)
        else:
            self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume_level)

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------
