# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import os
import requests
import constants as const # pylint: disable=unused-import

from automationbase import AutomationBase  # type: ignore
from datetime import datetime, timedelta, time

class FrontDoor(AutomationBase):
    """Documentation for Front Door"""

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.register_service('front_door/battery', self.front_door_battery_service)

        self.listen_event(self.front_door_battery_event, 'front_door_battery')
        self.listen_event(self.front_door_ding_event, 'front_door_ding')

        self.listen_state(self.front_door_ding, 'event.front_door_ding')

        self.run_daily(self.front_door_battery, 'sunset')

        runtime = time(0, 0, 0) # run hourly on the hour
        self.run_hourly(self.cleanup_clips, runtime, random_start=60, random_end=300)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def front_door_battery_service(self, namespace, domain, service, kwargs) -> None:
        """front door battery service"""

        self.front_door_battery({})

# -----------------------------------------------------------------------------------

    def front_door_battery_event(self, event, data, kwargs) -> None:
        """front door battery event"""

        self.front_door_battery({})

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event, data, kwargs) -> None:
        """front door ding event"""

        self.log(f'front_door_ding_event: event={event} data={data} kwargs={kwargs}', level='INFO')

        self.front_door_ding(None, None, None, None, {})

# -----------------------------------------------------------------------------------

    def front_door_ding(self, entity, attribute, old, new, kwargs) -> None:
        """front door ding"""

        self.log(f'front_door_ding: entity={entity} attribute={attribute} old={old} new={new} kwargs={kwargs}', level='INFO')

        self.run_in(self.siren_on, 0)
        self.run_in(self.front_door_announce, 0)

        if self._is_night():
            self.call_service('lighting/front_door_ding', seconds=const.DING_TIMEOUT, cb='front_door_hallway_off')

# -----------------------------------------------------------------------------------

    def front_door_battery(self, kwargs) -> None:

        level = self.get_state('sensor.front_door_battery')

        if level == 'unavailable':
            self.log('Battery level not available', level='ERROR')
            return

        message = None
        battery = ''
        level = int(level)

        if level <= 50:
            if level <= 20:
                battery = ' - CRITICAL'
                message = 'Urgent! Please replace the front door battery immediately'
            elif level <= 25:
                battery = ' - dangerously low'
                message = 'Warning! Please replace the front door battery as soon as possible'
            elif level <= 30:
                battery = ' - low'
                message = 'Important! Please charge the second front door battery'
            else:
                message = 'Please charge the second front door battery'

            self.call_service('announcer/announce', message=message)

            message=f'Recharge front door battery ({level:d}%{battery})'
            self.call_service('announcer/notification', message=message)

# -----------------------------------------------------------------------------------

    def siren_on(self, kwargs) -> None:
        """turn on siren for front door ding"""

        delay = 1 if self._get_testing() else 3

        self.call_service('siren/turn_on', entity_id=['siren.tapo_hub','siren.kasa_hub'])

        self.run_in(self.siren_off, delay)

# -----------------------------------------------------------------------------------

    def siren_off(self, kwargs) -> None:
        """turn off siren for front door ding"""

        self.call_service('siren/turn_off', entity_id=['siren.tapo_hub','siren.kasa_hub'])

# -----------------------------------------------------------------------------------

    def front_door_announce(self, kwargs) -> None:
        """front door announcement"""

        message = 'Someone is at the front door' if not (self.get_state('input_boolean.testing')) == 'on' else 'just testing'
        self.call_service('announcer/broadcast', message=message, timestamp='front_door')

# -----------------------------------------------------------------------------------

    def take_snapshot(self, kwargs):

        entity_id=kwargs.get("entity_id", "camera.front_door")

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"/config/www/snapshots/front_door_{timestamp}.jpg"

        self.call_service("camera/snapshot", entity_id=entity_id, filename=filename)

# -----------------------------------------------------------------------------------

    def cleanup_clips(self, kwargs):
        """cleanup ring clips downloaded by ring stash older than 7 days"""

        folder = "/media/ring_clips"

        cutoff = datetime.now() - timedelta(days=7)

        for f in os.listdir(folder):
            path = os.path.join(folder, f)

            if not os.path.isfile(path):
                continue

            # Delete motion clips immediately
            if "motion" in f.lower():
                try:
                    os.remove(path)
                    self.log(f"Deleted motion clip: {path}", level='INFO')
                except Exception as e:
                    self.log(f"Failed to delete {path}: {e}", level="ERROR")
                continue

            # Parse date/time for doorbell clips
            try:
                parts = f.split("_")

                # parts:
                # 0 = front
                # 1 = door
                # 2 = YYYY-MM-DD
                # 3 = HH-MM-SS
                date_str = parts[2]
                time_str = parts[3]

                dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H-%M-%S")

            except Exception as e:
                self.log(f"Could not parse date for {f}: {e}", level="WARNING")
                continue

            # Delete doorbell clips older than 7 days
            if dt < cutoff:
                try:
                    os.remove(path)
                    self.log(f"Deleted old doorbell clip: {path}", level='INFO')
                except Exception as e:
                    self.log(f"Failed to delete {path}: {e}", level="ERROR")

# -----------------------------------------------------------------------------------
