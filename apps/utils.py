# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

# Server got itself in trouble
# 2024-07-21 20:06:40.697167 WARNING HASS: Error calling Home Assistant service default/media_player/volume_mute
# 2024-07-21 20:06:40.699485 WARNING HASS: Code: 500, error: 500 Internal Server Error

# import inspect
# import time
# import json
# import re
# import math
# import traceback
import requests  # pylint: disable=E0401
from datetime import datetime, timedelta

import yaml

import arrow  # pylint: disable=E0401
import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611
import appdaemon.adbase as ad  # pylint: disable=E0401,E0611
from ics import Calendar  # pylint: disable=E0401

class Utils(hass.Hass):
    """This is the documentation for Automation"""

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        # self.call_service('announcer/announce', message='Utils initialised')

# ---------------------------------------------------------------------------------------------------------

    def is_dusk(self):
        elev = self.get_sun_elevation()
        dusk = elev < -3
        t = 'is' if dusk else 'is not'
        self.log_debug(f'\t{t} dusk')
        return dusk

# ---------------------------------------------------------------------------------------------------------

    def is_predusk(self):
        elev = self.get_sun_elevation()
        predusk = elev < 1
        t = 'is' if predusk else 'is not'
        self.log_debug(f'\t{t} predusk')
        return predusk

# ---------------------------------------------------------------------------------------------------------

    def is_bank_holiday(self, dt=datetime.now()):
        self.log_debug(f'\tdt={dt}')

        url = 'https://www.gov.uk/bank-holidays.json'
        today = f'{dt:%Y-%m-%d}'

        is_bank_holiday = False

        resp = requests.get(url=url)
        # https://requests.readthedocs.io/en/master/user/quickstart/#json-response-content
        data = resp.json()

        events = data["england-and-wales"]["events"]

        for event in events:
            date_str = event["date"]
            dt = datetime.strptime(date_str, '%Y-%m-%d')

            if f'{dt.date():%Y-%m-%d}' == today:
                is_bank_holiday = True

        t = 'is not' if not is_bank_holiday else 'is'
        self.log_debug(f'\t{t} bank holiday')
        return is_bank_holiday

# ---------------------------------------------------------------------------------------------------------

    def is_weekday(self):
        dow = self.dow()
        weekday = 1 <= dow <= 5
        state = 'on' if weekday is True else 'off'
        self.set_state('input_boolean.is_weekday', state=state)
        return weekday

# ---------------------------------------------------------------------------------------------------------

    def is_sunday(self):
        return self.dow() == 7

# ---------------------------------------------------------------------------------------------------------

    def is_after(self, hour):
        dt = datetime.now()
        return dt.hour >= hour

# ---------------------------------------------------------------------------------------------------------

    def is_summer(self):
        (isoy, isow, isod) = arrow.now().isocalendar()
        return 17 <= isow <= 37  # end of april to mid-september

# ---------------------------------------------------------------------------------------------------------

    def dow(self):
        return arrow.now().isoweekday()

# ---------------------------------------------------------------------------------------------------------

    def no_rain(self):
        result = True if self.rain() < 1.0 else False
        self.log_debug('\tno rain')
        return result

# ---------------------------------------------------------------------------------------------------------

    def rain(self):
        result = float(self.get_state(entity_id='sensor.icambr4_precipitation_today'))
        self.log_debug(f'\tmmrain={result}')
        return result

# ---------------------------------------------------------------------------------------------------------

