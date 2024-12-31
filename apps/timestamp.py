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

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.status_event, 'timestamps')

        for name in self.const.TIMESTAMPS:
            if name == 'tap':
                self.ts[name] = None
            else:
                self.ts[name] = datetime.now() + timedelta(minutes=-15)

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

            # if name == "travel":
            #     self.travel_announce_ts = ts
            # elif name == "garage":
            #     self.garage_announce_ts = ts
            # elif name == "karoq":
            #     self.karoq_announce_ts = ts
            # elif name == "tap":
            #     self.tap_ts = ts
            # elif name == "general":
            #     self.general_announce_ts = ts
            # elif name == "upstairs":
            #     self.upstairs_ts = ts
            # elif name == "downstairs":
            #     self.downstairs_ts = ts
            # elif name == "prev_upstairs":
            #     self.prev_upstairs_ts = ts
            # elif name == "vacuum":
            #     self.vacuum_announce_ts = ts

            if self.lib.get_verbose_debug():
                self.log(f'\t\t{name} timestamp set to {ts}', level='DEBUG')

# -----------------------------------------------------------------------------------

    def get_timestamp_service(self, namespace, domain, service, kwargs):
        """get a named timestamp"""

        ts = None
        name = kwargs.get('name', None)

        if name is not None:
            ts = self.ts[name]

            # if name == "travel":
            #     ts = self.travel_announce_ts
            # elif name == "garage":
            #     ts = self.garage_announce_ts
            # elif name == "karoq":
            #     ts = self.karoq_announce_ts
            # elif name == "tap":
            #     ts = self.tap_ts
            # elif name == "general":
            #     ts = self.general_announce_ts
            # elif name == "upstairs":
            #     ts = self.upstairs_ts
            # elif name == "downstairs":
            #     ts = self.downstairs_ts
            # elif name == "prev_upstairs":
            #     ts = self.prev_upstairs_ts
            # elif name == "initialise":
            #     ts = self.initialise_ts
            # elif name == "vacuum":
            #     ts = self.vacuum_announce_ts

        return ts

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
