# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import traceback
from datetime import datetime
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611


class Lighting(Hass):
    """Documentation for Lighting"""

    lib = None
    const = None
    timers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.register_service('lighting/garage_on', self.garage_on_service)
        self.register_service('lighting/garage_off', self.garage_off_service)
        self.register_service('lighting/bannister_on', self.bannister_on_service)
        self.register_service('lighting/utility_on', self.utility_on_service)
        self.register_service('lighting/utility_off', self.utility_off_service)
        self.register_service('lighting/turn_on_if_off', self.turn_on_if_off_service)
        self.register_service('lighting/kitchen_on', self.kitchen_on_service)
        self.register_service('lighting/kitchen_off', self.kitchen_off_service)
        self.register_service('lighting/kitchen_floor_on', self.kitchen_floor_on_service)
        self.register_service('lighting/welcome_lights', self.welcome_lights_service)
        self.register_service('lighting/front_door_on', self.front_door_on_service)
        self.register_service('lighting/front_door_off', self.front_door_off_service)
        self.register_service('lighting/hallway_off', self.hallway_off_service)
        self.register_service('lighting/lumie_on', self.lumie_on_service)
        self.register_service('lighting/lumie_off', self.lumie_off_service)
        self.register_service('lighting/front_door_ding', self.front_door_ding_service)
        self.register_service('lighting/all_off', self.all_off_service)
        self.register_service('lighting/bathroom_on', self.bathroom_on_service)
        self.register_service('lighting/bathroom_off', self.bathroom_off_service)
        self.register_service('lighting/landing_on', self.landing_on_service)
        self.register_service('lighting/cloakroom_on', self.cloakroom_on_service)
        self.register_service('lighting/cloakroom_off', self.cloakroom_off_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timers')
        self.listen_event(self.cancel_timers_event, 'cancel_timers')
        self.listen_event(self.welcome_lights_event, 'welcome_lights') # see location for the real welcome_lights event handler
        self.listen_event(self.front_door_on_event, 'front_door_on')
        self.listen_event(self.front_door_ding_event, 'front_door_ding_lights')
        self.listen_event(self.lights_off_event, "ios.action_fired", actionName='Lights')
        self.listen_event(self.lumie_on_event, 'lumie_on')
        self.listen_event(self.lumie_wake_event, 'lumie_wake')
        self.listen_event(self.button_event, 'shelly.click')
        self.listen_event(self.all_off_event, 'all_off')
        self.listen_event(self.bathroom_on_event, 'bathroom_on')
        self.listen_event(self.bathroom_off_event, 'bathroom_off')

        self.run_daily(self.living_room_on, 'sunset + 00:10:00')
        self.run_daily(self.downstairs_off, '23:30:00')
        self.run_daily(self.outside_off, '21:30:00')
        self.run_daily(self.all_off, '02:00:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.purge_timers, runtime)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def all_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """all off service"""

        self.show_service(namespace, domain, service, data)

        self.fire_event('all_off')

# -----------------------------------------------------------------------------------

    def welcome_lights_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on welcome lights"""

        self.lib.log_function_name(True, True)

        if not self.lib.is_night():
            self.log('\ttoo early for welcome lights', level='DEBUG')
            return

        cb = data.get('cb', None)
        seconds = data.get('seconds', 5*60)

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb)

        self.call_service('lighting/turn_on_if_off', entity_id=self.const.WELCOME_LIGHTS, brightness=128) # TODO: cb=cb ??
        self.call_service('lighting/turn_on_if_off', entity_id=self.const.HALLWAY1, brightness=64)

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP)

        self.set_callback(cb, callback, seconds)

# -----------------------------------------------------------------------------------

    def front_door_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on front door lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        self.show_service(namespace, domain, service, data, cb)

        self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=self.lib.percent_to_brightness(80), transition=10)
        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=self.lib.percent_to_brightness(25), transition=10)

# -----------------------------------------------------------------------------------

    def front_door_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off front door lights"""

        # self.call_service('light/turn_off', entity_id=self.const.FRONT_DOOR)

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.set_callback(cb, callback)

        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def kitchen_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on kitchen lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        self.show_service(namespace, domain, service, data, cb)

        entity_ids = self.light_entities('kitchen', self.const.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights on', level='DEBUG')
        else:
            brightness = 128 if self.now_is_between('sunrise', 'sunset') else 64
            self.call_service('light/turn_on', entity_id=self.const.KITCHEN_LIGHTS, brightness=brightness)
            self.call_service('light/turn_on', entity_id=self.const.KITCHEN_FLOOR_LIGHTS, brightness=brightness*2)

        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def kitchen_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off kitchen lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)
        self._cancel_timer('kitchen_floor_off')

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        entity_ids = self.light_entities('kitchen', self.const.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights on', level='DEBUG')
        else:
            self.set_callback(cb, callback)

        self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def kitchen_floor_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        callback = None
        cb = data.get('cb', None)

        self.show_service(namespace, domain, service, data, cb, callback)

        brightness = 250 if self.now_is_between('sunrise', 'sunset') else 128

        self.call_service('light/turn_on', entity_id=self.const.KITCHEN_FLOOR_LIGHTS, brightness=brightness)

# -----------------------------------------------------------------------------------

    def utility_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        self.show_service(namespace, domain, service, data, cb)

        self.call_service('light/turn_on', entity_id=self.const.UTILITY_ROOM_LIGHTS)

# -----------------------------------------------------------------------------------

    def utility_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off utility lights"""

        cb = data.get('cb', None)

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        entity_ids = [self.const.UTILITY_ROOM_LIGHTS]

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - utility lights on', level='DEBUG')
        else:
           self.set_callback(cb, callback)

# -----------------------------------------------------------------------------------

    def lumie_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on lumie lights"""

        cb = data.get('cb', None)
        brightness = int(data.get('brightness', self.lib.percent_to_brightness(1)))

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.call_service('light/turn_on', entity_id=self.const.LUMIE, brightness=brightness)

        self.set_callback(cb, callback)

# -----------------------------------------------------------------------------------

    def landing_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on landing lights"""

        cb = data.get('cb', None)
        brightness = data.get('brightness', self.lib.percent_to_brightness(25))

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.call_service('light/turn_on', entity_id=self.const.LANDING, brightness=brightness)
        self.call_service('light/turn_on', entity_id=self.const.BEDROOM2, brightness=brightness)
        self.call_service('light/turn_on', entity_id=self.const.LUMIE, brightness=self.lib.percent_to_brightness(95))

        self.set_callback(cb, callback)

# -----------------------------------------------------------------------------------

    def turn_on_if_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on a light if it off"""

        self.lib.log_function_name(None, True)

        cb = data.get('cb', None)
        seconds = int(data.get('seconds', 30))
        brightness = int(data.get('brightness', 64))
        color_temp = int(data.get('color_temp', 152))
        entity_id = data.get('entity_id', [])

        if isinstance(entity_id, str):
            entity_id = [entity_id]

        callback = self.get_callback(cb)

        if self.lib.get_verbose_debug():
            self.show_service(namespace, domain, service, data, cb, callback)
            self.log(f'\tentity_id={entity_id} brightness={brightness} color_temp{color_temp}', level='DEBUG')

        for entity in entity_id:
            prev_state = self.get_state(entity)
            prev_brightness = self.get_state(entity, attribute="brightness")

            if prev_state == 'off':
                self.call_service('light/turn_on', entity_id=entity, brightness=brightness, color_temp=color_temp)
            else:
                self.log(f'\t{service}: ignored - {entity} already on brightness={prev_brightness}', level='WARNING')

        self.set_callback(cb, callback, seconds)

        self.lib.log_function_name(False, True)

# -----------------------------------------------------------------------------------

    def garage_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on garage lights"""

        if self.lib.is_below_horizon():
            self.call_service('light/turn_on', entity_id=self.const.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def garage_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off garage lights"""

        self.call_service('light/turn_off', entity_id=self.const.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def bathroom_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on bathroom lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        entity_ids = self.light_entities('bathroom', self.const.N_BATHROOM_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - bathroom lights on', level='DEBUG')
        else:
            sunrise = 'sunrise'
            plus1 = '+ 01:00:00'
            sunset = 'sunset'
            late = '23:00:00'

            if self.now_is_between(f'{sunrise} {plus1}', f'{sunset} {plus1}'):
                brightness = 250
                color_temp = 171
            elif self.now_is_between(sunrise, f'{sunrise} {plus1}') or self.now_is_between(f'{sunset} {plus1}', late):
                brightness = 64
                color_temp = 441
            else:
                brightness = 25
                color_temp = 441

            if self.lib.get_verbose_debug():
                self.show_service(namespace, domain, service, data, cb)
                self.log(f'brightness={brightness} color_temp={color_temp}', level='DEBUG')

            self.call_service('light/turn_on', entity_id=self.const.BATHROOM_LIGHTS, brightness=brightness, color_temp=color_temp)

# -----------------------------------------------------------------------------------

    def bathroom_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off bathroom lights"""

        cb = data.get('cb', None)

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.set_callback(cb, callback)

# -----------------------------------------------------------------------------------

    def cloakroom_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on cloakroom lights"""

        cb = data.get('cb', None)

        self._cancel_timer(cb)

        sunset = 'sunset'
        sunrise = 'sunrise'
        plus1 = ' + 01:00:00'

        if self.now_is_between(sunset, f'{sunrise}{plus1}'):
            brightness = 128 if self.now_is_between(sunset, f'{sunset}{plus1}') or self.now_is_between(sunrise, f'{sunrise}{plus1}') else 64

            if self.lib.get_verbose_debug():
                self.show_service(namespace, domain, service, data, cb)
                self.log(f'brightness={brightness}', level='DEBUG')

            self.call_service('light/turn_on', entity_id=self.const.CLOAKROOM, brightness=brightness)

# -----------------------------------------------------------------------------------

    def cloakroom_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off cloakroom lights"""

        cb = data.get('cb', None)

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        self.set_callback(cb, callback)

# -----------------------------------------------------------------------------------

    def lumie_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off lumie lights"""

        self.call_service('light/turn_off', entity_id=self.const.LUMIE)

# -----------------------------------------------------------------------------------

    def bannister_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on bannister and hallway lights"""

        cb = data.get('cb', None)
        seconds = int(data.get('seconds', 0))

        callback = self.get_callback(cb)

        if self.lib.get_verbose_debug():
            self.show_service(namespace, domain, service, data, cb, callback)
            self.log(f'seconds={seconds}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64)
        self.call_service('light/turn_on', entity_id=self.const.BANNISTER, brightness=self.lib.percent_to_brightness(12))

        self.set_callback(cb, callback, seconds)

# -----------------------------------------------------------------------------------

    def hallway_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off bannister and hallway lights"""

        cb = data.get('cb', None)
        seconds = int(data.get('seconds', 0))

        callback = self.get_callback(cb)

        if self.lib.get_verbose_debug():
            self.show_service(namespace, domain, service, data, cb, callback)
            self.log(f'interval={seconds}', level='DEBUG')

        self.set_callback(cb, callback, seconds)

# -----------------------------------------------------------------------------------

    def front_door_ding_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on front door/hallway lights"""

        cb = data.get('cb', None)
        seconds = int(data.get('seconds', 0))

        callback = self.get_callback(cb)

        self.show_service(namespace, domain, service, data, cb, callback)

        # self.call_service('hue/activate_scene', entity_id='scene.front_door_hallway_front_door_ding', transition=10)
        self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=200, transition=10)
        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64, transition=10)

        self.set_callback(cb, callback, seconds)

# -----------------------------------------------------------------------------------

    def all_off_event(self, event, data, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    def button_event(self, event, data, kwargs) -> None:

        event_type  = None
        device = data['device']
        click_type = data['click_type']

        if device != self.const.BEDROOM_BUTTON:
            return

        if self.lib.get_verbose_debug():
            self.log(f'\t{click_type} button press on bedroom button ({self.const.BEDROOM_BUTTON})')
            # self.log(f'\t{data}')

        if click_type == 'single':
            event_type  = 'all_off'
        elif click_type == 'long':
            event_type  = 'lumie_on'
        elif click_type == 'double':
            pass
        elif click_type == 'triple':
            pass

        if event_type is not None:
            self.fire_event(event_type)

# -----------------------------------------------------------------------------------

    def lights_off_event(self, event, data, kwargs) -> None:
        """turn off all lights"""

        self.call_service('light/turn_off', entity_id=self.const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    async def status_event(self, event, data, kwargs) -> None:

        await self.print_timers()

# -----------------------------------------------------------------------------------

    def cancel_timers_event(self, event, data, kwargs) -> None:

        self.cancel_timers()

# -----------------------------------------------------------------------------------

    def welcome_lights_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/welcome_lights', cb='welcome_lights_off') # , seconds=61)

# -----------------------------------------------------------------------------------

    def front_door_on_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/front_door_on', seconds=10, cb='front_door_off')

# -----------------------------------------------------------------------------------

    def bathroom_on_event(self, event, data, kwargs) -> None:

        brightness = data.get('brightness', 25)
        seconds = data.get('seconds', 10)

        self.call_service('lighting/bathroom_on', seconds=seconds, brightness=brightness, cb='bathroom_off')

# -----------------------------------------------------------------------------------

    def bathroom_off_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/bathroom_off', seconds=0, cb='bathroom_off')

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event, data, kwargs) -> None:

        self.call_service('lighting/front_door_ding', seconds=20, cb='front_door_hallway_off', key='front_door_ding')

# -----------------------------------------------------------------------------------

    def lumie_on_event(self, event, data, kwargs) -> None:

        force = data.get('force', False)
        brightness = data.get('brightness', 4)

        if self.now_is_between('23:30:00', '04:00:00') or force:
            self.call_service('light/turn_on', entity_id=self.const.LUMIE, brightness=brightness)
        else:
            self.log('\toutside time window for lumie', level='WARNING')

# -----------------------------------------------------------------------------------

    def lumie_wake_event(self, event, data, kwargs) -> None:

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=64, rgb_color=[255, 180, 10])

# -----------------------------------------------------------------------------------

    def stairs_on(self, kwargs) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id=self.const.LANDING, brightness=5, transition=10)

# -----------------------------------------------------------------------------------

    # def radiator_on(self, kwargs) -> None:
    #     """turn on radiator light"""

    #     self.call_service('light/turn_on', entity_id=self.const.RADIATOR, transition=10, brightness=102)

# -----------------------------------------------------------------------------------

    def living_room_on(self, kwargs) -> None:
        """turn on living room lights"""

        for entity_id in self.const.LIVING_ROOM:
            if not self.is_light_on(entity_id):
                self.call_service('light/turn_on', entity_id=entity_id, brightness=self.percent_to_brightness(40), transition=10)

# -----------------------------------------------------------------------------------

    def hallway_on(self, kwargs) -> None:

        verbose = self.lib.get_verbose_debug()

        if self.lib.is_night():  # civil dusk till civil dawn
            if verbose:
                self.log('\tturn on hallway light', level='DEBUG')

            self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64, transition=10)

# -----------------------------------------------------------------------------------

    def bannister_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.NIGHTTIME_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def kitchen_off(self, kwargs) -> None:

        entity_ids = self.light_entities('kitchen', self.const.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.const.KITCHEN_LIGHTS, transition=10)
            cb = 'kitchen_floor_off'
            callback = self.get_callback(cb)
            self.set_callback(cb, callback, 5*60)

# -----------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.KITCHEN_FLOOR_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def utility_off(self, kwargs) -> None:

        entity_ids = self.light_entities('utility') # just 1

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - utiltity lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.const.UTILITY_ROOM_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def front_door_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.FRONT_DOOR, transition=10)

# -----------------------------------------------------------------------------------

    def bathroom_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.BATHROOM_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def front_door_hallway_off(self, kwargs) -> None:

        key = kwargs.get('key', None)

        hallway_lights = self.light_entities('hallway', self.const.N_HALLWAY_ENTITIES - 1) # pylint: disable=C0103 disable=W0201

        self.front_door_off(kwargs)

        if key is not None:
            self.log(f'\tturn off hallway - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=hallway_lights, transition=10)

# -----------------------------------------------------------------------------------

    def outside_off(self, kwargs) -> None:
        """turn off outside lights"""

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off outside - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.const.OUTSIDE_LIGHTS)

# -----------------------------------------------------------------------------------

    def downstairs_off(self, kwargs) -> None:
        """turn off downstairslights"""

        self.call_service('light/turn_off', entity_id=self.const.LIVING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP) # try again - wasn't switching off
        self.call_service('light/turn_off', entity_id=self.const.UTILITY_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.DINING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.OUTSIDE_LIGHTS)
        self.call_service('switch/turn_off', entity_id=self.const.COOKER_LIGHTS)

# -----------------------------------------------------------------------------------

    def all_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    def hallway_off(self, kwargs) -> None:

        self.call_service('light/turn_off', entity_id=self.const.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def set_timer(self, name:str, timer:str) -> None:
        """set a timer"""

        verbose = self.lib.get_verbose_debug()

        old = self.timers.get(name, None)

        if old is not None:
            if self.check_timer(name, old):
                self.log(f'\treplacing name={name} old={old} with new={timer}', level='DEBUG')
                self._cancel_timer(name)

        if verbose:
            self.log(f'\tadding new timer name={name} timer={timer}')

        if self.check_timer(name, timer):
            self.timers[name] = timer
            # if verbose:
            #     self.print_timers()

# -----------------------------------------------------------------------------------

    def get_timer(self, name:str) -> str:
        """get a timer"""

        verbose = self.lib.get_verbose_debug()

        timer = self.timers.get(name, None)

        if timer is None:
            self.log(f'\tmissing timer name={name}', level='WARNING')
        else:
            if verbose:
                self.log(f'\treturning name={name} timer={timer}', level='DEBUG')

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name:str) -> None:
        """cancel a timer callback"""

        verbose = self.lib.get_verbose_debug()

        timer = self.get_timer(name)

        if timer is not None:
            if verbose:
                self.log(f'\tcancelling running timer name={name} timer={timer}', level='DEBUG')

            self.cancel_timer(timer)
            self.timers.pop(name)
        else:
            if verbose:
                self.log(f'\t_cancel_timer no timer name={name}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        verbose = self.lib.get_verbose_debug()

        timer = self.timers.get(name, None)

        if timer is not None:
            if verbose:
                self.log(f'\tremoving timer name={name} timer={timer}')

            self.timers.pop(name)
        else:
            if verbose:
                self.log(f'\tremove_timer no timer name={name}', level='WARNING')

# -----------------------------------------------------------------------------------

    def check_timer(self, name, timer) -> bool:

        verbose = self.lib.get_verbose_debug()

        if not verbose:
            return True

        if timer is None:
            self.log(f'timer is None name={name}', level='ERROR')
            return False

        extant = self.info_timer(timer)

        if extant is None:
            self.log(f'{name} timer is no longer extant. removing', level='ERROR')
            self.remove_timer(name)
            return False

        time, interval, kwargs = self.info_timer(timer)
        self.log(f'\tname={name} timer={timer} time={time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}')

        return True

# -----------------------------------------------------------------------------------

    async def print_timers(self) -> None:
        """print timers"""

        await self.purge_timers({})

        status = '\n\n\ttimers:\n\n'

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is not None and self.timer_running(timer):
                print(f'\tkey={key} timer={timer} isrunning={self.timer_running(timer)}')
                result = await self.info_timer(timer)
                if result is None:
                    self.log(f"Warning: info_timer() returned None for timer {timer}", level="WARNING")
                    continue

                time, interval, kwargs = result  # Unpack only if result is not None
                remaining = time - datetime.now()
                hours, remainder = divmod(remaining.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                status += f'\tremaining={minutes:02d}:{seconds:02d} time={time} kwargs={kwargs} isrunning={self.timer_running(timer)}\n'

        self.log(f'{status}')

# -----------------------------------------------------------------------------------

    async def purge_timers(self, kwargs) -> None:
        """purge timers"""

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key, None)
            if timer is not None and self.timer_running(timer):
                result = await self.info_timer(timer)
                if result is None:
                    self.log(f"purging timer {timer}", level="WARNING")
                    self.timers.pop(key, None) # ignore value
                    continue
            else:
                self.log(f'\t{key} timer is no longer extant or key ({key}) is invalid. pruning', level='WARNING')
                self.timers.pop(key, None) # ignore value

# -----------------------------------------------------------------------------------

    def cancel_timers(self) -> None:
        """cancel timers"""

        self.log('\ttimers:')

        keys = list(self.timers)

        for key in keys:
            timer = self.timers.get(key)
            if self.timer_running(timer):
                time, interval, kwargs = self.info_timer(timer)
                self.log(f'\tname={key} timer={timer} time={time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}')
            else:
                self.log(f'\t{key} timer is no longer extant or key ({key}) is invalid. pruning', level='WARNING')
                self.timers.pop(key, None) # ignore value

# -----------------------------------------------------------------------------------

    def light_entities(self, name, count=1):
        """generate a list of light entity names"""

        entities = []

        for entity in range(1, count+1):
            entities.append(f'light.{name}_{entity}')

        return entities

# -----------------------------------------------------------------------------------

    def any_light_on_full(self, entity_ids)  -> bool:
        """is any light on full"""

        for entity_id in entity_ids:
            brightness = self.get_state(entity_id=entity_id, attribute="brightness")
            if brightness is not None and brightness >= 253:
                return True

        return False

# -----------------------------------------------------------------------------------

    def any_light_on(self, entity_ids)  -> bool:
        """is any light on"""

        for entity_id in entity_ids:
            if self.is_light_on(entity_id):
                return True

        return False

# -----------------------------------------------------------------------------------

    def is_light_on(self, entity_id)  -> bool:
        """is light on"""

        brightness = self.get_state(entity_id=entity_id, attribute="brightness")

        return brightness is not None and brightness >= 5

# -----------------------------------------------------------------------------------

    def lumie_off(self, kwargs) -> None:
        """turn off lumie light"""

        self.call_service('light/turn_off', entity_id=self.const.LUMIE, transition=10)

# -----------------------------------------------------------------------------------

    def landing_off(self, kwargs) -> None:
        """turn off landing light"""

        self.call_service('light/turn_off', entity_id=self.const.LUMIE, transition=10)
        self.call_service('light/turn_off', entity_id=self.const.LANDING, transition=10)
        self.call_service('light/turn_off', entity_id=self.const.BEDROOM2, transition=10)

# -----------------------------------------------------------------------------------

    def cloakroom_off(self, kwargs) -> None:
        """turn off cloakroom light"""

        self.call_service('light/turn_off', entity_id=self.const.CLOAKROOM, transition=10)

# -----------------------------------------------------------------------------------

    def welcome_lights_off(self, kwargs) -> None:
        """turn off welcome lights excluding standard lamp"""

        self.call_service('light/turn_off', entity_id=self.const.FRONT_DOOR, transition=10)
        self.call_service('light/turn_off', entity_id=self.const.HALLWAY1, transition=10)

# -----------------------------------------------------------------------------------

    def set_callback(self, cb=None, callback=None, seconds=60) -> None:

        if cb is not None:
            self._cancel_timer(cb)

        if callback is None:
            self.log('no callback specified', 'ERROR')
            traceback.print_stack()
        else:
            timer = self.run_in(callback, seconds, key=cb, seconds=seconds)
            self.set_timer(cb, timer)
            self.fire_event('timers')

# -----------------------------------------------------------------------------------

    def get_callback(self, cb):

        callback = None

        if cb is not None:
            callback = getattr(self, cb)

        return callback

# -----------------------------------------------------------------------------------

    def show_service(self,namespace, domain, service, data, cb=None, callback=None) -> None:

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} callback={callback}', level='DEBUG')

# -----------------------------------------------------------------------------------

