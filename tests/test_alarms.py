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
)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def alarms() -> Alarms:
    pass

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04 19:00:00')
def test_initialised(hass_driver, alarms: Alarms):

    assert datetime.now() == datetime(2024, 8, 4, 19, 0, 0)

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm_time', '08:00:00')
        hass_driver.set_state('input_datetime.normal_alarm_time', {'hour': 8, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    call_service.assert_has_calls([
        mock.call("announcer/initialised", name='Alarms', announce=False)
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05 00:00:20')
def test_set_alarm_state_1(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 5, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm', '08:00:00')
        hass_driver.set_state('input_datetime.normal_alarm', {'hour': 8, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    alarms.set_alarm_state({})

    call_service.assert_has_calls([
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is set to 04:55', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 07:55', snapshot=False),
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05 00:00:20')
def test_set_alarm_state_2(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 5, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm', '07:00:00')
        hass_driver.set_state('input_datetime.early_alarm', {'hour': 7, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm', '09:00:00')
        hass_driver.set_state('input_datetime.normal_alarm', {'hour': 9, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    alarms.set_alarm_state({})

    call_service.assert_has_calls([
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is set to 06:55', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 08:55', snapshot=False),
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05 00:00:20')
def test_show_alarm_time(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 5, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_datetime.early_alarm', '07:00:00')
        hass_driver.set_state('input_datetime.early_alarm', {'hour': 7, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.early_alarm', 'on')
        hass_driver.set_state('input_datetime.normal_alarm', '09:00:00')
        hass_driver.set_state('input_datetime.normal_alarm', {'hour': 9, 'minute': 0, 'second': 0}, attribute_name='attributes')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    alarms.show_alarm_time('early')
    alarms.show_alarm_time('normal')

    call_service.assert_has_calls([
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is set to 06:55', snapshot=False),
        mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 08:55', snapshot=False),
    ])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-07 20:30:20') # wednesday -> thursday
def test_get_early_alarm_time_1(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 7, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-08 00:00:20') # thursday -> thursday
def test_get_early_alarm_time_2(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 8, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-08 20:30:20') # thursday -> friday
def test_get_early_alarm_time_3(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 8, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09 00:00:20') # friday -> friday
def test_get_early_alarm_time_4(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 9, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09 20:30:20') # friday -> saturday
def test_get_early_alarm_time_5(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 9, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-10 00:00:20') # saturday -> saturday
def test_get_early_alarm_time_6(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 10, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-10 20:30:20') # saturday -> sunday
def test_get_early_alarm_time_7(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 10, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'off'
    assert alarm_time == '08:00'
    assert hour == 8
    assert minute == 0

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-11 00:00:20') # sunday -> sunday
def test_get_early_alarm_time_8(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 11, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'off'
    assert alarm_time == '08:00'
    assert hour == 8
    assert minute == 0

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-11 20:30:20') # sunday -> monday
def test_get_early_alarm_time_9(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 11, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-12 00:00:20') # monnday -> monday
def test_get_early_alarm_time_10(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 12, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_early_alarm_time()

    assert state == 'on'
    assert alarm_time == '04:58'
    assert hour == 4
    assert minute == 58

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-08 20:30:20')
def test_get_normal_alarm_time_1(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 8, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_normal_alarm_time()

    assert state == 'on'
    assert alarm_time == '07:45'
    assert hour == 7
    assert minute == 45

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09 00:00:20')
def test_get_normal_alarm_time_2(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 9, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_normal_alarm_time()

    assert state == 'on'
    # assert alarm_time == '07:45'
    assert alarm_time == '10:00'
    assert hour == 10
    assert minute == 0

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09 20:30:20')
def test_get_normal_alarm_time_3(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 9, 20, 30, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_normal_alarm_time()

    assert state == 'on'
    assert alarm_time == '10:00'
    assert hour == 10
    assert minute == 0

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-10 00:00:20')
def test_get_normal_alarm_time_4(hass_driver, alarms: Alarms):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 10, 0, 0, 20)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.alarm_testing', 'off')
        hass_driver.set_state('input_boolean.normal_alarm', 'on')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    call_service = hass_driver.get_mock("call_service")

    (state, alarm_time, hour, minute) = alarms.get_normal_alarm_time()

    assert state == 'on'
    assert alarm_time == '10:00'
    assert hour == 10
    assert minute == 0

    call_service.assert_has_calls([])

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

