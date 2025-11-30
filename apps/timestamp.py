# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import time
from datetime import datetime, timedelta

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

# from typing import Dict
# from pprint import pprint

class Timestamp(Hass):
    """Documentation for Timestamp"""

    ts = {}
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.register_service('timestamp/set', self.set_timestamp_service)
        self.register_service('timestamp/get', self.get_timestamp_service)
        self.register_service('timestamp/status', self.status_service)
        self.register_service('timestamp/init', self.init_timestamp_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timestamps')

        self.call_service('timestamp/init')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def set_timestamp_service(self, namespace, domain, service, kwargs) -> None:
        """set a named timestamp"""

        name = kwargs.get('name', None)
        offset = kwargs.get('offset', None)
        value = kwargs.get('value', None)
        force = kwargs.get('force', False)

        if name is not None:
            if value is not None:
                ts = value
            else:
                if force:
                    ts = value
                else:
                    ts = datetime.now()

                if offset is not None:
                    ts += offset

            self.ts[name] = ts

            if self.lib.get_verbose_debug():
                self.log(f'\t{name} timestamp set to {ts}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def get_timestamp_service(self, namespace, domain, service, kwargs):
        """get a named timestamp"""

        ts = None
        name = kwargs.get('name', None)

        if name is not None:
            ts = self.ts.get(name, datetime.now())

        return ts

# -----------------------------------------------------------------------------------

    def init_timestamp_service(self, namespace, domain, service, kwargs) -> None:
        """initialise timestamps"""

        for name in const.TIMESTAMPS:
            if name == 'tap' or name == 'karoq_home':
                self.ts[name] = None
            elif name == 'upstairs_motion':
                self.ts[name] = datetime.now() + timedelta(hours=-6)
            else:
                self.ts[name] = datetime.now() + timedelta(minutes=-15)
            time.sleep(2.0)

        self.call_service('timestamp/status')

# -----------------------------------------------------------------------------------

    def status_service(self, namespace, domain, service, kwargs):
        """status service"""

        # self.lib.log_function_name(start=True, force=True)

        status = status = '\n\n'

        for name in const.TIMESTAMPS:
            ts = self.ts[name]
            status += f'\t{name}_ts={ts}\n'

        diff1 = (self.ts['upstairs'] - self.ts['downstairs']).seconds
        diff2 = (self.ts['upstairs'] - self.ts['prev_upstairs']).seconds

        status += f'\n\tupstairs vs downstairs diff={diff1}\n'
        status += f'\tupstairs vs prev_upstairs diff={diff2}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

        # self.lib.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:
        """status event"""

        self.call_service('timestamp/status')

# -----------------------------------------------------------------------------------
