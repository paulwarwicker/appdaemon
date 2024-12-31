# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class FrontDoor(Hass):
    """Documentation for Front Door"""

    lib = None
    const = None

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.register_service('front_door/battery', self.front_door_battery_service)

        self.listen_event(self.front_door_battery_event, 'front_door_battery')
        self.listen_event(self.front_door_ding_event, 'front_door_ding')
        self.listen_state(self.front_door_ding, 'binary_sensor.front_door_ding', old='off', new='on')

        self.run_daily(self.front_door_battery, 'sunset + 00:05:00')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')
        # self.call_service('announcer/announce', entity_id='media_player.study', message="DS Smith Fordem")

# -----------------------------------------------------------------------------------

    def front_door_battery_service(self, namespace, domain, service, kwargs) -> None:
        """front door battery service"""

        self.front_door_battery({})

# -----------------------------------------------------------------------------------

    def front_door_battery_event(self, event:str, data:dict, kwargs) -> None:
        """front door battery event"""

        self.front_door_battery({})

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event:str, data:dict, kwargs) -> None:
        """front door ding event"""

        self.front_door_ding('','','','',{})

# -----------------------------------------------------------------------------------

    def front_door_battery(self, kwargs) -> None:

        message = None
        battery = ''
        level = int(self.get_state('sensor.front_door_battery'))

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

    def front_door_ding(self, entity, attribute, old, new, kwargs) -> None:

        self.run_in_thread(self.siren_on, self.const.APP_THREADS - 1)
        self.run_in_thread(self.front_door_announce, self.const.APP_THREADS - 2)
        if self.lib.is_night():
            self.call_service('lighting/front_door_ding', seconds=300, cb='front_door_hallway_off', key='front_door_ding')

# -----------------------------------------------------------------------------------

    def siren_on(self, kwargs) -> None:

        delay = 1 if self.lib.get_testing() else 5
        self.call_service('siren/turn_on', entity_id='siren.tapo_hub_siren')
        self.run_in(self.siren_off, delay)

# -----------------------------------------------------------------------------------

    def siren_off(self, kwargs) -> None:

        self.call_service('siren/turn_off', entity_id='siren.tapo_hub_siren')

# -----------------------------------------------------------------------------------

    def front_door_announce(self, kwargs) -> None:

        message = 'Someone is at the front door' if not self.get_state('input_boolean.testing') == 'on' else 'just testing'
        self.call_service('announcer/broadcast', message=message, timestamp='front_door')

# -----------------------------------------------------------------------------------

    def ding_front_door_light(self, kwargs) -> None:
        """Turn on front door light when dark when someone calls. see also front_door_light_on/off"""

        if self.now_is_between('sunset', 'sunrise'):
            # TODO: return to previous level if was previously on
            brightness = self.get_state('light.front_door_1', attribute='brightness')
            state = self.get_state('light.front_door_1')
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=192, transition=10)
            # self.turn_on('scene.front_door_ding_2') # FIXME: not working - scenes dont allow transitiona
            seconds = 12*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            # FIXME:, brightness=brightness) # state=state??
            self.run_in(self.front_door_light_off, seconds)

# -----------------------------------------------------------------------------------

    def ding_hallway_light(self, kwargs) -> None:
        """Turn on hallway light when dark"""

        if self.lib.is_night():  # civil dusk till civil dawn
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64, transition=5)
            seconds = 10*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.hallway_off, seconds)

# -----------------------------------------------------------------------------------

    def front_door_light_on(self, kwargs) -> None:

        self.run_in(self._front_door_light_on, 0)

# -----------------------------------------------------------------------------------

    def _front_door_light_on(self, kwargs) -> None:

        if self.now_is_between('sunset', 'sunrise + 1:00:00'):
            if self.lib.is_below_horizon():
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=128, transition=10)
                self.call_service('light/turn_on', entity_id='light.garage_1', brightness=128, transition=10)
            else:
                self.run_in(self.int_front_door_light_on, 60)  # respawn self in 60s

# -----------------------------------------------------------------------------------

    def front_door_light_off(self, kwargs) -> None:

        # scene = 'scene.front_door_ding_2'
        # self.log(f'\tscene={scene}', level='DEBUG')
        # self.turn_off(scene) # TODO: not working
        self.call_service('light/turn_off', entity_id='light.hallway_1', transition=10)
        self.call_service('light/turn_off', entity_id='light.front_door_1', transition=10)

# -----------------------------------------------------------------------------------
