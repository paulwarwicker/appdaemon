# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

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

class Remote(Hass):
    """
    Docstringfor Remote (Harmony)
    """

    # Expose lib as AutomationLib for the type checker; default to the helper module so
    # pylint/mypy see the attributes without requiring per-file casts. initialise()
    # will replace this with the running AppDaemon app instance.
    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))  # type: ignore
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # fallback
        assert self.lib is not None

        self.register_service('remote/power_off_media', self.power_off_media_service)

        # self.listen_event(self.status_event, 'status')
        self.listen_event(self.test_power_off_media_event, 'test_power_off_media')

        self.listen_state(self.power_off_media, 'input_boolean.power_off_media', new='on')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def power_off_media_service(self, namespace, domain, service, data) -> None:
        """power off media service"""

        self.lib.log_function_name(start=True)

        self.power_off_media(None, None, None, None, {})

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def test_power_off_media_event(self, event, data, kwargs) -> None:

        self.power_off_living_room(None, None, None, None, {})

# -----------------------------------------------------------------------------------

    def power_off_media(self, entity_id, attribute, old, new, kwargs) -> None:

        self.lib.log_function_name(start=True)

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="Sky Q",
            command="PowerOff"
        )

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="LG TV",
            command="PowerOff"
        )

        self.set_state('input_boolean.power_off_media', state='off')

        self.lib.log_function_name(start=False)

# -----------------------------------------------------------------------------------
