# -*- coding: utf-8 -*-
# pylint: disable=unused-argument disable=broad-exception-caught

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import inspect
# from typing import TYPE_CHECKING, cast

import constants as const # pylint: disable=unused-import
# import automationlib as _helpers  # type: ignore

# from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

# if TYPE_CHECKING:
#     from automationlib import AutomationLib  # type: ignore

from automationbase import AutomationBase  # type: ignore

class Remote(AutomationBase):
    """
    Docstringfor Remote (Harmony)
    """

    # Expose lib as AutomationLib for the type checker; default to the helper module so
    # pylint/mypy see the attributes without requiring per-file casts. initialise()
    # will replace this with the running AppDaemon app instance.
    # lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # # runtime: get the running AutomationLib app instance (do not instantiate directly)
        # self.lib = cast("AutomationLib", self.get_app('automationlib'))  # type: ignore
        # if self.lib is None:
        #     # defensive fallback to module if app not present (optional)
        #     self.lib = _helpers  # fallback
        # assert self.lib is not None

        super().initialize()

        self.register_service('remote/power_off_media', self.power_off_media_service)
        self.register_service('remote/watch_dvd', self.watch_dvd_service)

        self.listen_event(self.power_off_media_event, 'power_off_media')
        self.listen_event(self.watch_dvd_event, 'watch_dvd')
        self.listen_event(self.power_on_media_event, 'power_on_media')

        self.listen_state(self.power_off_media, 'input_boolean.power_off_media', new='on')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    async def power_off_media_service(self, namespace, domain, service, data) -> None:
        """power off media service"""

        await self._log_function_name_async(start=True)

        await self.power_off_media(None, None, None, None, {})

        await self._log_function_name_async(start=False)

# -----------------------------------------------------------------------------------

    async def watch_dvd_service(self, namespace, domain, service, data) -> None:
        """power off media service"""

        await self._log_function_name_async(start=True)

        await self.watch_dvd(None, None, None, None, {'dvd': True})

        await self._log_function_name_async(start=False)

# -----------------------------------------------------------------------------------

    async def power_off_media_event(self, event_name, data, kwargs) -> None:

        await self.power_off_media(None, None, None, None, {})

# -----------------------------------------------------------------------------------

    async def power_on_media_event(self, event_name, data, kwargs) -> None:

        await self.power_on_media(None, None, None, None, {})

# -----------------------------------------------------------------------------------
    async def watch_dvd_event(self, event, data, kwargs) -> None:

        await self.watch_dvd(None, None, None, None, {})

# -----------------------------------------------------------------------------------

    async def power_off_media(self, entity_id, attribute, old, new, kwargs) -> None:

        # await self._log_function_name_async(start=True)

        await self.power_off_skyq()
        await self.power_off_tv()
        await self.power_off_dvd()

        await self.set_state('input_boolean.power_off_media', state='off')

        # await self._log_function_name_async(start=False)

# -----------------------------------------------------------------------------------

    async def power_on_media(self, entity_id, attribute, old, new, kwargs) -> None:

        # await self._log_function_name_async(start=True)

        dvd = kwargs.get('dvd', False)

        await self.power_on_skyq()

        if dvd:
            await self.watch_dvd(None, None, None, None, {})
        else:
            await self.power_on_tv()

        # await self._log_function_name_async(start=False)

# -----------------------------------------------------------------------------------

    async def watch_dvd(self, entity_id, attribute, old, new, kwargs) -> None:

        await self._log_function_name_async(start=True)

        await self.power_on_media(None, None, None, None, {'dvd': True})

        await self._log_function_name_async(start=False)

# -----------------------------------------------------------------------------------

    async def power_on_skyq(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="Sky Q",
            command="PowerOn"
        )

# -----------------------------------------------------------------------------------

    async def power_off_skyq(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="Sky Q",
            command="PowerOff"
        )

# -----------------------------------------------------------------------------------

    async def power_on_tv(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="LG TV",
            command="PowerOn"
        )

# -----------------------------------------------------------------------------------

    async def power_off_tv(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="LG TV",
            command="PowerOff"
        )

# -----------------------------------------------------------------------------------

    async def power_on_dvd(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="Samsung DVD/Blu-ray player",
            command="PowerOn"
        )

# -----------------------------------------------------------------------------------

    async def power_off_dvd(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
            device="Samsung DVD/Blu-ray player",
            command="PowerOff"
        )

# -----------------------------------------------------------------------------------

    async def eject_disc(self):

        self.call_service(
            "remote/send_command",
            entity_id="remote.living_room",
                device="Samsung DVD/Blu-ray player",
            command="Eject"
        )

# -----------------------------------------------------------------------------------

    async def log_function_name(self, **kwargs) -> None:
        """log function name as log message"""

        start = kwargs.get('start', True)
        separator = kwargs.get('separator', True)
        notification = kwargs.get('notification', False)
        stacktrace = kwargs.get('stacktrace', False)
        force = kwargs.get('force', False)

        if force:
            trace = separator = notification = True
        else:
            trace = await self.get_state('input_boolean.trace') == 'on'

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
