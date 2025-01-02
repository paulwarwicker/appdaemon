# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611

class Snoozer(Hass):
    """Documentation for Snoozer"""
    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise snoozer"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.listen_event(self.snooze_event, "snooze_1", minutes=1)
        self.listen_event(self.snooze_event, "snooze_5", minutes=5)
        self.listen_event(self.snooze_event, "snooze_10", minutes=10)
        self.listen_event(self.snooze_event, "snooze_30", minutes=30)
        self.listen_event(self.snooze_event, "snooze_60", minutes=60)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def snooze_event(self, event_name, data, kwargs):

        minutes = kwargs.get("minutes", 10)
        entity_id = self.const.STUDY_SPEAKER if self.lib.get_alarm_testing() else self.const.BEDROOM_SPEAKER

        self.call_service("media_player/media_pause", entity_id=entity_id)
        self.log(f"\tsnooze activated: paused {entity_id}", level='WARNING')

        self.run_in(self.resume, minutes * 60, entity_id=entity_id)

# -----------------------------------------------------------------------------------

    def resume(self, kwargs):

        entity_id = kwargs["entity_id"]

        self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0.2)
        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
        self.call_service("media_player/media_play", entity_id=entity_id)
        self.log(f"\tsnooze ended: resumed {entity_id}", level='WARNING')

# -----------------------------------------------------------------------------------
