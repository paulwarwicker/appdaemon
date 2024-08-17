# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import inspect
import math
import traceback
from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from appdaemon.plugins.hass.hassapi import Hass  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Automation(Hass):
    """Documentation for Automation"""

    debug = False
    testing = False
    verbose = False
    override = False
    downstairs_motion_flag = False

    lib = None
    tap_ts = None
    tap_ts = datetime(2024, 8, 16, 19, 30, 0)
    log_level = None
    stairs_timer = None
    utility_timer = None
    kitchen_timer = None
    kitchen_long_timer = None
    kitchen_floor_timer = None
    utility_long_timer = None

    handlers = {}

    default_early_alarm_schedule = 'daily'  # weekday|daily|none

    upstairs_ts = datetime.now()
    downstairs_ts = datetime.now()
    initialise_ts = datetime.now()
    prev_upstairs_ts = datetime.now()
    karoq_announce_ts = datetime.now()
    garage_announce_ts = datetime.now()
    vacuum_announce_ts = datetime.now()
    general_announce_ts = datetime.now() + timedelta(minutes=-15)
    travel_announce_ts = datetime.now() + timedelta(minutes=-15)

    DAILY_WATERING_MINUTES = 30
    GARAGE_ENTITY_ID = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'
    KAROQ_ENTITY_ID = 'binary_sensor.tmbkr7nu5p5079987_doors_locked'
    MAXINE_ENTITY_ID = 'device_tracker.maxine_iphone'
    PAUL_ENTITY_ID = 'device_tracker.paulw_iphone'
    BROADCAST_ENTITY_ID = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
    OTHER_ENTITY_IDd = ['media_player.study', 'media_player.bedroom_2']

# -------------------------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.log('-'*72)

        self.lib = AutomationLib(self)

        self.register_service('automation/set_downstairs_motion_flag', self.set_downstairs_motion_flag)
        self.register_service('automation/log_function_name', self._log_function_name)
        self.register_service('automation/max_home', self.max_home_service)

        self.debug = True if self.get_state('input_boolean.default_debug_state') == 'on' else False
        self.verbose = True if self.get_state('input_boolean.default_verbose_state') == 'on' else False
        self.testing = True if self.get_state('input_boolean.default_testing_state') == 'on' else False

        self.listen_event(self.lights_off, "ios.action_fired", actionName='Lights')
        self.listen_event(self.water_garden_for_action, "ios.action_fired", actionName='Water15', minutes=15)
        self.listen_event(self.set_all_state_event, 'set_all_state')
        self.listen_event(self.status_event, 'status')
        self.listen_event(self.max_home_event, 'max_home')
        self.listen_event(self.water_garden_event, 'water_garden')

        # self.listen_state(self.paul_home, self.PAUL_ENTITY_ID)
        self.listen_state(self.garage_door_open, self.PAUL_ENTITY_ID, old='not_home', new='home')
        self.listen_state(self.garage_door_close, self.PAUL_ENTITY_ID, old='home', new='not_home')
        self.listen_state(self.max_home, self.MAXINE_ENTITY_ID, new='Home')

        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_1', new='on', minutes=1)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_1', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_15', new='on', minutes=15)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_15', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_20', new='on', minutes=20)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_20', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_30', new='on', minutes=30)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_30', new='off')

        self.listen_state(self.garage_door_announce_opening, self.GARAGE_ENTITY_ID, new='opening')
        self.listen_state(self.garage_door_announce_closing, self.GARAGE_ENTITY_ID, new='closing')
        self.listen_state(self.garage_door_announce_open, self.GARAGE_ENTITY_ID, new='open')
        self.listen_state(self.garage_door_announce_closed, self.GARAGE_ENTITY_ID, new='closed')
        self.listen_state(self.garage_door_debug, self.GARAGE_ENTITY_ID)

        self.listen_state(self.set_console_log_level, 'input_boolean.debug', new='on')
        self.listen_state(self.set_console_log_level, 'input_boolean.debug', new='off')

        # self.listen_state(self.garden_tap_on, 'switch.garden_tap', new='on')
        # self.listen_state(self.garden_tap_off, 'switch.garden_tap', new='off')

        self.listen_state(self.front_door_ding, 'binary_sensor.front_door_ding', old='off', new='on')

        self.listen_state(self.kitchen_motion, 'binary_sensor.kitchen_sensor_motion', old='off', new='on', timer=300, location='kitchen')
        self.listen_state(self.utility_motion, 'binary_sensor.utility_room_motion_sensor_motion', old='off', new='on', timer=300, location='utility')
        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion', old='off', new='on', timer=300, check_override=True, location='downstairs')
        self.listen_state(self.upstairs_motion, 'binary_sensor.upstairs_sensor_motion', old='off', new='on', timer=600, check_override=False, location='upstairs')

        self.listen_state(self.reset_test1, 'input_boolean.test_1', new='on')
        self.listen_state(self.reset_test2, 'input_boolean.test_2', new='on')

        self.listen_state(self.fire_status_event, 'input_boolean.status', new='on')
        self.listen_state(self.set_debug_flag, 'input_boolean.debug')
        self.listen_state(self.set_verbose_flag, 'input_boolean.verbose')
        self.listen_state(self.vacuum_debug, 'vacuum.s7_max_ultra')

        # self.listen_state(self.set_utility_motion_test, 'input_boolean.test_utility_motion', new='on', action='set')
        # self.listen_state(self.set_utility_motion_test, 'input_boolean.test_utility_motion', new='off', action='cancel')
        # self.listen_state(self.set_bins_test, 'input_boolean.test_bins_announce', new='on', action='set')
        # self.listen_state(self.set_bins_test, 'input_boolean.test_bins_announce', new='off', action='cancel')
        # self.listen_state(self.set_frost_warning_test, 'input_boolean.test_frost_warning', new='on', action='set')
        # self.listen_state(self.set_frost_warning_test, 'input_boolean.test_frost_warning', new='off', action='cancel')
        # self.listen_state(self.set_notification_test, 'input_boolean.test_notification', new='on', action='set')
        # self.listen_state(self.set_notification_test, 'input_boolean.test_notification', new='off', action='cancel')
        # self.listen_state(self.set_announcement_test, 'input_boolean.test_announcement', new='on', action='set')
        # self.listen_state(self.set_announcement_test, 'input_boolean.test_announcement', new='off', action='cancel')
        # self.listen_state(self.set_max_home_test, 'input_boolean.test_max_home', new='on', action='set')
        # self.listen_state(self.set_max_home_test, 'input_boolean.test_max_home', new='off', action='cancel')
        # self.listen_state(self.set_front_door_ding_test, 'input_boolean.test_front_door_ding', new='on', action='set')
        # self.listen_state(self.set_front_door_ding_test, 'input_boolean.test_front_door_ding', new='off', action='cancel')
        # self.listen_state(self.set_front_door_light_on_test, 'input_boolean.test_front_door_light_on', new='on', action='set')
        # self.listen_state(self.set_front_door_light_on_test, 'input_boolean.test_front_door_light_on', new='off', action='cancel')
        # self.listen_state(self.set_test_test, 'input_boolean.test_test', new='on', action='set')
        # self.listen_state(self.set_test_test, 'input_boolean.test_test', new='off', action='cancel')
        # self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='on', action='set')
        # self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='off', action='cancel')
        # self.log('\tset* (for input_booleans) registered')

        # daily reset including booleans
        self.run_daily(self.reset, '04:00:00')

        # set state
        self.run_daily(self.set_all_state, '21:00:10') # pre-set - make sure before max retires (to bed)
        self.run_daily(self.set_all_state, '00:00:10') # re-set - possibly dodgy as won't be confirmed before max retires

        self.run_daily(self.downstairs_off, '02:00:00')

        self.run_daily(self.frost_warning, "sunset + 00:00:00")
        self.run_daily(self.frost_warning, "sunset + 01:00:00")

        self.run_daily(self.backup, '23:30:00')

        self.run_daily(self.stairs_on, "sunset + 00:00:00")

        self.run_daily(self.radiator_on, "sunset + 00:10:00")

        self.run_daily(self.living_room_lights_off, "23:30:00")

        self.run_daily(self.front_door_battery, "19:29:00")

        self.run_daily(self.water_garden_daily, '19:30:00')  # , 'minutes': 10)

        self.run_daily(self.outside_lights_off, "21:30:00")

        # self.run_daily(self.rearm_kitchen_alarm, '07:00:30')
        # self.run_daily(self.wardrobe_on, '07:00:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.max_travel_time_to_home, runtime)
        self.run_minutely(self.check_garden_tap, runtime)
        self.run_minutely(self.check_garage_door, runtime)
        self.run_minutely(self.check_karoq_door, runtime)

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.update_openweathermap, runtime)
        self.run_hourly(self.check_roborock, runtime)

        # interval = timedelta(minutes=5)
        # self.run_every(self.update_openweathermap, "now", interval.total_seconds())
        # self.log('\trun_every registered')

        self.set_all_state()
        self.run_in_thread(self.backup, 0)
        self._set_console_log_level()

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

        # self.dummy()

# -------------------------------------------------------------------------------------------------

    def dummy(self) -> None:
        """dummy"""

        self.log_function_name()
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def set_all_state(self, kwargs={}) -> None:
        """set all state - reset to false and then set_default_state"""

        self.log_function_name()

        booleans = {
            # !!! do NOT include debug/verbose/testing !!!
            # 'early_alarm', 'normal_alarm', 'test_alarm',
            'lumie', 'test_1', 'test_2', 'test_3', 'sonos',
            'water_garden_1', 'water_garden_15', 'water_garden_20', 'water_garden_30', 'bedtime',
            'reset_alarms', 'test_utility_motion', 'test_kitchen_motion', 'test_bins_announce', 'test_frost_warning', 'test_notification',
            'test_announcement', 'test_max_home', 'test_reset', 'test_front_door_ding', 'test_front_door_light_on', 'test_test',
            'test_early_alarm', 'mock_run', 'alarm_debug'
        }

        for boolean in booleans:
            self.set_state(f'input_boolean.{boolean}', state='off')

        self.set_default_state()

        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def set_console_log_level(self, entity, attribute, old, new, kwargs) -> None:
        """set console log level depending on the debug flag"""

        self._set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def _set_console_log_level(self) -> None:
        """internal method to set console level using the debug flag. set the property log_level and report a change"""

        level = "DEBUG" if self.get_state('input_boolean.debug') == 'on' else "INFO"

        if self.log_level != level:
            self.log(f'\tchanging log level to {level}', level='INFO')
            self.set_log_level(level)
            self.fire_event("set_log_level", level=level)
            self.log_level = level
        # else:
        #     self.log(f'\tlog level unchanged ({level})', level='INFO')

# -------------------------------------------------------------------------------------------------

    def set_debug_flag(self, entity, attribute, old, new, kwargs={}) -> None:
        """set debug flag"""

        self.debug = True if new == 'on' else False
        self.log(f'\tautomation debug now {self.debug}', level='INFO')
        self._set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def set_verbose_flag(self, entity, attribute, old, new, kwargs={}) -> None:
        """set verbose flag"""

        self.verbose = True if new == 'on' else False
        self.log(f'\tautomation verbose now {self.verbose}', level='INFO')
        self._set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def set_testing_flag(self, entity, attribute, old, new, kwargs={}) -> None:
        """set testing flag"""

        self.testing = True if new == 'on' else False
        self.log(f'\tautomation testing now {self.testing}', level='INFO')
        self._set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def reset_test1(self, entity, attribute, old, new, kwargs={}) -> None:
        """reset test_1 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_1', state='off')

# -------------------------------------------------------------------------------------------------

    def reset_test2(self, entity, attribute, old, new, kwargs={}) -> None:
        """reset test_2 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_2', state='off')

# -------------------------------------------------------------------------------------------------

    def reset_test3(self, entity, attribute, old, new, kwargs={}) -> None:
        """reset test_3 flag"""

        self.delay(0.5)
        self.set_state('input_boolean.test_3', state='off')

# -------------------------------------------------------------------------------------------------

    def set_default_state(self) -> None:
        """set default values from backstop default values"""

        # self.set_state('input_boolean.early_alarm', state=self.get_state('input_boolean.default_early_alarm_state'))
        self.set_state('input_boolean.normal_alarm', state=self.get_state('input_boolean.default_normal_alarm_state'))
        self.set_state('input_boolean.lumie', state=self.get_state('input_boolean.default_lumie_state'))
        self.set_state('input_boolean.debug', state=self.get_state('input_boolean.default_debug_state'))
        self.set_state('input_boolean.verbose', state=self.get_state('input_boolean.default_verbose_state'))
        self.set_state('input_boolean.testing', state=self.get_state('input_boolean.default_testing_state'))

# -------------------------------------------------------------------------------------------------

    def register_test(self, callback, entity_id='input_boolean.test_1', **kwargs) -> None:
        """register test"""

        handler = self.listen_state(callback, entity_id, **kwargs)
        self.log(f'\tcallback {callback.__name__} registered on {entity_id}', level='WARNING')
        self.handlers[entity_id] = handler

# -------------------------------------------------------------------------------------------------

    def deregister_test(self, entity_id, **kwargs) -> None:
        """deregister test"""

        handler = self.handlers[entity_id] if entity_id in self.handlers else None
        if handler is not None:
            self.log(f'\tcallback {handler} deregistered on {entity_id}', level='WARNING')
            self.cancel_listen_state(handler, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_1(self, callback, entity_id='input_boolean.test_1', **kwargs) -> None:
        """register test 1"""

        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_2(self, callback, entity_id='input_boolean.test_2', **kwargs) -> None:
        """register test 2"""

        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_3(self, callback, entity_id='input_boolean.test_3', **kwargs) -> None:
        """register test 3"""

        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_1(self, **kwargs) -> None:
        """deregister test 1"""

        self.deregister_test('input_boolean.test_1', **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_2(self, **kwargs) -> None:
        """deregister test 2"""

        self.deregister_test('input_boolean.test_2', **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_3(self, **kwargs) -> None:
        """deregister test 3 and unset test_3 flag"""

        self.deregister_test('input_boolean.test_3', **kwargs)
        self.set_state('input_boolean.test_3', state='off')

# ---------------------------------------------------------------------------------------------------------

    def test_test(self, entity, attribute, old, new, kwargs) -> None:
        """test test"""

        self.log_function_name()
        self.run_in(self.test, 0)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def test(self, kwargs={}) -> None:
        """test method"""

        self.log_function_name()
        traceback.print_stack() # leave
        # future_time = self.parse_time('07:00:00')
        # self.log(future_time)
        # self.log(future_time.hour)
        # self.log(future_time.minute)
        # self.log(future_time.second)
        # self.set_all_state()
        state = self.get_state(entity_id='media_player.kitchen', attribute="all")
        self.log(f'{state}')
        attributes = state['attributes']
        self.log(f'{attributes}')
        media_content_id = attributes.get('media_content_id', '')
        media_content_type = attributes.get('media_content_type', '')
        muted = attributes.get('is_volume_muted', True)
        self.log(f'{media_content_type} {media_content_id} {muted}')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def reset(self, kwargs={}) -> None:
        """reset dowstairs motion flag and set default sonos configuration"""

        self.reset_downstairs_motion_flag()
        self.sonos_unjoin_all({})
        self.sonos_configure1({})  # failsafe for bank holiday

        self.set_state('input_boolean.override', state='off')
        self.set_state('input_boolean.sonos', state='off')
        self.set_state('input_boolean.test_1', state='off')
        self.set_state('input_boolean.test_2', state='off')
        self.set_state('input_boolean.test_3', state='off')
        self.log('\treset')

# ---------------------------------------------------------------------------------------------------------

    def notification(self, message, log=False, title='') -> None:
        """send notification to log, tv and discord"""

        if log or self.get_state('input_boolean.debug') == 'on':
            self.log(f'\tmessage="{message}" title="{title}"')

        self.call_service('notify/lg_webos_tv_oled65c7v', message=message)
        self.call_service('notify/disc0rd', title=title, message=message, target="1250932196613685313")

# -------------------------------------------------------------------------------------------------

    def desktop_notification(self, message) -> None:
        """send desktop notification to discord using announcer"""

        self.call_service('announcer/desktop_notification', message=message)

# -------------------------------------------------------------------------------------------------

    def announce(self, message, entity_id=None, kwargs={}) -> None:
        """announce to a single device using announcer"""

        self.call_service("announcer/announce", entity_id=entity_id, message=message, snapshot=False)

# -------------------------------------------------------------------------------------------------

    def broadcast(self, volume, message) -> None:
        """broadcast to multiple devices using announcer"""

        self.call_service("announcer/broadcast", BROADCAST_ENTITY_ID=self.BROADCAST_ENTITY_ID, OTHER_ENTITY_IDd=self.OTHER_ENTITY_IDd, volume=volume, message=message, snapshot=False)

# ---------------------------------------------------------------------------------------------------------

    def is_garage_door_closed(self) -> bool:
        """is garage door closed"""

        state = self.get_state(self.GARAGE_ENTITY_ID)

        return state == 'closed'

# ---------------------------------------------------------------------------------------------------------

    def turn_on_if_off(self, entity_id, brightness=64): # -> Any
        """turn on a light if it off"""

        prev_state = self.get_state(entity_id)
        prev_brightness = self.get_state(entity_id, attribute="brightness")
        debug = self.debug

        if prev_state == 'off':
            if debug:
                self.log(f'\tturn on {entity_id} brightness={brightness}', level='DEBUG')
            self.call_service('light/turn_on', entity_id=entity_id, brightness=brightness)
        else:
            if debug:
                self.log(f'\tignored - {entity_id} already on brightness={prev_brightness}', level='DEBUG')
        return prev_state

# ---------------------------------------------------------------------------------------------------------

    # def rearm_kitchen_alarm(self, kwargs={}) -> None:
    #     """rearm kitch alarm"""

    #     self.call_service('switch/turn_on', entity_id='switch.sonos_alarm_1392')

# ---------------------------------------------------------------------------------------------------------

    def reset_downstairs_motion_flag(self) -> None:
        """reset downstairs motion flag"""

        self.log(f'\tdownstairs_motion_flag was {self.downstairs_motion_flag} now False')
        self.downstairs_motion_flag = False

# ---------------------------------------------------------------------------------------------------------

    def any_light_on_full(self, entity_ids)  -> bool:
        """is any light on full"""

        for entity_id in entity_ids:
            brightness = self.get_state(entity_id=entity_id, attribute="brightness")
            if brightness is not None and brightness >= 250:
                return True

        return False

# ---------------------------------------------------------------------------------------------------------

    def light_entities(self, name, count=1): # -> Any # FIXME
        """generate a list of light entity names"""

        entities = []

        for entity in range(1, count+1):
            entities.append(f'light.{name}_{entity}')

        return entities

# ---------------------------------------------------------------------------------------------------------

    def _cancel_timer(self, timer, message=None) -> None:
        """cancel a timer if set"""

        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def max_travel_time_to_home(self, kwargs={}) -> None:
        """set travel time to home for max. set max_driving_status sensor"""

        minutes = int(self.get_state('sensor.google_travel_time'))
        direction = self.get_state('sensor.max_dir_of_travel')
        state = self.get_state('sensor.maxine_iphone_activity')

        if state == "Automotive":
            self.set_state('sensor.max_driving_status', state='Driving')
        else:
            self.set_state('sensor.max_driving_status', state='Not Driving')

        diff = (datetime.now() - self.travel_announce_ts).seconds

        announce = self.now_is_between('10:00:00', '00:30:00') and (10 <= minutes <= 15) and (diff >= 4 * 60) and direction in ('towards', 'unknown', None)

        message = f'Max is {minutes} minutes away'

        if announce: # or self.lib.is_mock_run():
            if self.lib.is_playing('media_player.study'):
                self.desktop_notification(message)
            else:
                self.log(f'\tmessage={message} ts={self.travel_announce_ts.ctime()} ({self.travel_announce_ts.timestamp():6.3f})', level='DEBUG')
                self.announce(entity_id='media_player.study', message=message)
                self.set_timestamp('travel')

# ---------------------------------------------------------------------------------------------------------

    def set_timestamp(self, timestamp) -> None:
        """set a named timestamo"""

        if timestamp is not None:
            ts = datetime.now()
            if timestamp == "travel":
                self.travel_announce_ts = ts
            elif timestamp == "garage":
                self.garage_announce_ts = ts
            elif timestamp == "karoq":
                self.karoq_announce_ts = ts
            elif timestamp == "tap":
                self.tap_ts = ts
            elif timestamp == "general":
                self.general_announce_ts = ts

# ---------------------------------------------------------------------------------------------------------

    async def max_home(self, entity='', attribute='', old='', new='', kwargs={}) -> None:
        """turn on lights when returning after dark. start timer to turn off front door light"""

        if await self.is_dusk():
            self.run_sequence(
                [
                    {'light/turn_on': {'entity_id': ['light.standard_lamp_1', 'light.front_door_1'], 'brightness': 128}},
                    {'light/turn_on': {'entity_id': ['light.hallway_1'], 'brightness': 64}},
                ]
            )

            self.front_door_light_on()
            seconds = self.lib.interval(minutes=10)
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.front_door_light_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    # def paul_home(self, entity='', attribute='', old='', new='', kwargs={}) -> None:
    #     """."""

    #     self.log(f'\tentity={entity} attribute={attribute} old={old} new={new}')  # kwargs={kwargs}')

# ---------------------------------------------------------------------------------------------------------

    def activate_scene(self, entity, attribute, old, new, kwargs) -> None:
        """activate a scene <scene> and set <entity_id> off"""

        scene = kwargs['scene']
        entity_id = kwargs['entity_id']

        if scene:
            scene = 'scene.'+scene
            if new == 'on':
                self.turn_on(scene)
            else:
                self.turn_off(scene)

        if entity_id:
            self.delay(1)
            self.set_state(entity_id, state='off')

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for(self, entity, attribute, old, new, kwargs) -> None:
        """water garden for <minutes> minutes. different switches will set 1, 15, 20, 30 minutes"""

        minutes = kwargs['minutes']

        if minutes:
            self.tap_on(minutes=minutes)
        else:
            self.log('\tNo timer set', level="ERROR")

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_action(self, event, data, kwargs) -> None:
        """water garden for 15 minutes as an iOS action"""

        minutes = kwargs['minutes']

        self.water_garden_for_n_minutes({minutes: minutes})  # was minutes=minutes

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_n_minutes(self, kwargs) -> None:
        """water garden for <minutes> minutes"""

        self.water_garden_for('', '', '', '', kwargs)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_stop(self, entity, attribute, old, new, kwargs) -> None:
        """stop watering garden"""

        # self.tap_off() # TODO: stop running thread
        pass

# ---------------------------------------------------------------------------------------------------------

    def water_garden_daily(self, kwargs) -> None:
        """water garden daily"""

        if self.lib.is_summer():
            if self.lib.no_rain():
                kwargs = {**kwargs, 'minutes': self.DAILY_WATERING_MINUTES}
                self.water_garden_for_n_minutes(kwargs)

# ---------------------------------------------------------------------------------------------------------

    def tap_on(self, **kwargs) -> None:
        """turn garden tap on for <minutes> minutes"""

        minutes = kwargs.get('minutes', 0)

        self.call_service('switch/turn_on', entity_id='switch.garden_tap')

        if minutes > 0:
            self.announce(message=f'Watering garden for {minutes} minutes')
            self.log(f'\ttap_on for {minutes:d} minutes')
            self.tap_ts = datetime.now()
            seconds = self.lib.interval(minutes=minutes)
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.tap_off, seconds)
        else:
            self.announce(message=f'The garden tap is on without a timer')


# ---------------------------------------------------------------------------------------------------------

    def tap_off(self, kwargs={}) -> None:
        """turn garden tap off"""

        self.call_service('switch/turn_off', entity_id='switch.garden_tap')
        self.announce(message='The garden tap is now off')
        self.tap_ts = None
        self.set_state('input_boolean.water_garden_1', state='off')
        self.set_state('input_boolean.water_garden_15', state='off')
        self.set_state('input_boolean.water_garden_20', state='off')
        self.set_state('input_boolean.water_garden_30', state='off')

# ---------------------------------------------------------------------------------------------------------

    def garden_tap_on(self, entity, attribute, old, new, kwargs) -> None:
        """."""

        self.tap_on()

# ---------------------------------------------------------------------------------------------------------

    def garden_tap_off(self, entity, attribute, old, new, kwargs) -> None:
        """."""

        self.tap_off()

# ---------------------------------------------------------------------------------------------------------

    def check_garden_tap(self, kwargs) -> None:
        """check garden tap state"""

        state = self.get_state('switch.garden_tap')

        if state == 'on':
            self.log(f'\tGarden tap is {state}', level='WARNING')
            if self.tap_ts is None:
                self.log('\tTap timestamp not set', level="ERROR")
            else:
                seconds = (datetime.now() - self.tap_ts).seconds
                n = math.ceil(seconds / 60)
                diff1,diff2 = divmod(seconds, 60)
                nn = (diff1 + 1) % 10
                self.log(f'\t\t{diff1} {diff2} {nn}', level='DEBUG')
                if diff1 > 0 and ((diff1 + 1) % 10) == 0:
                    self.announce(message=f'The garden tap has been on for {nn} minutes', entity_id='media_player.kitchen')

# ---------------------------------------------------------------------------------------------------------

    def check_garage_door(self, kwargs={}) -> None:
        """check garage door state"""

        state = self.get_state(self.GARAGE_ENTITY_ID)

        if state != 'closed':
            self.log(f'\tGarage door is {state} garage_announce_ts={self.garage_announce_ts}', level='WARNING')
            diff = (datetime.now() - self.garage_announce_ts).seconds
            if diff >= self.lib.interval(minutes=60):
                self.garage_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    def check_karoq_door(self, kwargs={}) -> None:
        """check karoq door state"""

        state = self.get_state(self.KAROQ_ENTITY_ID)

        if state == 'unavailable':
            self.log(f'\tkaroq_door_state={state}', level='WARNING')
            return

        lock_state = 'locked' if state == 'off' else 'unlocked'
        # self.log(f'\tstate={state} karoq_announce_ts={self.karoq_announce_ts}', level='WARNING')

        if state != 'off':
            if self.lib.is_after(19):
                self.call_service('lock/lock', entity_id='lock.tmbkr7nu5p5079987_door_locked')
                state = self.get_state(self.KAROQ_ENTITY_ID)
                self.log(f'\tThe car door lock request has been sent. state={state}', level='WARNING')
                return  # do not announce self.karoq_door_announce(state=state). check again in a minute

            self.log(f'\tThe car door is {lock_state} karoq_announce_ts={self.karoq_announce_ts}', level='WARNING')
            diff = (datetime.now() - self.karoq_announce_ts).seconds
            if diff > self.lib.interval(minutes=60):
                self.karoq_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    async def garage_door(self, entity, attribute, old, new, kwargs={}) -> None:
        """listener for garage door"""

        is_dusk = await self.is_dusk()

        if new == 'opening':
            if is_dusk:
                self.garage_door_lights(on=True)
        elif new == 'closed':
            if is_dusk:
                seconds = self.lib.interval(minutes=1)
                self.log(f'\tstart garage_door_light timer for {seconds:d}s', level='DEBUG')
                self.run_in(self.garage_door_lights_off, seconds)

        self.garage_door_announce(state=new)

# ---------------------------------------------------------------------------------------------------------

    def karoq_door_announce(self, **kwargs) -> None:
        """karoq door announcement"""

        state = kwargs['state']

        if state == 'off':
            message = 'The car door is locked'
        elif state == 'on':
            message = 'The car door is unlocked'

        self.announce(message=message)
        self.set_timestamp('karoq')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce(self, **kwargs) -> None:
        """garage door announcement"""

        state = kwargs['state']

        if state == 'opening':
            message = 'The garage door is opening'
        elif state == 'closing':
            message = 'The garage door is closing'
        elif state == 'closed':
            message = 'The garage door is closed'
        elif state == 'open':
            message = 'The garage door is open'
        elif state == 'unavailable':
            return
        else:
            state = self.get_state(self.GARAGE_ENTITY_ID)
            message = f'The garage door is {state}'

        self.announce(message=message)
        self.set_timestamp('garage')

# ---------------------------------------------------------------------------------------------------------

    async def garage_door_open(self, entity, attribute, old, new, kwargs) -> None:
        """open garage door"""

        self.call_service('cover/open_cover', entity_id=self.GARAGE_ENTITY_ID)
        if await self.is_dusk():
            self.garage_door_lights(on=True)

# ---------------------------------------------------------------------------------------------------------

    async def garage_door_close(self, entity, attribute, old, new, kwargs) -> None:
        """close garage door"""

        self.call_service('cover/close_cover', entity_id=self.GARAGE_ENTITY_ID)
        if await self.is_dusk():
            self.garage_door_lights(on=False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_opening(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door opening"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closed', 'opening')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closing(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door closing"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'open', 'closing')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_open(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now open"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'opening', 'open')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closed(self, entity, attribute, old, new, kwargs) -> None:
        """announce garage door is now closed"""

        self.garage_door(self.GARAGE_ENTITY_ID, 'state', 'closing', 'closed')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_debug(self, entity, attribute, old, new, kwarg) -> None:

        state = self.get_state(self.GARAGE_ENTITY_ID)
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights(self, **kwargs) -> None:
        """turn on garage door lights"""

        entities = {'light.garage_2', 'light.garage_1'}

        if kwargs['on'] is True:
            self.call_service('light/turn_on', entity_id=entities)
        else:
            s = self.lib.interval(minutes=5)
            self.run_in(self.garage_door_lights, s, on=False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights_off(self, kwargs={}) -> None:
        """turn off garage door lights"""

        self.garage_door_lights(on=False)

# ---------------------------------------------------------------------------------------------------------

    def vacuum_debug(self, entity, attribute, old, new, kwargs={}) -> None:
        """vacuum debug function"""

        state = self.get_state('vacuum.s7_max_ultra')
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# ---------------------------------------------------------------------------------------------------------

    def lights_off(self, event, data, kwargs={}) -> None:
        """turn off hallway, garage and front door lights"""

        self.call_service('light/turn_off', entity_id=['light.hallway_1', 'light.hallway_2', 'light.front_door_1', 'light.garage_1', 'light.garage_2']) # not light.standard_lamp_1 !!

# ---------------------------------------------------------------------------------------------------------

    def set_all_state_event(self, event, data, kwargs={}) -> None:
        """listener for set_all_state event"""

        self.set_all_state()

# ---------------------------------------------------------------------------------------------------------

    def stairs_on(self, kwargs={}) -> None:
        """turn on landing light"""

        self.call_service('light/turn_on', entity_id='light.hallway_3', brightness=5)

# ---------------------------------------------------------------------------------------------------------

    def radiator_on(self, kwargs={}) -> None:
        """turn on radiator light"""

        self.call_service('light/turn_on', entity_id='light.radiator')

# ---------------------------------------------------------------------------------------------------------

    def living_room_lights_off(self, kwargs={}) -> None:
        """turn living room lights"""

        self.run_sequence(
            [
                {'light/turn_off': {'entity_id': ['light.radiator', 'light.standard_lamp_1', 'light.table_lamp_1']}},
                {'light/turn_off': {'entity_id': ['light.standard_lamp_1']}},
            ]
        )

        # self.call_service('light/turn_off', entity_id='light.radiator')
        # self.call_service('light/turn_off', entity_id='light.standard_lamp_1')
        # self.call_service('light/turn_off', entity_id='light.table_lamp_1')
        # # try again - wasn't switching off
        # self.call_service('light/turn_off', entity_id='light.standard_lamp_1')

# ---------------------------------------------------------------------------------------------------------

    def outside_lights_off(self, kwargs={}) -> None:
        """turn off outside lights"""

        self.run_sequence(
            [
                {'light/turn_off': {'entity_id': ['light.front_door_1', 'light.garage_1', 'light.garage_2']}},
            ]
        )

        # self.call_service('light/turn_off', entity_id='light.front_door_1')
        # self.call_service('light/turn_off', entity_id='light.garage_1')
        self.log('\toutside lights off')

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_on(self, kwargs={}) -> None:
        """turn on wardrobe light"""

        if 'dow' in kwargs:
            dow = kwargs['dow']
        else:
            dow = self.lib.dow()

        turn_on = (not (dow == 3 or dow >= 6)) and self.sun_down()

        if turn_on:
            self.log('\tturn on wardrobe')
            self.call_service('switch/turn_on', entity_id='switch.wardrobe')
            s = self.lib.interval(minutes=15)
            self.log(f'\tstart wardrobe timer for {s:d}s')
            self.run_in(self.wardrobe_off, s)

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_off(self, kwargs={}) -> None:
        """turn off wardrobe light"""

        self.call_service('switch/turn_off', entity_id='switch.wardrobe')

# ---------------------------------------------------------------------------------------------------------

    def hallway_on(self, kwargs={}) -> None:

        if self.sun_down(): # Turn on hallway lights when dark after 6am
            self.log('\tsun down - turn on hallway light', level='DEBUG')
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)
            self.log('\thallway off')
            self.log('\tset timer for hallway light', level='DEBUG')
            self.run_at(self.hallway_off, 'sunrise + 00:10:00')

# ---------------------------------------------------------------------------------------------------------

    def hallway_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.hallway_1')
        self.call_service('light/turn_off', entity_id='light.hallway_2')
        self.log('\thallway off')

# ---------------------------------------------------------------------------------------------------------

    async def upstairs_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.prev_upstairs_ts = self.upstairs_ts
        self.upstairs_ts = datetime.now()

        diff1 = (self.upstairs_ts - self.downstairs_ts).seconds
        diff2 = (self.upstairs_ts - self.prev_upstairs_ts).seconds
        self.log(f'\tdiff1={diff1} diff2={diff2}', level='DEBUG')

        if diff1 <= 300:
            timer = 600 # 5m timer for bannister
            if self.now_is_between('00:00:00', '03:00:00'):
                self.call_service('light/turn_on', entity_id='light.lumie', brightness=10)
        elif diff1 > 300 and diff2 <= 120:
            timer = 10
        else:
            timer = 120

        if self.now_is_between('22:00:00', 'sunrise') or self.get_state(entity_id='input_boolean.test_2'):
            kwargs = {**kwargs, 'timer': timer, 'check_override': False, 'location': 'upstairs'}
        await self.stairs_motion(**kwargs)

# ---------------------------------------------------------------------------------------------------------

    async def downstairs_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.downstairs_motion_flag = True
        self.log(f'\tdownstairs_motion_flag={self.downstairs_motion_flag}', level='DEBUG')
        self.downstairs_ts = datetime.now()
        # self.count = 2
        await self.stairs_motion(**kwargs)
        if self.now_is_between('05:00:00', '07:00:00'):
            self.sonos_unjoin_all(kwargs)
        # self.cancel_alarm_if_set('switch.sonos_alarm_1392', '07:00:00')  # 07:00 alarm
        self.cancel_alarm_if_set('input_boolean.early_alarm', '07:00:00', '06:00:00')

# ---------------------------------------------------------------------------------------------------------

    def cancel_alarm_if_set(self, entity_id, end_time, start_time='05:00:00') -> None:

        if self.now_is_between(start_time, end_time):
            self.log(f'\tmotion detected between {start_time} and {end_time}')
            state = self.get_state(entity_id=entity_id, attribute="state")
            if state == 'on':
                self.set_state(entity_id, state="off")
        else:
            self.log('\tmotion detected but outside time window')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        self.cancel_kitchen_timers()
        self.kitchen_floor_on()

        seconds = 5 * 60
        self.log(f'\tstart kitchen floor timer for {seconds:d}s', level='INFO')
        self.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)

        # if self.sun_down():
        if self.now_is_between('sunset + 00:15:00', 'sunrise + 00:30:00'):
            self.log('\tsun down - turn_on_if_off kitchen_1/4/5/6', level='INFO')
            self.turn_on_if_off('light.kitchen_1')
            self.turn_on_if_off('light.kitchen_4')
            self.turn_on_if_off('light.kitchen_5')
            self.turn_on_if_off('light.kitchen_6')
            seconds = 5 * 60
            self.log(f'\tstart short kitchen timer for {seconds:d}s', level='INFO')
            self.kitchen_timer = self.run_in(self.kitchen_off, seconds, **kwargs)
            seconds = 10 * 60
            self.log(f'\tstart long kitchen timer for {seconds:d}s', level='INFO')
            self.kitchen_long_timer = self.run_in(self.kitchen_all_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    def cancel_kitchen_timers(self) -> None:

        self._cancel_timer(self.kitchen_timer, 'short kitchen timer')
        self._cancel_timer(self.kitchen_long_timer, 'long kitchen timer')
        self._cancel_timer(self.kitchen_floor_timer, 'floor kitchen timer')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_floor_on(self) -> None:

        if self.now_is_between('08:00:00', '22:00:00'):
            self.call_service('light/turn_on', entity_id='light.kitchen_floor', brightness=255)
        if self.now_is_between('22:00:00', '08:00:00'):
            self.call_service('light/turn_on', entity_id='light.kitchen_floor', brightness=128)

# ---------------------------------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs={}) -> None:

        entity_id = 'light.utility_room_1'
        # state = self.get_state(entity_id=entity_id)
        brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        self.log(f'\tbrightness={brightness} st={self.utility_timer} lt={self.utility_long_timer}', level='DEBUG')

        # new motion detected - restart timers
        self.cancel_utility_timers(timer_type='both')

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            prev_state = self.turn_on_if_off(entity_id, brightness=64)
            self.log(f'\tprev_state={prev_state}', level='DEBUG')
            seconds = 5 * 60
            self.log(f'\tstart short utility timer for {seconds:d}s', level='DEBUG')
            self.utility_timer = self.run_in(self.utility_off, seconds, timer_type='short')
            seconds = 10 * 60
            self.log(f'\tstart long utility timer for {seconds:d}s', level='DEBUG')
            self.utility_long_timer = self.run_in(self.utility_off, seconds, timer_type='long')

# ---------------------------------------------------------------------------------------------------------

    def utility_off(self, kwargs={}) -> None:

        entity_id = 'light.utility_room_1'
        timer_type = kwargs['timer_type']
        brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        state = self.get_state(entity_id=entity_id, attribute="state")
        self.log(f'\ttimer_type={timer_type} brightness={brightness} state={state} st={self.utility_timer} lt={self.utility_long_timer}', level='DEBUG')
        self.cancel_utility_timers(timer_type='short')
        # (timer_type == 'long' or (brightness is not None and brightness <= 130)):
        if state == 'on' and timer_type == 'long':
            self.call_service('light/turn_off', entity_id=entity_id)
        else:
            self.log('\tlong timer running or brightness >= 130', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def cancel_utility_timers(self, **kwargs) -> None:

        timers = kwargs['timer_type']

        if timers in ('both', 'short'):
            self._cancel_timer(self.utility_timer, 'short utility timer')

        if timers in ('both', 'long'):
            self._cancel_timer(self.utility_long_timer, 'long utility timer')

# ---------------------------------------------------------------------------------------------------------

    async def stairs_motion(self, **kwargs) -> None:

        self.log(f'\tts1={self.downstairs_ts.ctime()} ({self.downstairs_ts.timestamp():6.3f})', level='DEBUG')
        self.log(f'\tts2={self.upstairs_ts.ctime()} ({self.upstairs_ts.timestamp():6.3f})', level='DEBUG')

        if await self.is_predusk():
            seconds = kwargs['timer']
            self._cancel_timer(self.stairs_timer, 'stairs timer')
            self.override = not kwargs['check_override']
            await self.bannister_on()
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.stairs_timer = self.run_in(self.bannister_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    async def bannister_on(self, kwargs={}) -> None:

        self.call_service('light/turn_on', entity_id='light.bannister', brightness=77)
        elevation = self.get_sun_elevation()
        if elevation < 5 and not self.now_is_between('01:30:00', 'sunrise'):
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)

# ---------------------------------------------------------------------------------------------------------

    def bannister_off(self, kwargs={}) -> None:

        check = kwargs['check_override']
        location = kwargs['location']
        if (check and not self.override) or not check:
            self.log(f'\tturn off bannister - {location}')
            self.call_service('light/turn_off', entity_id='light.bannister')
            self.call_service('light/turn_off', entity_id='light.hallway_1')
            self.override = False
            self.stairs_timer = None
        else:
            self.log(f'\tskip turn off bannister - {location}')

# ---------------------------------------------------------------------------------------------------------

    def downstairs_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.upstairs')
        self.call_service('light/turn_off', entity_id='light.downstairs')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs={}) -> None:

        self.call_service('light/turn_off', entity_id='light.kitchen_floor')
        self.kitchen_floor_timer = None

# ---------------------------------------------------------------------------------------------------------

    def kitchen_off(self, kwargs={}) -> None:

        entity_ids = self.light_entities('kitchen', 6)
        if not self.any_light_on_full(entity_ids):
            self.kitchen_all_off(kwargs)
        else:
            self.log('\tdeferring - kitchen lights high', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_all_off(self, kwargs={}) -> None:

        self.cancel_kitchen_timers()
        self.kitchen_floor_on()
        seconds = 60
        self.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)
        self.log(f'\tstart {seconds}s timer floor lights', level='DEBUG')
        for e in [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]:
            self.call_service('light/turn_off', entity_id=f'light.kitchen_{e}')

# ---------------------------------------------------------------------------------------------------------

    def front_door_ding(self, entity, attribute, old, new, kwargs={}) -> None:

        self.tapo_siren_on()
        self.front_door_announce()
        self.ding_front_door_light()
        self.ding_hallway_light()

# ---------------------------------------------------------------------------------------------------------

    def tapo_siren_on(self, kwargs={}) -> None:

        self.call_service('siren/turn_on', entity_id='siren.tapo_hub_siren')
        seconds = 5
        self.log(f'\tstart timer for{seconds:d}s', level='DEBUG')
        self.run_in(self.tapo_siren_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def tapo_siren_off(self, kwargs={}) -> None:

        self.call_service('siren/turn_off', entity_id='siren.tapo_hub_siren')

# ---------------------------------------------------------------------------------------------------------

    def front_door_announce(self, kwargs={}) -> None:

        message = 'Someone is at the front door' if not self.get_state('input_boolean.testing') == 'on' else 'just testing'
        self.broadcast(volume=0.5, message=message)

# ---------------------------------------------------------------------------------------------------------

    def ding_front_door_light(self, kwargs={}) -> None:
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

# ---------------------------------------------------------------------------------------------------------

    async def ding_hallway_light(self, kwargs={}) -> None:
        """Turn on hallway light when dark"""

        if await self.is_dusk():  # dusk till dawn
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64, transition=5)
            seconds = 10*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.hallway_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def front_door_battery(self, kwargs={}) -> None:

        level = int(self.get_state('sensor.front_door_battery'))
        message = None

        if level <= 50:
            battery = ''
            if level <= 20:
                battery = ' - CRITICAL'
                message = 'Please replace the front door battery immediately'
            elif level <= 25:
                battery = ' - dangerously low'
                message = 'Please replace the front door battery as soon as possible'
            elif level <= 30:
                battery = ' - low'
                message = 'Please charge the second front door battery'
            if message:
                self.announce(message=message)

            self.notification(f'Recharge front door battery ({level:d}%{battery})')

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_on(self, kwargs={}) -> None:

        self.run_in(self._front_door_light_on, 0)

# ---------------------------------------------------------------------------------------------------------

    async def _front_door_light_on(self, kwargs={}) -> None:

        if self.now_is_between('sunset', 'sunrise + 1:00:00'):
            if await self.is_dusk():
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=128, transition=10)
                self.call_service('light/turn_on', entity_id='light.garage_1', brightness=128, transition=10)
            else:
                self.run_in(self.int_front_door_light_on, 60)  # respawn self in 60s

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_off(self, kwargs={}) -> None:

        # scene = 'scene.front_door_ding_2'
        # self.log(f'\tscene={scene}', level='DEBUG')
        # self.turn_off(scene) # TODO: not working
        self.call_service('light/turn_off', entity_id='light.hallway_1', transition=10)
        self.call_service('light/turn_off', entity_id='light.front_door_1', transition=10)

# ---------------------------------------------------------------------------------------------------------

    def frost_warning(self, kwargs={}) -> bool:

        testing = self.get_state('input_boolean.testing') == 'on'
        stemp = self.get_state(entity_id='sensor.openweathermap_forecast_temperature_low')

        if stemp is None or stemp == 'unavailable':
            self.log(f'\tforecast low is {stemp}', level='WARNING')
            return False

        temp = float(stemp)
        self.log(f'\tforecast low is {temp}', level='DEBUG')
        warning = temp <= 3.0

        if warning or testing:
            self.log('\tfrost warning', level='WARNING')
            self.announce(message='There is a chance of frost overnight')

        return warning

# ---------------------------------------------------------------------------------------------------------

    def update_available(self, entity, attribute, old, new, kwargs={}) -> None:

        self.utils.log_function_name()
        self.utils.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def set_utility_motion_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.utility_motion_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_kitchen_motion_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.kitchen_motion_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_bins_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.bins_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_frost_warning_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.frost_warning_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_notification_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.notification_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_announcement_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.announce_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_max_home_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            # self.register_test_3(self.max_home_test)
            self.register_test_3(self.max_village_announce)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_front_door_ding_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_ding_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_front_door_light_on_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.front_door_light_on_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_test_test(self, entity, attribute, old, new, kwargs={}) -> None:

        action = kwargs['action']

        if action == 'set':
            self.register_test_3(self.test_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_tap_timestamp(self, entity, attribute, old, new, kwargs={}) -> None:
        action = kwargs['action']
        if action == 'set':
            self.tap_ts = datetime.now()
        elif action == 'cancel':
            self.tap_ts = None

# ---------------------------------------------------------------------------------

    def backup(self, entity='', attribute='', old='', new='', kwargs={}) -> None:

        self.call_service('hassio/backup_full', compressed=True, homeassistant_exclude_database=True)

# ---------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs={}) -> None:

        self.status('','','','')

# ---------------------------------------------------------------------------------

    def water_garden_event(self, event, data, kwargs={}) -> None:

        minutes = data['minutes']
        self.water_garden_for_n_minutes({'minutes': minutes})
        self.announce(message=f'Watering garden for {minutes} minutes')

# ---------------------------------------------------------------------------------

    async def max_home_event(self, event, data, kwargs={}) -> None:

        await self.max_home('', '', '', '', {})

# ---------------------------------------------------------------------------------

    def fire_status_event(self, entity='', attribute='', old='', new='', kwargs={}) -> None:

        self.fire_event("status")

# ---------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs={}) -> None:

        status = f'\n\n\tkitchen_timer={self.kitchen_timer}\n'
        status += f'\tkitchen_long_timer={self.kitchen_long_timer}\n'
        status += f'\tkitchen_floor_timer={self.kitchen_floor_timer}\n'
        status += f'\tutility_timer={self.utility_timer}\n'
        status += f'\tutility_timer={self.utility_long_timer}\n'
        status += f'\tstairs_timer={self.stairs_timer}\n'
        status += f'\n\tupstairs_ts={self.upstairs_ts}\n'
        status += f'\tdownstairs_ts={self.downstairs_ts}\n'
        status += f'\tprev_upstairs_ts={self.prev_upstairs_ts}\n'
        status += f'\tgeneral_announce_ts={self.general_announce_ts}\n'
        status += f'\ttravel_announce_ts={self.travel_announce_ts}\n'
        status += f'\tgarage_announce_ts={self.garage_announce_ts}\n'
        status += f'\ttap_ts={self.tap_ts}\n'
        status += f'\n\tdownstairs_motion_flag={self.downstairs_motion_flag}\n'
        state = self.get_state('input_boolean.default_debug_state')
        status += f'\tdefault_debug_state={state}\n'
        state = self.get_state('input_boolean.default_verbose_state')
        status += f'\tdefault_verbose_state={state}\n'
        state = self.get_state('input_boolean.default_testing_state')
        status += f'\tdefault_testing_state={state}\n'
        status += f'\n\tdebug={self.debug}\n'
        status += f'\tverbose={self.verbose}\n'
        status += f'\ttesting={self.testing}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# ---------------------------------------------------------------------------------

    def update_openweathermap(self, kwargs) -> None:

        self.call_service('homeassistant/update_entity', entity_id='weather.openweathermap')

# ---------------------------------------------------------------------------------

    def check_roborock(self, kwargs) -> None:

        state = self.get_state('sensor.s7_max_ultra_dock_error')

        if state == 'ok':
            return

        if state == "duct_blockage":
            message = 'Vacuum duct blockage'
        elif state == "water_empty":
            message = 'Vacuum clean water tank empty or not installed'
        elif state == "waste_water_tank_full":
            message = 'Vacuum waste water tank full'
        elif state == "cleaning_tank_full_or_blocked":
            message = 'Vacuum cleaning tank full or blocked'
        elif state == "maintenance_brush_jammed":
            message = 'Vacuum maintenance brush jammed'
        elif state == "dirty_tank_latch_open":
            message = 'Vacuum dirty tank latch open'
        elif state == "no_dustbin":
            message = 'Vacuum has no dustbin'
        else:
            self.desktop_notification(f'Roborock has an unknown error {state}')
            return

        diff = (datetime.now() - self.vacuum_announce_ts).seconds

        if diff > ( 3 * 60 ):
            self.announce(message=message)
            self.vacuum_announce_ts = datetime.now()

# ---------------------------------------------------------------------------------

    async def set_downstairs_motion_flag(self, namespace, domain, service, data) -> None:

        self.downstairs_motion_flag = data['state']

# ---------------------------------------------------------------------------------

    async def _log_function_name(self, namespace, domain, service, data) -> None:

        type = data.get('start', True)
        self.log(f'\ttype={type}')
        self.log_function_name() # FIXME

# ---------------------------------------------------------------------------------

    async def max_home_service(self, namespace, domain, service, data) -> None:

        await self.max_home('', '', '', '', {})

# -------------------------------------------------------------------------------------------------

    def log_test(self, kwargs={}):

        # INFO comes last to ensure we have a final successful log entry
        for level in ['CRITICAL', 'ERROR', 'WARNING', 'DEBUG', 'NOTSET', 'INFO']:
            self.log(f'\ttesting {level}', level=level)

# ---------------------------------------------------------------------------------------------------------

    def log_function_name(self, start=True) -> None:

        name = inspect.currentframe().f_back.f_code.co_name
        # print(inspect.currentframe())

        if self.verbose or self.debug:
            self.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

    async def is_dusk(self) -> bool:
        """is it dusk (dusk less than -3 degrees sun elevation)"""

        elevation = await self.get_sun_elevation()
        dusk = elevation < -3
        t = 'is' if dusk else 'is not'
        self.log_debug(f'{t} dusk')

        return dusk

# ---------------------------------------------------------------------------------------------------------

    async def is_predusk(self) -> bool:
        """is it dusk (dusk less than 1 degree sun elevation)"""

        elevation = await self.get_sun_elevation()
        predusk = elevation < 1
        t = 'is' if predusk else 'is not'
        self.log_debug(f'{t} predusk')

        return predusk

# ---------------------------------------------------------------------------------------------------------

    async def get_sun_elevation(self) -> float:
        """get sun elevation"""

        elevation = await self.get_state('sun.sun', attribute='elevation')
        self.log_debug(f'elevation={elevation:2.2f}')
        # self.log_debug(f'elevation={elevation}')

        return elevation

# ---------------------------------------------------------------------------------------------------------

    def log_debug(self, message) -> None:
        """log debug message"""

        self.log(f'\t{message}', level="DEBUG")

# ---------------------------------------------------------------------------------------------------------

