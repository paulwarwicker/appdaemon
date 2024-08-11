# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import time
import requests  # pylint: disable=E0401
import inspect
from datetime import datetime

import arrow  # pylint: disable=E0401
import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611

class Utils(hass.Hass):
    """This is the documentation for Utils"""

    debug = None
    verbose = None
    testing = None

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

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

    # def is_weekday(self):

    #     dow = self.dow()
    #     weekday = 1 <= dow <= 5
    #     state = 'on' if weekday is True else 'off'
    #     self.set_state('input_boolean.is_weekday', state=state)

    #     return weekday

# ---------------------------------------------------------------------------------------------------------

    # def is_sunday(self):

    #     return self.dow() == 7

# ---------------------------------------------------------------------------------------------------------

    def is_weekend(self):

        return self.dow() >= 6

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
        if result:
            self.log_debug('\tno rain')

        return result

# ---------------------------------------------------------------------------------------------------------

    def rain(self):

        result = float(self.get_state(entity_id='sensor.icambr4_precipitation_today'))
        self.log_debug(f'\tmmrain={result}')

        return result

# ---------------------------------------------------------------------------------------------------------

    def delay(self, s):

        if not self.is_mock_run():
            time.sleep(s)

# -------------------------------------------------------------------------------------------------

    def is_mock_run(self):

        return self.get_state('input_boolean.mock_run') == 'on'

# ---------------------------------------------------------------------------------------------------------

    def log_debug(self, message):

        self.log(f'\t{message}', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def get_sun_elevation(self):

        elev = self.get_state('sun.sun', attribute='elevation')
        self.log(f'\telev={elev:2.2f}', level='DEBUG')

        return elev

# ---------------------------------------------------------------------------------------------------------

    def log_function_name(self, start=True):

        name = inspect.currentframe().f_back.f_code.co_name
        # print(inspect.currentframe())

        if self.verbose or self.debug:
            self.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

    def get_debug(self):

        self.debug = self.get_state('input_boolean.debug') == 'on'

        return self.debug

# ---------------------------------------------------------------------------------------------------------

    def get_verbose(self):

        self.verbose = self.get_state('input_boolean.verbose') == 'on'

        return self.verbose

# ---------------------------------------------------------------------------------------------------------

    def get_testing(self):

        self.testing = self.get_state('input_boolean.testing') == 'on'

        return self.testing

# ---------------------------------------------------------------------------------------------------------

    def get_alarm_debug(self):

        return self.get_state("input_boolean.alarm_debug") == "on"

# ---------------------------------------------------------------------------------------------------------

    def set_debug(self, torf):

        old_state = self.get_state("input_boolean.debug")
        new_state = 'on' if torf else 'off'
        self.set_state("input_boolean.debug", state=new_state)

        return old_state == 'on'

# ---------------------------------------------------------------------------------------------------------

    def log_test(self, kwargs={}):

        # INFO comes last to ensure we have a final successful log entry
        for level in ['CRITICAL', 'ERROR', 'WARNING', 'DEBUG', 'NOTSET', 'INFO']:
            self.log(f'\ttesting {level}', level=level)

# ---------------------------------------------------------------------------------------------------------

    def get_entity_id(self):

        if self.get_state('input_boolean.testing') == 'on':
            entity_id = 'media_player.study'
            volume = 0.2
        else:
            entity_id = 'media_player.kitchen'
            volume = 0.5

        return (entity_id, volume)

# -------------------------------------------------------------------------------------------------

