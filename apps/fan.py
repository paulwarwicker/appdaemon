# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing


from typing import TYPE_CHECKING, cast

import constants as const # pylint: disable=unused-import
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Fan(Hass):
    """Documentation for Fan"""

    DEFAULT_TIMEOUT = 2*60

    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.register_service('fan/fan_on', self.fan_on_service)
        self.register_service('fan/fan_off', self.fan_off_service)
        self.register_service('fan/light_on', self.light_on_service)
        self.register_service('fan/light_off', self.light_off_service)

        self.listen_event(self.status_event, 'status')

        self.listen_state(self.fan_on, 'input_boolean.fan', new='on')
        self.listen_state(self.fan_off, 'input_boolean.fan', new='off')
        self.listen_state(self.light_on, 'input_boolean.fan_light', new='on')
        self.listen_state(self.light_off, 'input_boolean.fan_light', new='off')

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def fan_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom fan"""

        self.lib.log_function_name(start=True)

        # if self.any_light_on_full('kitchen'):
        #     self.log('\tignoring kitchen on service', level='INFO')
        #     self.lib.log_function_name(start=False)
        #     return

        # brightness = const_ON if self.now_is_between('sunrise', 'sunset') else const.QUARTER_ON
        # self.call_service('light/turn_on', entity_id=const.KITCHEN_LIGHTS, brightness=brightness)
        # self.call_service('light/turn_on', entity_id=const.KITCHEN_FLOOR_LIGHTS, brightness=brightness*2)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_off_service(self, namespace, domain, service, data) -> None:
        """turn off bedroom fan"""

        self.lib.log_function_name(start=True)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom fan light"""

        self.lib.log_function_name(start=True)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_off_service(self, namespace, domain, service, data) -> None:

        self.lib.log_function_name(start=True)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def status_event(self, event_name, data, kwargs) -> None:
        """status event"""

        self.lib.log_function_name(start=True)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_on(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan on with level"""

        self.lib.log_function_name(start=True)

        level = kwargs.get('level', 'low')

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command=level)

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_off(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan off"""

        self.lib.log_function_name(start=True)

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_on(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan light on"""

        self.lib.log_function_name(start=True)

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_off(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan light off"""

        self.lib.log_function_name(start=True)

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------
