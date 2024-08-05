# -*- coding: utf-8 -*-
# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing
# https://pypi.org/project/pytest-freezer/
# https://github.com/pytest-dev/pytest-freezer

from datetime import datetime
from appdaemon_testing.pytest import automation_fixture
from appdaemon_testing.pytest import mock
from freezegun import freeze_time
from apps.alarms import Alarms

STUDY_ENTITY_ID = 'media_player.study'
KITCHEN_ENTITY_ID = 'media_player.kitchen'
STUDY_VOLUME = 0.3

@automation_fixture(
    Alarms,
    args={
    },
    # initialize=False
)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def alarms() -> Alarms:
    pass

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04 19:00:00')
def test_initialised(hass_driver, alarms: Alarms):

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')
        hass_driver.set_state('input_datetime.early_alarm_time', 0, attribute_name='minute')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm_time', '07:00:00')
        hass_driver.set_state('input_datetime.normal_alarm_time', 7, attribute_name='hour')
        hass_driver.set_state('input_datetime.normal_alarm_time', 0, attribute_name='minute')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        # hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    assert datetime.now() == datetime(2024, 8, 4, 19, 0, 0)

    call_service.assert_has_calls([
        mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='The early morning alarm is cancelled', snapshot=False),
        mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is cancelled', snapshot=False),
        # mock.call("announcer/initialised", name='Alarms')
    ])
        # mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 07:40', snapshot=False),

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05 00:00:20')
def test_set_alarm_state_1(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm_time', '08:00:00')
        hass_driver.set_state('input_datetime.normal_alarm_time', {'hour': 8, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.alarm_debug', 'off')
        # hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    assert datetime.now() == datetime(2024, 8, 5, 0, 0, 20)

    alarms.set_alarm_state()

    call_service.assert_has_calls([
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is cancelled', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is cancelled', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is set to unset', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 07:55', snapshot=False)
        # mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='The early morning alarm is cancelled', snapshot=False),
        # mock.call("announcer/announce", entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is cancelled', snapshot=False),
    ])
