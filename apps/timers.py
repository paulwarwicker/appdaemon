# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

class Timers(Hass):
    """Documentation for Timers"""

    lib = None
    # timers = {'empty': (None, None)}
    timers = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)

        self.register_service('timers/set', self.set_timer_service)
        self.register_service('timers/get', self.get_timer_service)
        self.register_service('timers/cancel', self.cancel_timer_service)
        self.register_service('timers/remove', self.remove_timer_service)
        self.register_service('timers/status', self.timer_status_service)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def set_timer_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """set a timer service"""

        name = kwargs.get('name', None)
        timer = kwargs.get('timer', None)

        self.set_timer(name, timer)

# -----------------------------------------------------------------------------------

    def get_timer_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> str: # None:
        """get a timer service"""

        name = kwargs.get('name', None)

        return self.get_timer(name)

# -----------------------------------------------------------------------------------

    def cancel_timer_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """cancel a timer service"""

        name = kwargs.get('name', None)

        self._cancel_timer(name)

# -----------------------------------------------------------------------------------

    def remove_timer_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """remove a timer callback"""

        name = kwargs.get('name', None)

        self.remove_timer(name)

# -----------------------------------------------------------------------------------

    def timer_status_service(self, namespace:str, domain:str, service:str, kwargs:dict) -> None:
        """status"""

        status = ""

        self.log(f'\t{status}\n\n')
        self.log(f'\t{self.timers}')

# -----------------------------------------------------------------------------------

    def set_timer(self, name:str, timer:str) -> None:
        """set a timer"""

        self.lib.log_function_name()

        print(timer)
        extant = self.info_timer(timer)
        print(extant)

        if name is None or timer is None:
            self.log(f'set_timer missing paramater name={name} timer={timer}', level='ERROR')
            return

        verbose = self.lib.get_verbose_debug()

        if verbose:
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

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def get_timer(self, name:str) -> str:
        """get a timer"""

        self.lib.log_function_name()

        verbose = self.lib.get_verbose_debug()

        if verbose:
            self.log(f'name={name}', level='DEBUG')

        timer = self.timers.get(name, None)

        if timer is not None:
            self.log(f'\t\t\treturning name={name} timer={timer}', level='INFO')
        else:
            self.log(f'\t\t\tdid not find timer name={name}', level='WARNING')

        self.lib.log_function_name(False)

        return timer

# -----------------------------------------------------------------------------------

    def _cancel_timer(self, name:str) -> None:
        """cancel a timer callback"""

        self.lib.log_function_name()

        timer = self.get_timer(name)

        if timer is not None:
            self.check_timer('cancel', timer)
            self.log(f'\t\t\tcancelling running timer name={name} timer={timer}', level='WARNING')
            self.cancel_timer(timer)
            self.print_timers()
            self.timers.pop(name)
            self.print_timers()
        else:
            self.log(f'_cancel_timer did not find timer name={name}', level='ERROR')

        self.lib.log_function_name(False)

# -----------------------------------------------------------------------------------

    def remove_timer(self, name) -> None:
        """remove timer"""

        timer = self.timers.get(name, None)

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
