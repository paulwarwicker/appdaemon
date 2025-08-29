# -*- coding: utf-8 -*-

import datetime

from appdaemon_testing.pytest import automation_fixture
from appdaemon_testing.pytest import mock
from freezegun import freeze_time
from apps.announcer import Announcer

@automation_fixture(
    Announcer,
    args={
    },
)

# -----------------------------------------------------------------------------------

def announcer() -> Announcer: # pylint: disable=W0212 disable=W0621
    pass

# if self.get_state('input_boolean.force_announcement') == 'on':
#             return True

#         if hint is False or self.get_state('input_boolean.mute_announcement') == 'on':

# -----------------------------------------------------------------------------------

@freeze_time('2024-01-01 21:29:59')
def test_announceable_1(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 29, 59)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mute_announcement', 'off')

    # assert announcer._announceable(True)  # pylint: disable=W0212 disable=W0621
    assert not announcer._announceable(False) # pylint: disable=W0212 disable=W0621 # FIXME

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mute_announcement', 'on')

    assert not announcer._announceable(False)  # pylint: disable=W0212 disable=W0621
    assert not announcer._announceable(True)  # pylint: disable=W0212 disable=W0621 # FIXME

# -----------------------------------------------------------------------------------

@freeze_time('2024-01-01 21:30:01')
def test_announceable_2(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

    # with hass_driver.setup():
        # hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
        # hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 30, 1)

    assert not announcer._announceable(True) # pylint: disable=W0212 disable=W0621
    assert not announcer._announceable(False) # pylint: disable=W0212 disable=W0621

# -----------------------------------------------------------------------------------

@freeze_time('2024-01-01 21:29:59')
def test_announceable_3(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

    assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 29, 59)

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.force_announcement', 'off')

    # assert announcer._announceable(True)  # pylint: disable=W0212 disable=W0621
    assert not announcer._announceable(False) # pylint: disable=W0212 disable=W0621 # FIXME

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mute_announcement', 'on')

    assert announcer._announceable(False)  # pylint: disable=W0212 disable=W0621
    assert announcer._announceable(True)  # pylint: disable=W0212 disable=W0621 # FIXME

# -----------------------------------------------------------------------------------

# @freeze_time('2024-01-01 21:29:59')
# def test_announceable3(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.force_announcement', 'off')
#         hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
#         # hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
#         hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 29, 59)
#     assert announcer._announceable()

# @freeze_time('2024-01-01 21:29:59')
# def test_announceable4(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.mute_announcement', 'on')
#         hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
#         # hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
#         hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 29, 59)
#     assert not announcer._announceable()


# @freeze_time('2024-01-01 21:30:01')
# def test_announceable5(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.force_announcement', 'off')
#         hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
#         # hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
#         hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

#     print(datetime.datetime.now())

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 30, 1)
#     assert not announcer._announceable()

# @freeze_time('2024-01-01 21:30:01')
# def test_announceable6(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.force_announcement', 'on')
#         hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
#         # hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
#         hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

#     print(datetime.datetime.now())

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 30, 1)
#     assert announcer._announceable()

# @freeze_time('2024-01-01 21:30:01')
# def test_announceable7(hass_driver, announcer: Announcer): # pylint: disable=W0212 disable=W0621

#     with hass_driver.setup():
#         hass_driver.set_state('input_boolean.force_announcement', 'on')
#         hass_driver.set_state('input_boolean.mute_announcement', 'on')
#         hass_driver.set_state('input_datetime.early_alarm_time', '05:00:00')
#         # hass_driver.set_state('input_datetime.early_alarm_time', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
#         hass_driver.set_state('input_datetime.early_alarm_time', 5, attribute_name='hour')

#     print(datetime.datetime.now())

#     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 21, 30, 1)
#     assert announcer._announceable()


# # @freeze_time('2024-01-01 00:00:00')
# # def test_announceable5(hass_driver, announcer: Announcer):

# #     call_service = hass_driver.get_mock("call_service")

# #     with hass_driver.setup():
# #         hass_driver.set_state('input_boolean.mock_run', 'on')

# #     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 0, 0, 0)
# #     assert not announcer.announceable()


# # @freeze_time('2024-01-01 07:59:59')
# # def test_announceable6(hass_driver, announcer: Announcer):

# #     call_service = hass_driver.get_mock("call_service")

# #     with hass_driver.setup():
# #         hass_driver.set_state('input_boolean.mock_run', 'on')

# #     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 7, 59, 59)
# #     assert not announcer.announceable()


# # @freeze_time('2024-01-01 08:00:00')
# # def test_announceable7(hass_driver, announcer: Announcer):

# #     call_service = hass_driver.get_mock("call_service")

# #     with hass_driver.setup():
# #         hass_driver.set_state('input_boolean.mock_run', 'on')

# #     assert datetime.datetime.now() == datetime.datetime(2024, 1, 1, 8, 0, 0)
# #     assert announcer.announceable()


