# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import pprint
import random
import textwrap
from io import StringIO

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

# # Cancel any existing playback task
# if hasattr(self, "playback_task") and self.playback_task is not None:

class Sonos(Hass):
    """Documentation for Sonos"""

    task = None
    timer = None
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self):
        """Documentation for sonos app"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.register_service('sonos/snooze', self.snooze_service)
        self.register_service('sonos/mute_all', self.mute_all_service)
        self.register_service('sonos/unjoin_all', self.unjoin_all_service)
        self.register_service('sonos/unjoin_entity', self.unjoin_entity_service)
        self.register_service('sonos/mute_unjoin_all', self.mute_unjoin_all_service)
        self.register_service('sonos/set_configuration', self.set_configuration_service)
        # self.register_service('sonos/stop_bedroom', self.stop_service, entity_id=const.BEDROOM_SPEAKER)
        # self.register_service('sonos/stop_hallway', self.stop_service, entity_id=const.HALLWAY_SPEAKER)
        # self.register_service('sonos/stop_study', self.stop_service, entity_id=const.STUDY_SPEAKER)
        self.register_service('sonos/stop_bedroom', self.stop_bedroom_service)
        self.register_service('sonos/stop_hallway', self.stop_hallway_service)
        self.register_service('sonos/stop_study', self.stop_study_service)
        self.register_service('sonos/play_thing', self.play_thing_service)
        self.register_service('sonos/stop', self.stop_service)

        self.listen_event(self.status_event, 'status')
        # self.listen_event(self.snooze_event, 'snooze')
        self.listen_event(self.snooze_event, 'snooze10', seconds=10*60)
        self.listen_event(self.snooze_event, 'snooze30', seconds=30*60)
        self.listen_event(self.play_thing_event, 'play_thing')
        self.listen_event(self.join_test_event, 'join_test')
        self.listen_event(self.test_event, 'test')
        self.listen_event(self.test_sonos_event, 'sonos')
        self.listen_event(self.mute_all_event, 'mute_all')
        self.listen_event(self.unjoin_all_event, 'unjoin_all')
        self.listen_event(self.play_hallway_event, 'play_hallway')
        self.listen_event(self.stop_hallway_event, 'stop_hallway')
        self.listen_event(self.stop_bedroom_event, 'stop_bedroom')
        self.listen_event(self.stop_study_event, 'stop_study')

        self.run_daily(self.play_hallway, '08:00:00')
        self.run_daily(self.stop_hallway, '21:00:00')
        # self.run_daily(self.play_hallway, '00:17:00')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def mute_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(const.BROADCAST_ENTITY_ID, {}, unjoin=False, join=False, mute=True)

# -----------------------------------------------------------------------------------

    def unjoin_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(const.BROADCAST_ENTITY_ID, {}, unjoin=True, join=False, mute=False)

# -----------------------------------------------------------------------------------

    def mute_unjoin_all_service(self, namespace, domain, service, kwargs) -> None:

        self._configure(const.BROADCAST_ENTITY_ID, {}, unjoin=True, join=False, mute=True)

# -----------------------------------------------------------------------------------

    def unjoin_entity_service(self, namespace, domain, service, kwargs) -> None:

        entity_id = kwargs['entity_id']

        self.call_service('media_player/unjoin', entity_id=entity_id)

# -----------------------------------------------------------------------------------

    async def snooze_service(self, namespace, domain, service, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        entity_id = kwargs.get('entity_id', None)
        seconds = kwargs.get('seconds', 10*60)

        if entity_id is None:
            return

        # ts = self.call_service('timestamp/get', name='snooze')

        self.call_service('timestamp/set', name='snooze')

        all_attributes = await self.get_state(entity_id=entity_id, attribute="all")

        self.log(f'{entity_id} {all_attributes}')

        attributes = all_attributes.get('attributes', None)
        volume_level = attributes.get('volume_level', None)
        media_content_id = attributes.get('media_content_id', None)
        media_content_type = attributes.get('media_content_type', None)
        shuffle = attributes.get('shuffle', None)
        repeat = attributes.get('repeat', None)

        volume_level = const.ALARM_VOLUME

        self.log(f'entity_id={entity_id} volume_level={volume_level}', level='DEBUG')
        self.log(f'media_content_id={media_content_id} media_content_type={media_content_type}', level='DEBUG')
        self.log(f'shuffle={shuffle} repeat={repeat}', level='DEBUG')

        self.call_service('media_player/media_stop', entity_id=entity_id)
        # self.call_service('media_player/pause', entity_id=entity_id)

        # if self.task is not None and not self.task.done():
        #     self.log("Cancelling existing playback task", level="WARNING")
        #     self.task.cancel()

        kwargs = {
            'entity_id': entity_id,
            'volume_level': volume_level,
            'media_content_id': media_content_id,
            'media_content_type': media_content_type,
            'delayed': True,
            'set_shuffle': shuffle,
            'set_repeat': repeat
        }

        # await self.sleep(seconds)

        # self.task = self.create_task(self.play_thing(**kwargs))
        # self.log(f"Started new playback task: task={self.task}", level="DEBUG")

        self.run_in(self.play_thing, seconds, **kwargs)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    async def play_thing_service(self, namespace, domain, service, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        # if self.task is not None and not self.task.done():
        #     self.log("Cancelling existing playback task", level="WARNING")
        #     self.task.cancel()

        # self.task = self.create_task(self.play_thing(**kwargs))
        # self.log(f"Started new playback task: task={self.task}", level="DEBUG")

        self.run_in(self.play_thing, 0, **kwargs)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    async def play_thing(self, **kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        entity_id = kwargs.get('entity_id')
        volume_level = kwargs.get('volume_level', const.ALARM_VOLUME)
        ramp_time = kwargs.get('ramp_time', const.RAMP_TIME)
        media_content_id = kwargs.get('media_content_id')
        delayed = kwargs.get('delayed', True)
        shuffle = kwargs.get("set_shuffle", False)
        repeat = kwargs.get("set_repeat", "all")
        media_content_type = kwargs.get("media_content_type", "music")

        if not entity_id or not media_content_id:
            self.log("entity_id or media_content_id missing", level="ERROR")
            return

        self.log(f"entity_id={entity_id}, media_content_id={media_content_id}, volume_level={volume_level}, ramp_time={ramp_time}", level="DEBUG") # original code

        await self.call_service("sonos/unjoin_entity", entity_id=entity_id)
        await self.call_service("media_player/media_stop", entity_id=entity_id)
        await self.sleep(1.0)
        await self.call_service("media_player/volume_mute", entity_id=entity_id, is_volume_muted=False)
        await self.call_service("media_player/volume_set", entity_id=entity_id, volume_level=0)
        await self.call_service("media_player/repeat_set", entity_id=entity_id, repeat=repeat)
        await self.call_service("media_player/shuffle_set", entity_id=entity_id, shuffle=shuffle)

        for attempt in range(const.ATTEMPTS):
            state = await self.get_state(entity_id, attribute="state")

            if state != "playing":
                self.log(f"attempt {attempt+1}: state={state}", level="DEBUG")
                await self.call_service("media_player/play_media",
                                        entity_id=entity_id,
                                        media_content_type=media_content_type,
                                        media_content_id=media_content_id)
                await self.sleep(0.5)
            else:
                break

        if delayed:
            factor = 100
            volume = 0
            target_volume = int(volume_level * factor)  # deal in integers for convenience

            # higher is coarser can be <1 (and decimal)
            # a value of 1 and volume of 0.3 gives 30 steps
            smoothness = 1
            steps = max(1, int(target_volume / smoothness))
            step_volume = target_volume / steps
            step_delay = ramp_time / steps
            self.log(f"steps={steps} step_volume={step_volume} step_delay={step_delay:.3f}", level="DEBUG")

            for i in range(steps):
                volume += step_volume
                self.log(f"volume step {i+1}/{steps}: setting volume to {volume} ({volume/factor:.3f})", level="DEBUG")
                await self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume/100.0)
                await self.sleep(step_delay)

            await self.sleep(ramp_time / 2.0)  # Wait for half the ramp time before setting final volume of half the target_volume

            for i in range(steps):
                volume -= (step_volume / 2)
                self.log(f"volume step {i+1}/{steps}: setting volume to {volume} ({volume/factor:.3f})", level="DEBUG")
                await self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume/100.0)
                await self.sleep(step_delay)
        else:
            await self.call_service("media_player/volume_set", entity_id=entity_id, volume_level=volume_level)

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def set_configuration_service(self, namespace, domain, service, kwargs) -> None:

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

    def stop_service(self, namespace, domain, service, kwargs) -> None:

        self.lib.log_function_name(start=True, force=True)

        entity_id = kwargs.get('entity_id', None)

        if entity_id is not None:
            self.call_service('media_player/media_stop', entity_id=entity_id)
        else:
            self.log('stop_service: entity_id is None', level='ERROR')

        self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def stop_bedroom_service(self, namespace, domain, service, kwargs) -> None:

        self.call_service('sonos/stop', entity_id=const.BEDROOM_SPEAKER)

# -----------------------------------------------------------------------------------

    def stop_hallway_service(self, namespace, domain, service, kwargs) -> None:

        self.call_service('sonos/stop', entity_id=const.HALLWAY_SPEAKER)

# -----------------------------------------------------------------------------------

    def stop_study_service(self, namespace, domain, service, kwargs) -> None:

        self.call_service('sonos/stop', entity_id=const.STUDY_SPEAKER)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs):

        status = '\n'

        for entity_id in const.BROADCAST_ENTITY_ID:
            playing = self.lib.is_playing(entity_id)
            status += f'\n\tentity_id={entity_id} is_playing={playing}\n\n'
            attributes = self.get_state(entity_id=entity_id, attribute="all")
            s = StringIO()
            pprint.pprint(attributes, s, indent=3, width=1, compact=True)
            status += textwrap.indent(s.getvalue(), '        ')

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    def play_hallway_event(self, event, data, kwargs):

        self.play_spotify({
            'entity_id': const.STUDY_SPEAKER,
            'volume_level': 0.2,
            'media_content_id': const.SUMMER_HITS_PLAYLIST,
            # 'media_content_id': const.SUMMER_VIBES_ALBUM,
            'delayed': False,
            'shuffle': True
            })

# -----------------------------------------------------------------------------------

    def stop_hallway_event(self, event, data, kwargs):

        self.call_service('sonos/stop_hallway')

# -----------------------------------------------------------------------------------

    def stop_bedroom_event(self, event, data, kwargs):

        self.call_service('sonos/stop_bedroom')

# -----------------------------------------------------------------------------------

    def stop_study_event(self, event, data, kwargs):

        # self.call_service('sonos/stop_study')
        self.call_service('sonos/stop', entity_id=const.STUDY_SPEAKER)

# -----------------------------------------------------------------------------------

    def snooze_event(self, event, data, kwargs):

        seconds = kwargs.get('seconds', 10*60)

        if self.lib.get_alarm_testing():
            entity_id = const.STUDY_SPEAKER
            seconds = 10
        else:
            entity_id = const.BEDROOM_SPEAKER

        self.call_service('sonos/snooze', seconds=seconds, entity_id=entity_id)

# -----------------------------------------------------------------------------------

    def mute_all_event(self, event, data, kwargs):

        self.mute_all_service('', '', '', {})

# -----------------------------------------------------------------------------------

    def unjoin_all_event(self, event, data, kwargs):

        self.unjoin_all_service('', '', '', {})

# -----------------------------------------------------------------------------------

    def join_test_event(self, event, data, kwargs):

        s=5
        print(100)
        self.unjoin_all_service('', '', '', {})
        self.lib.delay(s)
        self.configuration_1({})
        self.lib.delay(s)
        self.unjoin_all_service('', '', '', {})
        self.lib.delay(s)
        self.configuration_2({})
        self.lib.delay(s)
        self.unjoin_all_service('', '', '', {})
        self.lib.delay(s)
        self.configuration_3({})
        self.lib.delay(s)
        self.unjoin_all_service('', '', '', {})
        self.lib.delay(s)
        self.configuration_4({})
        self.lib.delay(s)
        self.unjoin_all_service('', '', '', {})
        print(200)

# -----------------------------------------------------------------------------------

    def test_sonos_event(self, event, data, kwargs):

        entity_id = const.BEDROOM_SPEAKER

        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
        self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0.01)
        self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')
        self.call_service(
            'media_player/play_media',
            entity_id=entity_id,
            media_content_type='music',
            # media_content_id='http://prem2.radiotunes.com:80/popchristmas?5fba91be81f6da5b573f89c1',
            media_content_id='http://prem2.zenradio.com:80/zrsoundsofrain_aac?5fba91be81f6da5b573f89c1',
        )

# -----------------------------------------------------------------------------------

    def test_event(self, event, data, kwargs):

        self.log(f'study_playing={self.lib.is_playing(const.STUDY_SPEAKER)}')
        self.log(f'bedroom_playing={self.lib.is_playing(const.BEDROOM_SPEAKER)}')
        self.log(f'hallyway_playing={self.lib.is_playing(const.HALLWAY_SPEAKER)}')

# -----------------------------------------------------------------------------------

    def play_thing_event(self, event, data, kwargs):

        # media_content_id = const.SUMMER_VIBES_ALBUM
        # media_content_id = const.SUMMER_VIBES_PLAYLIST

        # media_content_id = const.SUMMER_HITS_PLAYLIST
        # self.play_spotify({'entity_id': const.STUDY_SPEAKER, 'volume_level': const.ALARM_VOLUME, 'media_content_id': media_content_id, 'delay': True, 'shuffle': True})

        media_content_id = const.PROGRESSIVE_STREAM
        self.call_service('sonos/play_thing', entity_id=const.STUDY_SPEAKER, volume_level=const.ALARM_VOLUME, media_content_id=media_content_id, delayed=True)

# -----------------------------------------------------------------------------------

    def play_hallway(self, kwargs):

        # media_content_id = const.BOSSANOVA_STREAM
        media_content_id = self.select_stream(const.HALLWAY_STREAMS)

        if media_content_id.startswith('spotify:'):
            self.play_spotify({'entity_id': const.HALLWAY_SPEAKER, 'volume_level': 0.02, 'media_content_id': media_content_id, 'delayed': False, 'shuffle': True})
        else:
            self.call_service('sonos/play_thing', entity_id=const.HALLWAY_SPEAKER, volume_level=0.02, media_content_id=media_content_id, delayed=False, shuffle=True)

# -----------------------------------------------------------------------------------

    def stop_hallway(self, kwargs):

        self.call_service('sonos/stop_hallway')

# -----------------------------------------------------------------------------------

    def _configure(self, speakers: list, volumes: dict, unjoin: bool, join: bool, mute: bool):

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

    def configuration_1(self, kwargs):
        # bedroom/bathroom

        speakers = [const.BEDROOM_SPEAKER, const.BATHROOM_SPEAKER]
        volume = {
            const.BEDROOM_SPEAKER: 0.01,
            const.BATHROOM_SPEAKER: const.ALARM_VOLUME,
        }

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    def configuration_2(self, kwargs):
        # bedroom with join

        speakers = [const.BEDROOM_SPEAKER]
        volume = {const.BEDROOM_SPEAKER: 0.01}

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    def configuration_3(self, kwargs):
        # bedroom no join

        speakers = [const.BEDROOM_SPEAKER]
        volume = {const.BEDROOM_SPEAKER: 0.01}

        self._configure(speakers, volume, unjoin=True, join=False, mute=False)

# -----------------------------------------------------------------------------------

    def configuration_4(self, kwargs):
        # bedroom/kitchen

        speakers = [const.KITCHEN_SPEAKER, const.BEDROOM_SPEAKER]
        volume = {const.KITCHEN_SPEAKER: 0.05, const.BEDROOM_SPEAKER: 0.05}

        self._configure(speakers, volume, unjoin=True, join=True, mute=False)

# -----------------------------------------------------------------------------------

    def play_spotify(self, kwargs):

        self.lib.log_function_name(start=True)

        media_content_id = kwargs['media_content_id']

        if ":playlist:" in media_content_id:
            content_type = "playlist"
        elif ":album:" in media_content_id:
            content_type = "album"
        else:
            self.log(f"Unknown content type for URI: {media_content_id}", level='ERROR')
            return

        kwargs["content_type"] = content_type

        self.call_service('sonos/play_thing', **kwargs)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def set_repeat_mode(self, kwargs):

        entity_id = kwargs["entity_id"]
        repeat = kwargs["repeat_mode"]
        shuffle = kwargs["shuffle"]

        self.call_service("media_player/shuffle_set", entity_id=entity_id, shuffle=shuffle)
        self.call_service("media_player/repeat_set", entity_id=entity_id, repeat=repeat)

# -----------------------------------------------------------------------------------

    def truncate_2dp(self, value: float) -> float:
        """Truncate a float to 2 decimal places without rounding."""

        if value is None:
            return None

        return int(value * 100) / 100.0

# -----------------------------------------------------------------------------------

    def select_stream(self, streams):

        return streams[random.randint(0, len(streams) - 1)]  # randomise choice.

# -----------------------------------------------------------------------------------
