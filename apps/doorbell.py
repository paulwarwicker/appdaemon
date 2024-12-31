# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

class DoorBell(Hass):
    """Documentation for Doorbell"""

    lib = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# # -----------------------------------------------------------------------------------

#     async def front_door_ding(self, entity, attribute, old, new, kwargs) -> None:

#         await self.run_in_executor(self.tapo_siren_on)
#         self.front_door_announce()
#         self.ding_front_door_light()
#         self.ding_hallway_light()

# # -----------------------------------------------------------------------------------

#     def tapo_siren_on(self, kwargs) -> None:

#         self.call_service('siren/turn_on', entity_id='siren.tapo_hub_siren')
#         seconds = 5
#         self.log(f'\tstart timer for{seconds:d}s', level='DEBUG')
#         self.run_in(self.tapo_siren_off, seconds)

# # -----------------------------------------------------------------------------------

#     def tapo_siren_off(self, kwargs) -> None:

#         self.call_service('siren/turn_off', entity_id='siren.tapo_hub_siren')

# # -----------------------------------------------------------------------------------

#     def front_door_announce(self, kwargs) -> None:

#         message = 'Someone is at the front door' if not self.get_state('input_boolean.testing') == 'on' else 'just testing'
#         self.call_service('announcer/broadcast', message=message, timestamp='front door')

# # -----------------------------------------------------------------------------------

#     def ding_front_door_light(self, kwargs) -> None:
#         """Turn on front door light when dark when someone calls. see also front_door_light_on/off"""

#         if self.now_is_between('sunset', 'sunrise'):
#             # TODO: return to previous level if was previously on
#             brightness = self.get_state('light.front_door_1', attribute='brightness')
#             state = self.get_state('light.front_door_1')
#             self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
#             self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=192, transition=10)
#             # self.turn_on('scene.front_door_ding_2') # FIXME: not working - scenes dont allow transitiona
#             seconds = 12*60
#             self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
#             # FIXME:, brightness=brightness) # state=state??
#             self.run_in(self.front_door_light_off, seconds)

# # -----------------------------------------------------------------------------------

#     def ding_hallway_light(self, kwargs) -> None:
#         """Turn on hallway light when dark"""

#         if self.lib.is_night():  # civil dusk till civil dawn
#             self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64, transition=5)
#             seconds = 10*60
#             self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
#             self.run_in(self.hallway_off, seconds)

# # -----------------------------------------------------------------------------------


# import adbase
# from alexa_utils import AlexaUtilities


# class Doorbell(adbase.ADBase):
#     def initialize(self):
#         """App initializer."""
#         self.adapi = self.get_ad_api()
#         self.alexa = AlexaUtilities(self.adapi)

#         # self.args
#         self.mqtt_namespace = self.args.get("mqtt_namespace", "mqtt")
#         self.mqtt_topic = self.args["mqtt_topic"]
#         self.doorbell_sound = self.args["doorbell_sound"]

#         # subscribe to mqtt topic
#         self.adapi.call_service("mqtt/subscribe", topic=self.mqtt_topic, namespace=self.mqtt_namespace)  # type: ignore

#         # event listener
#         self.adapi.listen_event(
#             self.doorbell_callback,
#             "MQTT_MESSAGE",
#             topic=self.mqtt_topic,
#             namespace=self.mqtt_namespace,
#         )  # type: ignore

#     def doorbell_callback(self, event_name, data, kwargs):
#         """Ring alexa doorbell sound when doorbell button is pressed."""
#         if data["payload"] == "on":
#             self.alexa.ring_doorbell(doorbell_sound=self.doorbell_sound)
