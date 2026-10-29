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
import datetime as dt

from appdaemon.utils import sync_decorator

from datetime import datetime,timedelta

from typing import Any, Callable, Coroutine, cast

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

    shared = SharedState()

    # pylint: disable=attribute-defined-outside-init
    def initialize(self):
        """base initialization logic"""

        self.shared.debug = self.resolve_state(self.get_state('input_boolean.debug')) == 'on'
        self.shared.verbose = self.resolve_state(self.get_state('input_boolean.verbose')) == 'on'
        self.shared.testing = self.resolve_state(self.get_state('input_boolean.testing')) == 'on'
        self.shared.trace = self.resolve_state(self.get_state('input_boolean.trace')) == 'on'
        self.shared.log_level = "INFO"
        # self.log(f"\tautomationbase: debug={self.shared.debug} verbose={self.shared.verbose} testing={self.shared.testing} trace={self.shared.trace}", level='WARNING')``

        self._set_console_log_level()

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

        t = 'is not' if not _is_bank_holiday else 'is'
        self.log(f'\t{t} bank holiday', level='DEBUG')

        return _is_bank_holiday

# -----------------------------------------------------------------------------------

    def _is_weekend(self) -> bool: # ??
        """is today a weekend"""

        return self._dow() >= 6

# -----------------------------------------------------------------------------------

    def _is_after(self, hour: int) -> bool: # ??
        """is now after a certain hour"""

        dt = self._now()

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
                    volume = const.ANNOUNCE_VOLUME_LOW
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

        return True if self._rain() < 1.0 else False

# -----------------------------------------------------------------------------------

    def _rain(self) -> float:
        """get preciptation today"""

        verbose, debug, trace, testing = self._get_tracing()

        # result = 0.0 # FIXME:
        result = float(self.get_state(entity_id='sensor.icambr4_precipitation_today'))

        if trace or debug or verbose:
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

    def _get_tracing(self):
        """get tracing setting"""

        return self.shared.verbose, self.shared.debug, self.shared.trace, self.shared.testing

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

    def _get_cleaning(self) -> bool:
        """get cleaning setting"""

        return self.get_state("input_boolean.cleaning") == "on"

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

        if any((force, self.shared.debug, self.shared.verbose, self.shared.trace)): # any(<tuple>)
            if separator:
                dashes = '-' * max(0, 80 - len(name))
                msg = f'{prefix} {name} {dashes}'
            else:
                msg = f'\t{prefix} {name}'
            self.log(msg, level='INFO')

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
        self.log(f'{entity_id=} state={state} attributes={attributes}', level='DEBUG')

        return state == 'playing'

# -----------------------------------------------------------------------------------

    def _interval(self, minutes: int = 0, seconds: int = 0) -> int:
        """return minutes or seconds as integer number of seconds"""

        return int(timedelta(minutes=minutes, seconds=seconds).total_seconds())

# -----------------------------------------------------------------------------------

    def resolve_state(self, value: Any) -> Any:
        """
        Resolve a value returned by get_state(), which may be:
        - a raw value
        - a coroutine
        - an asyncio.Task
        - an asyncio.Future
        - a concurrent.futures.Future

        Returns the resolved value, or None on failure.
        """

        # --- Case 1: coroutine ----------------------------------------------------
        if asyncio.iscoroutine(value):
            loop = getattr(self, "_loop", None)
            if loop is None:
                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

            if loop is None:
                return None

            try:
                fut = asyncio.run_coroutine_threadsafe(
                    cast(Coroutine[Any, Any, Any], value), loop
                )
                return fut.result(timeout=1)
            except Exception:
                return None

        # --- Case 2: asyncio.Task -------------------------------------------------
        if isinstance(value, asyncio.Task):
            try:
                return value.result()  # Task.result() has no timeout
            except Exception:
                return None

        # --- Case 3: Future -------------------------------------------------------
        if isinstance(value, (asyncio.Future, concurrent.futures.Future)):
            try:
                fut = cast(concurrent.futures.Future, value)
                return fut.result(timeout=1)
            except Exception:
                return None

        # --- Case 4: raw value ----------------------------------------------------
        return value

# -----------------------------------------------------------------------------------

    def _get_sun_elevation(self) -> float | None:
        elev = self.resolve_state(
            self.get_state("sun.sun", attribute="elevation")
        )

        if elev in (None, "unknown") or isinstance(elev, dict):
            return None

        try:
            return float(elev)
        except (TypeError, ValueError):
            return None

# -----------------------------------------------------------------------------------

    def _is_twilight(self) -> bool:
        elev = self._get_sun_elevation()
        return elev is not None and -6 < elev < 0

# -----------------------------------------------------------------------------------

    def _is_night(self) -> bool:
        elev = self._get_sun_elevation()
        return elev is not None and elev <= -6

# -----------------------------------------------------------------------------------

    def _is_below_horizon(self) -> bool:
        elev = self._get_sun_elevation()
        return elev is not None and elev <= 0

# -----------------------------------------------------------------------------------

    def _percent_to_brightness(self, percent:int):
        """convert percent (0-100) to brightness (0-255)"""

        return int(255/100 * percent)

# -----------------------------------------------------------------------------------

    def _call(self, name: str, *args, background: bool = True, wait: bool = False, timeout: float | None = None, **kwargs):
        """Dispatch a helper by name synchronously.

        - Calls a bound method on this instance if present, otherwise looks for a module-level
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
            self.log(f'automationbase.call: no function named {name}', level='WARNING')
            return None

        try:
            res = fn(*args, **kwargs)
        except TypeError:
            # try module-style signature that expects (caller, ...)
            try:
                res = fn(self, *args, **kwargs)
            except Exception as exc:
                self.log(f'automationbase.call: failed to call {name}: {exc}', level='ERROR')
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
                    self.log(f'automationbase.call: no event loop available to wait for {name}', level='ERROR')
                    return None
                fut = asyncio.run_coroutine_threadsafe(cast(Coroutine[Any, Any, Any], res), loop)
                try:
                    return fut.result(timeout)
                except Exception as exc:
                    self.log(f'automationbase.call: waiting for {name} failed: {exc}', level='ERROR')
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
                        self.log(f'automationbase.call background {name} exception: {exc}', level='ERROR')
                except Exception as e:
                    self.log(f'automationbase.call background {name} done-callback failed: {e}', level='ERROR')

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
                    self.log(f'setting log level {prefix}{level} on app {module} (app={app})', level='INFO')
                    app.set_log_level(level)

# -----------------------------------------------------------------------------------

    # @sync_decorator
    # async def run_weekly(
    #     self,
    #     callback: Callable,
    #     start: str | dt.time | dt.datetime | None = None,
    #     *args,
    #     random_start: int | dt.timedelta | None = None,
    #     random_end: int | dt.timedelta | None = None,
    #     pin: bool | None = None,
    #     pin_thread: int | None = None,
    #     **kwargs,
    # ) -> str:
    #     """Run a function at the same time every week depending on the specified days.

    #     Args:
    #         callback: Function that will be called every day at the specified time. It must conform to the standard
    #             scheduler callback format documented `here <APPGUIDE.html#scheduler-callbacks>`__.
    #         start (str, datetime.time, datetime.datetime, optional): Start time for the interval calculation. If this is
    #             in the future, this will be the first time the callback is triggered. If this is in the past, the
    #             intervals will be calculated forward from the start time, and the first trigger will be the first
    #             interval in the future.

    #             - If this is a ``str`` it will be parsed with :meth:`~appdaemon.adapi.ADAPI.parse_time()`.
    #             - If this is a ``datetime.time`` object, the current date will be assumed.
    #             - If this is a ``datetime.datetime`` object, it will be used as is.

    #         *args: Arbitrary positional arguments to be provided to the callback function when it is triggered.
    #         random_start (int, optional): Start of range of the random time.
    #         random_end (int, optional): End of range of the random time.
    #         pin (bool, optional): Optional setting to override the default thread pinning behavior. By default, this is
    #             effectively ``True``, and ``pin_thread`` gets set when the app starts.
    #         pin_thread (int, optional): Specify which thread from the worker pool will run the callback. The threads
    #             each have an ID number, which start at 0 and go through (number of threads - 1).
    #         **kwargs: Arbitrary keyword parameters to be provided to the callback function when it is triggered.

    #             Keyword Args:
    #                 days (int or list[int]): Days of the week on which the callback should run.
    #                         Monday = 0 ... Sunday = 6

    #     Raises:
    #         ValueError: If the 'days' argument is not specified.

    #     Returns:
    #         A handle that can be used to cancel the timer later before it's been executed.

    #     Note:
    #         The ``random_start`` value must always be numerically lower than ``random_end`` value, they can be negative
    #         to denote a random offset before and event, or positive to denote a random offset after an event.

    #     Examples:
    #         Run every weekly at 10:30am on a Monday.

    #         >>> self.run_weekly(self.weekly_callback, datetime.time(10, 30), days=0)

    #         Run at 7:30pm weekly on a Tuesday using the ``parse_time()`` function.

    #         >>> handle = self.run_weekly(self.weekly_callback, "07:30:00 PM", days=1)

    #     """

    #     self._log_function_name(start=True, force=True)

    #     if 'days' not in kwargs:
    #         raise ValueError("You must specify the 'days' argument")

    #     days = kwargs.pop('days')

    #     if isinstance(days, int):
    #         days = [days]

    #     async def wrapped_weekly_cb(cb_kwargs):
    #         # Only run on the specified weekdays. days is inherited from the outer scope.
    #         dt = await self.datetime()
    #         if dt.weekday() in days:
    #             await callback(cb_kwargs)

    #     handle = await self.run_daily(
    #         wrapped_weekly_cb,
    #         start,
    #         *args,
    #         random_start=random_start,
    #         random_end=random_end,
    #         pin=pin,
    #         pin_thread=pin_thread,
    #         **kwargs,
    #     )

    #     self.log(f'{handle=} {args=} {kwargs=}', level='INFO')
    #     self._log_function_name(start=False, force=True)

    #     return handle

# -----------------------------------------------------------------------------------
