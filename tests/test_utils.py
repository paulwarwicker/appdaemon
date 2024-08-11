# -*- coding: utf-8 -*-
# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing
# https://pypi.org/project/pytest-freezer/
# https://github.com/pytest-dev/pytest-freezer

import datetime

from appdaemon_testing.pytest import automation_fixture
from appdaemon_testing.pytest import mock
from freezegun import freeze_time
from apps.utils import Utils

@automation_fixture(
    Utils,
    args={
    },
)

def utils() -> Utils:
    pass

# def is_dusk(self): *
# def is_predusk(self):*
# def is_bank_holiday(self, dt=datetime.now()): *
# def is_weekend(self): *
# def is_after(self, hour):
# def is_summer(self): *
# def dow(self): *
# def no_rain(self): *
# def rain(self): *
# def delay(self, s):
# def is_mock_run(self): *
# def log_debug(self, message):
# def get_sun_elevation(self): *

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01')
def test_is_bank_holiday(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1)
    assert utils.is_bank_holiday(datetime.datetime.now())

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# @freeze_time('2024-01-01')
# def test_is_bank_holiday2(hass_driver, utils: Utils):

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.mock_run', 'on')

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1)
#     assert utils.is_bank_holiday()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02')
def test_not_is_bank_holiday_1(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2)
    assert not utils.is_bank_holiday()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-02')
def test_not_is_bank_holiday_2(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 2)
    assert not utils.is_bank_holiday()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_rain(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('sensor.icambr4_precipitation_today', 5)
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.rain() == 5
    assert not utils.no_rain()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_no_rain(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('media_player.study', {'volume_level': 1, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('sensor.icambr4_precipitation_today', 0)
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.rain() == 0
    assert utils.no_rain()

    with hass_driver.setup():
        hass_driver.set_state('media_player.study', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('media_player.kitchen', {'volume_level': 0, 'is_volume_muted': True, 'media_content_id': '', 'media_content_type': ''}, attribute_name='attributes')
        hass_driver.set_state('sensor.icambr4_precipitation_today', 0)
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.no_rain()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-05-18')
def test_is_summer(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01')
def test_not_is_summer(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not utils.is_summer()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_dusk(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', -4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.is_dusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_not_is_dusk(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 2, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not utils.is_dusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_predusk(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 0, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.is_predusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_not_is_predusk(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert not utils.is_predusk()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_not_is_mock_run(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'off')

    assert not utils.is_mock_run()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_is_mock_run(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.is_mock_run()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

def test_get_sun_elevation(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('sun.sun', 4, attribute_name='elevation')
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert utils.get_sun_elevation() == 4

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-03')
def test_is_weekend_1(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 3)
    assert utils.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04')
def test_is_weekend_2(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 4)
    assert utils.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05')
def test_not_is_weekend(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 5)
    assert not utils.is_weekend()

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-03')
def test_dow_1(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 3)
    assert utils.dow() == 6

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-04')
def test_dow_2(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 4)
    assert utils.dow() == 7

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-05')
def test_dow_3(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 5)
    assert utils.dow() == 1

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-06')
def test_dow_4(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 6)
    assert utils.dow() == 2

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-07')
def test_dow_5(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 7)
    assert utils.dow() == 3

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-08')
def test_dow_6(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 8)
    assert utils.dow() == 4

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-08-09')
def test_dow_7(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert datetime.datetime.now() == datetime.datetime(2024, 8, 9)
    assert utils.dow() == 5

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01 19:00:01')
def test_is_after(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.early_alarm', 'off')
        hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')

    assert utils.is_after(19)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

@freeze_time('2024-01-01 19:00:01')
def test_not_is_after(hass_driver, utils: Utils):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.early_alarm', 'off')
        hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')

    assert not utils.is_after(20)

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

