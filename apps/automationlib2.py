from datetime import datetime

from adapi import ADAPI # type: ignore # pylint: disable=E0401 disable=E0611

class AutomationLib():
    """Documentation for AutomationLib"""

    def __init__(self, adapi: ADAPI, dummy=None) -> None:
        self.adapi = adapi
        self.debug = False
        self.verbose = False
        self.testing = False
        self.trace = False

    async def initialize(self):
        """Async initialization logic"""

        self.debug = await self.adapi.get_state('input_boolean.default_debug_state') == 'on'
        self.verbose = await self.adapi.get_state('input_boolean.default_verbose_state') == 'on'
        self.testing = await self.adapi.get_state('input_boolean.default_testing_state') == 'on'
        self.trace = await self.adapi.get_state('input_boolean.default_trace_state') == 'on'

        self.adapi.log('initialised')

# -----------------------------------------------------------------------------------

    def now(self):
        """now"""

        return datetime.now()

# -----------------------------------------------------------------------------------

    def is_summer(self) -> bool:
        """is today a summer day (end of april to mid-september)"""

        (_, isow, _) = self.now().isocalendar()

        return 17 <= isow <= 37

# -----------------------------------------------------------------------------------

    def get_debug(self) -> bool:
        """get debug setting"""

        return self.debug

# -----------------------------------------------------------------------------------

    def get_verbose(self) -> bool:
        """get verbose setting"""

        return self.verbose

# -----------------------------------------------------------------------------------

    def get_verbose_debug(self) -> bool:
        """get verbose debug setting"""

        return self.get_verbose() and self.get_debug()

# -----------------------------------------------------------------------------------

    def get_testing(self) -> bool:
        """get testing setting"""

        # return self.adapi.get_state('input_boolean.testing') == 'on'
        return self.testing

# -----------------------------------------------------------------------------------

    def get_testing_verbose_debug(self) -> bool:
        """get verbose debug setting"""

        return self.get_testing() and self.get_verbose_debug()

# -----------------------------------------------------------------------------------
