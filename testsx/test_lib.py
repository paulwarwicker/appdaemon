from unittest import mock

import appdaemon.plugins.hass.hassapi as Hass
# from appdaemon_testing.pytest import with_app

import pytest

from appdaemon_testing import HassDriver
from appdaemon_testing.pytest import automation_fixture

from freezegun import freeze_time
from apps.automationlib2 import AutomationLib

# @automation_fixture(
#     AutomationLib,
#     args={
#         "thing": Hass
#     },
# )

@automation_fixture(AutomationLib)
def lib() -> AutomationLib:
    pass

# -----------------------------------------------------------------------------------

@freeze_time('2024-05-18')
# @with_app(AutomationLib)
def test_is_summer(hass_driver, lib: AutomationLib):

    with hass_driver.setup():
        hass_driver.set_state('input_boolean.mock_run', 'on')

    assert lib.is_summer()

# -----------------------------------------------------------------------------------
