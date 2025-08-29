import pytest
from loc import Location # was apps.loc
from appdaemon_testing.pytest_plugin import automation_fixture
from hass_driver import HassDriver # was appdaemon_testing.hass_driver

@automation_fixture(Location, initialize=True)
async def app(hass_driver) -> Location:
    return None

@pytest.mark.asyncio
async def test_initialize(app: Location, hass_driver: HassDriver):
    await hass_driver.set_state('input_boolean.default_debug_state', 'on')
    state = await hass_driver.get_state("input_boolean.default_debug_state")
    assert state == "on"
    await hass_driver.set_state('input_boolean.default_verbose_state', 'off')
    await hass_driver.set_state('input_boolean.default_testing_state', 'off')
    await hass_driver.set_state('input_boolean.default_trace_state', 'off')
    await app.initialize()

    assert isinstance(app.lib, object)
    assert app.lib.get_debug() is True
    assert app.lib.get_verbose() is False
    assert app.lib.get_testing() is False
    assert app.lib.get_verbose_debug() is False
