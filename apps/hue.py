import asyncio

from aiohue import HueBridgeV2

from hassapi import Hass # type: ignore

HUE_HOST = "192.168.x.x"
HUE_KEY = "secret"

class HueEventStream(Hass):
    """Listen to a Hue EventStream."""

    async def initialize(self):
        """Initialize the application."""

        self.log("Intializing HueEventStream")
        await self.main()

    async def main(self):
        """Communicate with Hue."""
        async with HueBridgeV2(HUE_HOST, HUE_KEY) as bridge:
            self.log(f"Connected to bridge: {bridge.bridge_id}")
            self.log("Subscribing to events...")

            def log_event(event_type, item):
                self.log(f"Received event {event_type.value}: {item}")

            bridge.subscribe(log_event)

            while True:
                await asyncio.sleep(1)
