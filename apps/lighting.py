# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

class Lighting(Hass):
    """Documentation for Lighting"""

    lib = None
    timers = {}

    RADIATOR = ['light.radiator']
    TABLE_LAMP = ['light.table_lamp_1']
    STANDARD_LAMP = ['light.standard_lamp_1']
    BANNISTER = ['light.bannister']
    HALLWAY = ['light.hallway_1']
    FRONT_DOOR = ['light.front_door_1']
    UTILITY = ['light.utility_room_1']
    LANDING = ['light.hallway_3']
    LUMIE = ['light.lumie']

    GARAGE_LIGHTS = ['light.garage'] # group
    KITCHEN_LIGHTS = ['light.kitchen'] # group
    KITCHEN_FLOOR_LIGHTS = ['light.kitchen_floor'] # group
    UPSTAIRS_DOWNSTAIRS_LIGHTS = ['light.upstairs', 'light.downstairs']

    OUTSIDE_LIGHTS = GARAGE_LIGHTS + FRONT_DOOR
    WELCOME_LIGHTS = HALLWAY + FRONT_DOOR + STANDARD_LAMP
    NIGHTTIME_LIGHTS = HALLWAY + BANNISTER
    LIVING_ROOM_LIGHTS = RADIATOR + TABLE_LAMP + STANDARD_LAMP
    HALLWAY_GARAGE_LIGHTS = HALLWAY + GARAGE_LIGHTS + FRONT_DOOR
    FRONT_DOOR_DING_LIGHTS = HALLWAY + FRONT_DOOR

    N_KITCHEN_ENTITIES = 6
    N_KITCHEN_FLOOR_ENTITIES = 2
    N_HALLWAY_ENTITIES = 3

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.HALLWAY_LIGHTS = self.light_entities('hallway', self.N_HALLWAY_ENTITIES) # pylint: disable=C0103 disable=W0201
        # self.KITCHEN_LIGHTS = self.light_entities('kitchen', self.N_KITCHEN_ENTITIES) # pylint: disable=C0103 disable=W0201
        # self.KITCHEN_FLOOR_LIGHTS = self.light_entities('kitchen_floor', self.N_KITCHEN_FLOOR_ENTITIES) # pylint: disable=C0103 disable=W0201

        self.register_service('lighting/garage_on', self.garage_on_service)
        self.register_service('lighting/garage_off', self.garage_off_service)
        self.register_service('lighting/bannister_on', self.bannister_on_service)
        self.register_service('lighting/utility_on', self.utility_on_service)
        self.register_service('lighting/turn_on_if_off', self.turn_on_if_off_service)
        self.register_service('lighting/kitchen_on', self.kitchen_on_service)
        self.register_service('lighting/kitchen_floor_on', self.kitchen_floor_on_service)
        self.register_service('lighting/welcome_lights', self.welcome_lights_service)
        self.register_service('lighting/front_door_on', self.front_door_on_service)
        self.register_service('lighting/hallway_off', self.hallway_off_service)
        self.register_service('lighting/lumie_on', self.lumie_on_service)
        self.register_service('lighting/front_door_ding', self.front_door_ding_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timers')
        self.listen_event(self.cancel_timers_event, 'cancel_timers')
        self.listen_event(self.welcome_lights_event, 'welcome_lights') # see location for the real welcome_lights event handler
        self.listen_event(self.front_door_on_event, 'front_door_on')
        self.listen_event(self.front_door_ding_event, 'front_door_ding_lights')
        self.listen_event(self.lights_off_event, "ios.action_fired", actionName='Lights')

        self.run_daily(self.living_room_on, 'sunset + 00:10:00')
        self.run_daily(self.living_room_off, '23:30:00')
        self.run_daily(self.outside_off, '21:30:00')
        self.run_daily(self.downstairs_off, '02:00:00')
        self.run_daily(self.stairs_on, 'sunset + 00:10:00')
        # self.run_daily(self.radiator_on, "sunset + 00:10:00")

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    def welcome_lights_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on welcome lights"""

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        if not self.lib.is_night():
            return

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))
        delay = int(data.get('delay', 0))

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} key={key} interval={seconds} callback={callback} delay={delay}', level='DEBUG')

        self.run_sequence(
            [
                {'light/turn_on': {'entity_id': self.WELCOME_LIGHTS, 'brightness': 128}},
                {'light/turn_on': {'entity_id': self.HALLWAY, 'brightness': 64}},
            ]
        )

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', entity_id=self.STANDARD_LAMP)

        if callback and seconds and key:
            if verbose:
                self.log(f'welcome_lights_service data={data}', level='DEBUG')

            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def front_door_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on front door lights"""

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        self.run_sequence(
            [
                {'light/turn_on': {'entity_id': self.FRONT_DOOR, 'brightness': 128}},
                {'light/turn_on': {'entity_id': self.HALLWAY, 'brightness': 64}},
            ]
        )

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def kitchen_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

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

        entity_ids = self.light_entities('kitchen', self.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights on', level='DEBUG')
        else:
            brightness = 128 if self.now_is_between('sunrise', 'sunset') else 64

            self.call_service('light/turn_on', entity_id=self.KITCHEN_LIGHTS, brightness=brightness)

            if callback and seconds and key:
                timer = self.run_in(callback, seconds, key=key)
                self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def kitchen_floor_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

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

        brightness = 255 if self.now_is_between('sunrise', 'sunset') else 128

        self.call_service('light/turn_on', entity_id=self.KITCHEN_FLOOR_LIGHTS, brightness=brightness)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def utility_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if self.lib.get_verbose_debug():
            self.log(f'cb={cb} interval={seconds} key={key} callback={callback}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.UTILITY_LIGHTS)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def lumie_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on utility lights"""

        if self.lib.get_verbose_debug():
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        if self.now_is_between('23:30:00', '03:00:00'):
            self.call_service('light/turn_on', entity_id=self.LUMIE, brightness=10)

# -----------------------------------------------------------------------------------

    def turn_on_if_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn on a light if it off"""

        # self.lib.log_function_name()

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

        # self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def garage_on_service(self, namespace, domain, service, data) -> None:
        """turn on garage lights"""

        self.call_service('light/turn_on', entity_id=self.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def garage_off_service(self, namespace, domain, service, data) -> None:
        """turn off garage lights"""

        self.call_service('light/turn_off', entity_id=self.GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def bannister_on_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off garage lights"""

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        self.call_service('light/turn_on', entity_id=self.NIGHTTIME_LIGHTS)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def hallway_off_service(self, namespace:str, domain:str, service:str, data:dict) -> None:
        """turn off garage lights"""

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'namespace={namespace}, domain={domain}, service={service}, data={data}', level='DEBUG')

        callback = None
        cb = data.get('cb', None)
        key = data.get('key', None)
        seconds = int(data.get('seconds', 0))

        if cb:
            callback = getattr(self, cb)

        if verbose:
            self.log(f'cb={cb} interval={seconds} callback={callback}', level='DEBUG')

        # just call callback

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
        # self.call_service('light/turn_on', entity_id=self.FRONT_DOOR, brightness=200, transition=transition)
        # self.call_service('light/turn_on', entity_id=self.HALLWAY, brightness=64, transition=transition)

        if callback and seconds and key:
            timer = self.run_in(callback, seconds, key=key)
            self.set_timer(key, timer)

# -----------------------------------------------------------------------------------

    def lights_off_event(self, event, data, kwargs:dict) -> None:
        """turn off hallway, garage and front door lights"""

        self.call_service('light/turn_off', entity_id=self.HALLWAY_GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    async def status_event(self, event, data, kwargs:dict) -> None:

        await self.print_timers()

# -----------------------------------------------------------------------------------

    def cancel_timers_event(self, event, data, kwargs:dict) -> None:

        self.cancel_timers()

# -----------------------------------------------------------------------------------

    def welcome_lights_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/welcome_lights', seconds=10, delay=10, cb='welcome_lights_off', key='welcome_lights')

# -----------------------------------------------------------------------------------

    def front_door_on_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/front_door_on', seconds=10, cb='front_door_off', key='front_door')

# -----------------------------------------------------------------------------------

    def front_door_ding_event(self, event, data, kwargs:dict) -> None:

        self.call_service('lighting/front_door_ding', seconds=20, cb='front_door_hallway_off', key='front_door_ding')

# -----------------------------------------------------------------------------------

    def stairs_on(self, kwargs:dict) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id=self.LANDING, brightness=5)

# -----------------------------------------------------------------------------------

    def radiator_on(self, kwargs:dict) -> None:
        """turn on radiator light"""

        self.call_service('light/turn_on', entity_id=self.RADIATOR)

# -----------------------------------------------------------------------------------

    def living_room_on(self, kwargs:dict) -> None:
        """turn on living room lights"""

        for entity_id in self.LIVING_ROOM_LIGHTS:
            if not self.is_light_on(entity_id):
                self.call_service('light/turn_on', entity_id=entity_id, brightness=30)

# -----------------------------------------------------------------------------------

    def hallway_on(self, kwargs:dict) -> None:

        verbose = self.lib.get_verbose_debug()

        if self.lib.is_night():  # civil dusk till civil dawn
            if verbose:
                self.log('\tturn on hallway light', level='DEBUG')

            self.call_service('light/turn_on', entity_id=self.HALLWAY, brightness=64, transition=5)

# -----------------------------------------------------------------------------------

    def front_door_on(self, kwargs:dict) -> None:

        if self.now_is_between('sunset', 'sunrise + 0:20:00'):
            if self.lib.is_below_horizon():
#             brightness = self.get_state('light.front_door_1', attribute='brightness')
#             state = self.get_state('light.front_door_1')
                self.call_service('light/turn_on', entity_id=self.FRONT_DOOR, brightness=5)
                self.call_service('light/turn_on', entity_id=self.FRONT_DOOR, brightness=128, transition=10)
            else:
                self.run_in(self.front_door_light_on, 60)  # respawn self in 60s

# -----------------------------------------------------------------------------------

    def bannister_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off bannister - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.NIGHTTIME_LIGHTS)

# -----------------------------------------------------------------------------------

    def kitchen_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off kitchen - {key}', level='WARNING')

        entity_ids = self.light_entities('kitchen', self.N_KITCHEN_ENTITIES)

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - kitchen lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.KITCHEN_LIGHTS)

# -----------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off kitchen floor lights - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.KITCHEN_FLOOR_LIGHTS)

# -----------------------------------------------------------------------------------

    def utility_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off utility - {key}', level='WARNING')

        entity_ids = self.light_entities('utility') # just 1

        if self.any_light_on_full(entity_ids):
            self.log('\tdeferring - utiltity lights high', level='DEBUG')
        else:
            self.call_service('light/turn_off', entity_id=self.UTILITY)

# -----------------------------------------------------------------------------------

    def front_door_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off front door - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.FRONT_DOOR, transition=10)

# -----------------------------------------------------------------------------------

    def front_door_hallway_off(self, kwargs:dict) -> None:

        key = kwargs.get('key', None)

        self.front_door_off(kwargs)

        if key is not None:
            self.log(f'\tturn off hallway - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def outside_off(self, kwargs:dict) -> None:
        """turn off outside lights"""

        key = kwargs.get('key', None)

        if key is not None:
            self.log(f'\tturn off outside - {key}', level='WARNING')

        self.call_service('light/turn_off', entity_id=self.HALLWAY_GARAGE_LIGHTS)

# -----------------------------------------------------------------------------------

    def living_room_off(self, kwargs:dict) -> None:
        """turn off living room lights"""

        self.call_service('light/turn_off', entity_id=self.LIVING_ROOM_LIGHTS)
        self.call_service('light/turn_off', entity_id=self.STANDARD_LAMP) # try again - wasn't switching off

# -----------------------------------------------------------------------------------

    def downstairs_off(self, kwargs:dict) -> None:

        self.call_service('light/turn_off', entity_id=self.UPSTAIRS_DOWNSTAIRS_LIGHTS)

# -----------------------------------------------------------------------------------

    def hallway_off(self, kwargs:dict) -> None:

        self.call_service('light/turn_off', entity_id=self.HALLWAY_LIGHTS, transition=10)

# -----------------------------------------------------------------------------------

    def welcome_lights_off(self, kwargs:dict) -> None:
        """turn off welcome lights"""

        delay = kwargs.get('delay', 5*60)

        self.call_service('light/turn_off', entity_id=self.OUTSIDE_LIGHTS)

        # delay turning off hallway
        # self.call_service('lighting/hallway_off', seconds=delay, cb='hallway_off', key='hallway')

        if self.now_is_between('05:00:00', '06:30:00'):
            self.call_service('light/turn_off', self.STANDARD_LAMP)
            self.call_service('light/turn_off', self.HALLWAY)

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
            timer = self.timers.get(key, None)
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
