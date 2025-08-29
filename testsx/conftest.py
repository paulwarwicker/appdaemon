import threading
import asyncio

from types import MethodType
from types import SimpleNamespace

import pytest

from appdaemon_testing.hass_driver import HassDriver

class MockAD:
    def __init__(self, logger, hd):
        self._states = {"default": {}}  # per-namespace store
        self._state_store = {}

        # def set_state(entity_id, state, namespace="default"):
        #     self._states.setdefault(namespace, {})[entity_id] = state

        # async def get_state(**kwargs):
        #     ns = kwargs.get("namespace", "default")
        #     eid = kwargs.get("entity_id")
        #     return hd._states.get(ns, {}).get(eid)

        async def fake_set_state(entity_id, value, **kwargs):
            self._state_store[entity_id] = value
            return True

        async def fake_get_state(entity_id, **kwargs):
            return self._state_store.get(entity_id)

        self.logger = logger
        self.events = SimpleNamespace(add_event_callback=lambda *a, **k: None)
        self.plugins = SimpleNamespace(get_plugin_object=lambda ns: SimpleNamespace(name="mock_plugin"))
        self.futures = SimpleNamespace(add_future=lambda name, task: None)
        self.main_thread_id = threading.current_thread().ident
        self.http = None

        self.events = SimpleNamespace(
            add_event_callback=lambda *a, **k: asyncio.sleep(0)
        )

        self.services = SimpleNamespace(
            register_service=lambda *a, **k: None,
            call_service=lambda **kwargs: asyncio.sleep(0)
        )

        self.config = SimpleNamespace(
            model_dump=lambda **kwargs: {"some_key": "some_value"},
            ascii_encode=True
        )

        # self.state = SimpleNamespace(
        #     add_state_callback=lambda *a, **k: None,
        #     namespace_exists=lambda ns: True,
        #     entity_exists=lambda ns, eid: eid in hd._states.get(ns or "default", {}),
        #     get_state=get_state,
        # )

        self.state = SimpleNamespace(
            add_state_callback=lambda *a, **k: None,
            set_state=fake_set_state,
            get_state=fake_get_state,
            namespace_exists=lambda ns: True,
            entity_exists=lambda ns, eid: eid in hd._states.get(ns or "default", {}),
        )


def compatible_logger():
    class DummyLogger:
        def debug(self, msg, *args, **kwargs): print("[DEBUG]", msg % args if args else msg)
        def info(self, msg, *args, **kwargs): print("[INFO]", msg % args if args else msg)
        def warning(self, msg, *args, **kwargs): print("[WARN]", msg % args if args else msg)
        def error(self, msg, *args, **kwargs): print("[ERROR]", msg % args if args else msg)
        def setLevel(self, level): pass
        def log(self, level, msg, *args, **kwargs): print(f"[LOG-{level}]", msg % args if args else msg)

        def get_child(self, name):
            return self  # Simulate child logger

        def get_error(self):
            return self  # For .get_error().getChild()

        def getChild(self, name):  # Alias for get_child
            return self

    return DummyLogger()

@pytest.fixture
def hass_driver() -> HassDriver:
    logger = compatible_logger()

    hass_driver.get_state = MethodType(lambda self, *a, **k: self.state.get_state(*a, **k), hass_driver)
    hass_driver.set_state = MethodType(lambda self, *a, **k: self.state.set_state(*a, **k), hass_driver)

    hd = HassDriver()
    hd.logger = logger
    mock_ad = MockAD(logger, hd)
    # hd.logging = mock_ad.logger
    hd.services = mock_ad.services
    hd.state = mock_ad.state
    # hd.events = mock_ad.events
    # hd.http = mock_ad.http
    # hd.plugins = mock_ad.plugins
    # hd.config = mock_ad.config
    hd.futures = mock_ad.futures
    hd.main_thread_id = mock_ad.main_thread_id

    hd.set_state = mock_ad.state.set_state
    hd.get_state = mock_ad.state.get_state

    return hd
