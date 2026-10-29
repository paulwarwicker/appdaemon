# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=unused-variable disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime, timedelta

# from typing import TYPE_CHECKING, cast

import constants as const
from automationbase import AutomationBase  # type: ignore

class Timestamp(AutomationBase):
    """Documentation for Timestamp"""

    ts = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

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

        if name is None:
            self.log(f'\tsetting timestamp for {name} with offset={offset} value={value} force={force}', level='WARNING')
            return
            # if value is not None:
            #     ts = value

        # Honor an explicit `value` parameter even when `force` is not set.
        # Preserve backward-compatibility: if `force` is True and no `value`
        # was provided, behave as before (allow clearing by setting to None).
        if 'value' in kwargs:
            ts = value
        elif force:
            ts = value
        else:
            ts = datetime.now()

        if offset is not None:
            ts += offset

        self.ts[name] = ts

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

    async def init_timestamp_service(self, namespace, domain, service, kwargs) -> None:
        """initialise timestamps"""

        for name in const.TIMESTAMPS:
            if name in ('tap', 'karoq_home', 'garage'):
                self.ts[name] = None
            elif name == 'upstairs_motion':
                self.ts[name] = datetime.now() + timedelta(hours=-6)
            else:
                self.ts[name] = datetime.now() + timedelta(minutes=-15)
            await self.sleep(2.0)

        self.call_service('timestamp/status')

# -----------------------------------------------------------------------------------

    def status_service(self, namespace, domain, service, kwargs):
        """status service"""

        # self._log_function_name(start=True, force=True)

        status = status = '\n\n'

        for name in const.TIMESTAMPS:
            ts = self.ts[name]
            status += f'\t{name}={ts}\n'

        diff1 = (self.ts['upstairs'] - self.ts['downstairs']).seconds
        diff2 = (self.ts['upstairs'] - self.ts['prev_upstairs']).seconds

        status += f'\n\tupstairs vs downstairs diff={diff1}\n'
        status += f'\tupstairs vs prev_upstairs diff={diff2}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

        # self._log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:
        """status event"""

        self.call_service('timestamp/status')

# -----------------------------------------------------------------------------------
