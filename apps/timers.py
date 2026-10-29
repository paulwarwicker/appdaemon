# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# from typing import TYPE_CHECKING, cast

import json
import constants as const # pylint: disable=unused-import
from automationbase import AutomationBase  # type: ignore

class Timers(AutomationBase):
    """Documentation for Timers"""

    timers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.register_service('timers/set', self.set_timer_service)
        self.register_service('timers/get', self.get_timer_service)
        self.register_service('timers/cancel', self.cancel_timer_service)
        self.register_service('timers/remove', self.remove_timer_service)
        self.register_service('timers/status', self.timer_status_service)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def set_timer_service(self, namespace, domain, service, kwargs) -> None:
        """set a timer service"""

        name = kwargs.get('name', None)
        timer = kwargs.get('timer', None)

        self.set_timer(name, timer)

# -----------------------------------------------------------------------------------

    def get_timer_service(self, namespace, domain, service, kwargs): # None:
        """get a timer service"""

        name = kwargs.get('name', None)

        return self.get_timer(name)

# -----------------------------------------------------------------------------------

    def cancel_timer_service(self, namespace, domain, service, kwargs) -> None:
        """cancel a timer service"""

        name = kwargs.get('name', None)

        self._cancel_timer(name)

# -----------------------------------------------------------------------------------

    def remove_timer_service(self, namespace, domain, service, kwargs) -> None:
        """remove a timer callback"""

        name = kwargs.get('name', None)

        self.remove_timer(name)

# -----------------------------------------------------------------------------------

    def timer_status_service(self, namespace, domain, service, kwargs) -> None:
        """status"""
        status_lines = []

        for name, timer in self.timers.items():
            handle = timer.get('handle') if isinstance(timer, dict) else timer

            if handle is None:
                status_lines.append(f"name={name} timer=<none>")
                continue

            info = self.info_timer(handle)
            if info is None:
                status_lines.append(f"name={name} timer={handle} status=missing")
                continue

            time, interval, timer_kwargs = info
            # human readable interval
            if interval:
                secs = int(interval)
                h, rem = divmod(secs, 3600)
                m, s = divmod(rem, 60)
                interval_hr = f"{h}h{m}m{s}s" if h else f"{m}m{s}s"
            else:
                interval_hr = "one-shot"

            try:
                kw_str = json.dumps(timer_kwargs, default=str)
            except Exception:
                kw_str = repr(timer_kwargs)

            status_lines.append(
                f"name={name} timer={handle} interval={interval} ({interval_hr}) kwargs={kw_str} next={time}"
            )

        for line in status_lines:
            self.log(f'\t{line}')

# -----------------------------------------------------------------------------------

    def set_timer(self, name, timer) -> None:
        """set a timer"""

        self._log_function_name(start=True)

        print(timer)
        extant = self.info_timer(timer)
        print(extant)

        if name is None or timer is None:
            self.log(f'set_timer missing paramater name={name} timer={timer}', level='ERROR')
            return

        self.log(f'name={name} timer={timer}', level='DEBUG')

        old = self.timers.get(name, None)

        if old is not None:
            if self.check_timer('old', old):
                self.log(f'\t\t\treplacing name={name} old={old} with new={timer}', level='INFO')
                self._cancel_timer(name)

        self.log(f'\t\t\tadding new timer name={name} timer={timer}')
        if self.check_timer('new', timer):
            self.timers[name] = timer
            self.print_timers()

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def get_timer(self, name):
        """get a timer"""

        self._log_function_name(start=True)

        self.log(f'name={name}', level='DEBUG')

        timer = self.timers.get(name, None)

        if timer is not None:
            self.log(f'\t\t\treturning name={name} timer={timer}', level='INFO')
        else:
            self.log(f'\t\t\tdid not find timer name={name}', level='WARNING')

        self._log_function_name(start=False)

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name) -> None:
        """cancel a timer callback"""

        self._log_function_name(start=True)

        timer = self.get_timer(name)

        if timer is not None:
            self.check_timer('cancel', timer)
            self.log(f'\t\t\tcancelling running timer name={name} timer={timer}', level='WARNING')
            self.cancel_timer(timer)
            self.remove_timer(timer)
        else:
            self.log(f'_cancel_timer did not find timer name={name}', level='ERROR')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        # timer = self.timers.get(name, None)
        timer = self.get_timer(name)

        if timer is not None:
            self.log(f'\t\t\tremoving timer name={name} timer={timer}')
            self.timers.pop(name)
            self.print_timers()
        else:
            self.log(f'\t\t\tremove_timer did not find timer name={name}', level='WARNING')

# -----------------------------------------------------------------------------------

    def check_timer(self, name, timer) -> bool:

        self.log(f'name={name} timer={timer}\n\n')

        if timer is not None:
            extant = self.info_timer(timer)
            if extant is not None:
                time, interval, kwargs = self.info_timer(timer)
                self.log(f'{name} timer={timer} time={time} interval={interval} kwargs={kwargs} isrunning={self.timer_running(timer)}')
                return True
            else:
                self.log(f'{name} timer is no longer extant', level='ERROR')
                return False

        else:
            self.log(f'timer is None name={name}', level='ERROR')
            return False


# -----------------------------------------------------------------------------------

    def print_timers(self) -> None:
        """print timers"""

        print(f'\t\t\t{self.timers}')

# -----------------------------------------------------------------------------------
