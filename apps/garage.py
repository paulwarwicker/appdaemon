# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import inspect
from datetime import datetime,timedelta

# from typing import TYPE_CHECKING, cast

import constants as const
from automationbase import AutomationBase  # type: ignore

class Garage(AutomationBase):
    """Documentation for Garage"""

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.register_service('garage/open', self.garage_open_service)
        self.register_service('garage/close', self.garage_close_service)
        self.register_service('garage/is_open', self.garage_is_open_service)

        garage = const.GARAGE_ENTITY_ID

        self.listen_state(self.garage, garage, new='open')
        self.listen_state(self.garage, garage, new='opening')
        self.listen_state(self.garage, garage, new='closing')
        self.listen_state(self.garage, garage, new='closed')
        self.listen_state(self.garage_debug, garage)

        self.listen_event(self.garage_open_event, 'garage_open')
        self.listen_event(self.garage_close_event, 'garage_close')
        self.listen_event(self.garage_open_close_event, 'garage_open_close')
        self.listen_event(self.garage_debug_event, 'garage_debug')
        self.listen_event(self.garage_test_event, 'garage_test')

        self.run_daily(self.close_garage, "21:00")

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garage, runtime)

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    async def garage_open_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        await self.log_function_name(start=True)

        self.call_service('timestamp/set', name='garage')
        await self.garage_open('', '', '', '', {})

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_close_service(self, namespace, domain, service, kwargs) -> None:
        """close the garage"""

        await self.log_function_name(start=True)

        self.call_service('timestamp/set', name='garage')
        await self.garage_close('', '', '', '', {})

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_is_open_service(self, namespace, domain, service, kwargs) -> bool:
        """is garage open"""

        await self.log_function_name(start=True)

        is_open = await self.is_garage_open()

        await self.log_function_name(start=False)

        return is_open

# -----------------------------------------------------------------------------------

    async def garage_open_event(self, event, data, kwargs) -> None:

        self.call_service('garage/open')

# -----------------------------------------------------------------------------------

    async def garage_close_event(self, event, data, kwargs) -> None:

        self.call_service('garage/close')

# -----------------------------------------------------------------------------------

    async def garage_test_event(self, event, data, kwargs) -> None:

        await self.log_function_name(start=True, force=True)

        await self.log_function_name(start=False, force=True)

# -----------------------------------------------------------------------------------

    async def garage_debug_event(self, event, data, kwargs) -> None:

        await self.garage_debug('', '', '', '', {})

# -----------------------------------------------------------------------------------

    async def garage_open_close_event(self, event, data, kwargs) -> None:

        await self.log_function_name(start=True)

        self.call_service('garage/open')
        await self.sleep(30)
        self.call_service('garage/close')

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_open(self, entity, attribute, old, new, kwargs) -> None:
        """open garage door"""

        await self.log_function_name(start=True)

        self.call_service('cover/open_cover', entity_id=const.GARAGE_ENTITY_ID)
        self.call_service('timestamp/set', name='garage')
        self.call_service('lighting/garage_on')

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_close(self, entity, attribute, old, new, kwargs) -> None:
        """close garage door"""

        await self.log_function_name(start=True)

        self.call_service('cover/close_cover', entity_id=const.GARAGE_ENTITY_ID)
        self.call_service('timestamp/set', name='garage', value=None)
        self.call_service('lighting/garage_off')

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage(self, entity, attribute, old, new, kwargs) -> None:
        """listener for garage door"""

        await self.log_function_name(start=True)

        below = await self.is_below_horizon()

        if new == 'opening' and below:
            self.call_service('lighting/garage_on', seconds=self.interval(minutes=30), cb='garage_off')
        elif new == 'closed' and below:
            self.call_service('lighting/garage_off', seconds=self.interval(minutes=1), cb='garage_off')

        await self.garage_announcement(state=new)

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_announcement(self, **kwargs) -> None:
        """garage door announcement"""

        await self.log_function_name(start=True)

        state = kwargs['state']

        if state == 'open':
            await self.sleep(6.0) # just delay open announcement because this will be triggered immediately after opening

        message = f'The garage door is {state}'

        self.call_service('announcer/broadcast', message=message, timestamp='garage_announcement')

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def is_garage_open(self) -> bool:
        """is garage door open"""

        return (await self.get_state(const.GARAGE_ENTITY_ID)) == 'open'

# -----------------------------------------------------------------------------------

    async def check_garage(self, kwargs) -> None:
        """check garage door state"""

        await self.log_function_name(start=True)

        if await self.is_garage_open():
            (state, _) = await self.garage_state()
            ts = await self.call_service('timestamp/get', name='garage_announcement')
            if ts is not None:
                diff = (datetime.now() - ts).seconds
                if diff >= self.interval(minutes=60):
                    await self.garage_announcement(state=state)

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def close_garage(self, kwargs) -> None:
        """close garage door automatically"""

        await self.log_function_name(start=True)

        await self.garage_close('', '', '', '', {})

        await self.log_function_name(start=False)

# -----------------------------------------------------------------------------------

    async def garage_state(self, entity='', attribute='', old='', new='', kwarg=None) -> tuple:
        """get garage door state for debugging"""

        await self.log_function_name(start=True)

        state = await self.get_state(const.GARAGE_ENTITY_ID)
        ts = await self.call_service('timestamp/get', name='garage')
        if await self.get_verbose_debug():
            self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} kwargs={kwarg} state={state} ts={ts}', level='INFO')

        await self.log_function_name(start=False)

        return state,ts

# -----------------------------------------------------------------------------------

    async def garage_debug(self, entity='', attribute='', old='', new='', kwarg=None):

        (state, ts) = await self.garage_state()
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} kwargs={kwarg} state={state} ts={ts}', level='INFO')

# -----------------------------------------------------------------------------------

    async def is_below_horizon(self) -> bool:
        """is sun below the horizon (defensive: resolve awaitables, coerce to float)"""

        elev = await self.get_state('sun.sun', attribute='elevation')
        self.log(f'async is_below_horizon raw elev type={type(elev)} value={elev!r}', level='DEBUG')

        if elev in (None, 'unknown'):
            return False

        try:
            elev_val = float(elev)
        except (TypeError, ValueError):
            return False

        below = elev_val <= 0

        if await self.get_verbose_debug():
            t = 'is' if below else 'is not'
            self.log(f'{t} below horizon (elev={elev_val})', level='DEBUG')

        return below

# -----------------------------------------------------------------------------------

    async def get_trace(self):
        """get trace setting"""

        return await self.get_state('input_boolean.trace') == 'on'

# -----------------------------------------------------------------------------------

    async def get_verbose_debug(self):
        """get verbose debug setting"""

        return await self.get_state('input_boolean.debug')  == 'on'and await self.get_state('input_boolean.verbose') == 'on'

# -----------------------------------------------------------------------------------

    def interval(self, minutes: int) -> int:
        """return minutes as integer number """

        return int(timedelta(minutes=minutes).total_seconds())

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
            trace = await self.get_trace()

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
