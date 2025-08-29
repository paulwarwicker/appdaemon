from datetime import datetime
from unittest import mock
# from unittest.mock import AsyncMock, patch

import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.hass.hassapi as Hass
import pytest

from appdaemon_testing import HassDriver
from appdaemon_testing.pytest import automation_fixture

from freezegun import freeze_time
from alarms_async import Alarms2

STUDY_ENTITY_ID = 'media_player.study'

# def test_get_state(hass_driver):
#     get_state = hass_driver.get_mock("get_state")
#     assert get_state("light.1") == "off"

# @pytest.fixture
# def hass_driver() -> HassDriver:
#     hass_driver = HassDriver()
#     hass_driver._states = {
#         "light.1": {"state": "off", "linkquality": 60},
#         "light.2": {"state": "on", "linkquality": 10, "brightness": 60},
#         "media_player.smart_tv": {"state": "on", "source": None},
#     }
#     return hass_driver


# @automation_fixture(
#     Alarms,
#     args={
#     },
# )

@automation_fixture(
    Alarms2,
    initialize=False
)

# -----------------------------------------------------------------------------------

def alarms() -> Alarms2:
    pass

# -----------------------------------------------------------------------------------

@freeze_time('2024-08-05 00:00:20')
# @patch("alarms.Alarms.initialize", return_value=None)
# @pytest.mark.asyncio
async def test_set_alarm_state_1(hass_driver, alarms: Alarms2):  # pylint: disable=W0621

    assert datetime.now() == datetime(2024, 8, 5, 0, 0, 20)

    with hass_driver.setup():
        # hass_driver.set_state('input_datetime.early_alarm', '05:00:00')
        # hass_driver.set_state('input_datetime.early_alarm', {'hour': 5, 'minute': 0, 'second': 0}, attribute_name='attributes')
        # hass_driver.set_state('input_boolean.early_alarm', 'on')
        # hass_driver.set_state('input_datetime.normal_alarm', '08:00:00')
        # hass_driver.set_state('input_datetime.normal_alarm', {'hour': 8, 'minute': 0, 'second': 0}, attribute_name='attributes')
        # hass_driver.set_state('input_boolean.normal_alarm', 'on')
        # hass_driver.set_state('input_boolean.alarm_testing', 'off')
        # hass_driver.set_state('input_boolean.mock_run', 'on')
        hass_driver.set_state('input_boolean.alarms_disabled', 'on')

    # # Mock call_service
    # call_service = AsyncMock()
    # hass_driver.get_mock = AsyncMock(return_value=call_service)

    # # Mock alarms.get_state
    # alarms.get_state = AsyncMock(return_value="on")

    # # Set the timeout directly as a float or integer
    # alarms.internal_function_timeout = 5  # Fixed

    # Call the async method
    await alarms.get_alarm_state()

    # # Validate calls
    # call_service.assert_has_calls([
    #     mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The early morning alarm is set to 04:55'),
    #     mock.call('announcer/announce', entity_id=STUDY_ENTITY_ID, message='The normal morning alarm is set to 07:55'),
    # ])
