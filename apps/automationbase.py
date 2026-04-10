# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import concurrent.futures
import asyncio
import time
import inspect
import sys

from datetime import datetime,timedelta
from typing import cast, Coroutine, Any

import requests # type: ignore pylint: disable=import-error

from hassapi import Hass # type: ignore

import constants as const # pylint: disable=unused-import

class SharedState:
    """Shared state for AutomationBase and derived classes"""
    trace: bool = False
    debug: bool = False
    verbose: bool = False
    testing: bool = False
    log_level: str | None = "INFO"

class AutomationBase(Hass):
    """Documentation for AutomationBase"""

    # trace = False
    # debug = False
    # verbose = False
    # testing = False
    # log_level = None

    shared = SharedState()

    # pylint: disable=attribute-defined-outside-init
    def initialize(self):
        """base initialization logic"""

        self.shared.debug = self.get_state('input_boolean.debug') == 'on'
        self.shared.verbose = self.get_state('input_boolean.verbose') == 'on'
        self.shared.testing = self.get_state('input_boolean.testing') == 'on'
        self.shared.trace = self.get_state('input_boolean.trace') == 'on'
        self.shared.log_level = None
        # self.log(f"\tautomationbase: debug={self.shared.debug} verbose={self.shared.verbose} testing={self.shared.testing} trace={self.shared.trace}", level='WARNING')

        self._set_console_log_level()

# -----------------------------------------------------------------------------------

    # async def initialize_async(self):
    #     """base initialization logic async version"""

    #     self.shared.debug = await self.get_state('input_boolean.debug') == 'on'
    #     self.shared.verbose = await self.get_state('input_boolean.verbose') == 'on'
    #     self.shared.testing = await self.get_state('input_boolean.testing') == 'on'
    #     self.shared.trace = await self.get_state('input_boolean.trace') == 'on'
    #     self.log(f"\tautomationbase: debug={self.shared.debug} verbose={self.shared.verbose} testing={self.shared.testing} trace={self.shared.trace}", level='WARNING')

# -----------------------------------------------------------------------------------

    def _now(self) -> datetime:
        """now"""

        return datetime.now()

# -----------------------------------------------------------------------------------

    def _dow(self) -> int:
        """day of week"""

        return self._now().isoweekday()

# -----------------------------------------------------------------------------------

    def _is_bank_holiday(self, dt: datetime=datetime.now()) -> bool:
        """is today (or dt argument) a bank holiday"""

        self.log(f'\tdt={dt}', level='DEBUG')

        url = 'https://www.gov.uk/bank-holidays.json'
        today = f'{dt:%Y-%m-%d}'

        _is_bank_holiday = False

        try:
            resp = requests.get(url=url, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()  # https://requests.readthedocs.io/en/master/user/quickstart/#json-response-content
        except requests.RequestException as exc:
            self.log(f'Failed to fetch bank holidays: {exc}', level='ERROR')
            return False

        events = data["england-and-wales"]["events"]

        for event in events:
            date_str = event["date"]
            dt = datetime.strptime(date_str, '%Y-%m-%d')

            if f'{dt.date():%Y-%m-%d}' == today:
                _is_bank_holiday = True

        if self._get_verbose_debug():
            t = 'is not' if not _is_bank_holiday else 'is'
            self.log(f'\t{t} bank holiday', level='DEBUG')

        return _is_bank_holiday

# -----------------------------------------------------------------------------------

    def _is_weekend(self) -> bool: # ??
        """is today a weekend"""

        return self.dow() >= 6

# -----------------------------------------------------------------------------------

    def _is_after(self, hour: int) -> bool: # ??
        """is now after a certain hour"""

        dt = datetime.now()

        return dt.hour >= hour

# -----------------------------------------------------------------------------------

    def _is_summer(self) -> bool:
        """is today a summer day (end of april to mid-september)"""

        (_, isow, _) = self._now().isocalendar()

        return 17 <= isow <= 37

# -----------------------------------------------------------------------------------

    def _summer_heating(self) -> bool:
        """summer heating"""

        return self._is_summer() # TODO: review

# -----------------------------------------------------------------------------------

    def _get_entity_id(self, entity_id) -> tuple:
        """get entity id and volume. if testing is set, use study, else use kitchen"""

        volume = 0

        if entity_id is None:
            if self.get_state('input_boolean.alarm_testing') == 'on':
                entity_id = 'media_player.study'

                if self.now_is_between('08:00:00', '22:29:59'):
                    volume = const.STUDY_ANNOUNCE_VOLUME
                elif self.now_is_between('22:30:00', '07:59:59'):
                    volume = const.STUDY_ANNOUNCE_VOLUME_LOW
            else:
                entity_id = 'media_player.kitchen'

                if self.now_is_between('08:00:00', '22:29:59'):
                    volume = const.ANNOUNCE_VOLUME
                elif self.now_is_between('22:30:00', '07:59:59'):
                    volume = const.ANNOUNCE_VOLUME_LOW
        else:
            # just set volume
            if self.now_is_between('08:00:00', '22:29:59'):
                volume = const.ANNOUNCE_VOLUME
            elif self.now_is_between('22:30:00', '07:59:59'):
                volume = const.ANNOUNCE_VOLUME_LOW

        return (entity_id, volume)

# -----------------------------------------------------------------------------------

    def _no_rain(self) -> bool:
        """was there more than 1mm of rain today"""

        return True if self.rain() < 1.0 else False

# -----------------------------------------------------------------------------------

    def _rain(self) -> float:
        """get preciptation today"""

        result = 0.0 # FIXME: float(self.get_state(entity_id='sensor.icambr4_precipitation_today'))

        if self._get_verbose_debug():
            self.log(f'\tmmrain={result}', level='DEBUG')

        return result

# -----------------------------------------------------------------------------------

    def _delay(self, seconds: float) -> None:
        """sleep for s seconds if not a mock run"""

        if not self._is_mock_run():
            time.sleep(seconds)

# -----------------------------------------------------------------------------------

    def _is_mock_run(self) -> bool:
        """is this a mock run"""

        return self.get_state('input_boolean.mock_run') == 'on'

# -----------------------------------------------------------------------------------

    def _get_debug(self):
        """get debug setting"""

        return self.shared.debug

# -----------------------------------------------------------------------------------

    def _get_verbose(self):
        """get verbose setting"""

        return self.shared.verbose

# -----------------------------------------------------------------------------------

    def _get_verbose_debug(self):
        """get verbose debug setting"""

        return self._get_verbose() and self._get_debug()

# -----------------------------------------------------------------------------------

    def _get_testing(self):
        """get testing setting"""

        return self.shared.testing

# -----------------------------------------------------------------------------------

    def _get_testing_verbose_debug(self):
        """get verbose testing flag"""

        return self._get_testing() and self._get_verbose_debug()

# -----------------------------------------------------------------------------------

    def _get_alarm_testing(self) -> bool:
        """get alrm debug setting"""

        return self.get_state("input_boolean.alarm_testing") == "on"

# -----------------------------------------------------------------------------------

    def _set_flag_value(self, _type, value: bool) -> bool:
        """set cached flag setting"""

        match _type:
            case 'debug':
                self.shared.debug = value
            case 'trace':
                self.shared.trace = value
            case 'verbose':
                self.shared.verbose = value
            case 'testing':
                self.shared.testing = value

        return value

# -----------------------------------------------------------------------------------

    def _log_function_name(self, **kwargs) -> None:
        """log function name as log message"""

        start = kwargs.get('start', True)
        separator = kwargs.get('separator', True)
        notification = kwargs.get('notification', False)
        stacktrace = kwargs.get('stacktrace', False)
        force = kwargs.get('force', False)

        if force:
            trace = separator = notification = True
        else:
            trace = self.shared.trace

        frame = inspect.currentframe()

        if frame is not None and frame.f_back is not None:
            name = frame.f_back.f_code.co_name
        else:
            name = "<unknown>"

        prefix = '>>' if start else '<<'

        if notification:
            _ = self.call_service('announcer/notification', message=f'{prefix} {name}', type='desktop') # TODO: why needed to shutup pylint

        if stacktrace:
            frame = inspect.currentframe()
            print(frame)
            if frame is not None and frame.f_back is not None:
                print(frame.f_back)

        if trace:
            if separator:
                dashes = '-' * (80 - len(name))
                self.log(f'{prefix} {name} {dashes}',level='INFO')
            else:
                self.log(f'\t{prefix} {name}', level='DEBUG')

# -----------------------------------------------------------------------------------

    async def _log_function_name_async(self, **kwargs) -> None:
        """log function name as log message (async version)"""

        self._log_function_name(**kwargs)

# -----------------------------------------------------------------------------------

    def _is_playing(self, entity_id) -> bool:
        """is entity id playing"""

        if entity_id is None:
            (entity_id, volume) = self._get_entity_id(None)

        _ = self.call_service('homeassistant/update_entity', entity_id=entity_id) # TODO: why needed to shutup pylint
        attributes = self.get_state(entity_id=entity_id, attribute="attributes")
        state = self.get_state(entity_id=entity_id)
        self.log(f'entity_id={entity_id} state={state} attributes={attributes}', level='DEBUG')

        return state == 'playing'

# -----------------------------------------------------------------------------------

    def _interval(self, minutes: int = 0, seconds: int = 0) -> int:
        """return minutes or seconds as integer number of seconds"""

        return int(timedelta(minutes=minutes, seconds=seconds).total_seconds())

# -----------------------------------------------------------------------------------

    def _is_twilight(self) -> bool:
        """is it twilight (civil twilight: sun elevation between -6 and 0 degrees)"""

        elev = self.get_state('sun.sun', attribute='elevation')

        # If get_state leaked an awaitable/task, resolve it synchronously (with a short timeout)
        if asyncio.iscoroutine(elev) or isinstance(elev, asyncio.Task):
            # prefer a loop captured in initialize: self._loop = asyncio.get_running_loop()
            loop = getattr(self, "_loop", None)
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
            if loop is not None:
                fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], elev), loop)
                try:
                    elev = fut.result(timeout=1)
                except Exception:
                    elev = None
            else:
                elev = None
        elif isinstance(elev, (concurrent.futures.Future, asyncio.Future)):
            try:
                elev = elev.result() # (timeout=1)
            except Exception:
                elev = None

        if elev in (None, 'unknown'):
            return False

        try:
            elev_val = float(elev)
        except (TypeError, ValueError):
            return False

        twilight = -6 < elev_val < 0

        if self._get_verbose_debug():
            t = 'is' if twilight else 'is not'
            self.log(f'{t} twilight (elev={elev_val})', level='DEBUG')

        return twilight

# -----------------------------------------------------------------------------------

    def _is_night(self) -> bool:
        """is it night (sun elevation <= -6 degrees)"""

        elev = self.get_state('sun.sun', attribute='elevation')

        # If get_state leaked an awaitable/task, resolve it synchronously (with a short timeout)
        if asyncio.iscoroutine(elev) or isinstance(elev, asyncio.Task):
            # prefer a loop captured in initialize: self._loop = asyncio.get_running_loop()
            loop = getattr(self, "_loop", None)
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
            if loop is not None:
                fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], elev), loop)
                try:
                    elev = fut.result(timeout=1)
                except Exception:
                    elev = None
            else:
                elev = None
        elif isinstance(elev, (concurrent.futures.Future, asyncio.Future)):
            try:
                elev = elev.result() # (timeout=1)
            except Exception:
                elev = None

        if elev in (None, 'unknown'):
            return False

        try:
            elev_val = float(elev)
        except (TypeError, ValueError):
            return False

        night = elev_val <= -6

        if self._get_verbose_debug():
            t = 'is' if night else 'is not'
            self.log(f'{t} night (elev={elev_val})', level='DEBUG')

        return night

# -----------------------------------------------------------------------------------

    def _is_below_horizon(self) -> bool:
        """is sun below the horizon (defensive: resolve awaitables, coerce to float)"""

        self.log(f'is_below_horizon: app={type(self)} log_attr={type(getattr(self, "log", None))}', level='DEBUG')

        elev = self.get_state('sun.sun', attribute='elevation')
        self.log(f'raw elev type={type(elev)} value={elev!r}', level='DEBUG')

        # resolve if get_state returned a coroutine/Task or a Future
        if asyncio.iscoroutine(elev) or isinstance(elev, asyncio.Task):
            # prefer a loop captured in initialize: self._loop = asyncio.get_running_loop()
            loop = getattr(self, "_loop", None)
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None
            if loop is not None:
                try:
                    fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], elev), loop)
                    elev = fut.result(timeout=1)
                except Exception:
                    elev = None
            else:
                elev = None
        elif isinstance(elev, (concurrent.futures.Future, asyncio.Future)):
            try:
                elev = elev.result() # (timeout=1)
            except Exception:
                elev = None

        if elev in (None, 'unknown'):
            return False

        try:
            elev_val = float(elev)
        except (TypeError, ValueError):
            return False

        below = elev_val <= 0

        if self._get_verbose_debug():
            t = 'is' if below else 'is not'
            self.log(f'{t} below horizon (elev={elev_val})', level='DEBUG')

        return below

# -----------------------------------------------------------------------------------

    def _percent_to_brightness(self, percent:int):
        """convert percent (0-100) to brightness (0-255)"""

        return int(255/100 * percent)

# -----------------------------------------------------------------------------------

    def _call(self, name: str, *args, background: bool = True, wait: bool = False, timeout: float | None = None, **kwargs):
        """Dispatch a helper by name synchronously.

        - Calls a bound method on this AutomationLib instance if present, otherwise looks for a module-level
          function in this module.
        - If the target returns a coroutine/Task:
            - if background=True: schedule it with create_task and return the Task (fire-and-forget).
            - if wait=True: block until completion via run_coroutine_threadsafe and return the result.
            - otherwise: return the coroutine/Task to the caller (they must await it).

        # sync caller
        result = self.lib.call('some_helper', arg1, wait=True, timeout=5)
        # result is the helper return value (or None on error/timeout)

        # async caller
        coro = self.lib.call('some_helper', arg1, background=False)
        result = await coro

        # async caller
        task = self.lib.call('some_helper', arg1)  # background=True by default => returns Task
        result = await task
        """

        fn = getattr(self, name, None)

        if fn is None:
            fn = globals().get(name)
            if fn is None:
                mod = sys.modules.get(__name__)
                if mod is not None:
                    fn = getattr(mod, name, None)

        if fn is None:
            self.log(f'automationlib.call: no function named {name}', level='WARNING')
            return None

        try:
            res = fn(*args, **kwargs)
        except TypeError:
            # try module-style signature that expects (caller, ...)
            try:
                res = fn(self, *args, **kwargs)
            except Exception as exc:
                self.log(f'automationlib.call: failed to call {name}: {exc}', level='ERROR')
                return None

        # If it's a coroutine or Task, handle according to flags
        if asyncio.iscoroutine(res) or isinstance(res, asyncio.Task):
            # if caller wants to wait synchronously for the result
            if wait:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    # no running loop in this thread; try scheduling on main loop if available
                    loop = getattr(self, "_loop", None)
                if loop is None:
                    self.log(f'automationlib.call: no event loop available to wait for {name}', level='ERROR')
                    return None
                fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], res), loop)
                try:
                    return fut.result(timeout)
                except Exception as exc:
                    self.log(f'automationlib.call: waiting for {name} failed: {exc}', level='ERROR')
                    return None

            # background scheduling (non-blocking)
            # res may be a coroutine or an already-created Task.
            # If it's a Task, reuse it; if it's a coroutine, create a task from it.
            if isinstance(res, asyncio.Task):
                task = res
            else:
                try:
                    task = asyncio.create_task(cast(Coroutine[Any, Any, Any], res))
                except RuntimeError:
                    # no running loop in this thread ? return coroutine/Task to caller
                    return res

            def _on_done(t):
                try:
                    exc = t.exception()
                    if exc:
                        self.log(f'automationlib.call background {name} exception: {exc}', level='ERROR')
                except Exception as e:
                    self.log(f'automationlib.call background {name} done-callback failed: {e}', level='ERROR')

            task.add_done_callback(_on_done)
            return task if background else res

        return res

# -----------------------------------------------------------------------------------

    def _reset_trace(self, event, data, kwargs) -> None:
        """reset tracing flag from input_boolean"""

        self.shared.trace = self.shared.verbose = self.shared.debug = self.shared.testing = False

# -----------------------------------------------------------------------------------

    def _set_console_log_level(self) -> None:
        """internal method to set console level using the debug flag. set the property log_level and report a change"""

        level = "DEBUG" if self.get_state('input_boolean.debug') == 'on' else "INFO"
        prefix = "VERBOSE " if self.get_state('input_boolean.verbose') == 'on' else ""
        log_level = level+prefix

        if self.shared.log_level != log_level:
            self.log(f'\tchanging log level to {prefix}{level} (now {log_level} was {self.shared.log_level})', level='INFO')
            self.shared.log_level = log_level

            for module in const.MODULES:
                app = self.get_app(module)
                if app is not None:
                    self.log(f'setting log level {prefix}{level} on app {module} (app={app})', level='DEBUG')
                    app.set_log_level(level)

# -----------------------------------------------------------------------------------

    # async def _log_function_name_async(self, **kwargs) -> None:
    #     """log function name as log message"""

    #     self._log_function_name(**kwargs)

    #     # start = kwargs.get('start', True)
    #     # separator = kwargs.get('separator', True)
    #     # notification = kwargs.get('notification', False)
    #     # stacktrace = kwargs.get('stacktrace', False)
    #     # force = kwargs.get('force', False)

    #     # if force:
    #     #     trace = separator = notification = True
    #     # else:
    #     #     trace = await self.get_state('input_boolean.trace') == 'on'

    #     # frame = inspect.currentframe()

    #     # if frame is not None and frame.f_back is not None:
    #     #     name = frame.f_back.f_code.co_name
    #     # else:
    #     #     name = "<unknown>"

    #     # prefix = '>>' if start else '<<'

    #     # if notification:
    #     #     _ = self.call_service('announcer/notification', message=f'{prefix} {name}', type='desktop') # TODO: why needed to shutup pylint

    #     # if stacktrace:
    #     #     frame = inspect.currentframe()
    #     #     print(frame)
    #     #     if frame is not None and frame.f_back is not None:
    #     #         print(frame.f_back)

    #     # if trace:
    #     #     if separator:
    #     #         dashes = '-' * (80 - len(name))
    #     #         self.log(f'{prefix} {name} {dashes}',level='INFO')
    #     #     else:
    #     #         self.log(f'\t{prefix} {name}', level='DEBUG')

# -----------------------------------------------------------------------------------

    # def get_state(self, caller, *args, **kwargs):
    #     """Call a helper by name.

    #     - If a bound method exists on this AutomationLib instance, call it.
    #     - Otherwise try to call a module-level function from automationlib module and pass `caller` as the first arg.
    #     - Await and return coroutine results when needed.
    #     """

    #     fn = getattr(caller, 'get_state', None)

    #     if fn is not None:
    #         res = asyncio.run_coroutine_threadsafe(fn(*args, **kwargs), asyncio.get_running_loop())
    #     else:
    #         res = None # fn(*args, **kwargs)

    #     return res  # caller can ignore or keep future result

# -----------------------------------------------------------------------------------

    # def _get_state(self, *args, **kwargs):
    #     """Call a helper by name (module-level get_state)."""

    #     # look for a module-level function named 'get_state' (works regardless of import name)
    #     fn = globals().get('get_state')
    #     if fn is None:
    #         mod = sys.modules.get(__name__)
    #         if mod is not None:
    #             fn = getattr(mod, 'get_state', None)

    #     if fn is not None:
    #         # fn may be a coroutine function; schedule it on the running loop
    #         try:
    #             coro = fn(*args, **kwargs)
    #             fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], coro), asyncio.get_running_loop())
    #             res = fut
    #         except Exception:
    #             res = None
    #     else:
    #         res = None

    #     return res  # caller can ignore or keep future result

# -----------------------------------------------------------------------------------

    # def get_elevation(self, elev):
    #     """get sun elevation value from get_state result"""

    #     if isinstance(elev, (concurrent.futures.Future, asyncio.Future)):
    #         try:
    #             elev = elev.result(timeout=1)
    #         except Exception:
    #             elev = None

    #     if elev in (None, 'unknown'):
    #         elev_val = None

    #     try:
    #         elev_val = float(elev)
    #     except (TypeError, ValueError):
    #         elev_val = None

    #     return elev_val

# -----------------------------------------------------------------------------------
