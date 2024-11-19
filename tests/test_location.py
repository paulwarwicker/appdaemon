# -*- coding: utf-8 -*-

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing
# https://pypi.org/project/pytest-freezer/
# https://github.com/pytest-dev/pytest-freezer

from appdaemon_testing.pytest import automation_fixture
from appdaemon_testing.pytest import mock
from freezegun import freeze_time
from apps.location import Location

MESSAGE_VILLAGE = 'Max is in the village'
STUDY_VOLUME = 0.3
STUDY_ENTITY_ID = 'media_player.study'
KITCHEN_ENTITY_ID = 'media_player.kitchen'

@automation_fixture(
    Location,
    args={
    },
)

# -----------------------------------------------------------------------------------

def location() -> Location:
    pass

# -----------------------------------------------------------------------------------

def test_initialize(hass_driver, location: Location):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    call_service.assert_has_calls([
        mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='Location initialised')
    ])

# -----------------------------------------------------------------------------------

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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


# def test_max_dssmith_announce1(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'off')
#         hass_driver.set_state('input_boolean.verbose', 'off')
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'old', 'DS_Smith_Fordham', {'name': 'DS_Smith_Fordham', 'location': 'proximity.ds_smith_fordham', 'test': True})

# # -----------------------------------------------------------------------------------


# def test_max_dssmith_announce2(hass_driver, automation: Automation):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.debug', 'on')
#         hass_driver.set_state('input_boolean.verbose', 'on')
#         hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     automation.max_location_detect('entity', 'attribute', 'DS_Smith_Fordham', 'new', {'name': 'DS_Smith_Fordham', 'location': 'proximity.ds_smith_fordham', 'test': True})

# # -----------------------------------------------------------------------------------

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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------


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

# # -----------------------------------------------------------------------------------
