# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

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
        self.register_service('lighting/turn_on_if_off', self.turn_on_if_off_service)
        self.register_service('lighting/kitchen_on', self.kitchen_on_service)
        self.register_service('lighting/kitchen_floor_on', self.kitchen_floor_on_service)
        self.register_service('lighting/welcome_lights', self.welcome_lights_service)
        self.register_service('lighting/front_door_on', self.front_door_on_service)
        self.register_service('lighting/front_door_off', self.front_door_off_service)
        self.register_service('lighting/hallway_off', self.hallway_off_service)
        self.register_service('lighting/lumie_on', self.lumie_on_service)
        self.register_service('lighting/front_door_ding', self.front_door_ding_service)
        self.register_service('lighting/all_off', self.all_off_service)

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

        self.listen_event(self.test_welcome_lights_event, 'test_welcome_lights')

        self.run_daily(self.living_room_on, 'sunset + 00:10:00')
        self.run_daily(self.downstairs_off, '23:30:00')
        self.run_daily(self.outside_off, '21:30:00')
        self.run_daily(self.all_off, '02:00:00')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def all_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """all off service"""

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        self.fire_event('all_off')

# -----------------------------------------------------------------------------------

    def welcome_lights_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on welcome lights"""

        self.log_function_name(True, True)

        if not self.lib.is_night():
            self.log('\ttoo early for welcome lights', level='DEBUG')
            return

        print(data)

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))
        delay = int(data.get('xdelay', 0))

        if cb:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} key={key} interval={seconds} callback={callback} delay={delay}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.WELCOME_LIGHTS, brightness=128)
        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64)

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key) # , xdelay=delay)
            self.set_timer(key, timer)

        # print(**data)
        # self.fire_event('welcome_lights', **data)

# -----------------------------------------------------------------------------------

    def front_door_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on front door lights"""

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb is not None:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=128)
        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def front_door_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off front door lights"""

        self.call_service('light/turn_off', entity_id=self.const.FRONT_DOOR)

# -----------------------------------------------------------------------------------

    def kitchen_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb is not None:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} interval={seconds} key={key} callback={callback}', level='DEBUG')

        entity_ids = self.light_entities('kitchen', self.const.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights on', level='DEBUG')
        else:
            brightness = 128 if self.now_is_between('sunrise', 'sunset') else 64

            self.call_service('light/turn_on', entity_id=self.const.KITCHEN_LIGHTS, brightness=brightness)
            # self.call_service('light/turn_on', entity_id='light.kitchen_lights', brightness=brightness)

            if callback and seconds and key:
                timer = self.run_in(callback, seconds, key=key)
                self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def kitchen_floor_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb is not None:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'cb={cb} interval={seconds} key={key} callback={callback}', level='DEBUG')
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        brightness = 255 if self.now_is_between('sunrise', 'sunset') else 128

        self.call_service('light/turn_on', entity_id=self.const.KITCHEN_FLOOR_LIGHTS, brightness=brightness)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def utility_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb is not None:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} interval={seconds} key={key} callback={callback}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.UTILITY_ROOM_LIGHTS)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def lumie_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on lumie lights"""

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        self.fire_event('lumie_on')

# -----------------------------------------------------------------------------------

    def turn_on_if_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on a light if it off"""

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))
        brightness = int(data.get('brightness', 64))
        entity_id = data.get('entity_id', [])

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        prev_state = self.get_state(entity_id)
        prev_brightness = self.get_state(entity_id, attribute="brightness")

        if prev_state == 'off':
            if verbose:
                self.log(f'\tturn on {entity_id} brightness={brightness}', level='DEBUG')
            self.call_service('light/turn_on', entity_id=entity_id, brightness=brightness)
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)
        else:
            if verbose:
                self.log(f'\t{service}: ignored - {entity_id} already on brightness={prev_brightness}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def garage_on_service(self, namespace, domain, service, data) -> None:
        """turn on garage lights"""

        if self.lib.is_below_horizon():
            self.call_service('light/turn_on', entity_id=self.const.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def garage_off_service(self, namespace, domain, service, data) -> None:
        """turn off garage lights"""

        self.call_service('light/turn_off', entity_id=self.const.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def bannister_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on bannister and hallway lights"""

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb is not None:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64)
        self.call_service('light/turn_on', entity_id=self.const.BANNISTER, brightness=30)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def hallway_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off bannister and hallway lights"""


        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def front_door_ding_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on front door/hallway lights"""

        verbose = self.lib.get_verbose_debug()

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} interval={seconds} key={key} callback={callback}', level='DEBUG')
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        self.call_service('hue/activate_scene', entity_id='scene.front_door_hallway_front_door_ding', transition=10)
        # self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=200, transition=transition)
        # self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64, transition=transition)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

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

    def lights_off_event(self, event, data, kwargs:dict) -> None:
        """turn off all lights"""

        self.call_service('light/turn_off', entity_id=self.const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    async def status_event(self, event, data, kwargs:dict) -> None:

        await self.print_timers()

# -----------------------------------------------------------------------------------

    def cancel_timers_event(self, event, data, kwargs:dict) -> None:

        self.cancel_timers()

# -----------------------------------------------------------------------------------

    def welcome_lights_event(self, event, data, kwargs:dict) -> None:

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))
        delay = int(data.get('xdelay', 0))

        if cb:
            callback = getattr(self, cb)

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'event={event}, data={data}', level='DEBUG')
            self.log(f'cb={cb} key={key} interval={seconds} callback={callback} delay={delay}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.const.WELCOME_LIGHTS, brightness=128)
        self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64)

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP)

        if callback and seconds and key:
            if verbose:
                self.log(f'welcome_lights_service data={data}', level='DEBUG')

            timer = self.run_in(callback, seconds, key=key) # , xdelay=delay)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def front_door_on_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/front_door_on', seconds=10, cb='front_door_off', key='front_door')

# -----------------------------------------------------------------------------------

    def test_welcome_lights_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/welcome_lights', seconds=10, xdelay=10, cb='welcome_lights_off', key='welcome_lights')

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/front_door_ding', seconds=20, cb='front_door_hallway_off', key='front_door_ding')

# -----------------------------------------------------------------------------------

    def lumie_on_event(self, event, data, kwargs:dict) -> None:

        force = data.get('force', False)

        if self.now_is_between('23:30:00', '04:00:00') or force:
            self.call_service('light/turn_on', entity_id=self.const.LUMIE, brightness=4)
        else:
            self.log('\toutside time window for lumie', level='WARNING')

# -----------------------------------------------------------------------------------

    def lumie_wake_event(self, event, data, kwargs:dict) -> None:

        self.call_service('light/turn_on', entity_id='light.lumie', brightness=64, rgb_color=[255, 180, 10])

# -----------------------------------------------------------------------------------

    def stairs_on(self, kwargs:dict) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id=self.const.LANDING, brightness=5)

# -----------------------------------------------------------------------------------

    def radiator_on(self, kwargs:dict) -> None:
        """turn on radiator light"""

        self.call_service('light/turn_on', entity_id=self.const.RADIATOR)

# -----------------------------------------------------------------------------------

    def living_room_on(self, kwargs:dict) -> None:
        """turn on living room lights"""

        for entity_id in self.const.LIVING_ROOM_LIGHTS:
            if not self.is_light_on(entity_id):
                self.call_service('light/turn_on', entity_id=entity_id, brightness=30)

# -----------------------------------------------------------------------------------

    def hallway_on(self, kwargs:dict) -> None:

        verbose = self.lib.get_verbose_debug()

        if self.lib.is_night():  # civil dusk till civil dawn
            if verbose:
                self.log('\tturn on hallway light', level='DEBUG')

            self.call_service('light/turn_on', entity_id=self.const.HALLWAY1, brightness=64, transition=5)

# -----------------------------------------------------------------------------------

    def front_door_on(self, kwargs:dict) -> None:

        if self.now_is_between('sunset', 'sunrise + 0:20:00'):
            if self.lib.is_below_horizon():
#             brightness = self.get_state('light.front_door_1', attribute='brightness')
#             state = self.get_state('light.front_door_1')
                self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=5)
                self.call_service('light/turn_on', entity_id=self.const.FRONT_DOOR, brightness=128, transition=10)
            else:
                self.run_in(self.front_door_light_on, 60)  # respawn self in 60s

# -----------------------------------------------------------------------------------

    def bannister_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off bannister - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.const.NIGHTTIME_LIGHTS)

# -----------------------------------------------------------------------------------

    def kitchen_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off kitchen - {key}', level='WARNING')

        entity_ids = self.light_entities('kitchen', self.const.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.const.KITCHEN_LIGHTS)

# -----------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off kitchen floor lights - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.const.KITCHEN_FLOOR_LIGHTS)

# -----------------------------------------------------------------------------------

    def utility_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off utility - {key}', level='WARNING')

        entity_ids = self.light_entities('utility') # just 1

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - utiltity lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.const.UTILITY_ROOM_LIGHTS)

# -----------------------------------------------------------------------------------

    def front_door_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off front door - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.const.FRONT_DOOR, transition=10)

# -----------------------------------------------------------------------------------

    def front_door_hallway_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        hallway_lights = self.light_entities('hallway', self.const.N_HALLWAY_ENTITIES - 1) # pylint: disable=C0103 disable=W0201

        self.front_door_off(kwargs)

        if key is not None:
            self.log(f'\tturn off hallway - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=hallway_lights, transition=10)

# -----------------------------------------------------------------------------------

    def outside_off(self, kwargs:dict) -> None:
        """turn off outside lights"""

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off outside - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.const.OUTSIDE_LIGHTS)

# -----------------------------------------------------------------------------------

    def downstairs_off(self, kwargs:dict) -> None:
        """turn off downstairslights"""

        self.call_service('light/turn_off', entity_id=self.const.LIVING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.STANDARD_LAMP) # try again - wasn't switching off
        self.call_service('light/turn_off', entity_id=self.const.UTILITY_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.DINING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.const.OUTSIDE_LIGHTS)
        self.call_service('switch/turn_off', entity_id=self.const.COOKER_LIGHTS)

# -----------------------------------------------------------------------------------

    def all_off(self, kwargs:dict) -> None:

        self.call_service('light/turn_off', entity_id=self.const.ALL_LIGHTS)

# -----------------------------------------------------------------------------------

    def hallway_off(self, kwargs:dict) -> None:

        self.call_service('light/turn_off', entity_id=self.const.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def welcome_lights_off(self, kwargs:dict) -> None:
        """turn off welcome lights"""

        delay = kwargs.get('xdelay', 5*60)

        self.call_service('light/turn_off', entity_id=self.const.OUTSIDE_LIGHTS)

        # delay turning off hallway
        self.call_service('lighting/hallway_off', seconds=delay, cb='hallway_off', key='hallway')

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', self.const.STANDARD_LAMP)
            self.call_service('light/turn_off', self.const.HALLWAY1)

# -----------------------------------------------------------------------------------

    def set_timer(self, name:str, timer:str) -> None:
        """set a timer"""

        verbose = self.lib.get_verbose_debug()

        old = self.timers.get(name, None)

        if old is not None:
            if self.check_timer(name, old):
                self.log(f'\t\treplacing name={name} old={old} with new={timer}', level='DEBUG')
                self._cancel_timer(name)

        if verbose:
            self.log(f'\t\tadding new timer name={name} timer={timer}')

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
            self.log(f'\t\tdid not find timer name={name}', level='WARNING')
        else:
            if verbose:
                self.log(f'\t\treturning name={name} timer={timer}', level='DEBUG')

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name:str) -> None:
        """cancel a timer callback"""

        verbose = self.lib.get_verbose_debug()

        timer = self.get_timer(name)

        if timer is not None:
            # self.check_timer('cancel', timer)

            if verbose:
                self.log(f'\t\tcancelling running timer name={name} timer={timer}', level='DEBUG')

            self.cancel_timer(timer)
            self.timers.pop(name)
        else:
            self.log(f'_cancel_timer did not find timer name={name}', level='ERROR')

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        verbose = self.lib.get_verbose_debug()

        timer = self.timers.get(name, None)

        if timer is not None:
            if verbose:
                self.log(f'\t\tremoving timer name={name} timer={timer}')

            self.timers.pop(name)
        else:
            self.log(f'\t\tremove_timer did not find timer name={name}', level='WARNING')

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
        self.log(f'\t\tname={name} timer={timer} time={time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}')

        return True

# -----------------------------------------------------------------------------------

    async def print_timers(self) -> None:
        """print timers"""

        status = '\n\n\ttimers:\n\n'

        keys = list(self.timers)

        for key in keys:
            print(key)
            timer = self.timers.get(key, None)
            print(timer)
            if timer is not None and self.timer_running(timer):
                time, interval, kwargs = await self.info_timer(timer)
                status += f'\tname={key} timer={timer} time={time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}\n'
            else:
                self.log(f'\t{key} timer is no longer extant or key ({key}) is invalid. pruning', level='WARNING')
                self.timers.pop(key, None) # ignore value

        self.log(f'{status}')

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
            if brightness is not None and brightness >= 250:
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
