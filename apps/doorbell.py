import adbase
from alexa_utils import AlexaUtilities


class Doorbell(adbase.ADBase):
    def initialize(self):
        """App initializer."""
        self.adapi = self.get_ad_api()
        self.alexa = AlexaUtilities(self.adapi)

        # self.args
        self.mqtt_namespace = self.args.get("mqtt_namespace", "mqtt")
        self.mqtt_topic = self.args["mqtt_topic"]
        self.doorbell_sound = self.args["doorbell_sound"]

        # subscribe to mqtt topic
        self.adapi.call_service("mqtt/subscribe", topic=self.mqtt_topic, namespace=self.mqtt_namespace)  # type: ignore

        # event listener
        self.adapi.listen_event(
            self.doorbell_callback,
            "MQTT_MESSAGE",
            topic=self.mqtt_topic,
            namespace=self.mqtt_namespace,
        )  # type: ignore

    def doorbell_callback(self, event_name, data, kwargs):
        """Ring alexa doorbell sound when doorbell button is pressed."""
        if data["payload"] == "on":
            self.alexa.ring_doorbell(doorbell_sound=self.doorbell_sound)
