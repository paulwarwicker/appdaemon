# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

from datetime import datetime, timedelta
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from const import ConstantsManagement  # pylint: disable=E0401 disable=E0611

# from typing import Dict
# from pprint import pprint

class Timestamp(Hass):
    """Documentation for Timestamp"""

    lib = None
    const = None
    ts = {}

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        self.lib = AutomationLib(self)
        self.const = ConstantsManagement(self)

        self.register_service('timestamp/set', self.set_timestamp_service)
        self.register_service('timestamp/get', self.get_timestamp_service)
        self.register_service('timestamp/status', self.status_service)
        self.register_service('timestamp/init', self.init_timestamp_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timestamps')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised --------------------------------------------------------------------', level='INFO')

# -----------------------------------------------------------------------------------

    def set_timestamp_service(self, namespace, domain, service, kwargs) -> None:
        """set a named timestamp"""

        name = kwargs.get('name', None)
        offset = kwargs.get('offset', None)
        value = kwargs.get('value', None)

        if name is not None:
            if value is not None:
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
            ts = self.ts[name]

        return ts

# -----------------------------------------------------------------------------------

    def init_timestamp_service(self, namespace, domain, service, kwargs) -> None:
        """initialise timestamps"""

        for name in self.const.TIMESTAMPS:
            if name == 'tap':
                self.ts[name] = None
            else:
                self.ts[name] = datetime.now() + timedelta(minutes=-15)

# -----------------------------------------------------------------------------------

    def status_service(self, namespace, domain, service, kwargs):
        """status event"""

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:

        status = status = '\n\n'

        for name in self.timestamps:
            ts = self.ts[name]
            status += f'\t{name}_ts={ts}\n'

        diff1 = (self.ts['upstairs'] - self.ts['downstairs']).seconds
        diff2 = (self.ts['upstairs'] - self.ts['prev_upstairs']).seconds

        status += f'\n\tupstairs vs downstairs diff={diff1}\n'
        status += f'\tupstairs vs prev_upstairs diff={diff2}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------
