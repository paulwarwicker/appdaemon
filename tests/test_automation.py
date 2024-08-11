# -*- coding: utf-8 -*-

import datetime

from appdaemon_testing.pytest import automation_fixture
from appdaemon_testing.pytest import mock
from freezegun import freeze_time
from apps.automation import Automation

LOG_FUNCTION = 2
LOG_TRAVEL_TIME = 2
MESSAGE_VILLAGE = 'Max is in the village'
MESSAGE_FRONTDOOR='Someone is at the front door'
STUDY_ENTITY_ID = 'media_player.study'
KITCHEN_ENTITY_ID = 'media_player.kitchen'
STUDY_VOLUME = 0.3

@automation_fixture(
    Automation,
    args={
    },
)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def automation() -> Automation:
    pass

    # TODO:
    # def delay(self, s) -> None:
    # def set_debug(self, torf) -> bool:
    # def log_debug(self, message) -> None:
    # def log_function_name(self, start=True) -> None:
    # def is_playing(self, entity_id=None) -> bool:
    # def interval(self, minutes) -> int:

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_travel_time_to_home_when_before_dusk_and_study_muted(hass_driver, automation: Automation):

#     entity_id = 'media_player.study'
#     minutes = 20
#     message = f'Max is {minutes} minutes away'

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.google_travel_time', str(minutes))
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_travel_time_to_home()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=0.4),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_travel_time_to_home_when_before_dusk_and_study_unmuted(hass_driver, automation: Automation):

#     entity_id = 'media_player.study'
#     minutes = 22
#     message = f'Max is {minutes} minutes away'

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.google_travel_time', str(minutes))
#         hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_travel_time_to_home()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=0.4),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_travel_time_to_home_when_after_dusk_and_study_muted(hass_driver, automation: Automation):

#     entity_id = 'media_player.study'
#     minutes = 14
#     message = f'Max is {minutes} minutes away'

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.google_travel_time', str(minutes))
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_travel_time_to_home()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=0.4),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_travel_time_to_home_when_after_dusk_and_study_unmuted(hass_driver, automation: Automation):

#     entity_id = 'media_player.study'
#     minutes = 14
#     message = f'Max is {minutes} minutes away'

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.google_travel_time', str(minutes))
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_travel_time_to_home()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=0.4),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_dssmith_announce1(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'off')
#         hass_driver.set_state('input_boolean.verbose', 'off')
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'DS_Smith_Fordham', {'name': 'DS_Smith_Fordham', 'location': 'proximity.ds_smith_fordham', 'test': True})

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_max_dssmith_announce2(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.verbose', 'on')
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'DS_Smith_Fordham', 'new', {'name': 'DS_Smith_Fordham', 'location': 'proximity.ds_smith_fordham', 'test': True})

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_light_entities(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    entities = automation.light_entities('light', 3)

    assert not entities == ['light.light_1', 'light.light_2']

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    entities = automation.light_entities('light', 2)

    assert entities == ['light.light_1', 'light.light_2']

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_any_light_on(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('light.light_1', 0, attribute_name='brightness')
        hass_driver.set_state('light.light_2', 255, attribute_name='brightness')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.any_light_on_full(['light.light_1', 'light.light_2'])

    with hass_driver.setup():
        hass_driver.set_state('light.light_1', 255, attribute_name='brightness')
        hass_driver.set_state('light.light_2', 0, attribute_name='brightness')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.any_light_on_full(['light.light_1', 'light.light_2'])

    with hass_driver.setup():
        hass_driver.set_state('light.light_1', 128, attribute_name='brightness')
        hass_driver.set_state('light.light_2', 128, attribute_name='brightness')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.any_light_on_full(['light.light_1', 'light.light_2'])

    with hass_driver.setup():
        hass_driver.set_state('light.light_1', 255, attribute_name='brightness')
        hass_driver.set_state('light.light_2', 255, attribute_name='brightness')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.any_light_on_full(['light.light_1', 'light.light_2'])

    with hass_driver.setup():
        hass_driver.set_state('light.light_1', None, attribute_name='brightness')
        hass_driver.set_state('light.light_2', None, attribute_name='brightness')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.any_light_on_full(['light.light_1', 'light.light_2'])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_reset_downstairs_motion_flag(hass_driver, automation: Automation):

    with hass_driver.setup():
        automation.downstairs_motion_flag = True
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.downstairs_motion_flag

    automation.reset_downstairs_motion_flag()

    assert not automation.downstairs_motion_flag

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_debug(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.debug', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.lib.get_debug()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.debug', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.get_debug()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_verbose(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.verbose', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.get_verbose()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.verbose', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.get_verbose()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_outside_light_off(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.outside_lights_off()

#     call_service.assert_has_calls([mock.call('light/turn_off', entity_id='light.front_door_1'), mock.call('light/turn_off', entity_id='light.garage_1')])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_downstairs_motion(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('binary_sensor.downstairs_sensor_motion', 'on', previous='off')
#         hass_driver.set_state('sun.sun', 5, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.downstairs_motion('binary_sensor.downstairs_sensor_motion', 'state', 'off', 'on', {})

#     with hass_driver.setup():
#         hass_driver.set_state('binary_sensor.downstairs_sensor_motion', 'on', previous='off')
#         hass_driver.set_state('sun.sun', -5, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.downstairs_motion('binary_sensor.downstairs_sensor_motion', 'state', 'off', 'on', {'timer': 1, 'check_override': False})
#     automation.downstairs_motion('binary_sensor.downstairs_sensor_motion', 'state', 'off', 'on', {'timer': 1, 'check_override': True})

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_upstairs_motion(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('binary_sensor.upstairs_sensor_motion', 'on', previous='off')
        hass_driver.set_state('sun.sun', 5, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    automation.upstairs_motion('binary_sensor.upstairs_sensor_motion', 'state', 'off', 'on', {})

    with hass_driver.setup():
        hass_driver.set_state('binary_sensor.upstairs_sensor_motion', 'on', previous='off')
        hass_driver.set_state('sun.sun', -5, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    automation.upstairs_motion('binary_sensor.upstairs_sensor_motion', 'state', 'off', 'on', {'timer': 1, 'check_override': False})
    automation.upstairs_motion('binary_sensor.upstairs_sensor_motion', 'state', 'off', 'on', {'timer': 1, 'check_override': True})

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_cancel_alarm_if_set(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('binary_sensor.downstairs_sensor_motion', 'on', previous='off')
        hass_driver.set_state('switch.sonos_alarm_1392', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    automation.cancel_alarm_if_set('switch.sonos_alarm_1392', '07:00:00')

    with hass_driver.setup():
        hass_driver.set_state('binary_sensor.downstairs_sensor_motion', 'on', previous='off')
        hass_driver.set_state('switch.sonos_alarm_1392', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    automation.cancel_alarm_if_set('switch.sonos_alarm_1392', '07:00:00')

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_rearm_kitchen_alarm(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('switch.sonos_alarm_1392', 'off')

#     automation.rearm_kitchen_alarm()

#     call_service.assert_has_calls([mock.call('switch/turn_on', entity_id='switch.sonos_alarm_1392')])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_wardrobe_on(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     for dow in (1, 2, 4, 5):
#         automation.wardrobe_on({'dow': dow})

#         call_service.assert_has_calls([mock.call('switch/turn_on', entity_id='switch.wardrobe')])

#     for dow in (3, 6, 7):
#         automation.wardrobe_on({'dow': dow})

#         call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_bins_announce(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.bins_announce('preannounce', True)

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='media_player.kitchen', with_group=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message='It is the orange bin this week', media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='It is the orange bin this week'),
#         # mock.call('notify/pushbullet', title='It is the orange bin this week', message=''),
#         mock.call('notify/disc0rd', title='', message='It is the orange bin this week', target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='media_player.kitchen', with_group=True)
#     ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_tapo_siren_on(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")
    run_in = hass_driver.get_mock("run_in")

    automation.tapo_siren_on()

    # assert call_service.call_count == 1

    call_service.assert_has_calls([
        mock.call('siren/turn_on', entity_id='siren.tapo_hub_siren')
    ])

    run_in.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_tapo_siren_off(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    automation.tapo_siren_off()

    # assert call_service.call_count == 1

    call_service.assert_has_calls([
        mock.call('siren/turn_off', entity_id='siren.tapo_hub_siren')
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_front_door_battery_1(hass_driver, automation: Automation):

    entity_id = 'media_player.kitchen'

    with hass_driver.setup():
        hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.mock_run', 'on')
        hass_driver.set_state('sensor.front_door_battery', 51)

    call_service = hass_driver.get_mock("call_service")

    automation.front_door_battery()

    call_service.assert_has_calls([])


def test_front_door_battery_2(hass_driver, automation: Automation):

    entity_id = 'media_player.kitchen'

    with hass_driver.setup():
        hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.mock_run', 'on')
        hass_driver.set_state('sensor.front_door_battery', 50)

    call_service = hass_driver.get_mock("call_service")

    automation.front_door_battery()

    call_service.assert_has_calls([
        # mock.call('notify/lg_webos_tv_oled65c7v', message='Recharge front door battery (50%)'),
        # mock.call('notify/pushbullet', title='Recharge front door battery (50%)', message='')
        mock.call('notify/disc0rd', title='', message='Recharge front door battery (50%)', target='1250932196613685313')
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_front_door_battery_3(hass_driver, automation: Automation):

#     entity_id = 'media_player.kitchen'

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')
#         hass_driver.set_state('sensor.front_door_battery', 30)

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_battery()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='media_player.kitchen', with_group=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message='Please charge the second front door battery', media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Please charge the second front door battery'),
#         # mock.call('notify/pushbullet', title='Please charge the second front door battery', message=''),
#         mock.call('notify/disc0rd', title='', message='Please charge the second front door battery', target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='media_player.kitchen', with_group=True),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Recharge front door battery (30% - low)'),
#         mock.call('notify/disc0rd', title='', message='Recharge front door battery (30% - low)', target='1250932196613685313')
#     ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_front_door_battery_4(hass_driver, automation: Automation):

#     entity_id = 'media_player.kitchen'

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')
#         hass_driver.set_state('sensor.front_door_battery', 25)

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_battery()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='media_player.kitchen', with_group=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message='Please replace the front door battery as soon as possible', media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Please charge the second front door battery'),
#         # mock.call('notify/pushbullet', title='Please charge the second front door battery', message=''),
#         mock.call('notify/disc0rd', title='', message='Please replace the front door battery as soon as possible', target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='media_player.kitchen', with_group=True),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Recharge front door battery (30% - low)'),
#         mock.call('notify/disc0rd', title='', message='Recharge front door battery (25% - dangerously low)', target='1250932196613685313')
#     ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_front_door_battery_5(hass_driver, automation: Automation):

#     entity_id = 'media_player.kitchen'

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')
#         hass_driver.set_state('sensor.front_door_battery', 20)

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_battery()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='media_player.kitchen', with_group=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message='Please replace the front door battery immediately', media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Please charge the second front door battery'),
#         # mock.call('notify/pushbullet', title='Please charge the second front door battery', message=''),
#         mock.call('notify/disc0rd', title='', message='Please replace the front door battery immediately', target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='media_player.kitchen', with_group=True),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='Recharge front door battery (30% - low)'),
#         mock.call('notify/disc0rd', title='', message='Recharge front door battery (20% - CRITICAL)', target='1250932196613685313')
#     ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# @freeze_time('2024-01-01 19:00:00')
# def test_front_door_announce1(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_announce()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='all'),
#         mock.call('media_player/join', entity_id='media_player.kitchen', group_members=['media_player.bathroom', 'media_player.dining_room']),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.bathroom', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.dining_room', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.study', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.bedroom_2', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_FRONTDOOR, media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_FRONTDOOR),
#         # mock.call('notify/pushbullet', title=MESSAGE_FRONTDOOR, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_FRONTDOOR, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='all'),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.bathroom', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.dining_room', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.study', is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id='media_player.bedroom_2', is_volume_muted=False)
#     ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# @freeze_time('2024-01-01 19:00:00')
# def test_front_door_ding1(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('binary_sensor.front_door_ding', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_ding('binary_sensor.front_door_ding', 'state', 'off', 'on', {})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='all'),
#         mock.call('media_player/join', entity_id='media_player.kitchen', group_members=['media_player.bathroom', 'media_player.dining_room']),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.bathroom', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.dining_room', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.study', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.bedroom_2', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_FRONTDOOR, media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_FRONTDOOR),
#         # mock.call('notify/pushbullet', title=MESSAGE_FRONTDOOR, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_FRONTDOOR, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='all')
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# @freeze_time('2024-06-16 19:00:00')
# def test_front_door_ding2(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', 0, attribute_name='elevation')
#         hass_driver.set_state('binary_sensor.front_door_ding', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.front_door_ding('binary_sensor.front_door_ding', 'state', 'off', 'on', {})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='all'),
#         mock.call('media_player/join', entity_id='media_player.kitchen', group_members=['media_player.bathroom', 'media_player.dining_room']),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.bathroom', volume_level=0.5),
#         mock.call('media_player/volume_set', entity_id='media_player.dining_room', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.study', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.bedroom_2', is_volume_muted=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_FRONTDOOR, media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_FRONTDOOR),
#         # mock.call('notify/pushbullet', title=MESSAGE_FRONTDOOR, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_FRONTDOOR, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='all')
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# def test_frost_warning(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.openweathermap_forecast_temperature_low', '4.0')
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     assert not automation.frost_warning()

#     with hass_driver.setup():
#         hass_driver.set_state('sensor.openweathermap_forecast_temperature_low', '0.0')
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     assert automation.frost_warning()

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_vouchers_announce(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.vouchers_announce()

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id='media_player.kitchen', with_group=True),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id='media_player.kitchen', volume_level=0.5),
#         mock.call('media_player/volume_mute', entity_id='media_player.kitchen', is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message='1 pounds of vouchers expiring end of whenever', media_player_entity_id='media_player.kitchen'),
#         mock.call('media_player/repeat_set', entity_id='media_player.kitchen', repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message='1 pounds of vouchers expiring end of whenever'),
#         # mock.call('notify/pushbullet', title='1 pounds of vouchers expiring end of whenever', message=''),
#         mock.call('notify/disc0rd', title='', message='1 pounds of vouchers expiring end of whenever', target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id='media_player.kitchen', with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_reset(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')
#         hass_driver.set_state('input_boolean.sonos', state='on')
#         hass_driver.set_state('input_boolean.debug', state='on')
#         hass_driver.set_state('input_boolean.test_1', state='on')
#         hass_driver.set_state('input_boolean.test_2', state='on')
#         hass_driver.set_state('input_boolean.test_3', state='on')

#     automation.reset('')

#     # assert hass_driver.get_state('input_boolean.debug') == 'off'
#     # self.reset_downstairs_motion_flag()
#     # self.sonos_unjoin_all({})
#     # self.sonos_configure1({}) # failsafe for bank holiday

#     # self.set_state('input_boolean.sonos', state='off')
#     # self.set_state('input_boolean.debug', state='off')
#     # self.set_state('input_boolean.test_1', state='off')
#     # self.set_state('input_boolean.test_2', state='off')
#     # self.set_state('input_boolean.test_3', state='off')

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_home(hass_driver, automation: Automation):

#     message = "Max is home"

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'arrived')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     entity_id = 'media_player.study' if automation.get_debug() else 'media_player.kitchen'

#     call_service = hass_driver.get_mock("call_service")

#     # hass_driver.set_state("proximity.home", 'arrived')

#     automation.max_home('', 'attribute', 'old', 'new', {})

#     call_service.assert_has_calls([
#         mock.call('light/turn_on', entity_id=['light.standard_lamp_1'], brightness=128),
#         mock.call('light/turn_on', entity_id=['light.front_door_1'], brightness=128),
#         mock.call('light/turn_on', entity_id='light.hallway_1', brightness=64)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_location_announce1(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'arrived')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     message = "Max has arrived at DS Smith Fordham"
#     entity_id = 'media_player.study'

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_location_announce('proximity.ds_smith_fordham', 'arrive', {})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         # mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('notify/disc0rd', title='', message=message, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_location_announce2(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'arrived')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     message = "Max has left DS Smith Fordham"
#     entity_id = 'media_player.study'

#     call_service = hass_driver.get_mock("call_service")

#     automation.max_location_announce('proximity.ds_smith_fordham', 'leave', {})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=entity_id, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=entity_id, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id),
#         mock.call('media_player/repeat_set', entity_id=entity_id, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=message),
#         # mock.call('notify/pushbullet', title=message, message=''),
#         mock.call('notify/disc0rd', title='', message=message, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=entity_id, with_group=True)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_village_announce1(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'towards', attribute_name="dir_of_travel")
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'Village', {'name': 'Village', 'location': 'proximity.village', 'test': True})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=STUDY_ENTITY_ID, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_VILLAGE, media_player_entity_id=STUDY_ENTITY_ID),
#         mock.call('media_player/repeat_set', entity_id=STUDY_ENTITY_ID, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_VILLAGE),
#         # mock.call('notify/pushbullet', title=MESSAGE_VILLAGE, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_VILLAGE, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('light/turn_on', entity_id=['light.standard_lamp_1'], brightness=128),
#         mock.call('light/turn_on', entity_id=['light.front_door_1'], brightness=128),
#         mock.call('light/turn_on', entity_id='light.hallway_1', brightness=64)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_village_announce2(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'towards', attribute_name="dir_of_travel")
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'Village', {'name': 'Village', 'location': 'proximity.village', 'test': True})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=STUDY_ENTITY_ID, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_VILLAGE, media_player_entity_id=STUDY_ENTITY_ID),
#         mock.call('media_player/repeat_set', entity_id=STUDY_ENTITY_ID, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_VILLAGE),
#         # mock.call('notify/pushbullet', title=MESSAGE_VILLAGE, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_VILLAGE, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('light/turn_on', entity_id=['light.standard_lamp_1'], brightness=128),
#         mock.call('light/turn_on', entity_id=['light.front_door_1'], brightness=128),
#         mock.call('light/turn_on', entity_id='light.hallway_1', brightness=64)
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_village_announce3(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': False, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'towards', attribute_name="dir_of_travel")
#         hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'Village', {'name': 'Village', 'location': 'proximity.village', 'test': True})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=STUDY_ENTITY_ID, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_VILLAGE, media_player_entity_id=STUDY_ENTITY_ID),
#         mock.call('media_player/repeat_set', entity_id=STUDY_ENTITY_ID, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_VILLAGE),
#         # mock.call('notify/pushbullet', title=MESSAGE_VILLAGE, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_VILLAGE, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=STUDY_ENTITY_ID, with_group=True),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_max_village_announce4(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state("proximity.home", 'towards', attribute_name="dir_of_travel")
#         hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'Village', {'name': 'Village', 'location': 'proximity.village', 'test': True})

#     call_service.assert_has_calls([
#         mock.call('sonos/snapshot', entity_id=STUDY_ENTITY_ID, with_group=True),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=True),
#         mock.call('media_player/volume_set', entity_id=STUDY_ENTITY_ID, volume_level=STUDY_VOLUME),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('media_player/volume_mute', entity_id=STUDY_ENTITY_ID, is_volume_muted=False),
#         mock.call('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=MESSAGE_VILLAGE, media_player_entity_id=STUDY_ENTITY_ID),
#         mock.call('media_player/repeat_set', entity_id=STUDY_ENTITY_ID, repeat='off'),
#         # mock.call('notify/lg_webos_tv_oled65c7v', message=MESSAGE_VILLAGE),
#         # mock.call('notify/pushbullet', title=MESSAGE_VILLAGE, message=''),
#         mock.call('notify/disc0rd', title='', message=MESSAGE_VILLAGE, target='1250932196613685313'),
#         mock.call('sonos/restore', entity_id=STUDY_ENTITY_ID, with_group=True),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_set_all_state_when_off(hass_driver, automation: Automation):

#     default = 'off'

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.default_early_alarm_state', 'on')
#         hass_driver.set_state('input_boolean.default_normal_alarm_state', 'on')
#         hass_driver.set_state('input_boolean.default_lumie_state', 'on')
#         hass_driver.set_state('input_boolean.default_debug_state', 'on')
#         hass_driver.set_state('input_boolean.default_verbose_state', 'off')
#         hass_driver.set_state('input_boolean.default_testing_state', 'off')

#         hass_driver.set_state('input_boolean.debug', default)
#         hass_driver.set_state('input_boolean.verbose', default)
#         hass_driver.set_state('input_boolean.early_alarm', default)
#         hass_driver.set_state('input_boolean.normal_alarm', default)
#         hass_driver.set_state('input_boolean.lumie', default)
#         hass_driver.set_state('input_boolean.testing', default)
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.set_all_state()

#     assert Automation.get_state("input_boolean.verbose") == Automation.get_state("input_boolean.default_verbose_state")
#     # assert Automation.get_state("input_boolean.debug") == Automation.get_state("input_boolean.default_debug_state") # FIXME:
#     assert Automation.get_state("input_boolean.testing") ==  Automation.get_state("input_boolean.default_testing_state")
#     # assert Automation.get_state("input_boolean.early_alarm") == Automation.get_state("input_boolean.default_early_alarm_state") # FIXME:
#     # assert Automation.get_state("input_boolean.normal_alarm") == Automation.get_state("input_boolean.default_normal_alarm_state") # FIXME:
#     # assert Automation.get_state("input_boolean.lumie") == Automation.get_state("input_boolean.default_lumie_state") # FIXME:

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_set_all_state_when_on(hass_driver, automation: Automation):

#     default = 'on'

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.default_early_alarm_state', 'on')
#         hass_driver.set_state('input_boolean.default_normal_alarm_state', 'on')
#         hass_driver.set_state('input_boolean.default_lumie_state', 'on')
#         hass_driver.set_state('input_boolean.default_debug_state', 'on')
#         hass_driver.set_state('input_boolean.default_verbose_state', 'off')
#         hass_driver.set_state('input_boolean.default_testing_state', 'off')

#         hass_driver.set_state('input_boolean.debug', default)
#         hass_driver.set_state('input_boolean.verbose', default)
#         hass_driver.set_state('input_boolean.early_alarm', default)
#         hass_driver.set_state('input_boolean.normal_alarm', default)
#         hass_driver.set_state('input_boolean.lumie', default)
#         hass_driver.set_state('input_boolean.testing', default)
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.set_all_state()

#     # assert Automation.get_state("input_boolean.verbose") == Automation.get_state("input_boolean.default_verbose_state") # FIXME:
#     assert Automation.get_state("input_boolean.debug") == Automation.get_state("input_boolean.default_debug_state")
#     # assert Automation.get_state("input_boolean.testing") ==  Automation.get_state("input_boolean.default_testing_state") # FIXME:
#     assert Automation.get_state("input_boolean.early_alarm") == Automation.get_state("input_boolean.default_early_alarm_state")
#     assert Automation.get_state("input_boolean.normal_alarm") == Automation.get_state("input_boolean.default_normal_alarm_state")
#     assert Automation.get_state("input_boolean.lumie") == Automation.get_state("input_boolean.default_lumie_state")

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_lumie_phase1_1(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.lumie', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.lumie_phase1({'test': True, 'brightness': 250, 'transition': 5, 'rgb_color': [255, 180, 10]})

#     call_service.assert_has_calls([
#         mock.call('light/turn_on', entity_id='light.lumie', brightness=250, transition=5, rgb_color=[255, 180, 10]),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_lumie_phase1_2(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.lumie', 'off')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.lumie_phase1({'test': True, 'brightness': 250, 'transition': 5, 'rgb_color': [255, 180, 10]})

#     call_service.assert_has_calls([
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_lumie_phase2_1(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.lumie', 'on')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.lumie_phase2({'test': True, 'brightness': 250, 'transition': 5, 'rgb_color': [255, 180, 10]})

#     call_service.assert_has_calls([
#         mock.call('light/turn_on', entity_id='light.lumie', brightness=250, transition=5, rgb_color=[255, 180, 10]),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_lumie_phase2_2(hass_driver, automation: Automation):

#     call_service = hass_driver.get_mock("call_service")

#     with hass_driver.setup():
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.lumie', 'off')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.lumie_phase2({'test': True, 'brightness': 250, 'transition': 5, 'rgb_color': [255, 180, 10]})

#     call_service.assert_has_calls([
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_garage_door_open_when_sun_above_horizon(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('device_tracker.paulw_iphone', 'Home')
#         hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.garage_door_open()

#     call_service.assert_has_calls([
#         mock.call('cover/open_cover', entity_id='cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_garage_door_open_when_sun_below_horizon(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         # , attribute_name='elevation')
#         hass_driver.set_state('device_tracker.paulw_iphone', 'Home')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.garage_door_open()

#     # print(call_service.call_args_list)

#     print(call_service.call_args_list)
#     for call in call_service.call_args_list:
#         # print('args: {}'.format(call[0]))
#         # print('kwargs: {}'.format(call[1]))
#         print(f'args: {call[0]}')
#         print(f'kwargs: {call[1]}')

#     print(100)

#     call_service.assert_has_calls([
#         mock.call('cover/open_cover', entity_id='cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'),
#         mock.call('light/turn_on', entity_id='light.garage_1'),
#         mock.call('light/turn_on', entity_id='light.garage_2')
#         # ])
#     ], any_order=True)

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------


# def test_garage_door_open(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'off')
#         hass_driver.set_state('input_boolean.verbose', 'off')
#         hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     call_service = hass_driver.get_mock("call_service")

#     automation.garage_door_open()

#     # automation.set_state(entity_id='device_tracker.paulw_iphone', state={'old':'not_home', 'new':'home'}) # , attribute_name='state')

#     # print(automation.get_state(entity_id='device_tracker.paulw_iphone'))

#     # print(call_service.call_args_list)
#     # for call in call_service.call_args_list:
#     #     print('args: {}'.format(call[0]))
#     #     print('kwargs: {}'.format(call[1]))

#     # print(200)

#     call_service.assert_has_calls([
#         mock.call('cover/open_cover', entity_id='cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'),
#     ])

# # ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01')
def test_is_bank_holiday(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 1, 1)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1)
    assert automation.lib.is_bank_holiday(datetime.datetime.now())

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02')
def test_is_not_bank_holiday(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 1, 2)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    # assert datetime.datetime.now() == datetime.datetime(2024, 1, 1) # will deliberately fail
    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2)
    assert not automation.lib.is_bank_holiday(datetime.datetime.now())

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_rain(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('sensor.icambr4_precipitation_today', 5)
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.rain() == 5
    assert not automation.lib.no_rain()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_no_rain(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('sensor.icambr4_precipitation_today', 0)
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.rain() == 0
    assert automation.lib.no_rain()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-05-18')
def test_is_summer_1(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 5, 18)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-09-09')
def test_is_summer_2(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 9, 9)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-03-18')
def test_is_not_summer_1(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 3, 18)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.lib.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-09-18')
def test_is_not_summer_2(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 9, 18)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.lib.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_dusk(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.is_dusk()

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 2, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.is_dusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_predusk(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 0, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.is_predusk()

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.is_predusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_mock_run(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_mock_run()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'off')

    assert not automation.lib.is_mock_run()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_sun_elevation(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.get_sun_elevation() == 4

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-03')
def test_is_weekend_1(hass_driver, automation: Automation):

    assert datetime.date.today() == datetime.date(2024, 8, 3)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04')
def test_is_weekend_2(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 4)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05')
def test_not_is_weekend_1(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 5)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.lib.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09')
def test_not_is_weekend_2(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 9)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not automation.lib.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-03')
def test_dow_1(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 3)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 6

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04')
def test_dow_2(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 4)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 7

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05')
def test_dow_3(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 5)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 1

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-06')
def test_dow_4(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 6)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 2

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-07')
def test_dow_5(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 7)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 3

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-08')
def test_dow_6(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 8)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 4

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09')
def test_dow_7(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 9)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.dow() == 5

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01 19:00:01')
def test_is_after(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 19, 0, 1)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.is_after(19)

    assert not automation.lib.is_after(20)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_alarm_testing(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')

    assert not automation.lib.get_alarm_testing()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'on')

    assert automation.lib.get_alarm_testing()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_testing(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.testing', 'off')

    assert not automation.lib.get_testing()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.testing', 'on')

    assert automation.lib.get_testing()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_debug(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.debug', 'off')

    assert not automation.lib.get_debug()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.debug', 'on')

    assert automation.lib.get_debug()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_verbose(hass_driver, automation: Automation):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.verbose', 'off')

    assert not automation.lib.get_verbose()

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.verbose', 'on')

    assert automation.lib.get_verbose()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02 19:00:00')
def test_get_entity_id_1(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2, 19, 0, 0)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.get_entity_id() == ('media_player.kitchen', 0.5)
    # assert automation.lib.get_entity_id() == ('media_player.study', 0.2)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02 19:00:00')
def test_get_entity_id_2(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2, 19, 0, 0)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.get_entity_id() == ('media_player.study', 0.2)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02 21:31:00')
def test_get_entity_id_3(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2, 21, 31, 0)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.get_entity_id() == ('media_player.study', 0.2) # FIXME
    # assert automation.lib.get_entity_id() == ('media_player.study', 0.1)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02 21:31:00')
def test_get_entity_id_4(hass_driver, automation: Automation):

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2, 21, 31, 0)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert automation.lib.get_entity_id('media_player.mock') == ('media_player.mock', 0.25)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------
