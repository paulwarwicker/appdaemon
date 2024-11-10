# -*- coding: utf-8 -*-

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611
from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611

class Test(Hass):
    """This is the documentation for Test"""

    lib = None

# ----------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.lib = AutomationLib(self)

        self.log('-'*72)
        # self.log(f'\t{self.name} initialised (dow={self.lib.dow()})')
        # self.call_service('announcer/initialised', name=self.name)
        self.call_service('announcer/initialised', name=self.name.lower())
