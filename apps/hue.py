# import asyncio

# from aiohue import HueBridgeV2

# from hassapi import Hass # type: ignore

# HUE_HOST = "192.168.x.x"
# HUE_KEY = "secret"

# class HueEventStream(Hass):
#     """Listen to a Hue EventStream."""

#     async def initialize(self):
#         """Initialize the application."""

#         self.log("Intializing HueEventStream")
#         await self.main()

#     async def main(self):
#         """Communicate with Hue."""
#         async with HueBridgeV2(HUE_HOST, HUE_KEY) as bridge:
#             self.log(f"Connected to bridge: {bridge.bridge_id}")
#             self.log("Subscribing to events...")

#             def log_event(event_type, item):
#                 self.log(f"Received event {event_type.value}: {item}")

#             bridge.subscribe(log_event)

#             while True:
#                 await asyncio.sleep(1)

# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from typing import TYPE_CHECKING, cast

import constants as const

from automationbase import AutomationBase  # type: ignore

class Hue(AutomationBase):
    """Documentation for Hue"""

    BUTTON_WINDOW_START = '00:00:00'
    BUTTON_WINDOW_END = '07:30:00'

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.listen_event(self.button_event, 'hue_event')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def button_event(self, event, data, kwargs) -> None:

        self._log_function_name(start=True)

        # _type = data['type']
        # _subtype = data['subtype']
        device_id = data["device_id"]
        # device_name = const.SWITCHES.get(device_id, device_id)
        # print(data)

        # if self._get_verbose_debug():
        #     print(data)
        #     if _type in ('short_release', 'long_release'):
        #         self.log(f'\t{_type} {_subtype} on {device_name} ({device_id})')
        #     if _type == 'start':
        #         self.log(f'\t{_type} on {device_name} ({device_id}) with subtype {_subtype}')
        #         if _subtype in ('clock_wise', 'counter_clock_wise'):
        #             self.log(f'\t\t{_subtype} for {data["duration"]}ms with {data["steps"]} steps')

        if device_id == const.BEDROOM_SWITCH:
            self.bedroom_button(data, kwargs)
        elif device_id == const.GARAGE_SWITCH:
            self.garage_button(data, kwargs)
        elif device_id == const.STUDY_SWITCH:
            self.study_button(data, kwargs)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_button(self, data, kwargs) -> None:

        self._log_function_name(start=True)

        event_type = None
        _type = data['type']
        _subtype = data['subtype']

        if _type == 'short_release':
            if _subtype in (1,2):
                event_type = 'stop_bedroom'
                # if self.get_state('input_boolean.physical_training') == 'on':
                #     event_type  = 'stop_bedroom'
                # else:
                #     if self.now_is_between(self.BUTTON_WINDOW_START, self.BUTTON_WINDOW_END): # midnight - 07:30
                #         event_type  = 'stop_bedroom'
                #     else:
                #         event_type  = 'snooze10'
            elif _subtype in (3,4):
                event_type = 'all_off'

        if _type == 'long_release':
            if _subtype == 1:
                event_type = 'snooze10'
            elif _subtype == 2:
                event_type = 'snooze15'
            elif _subtype == 3:
                event_type = 'snooze30'
            elif _subtype == 4:
                event_type = 'snooze60'

        if _type in ('start') and _subtype == 'counter_clock_wise':
            event_type = 'all_off'

        if _type in ('start') and _subtype == 'clock_wise':
            event_type = 'lumie_on'

        if event_type is not None:
            self.fire_event(event_type)

            if event_type == 'all_off':
                self.fire_event('stop_bedroom')
                self.call_service('sonos/cancel_snooze')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_button(self, data, kwargs) -> None:

        self._log_function_name(start=True)

        event_type = None
        _type = data['type']
        _subtype = data['subtype']

        if _type == 'short_release':
            if _subtype == 1:
                self.call_service('hue/activate_scene', entity_id='scene.living_room_lights_std60')
            elif _subtype == 2:
                self.call_service('hue/activate_scene', entity_id='scene.living_room_lights_puzzle200')
            elif _subtype == 3:
                pass
            elif _subtype == 4:
                pass

        if _type == 'long_release':
            if _subtype == 1:
                pass
            elif _subtype == 2:
                pass
            elif _subtype == 3:
                pass
            elif _subtype == 4:
                pass

        if _type in ('start') and _subtype == 'counter_clock_wise':
            pass

        if _type in ('start') and _subtype == 'clock_wise':
            pass

        if event_type is not None:
            self.fire_event(event_type)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def _garage_event_from_state(self) -> str | None:
        """Return the garage event based on the current garage sensor state."""

        state = self.get_state(const.GARAGE_ENTITY_ID)

        if state is None:
            return None

        return 'garage_close' if state == 'open' else 'garage_open'

# -----------------------------------------------------------------------------------

    def garage_button(self, data, kwargs) -> None:

        self._log_function_name(start=True)

        event_type = None
        _type = data['type']
        _subtype = data['subtype']

        if _type == 'short_release' and _subtype in (1,2,3,4):
            event_type = self._garage_event_from_state()
            if event_type is not None:
                self.fire_event(event_type)

        if _type == 'long_release' and _subtype in (1,2):
            self.fire_event('garage_open')

        if _type == 'long_release' and _subtype in (3,4):
            self.fire_event('garage_close')

        if _type in ('start') and _subtype in ('clock_wise', 'counter_clock_wise'):
            if _subtype == 'clock_wise':
                self.call_service('light/turn_on', entity_id=const.GARAGE_LIGHTS, brightness=const.FULL_ON)
            if _subtype == 'counter_clock_wise':
                self.call_service('light/turn_off', entity_id=const.GARAGE_LIGHTS)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------
