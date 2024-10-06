# -*- coding: utf-8 -*-

# import logging

import time
import inspect
from datetime import datetime,timedelta
import requests  # pylint: disable=E0401
import arrow  # pylint: disable=E0401

from adapi import ADAPI # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # pylint: disable=E0401 disable=E0611

class AutomationLib():
    """Documentation for AutomationLib"""

    def __init__(self, adapi: ADAPI) -> None:
        """__init__"""

        self.adapi = adapi
        self.debug = adapi.get_state('input_boolean.debug') == 'on'
        self.verbose = adapi.get_state('input_boolean.verbose') == 'on'
        self.testing = adapi.get_state('input_boolean.testing') == 'on'

        # message = ' AutomationLib initialised '.center(72, '-')
        # adapi.log(message, level="INFO")

        # self.logger = adapi._logging.get_child('automationlib')
        # self.logger.log(msg=f"\t{message}", level="INFO")

        adapi.log('initialised')

# ---------------------------------------------------------------------------------------------------------

    def dow(self) -> int:
        """day of week"""

        return arrow.now().isoweekday()  # pylint: disable=E0401 disable=E0611

# ---------------------------------------------------------------------------------------------------------

    def is_bank_holiday(self, dt=datetime.now()) -> bool:
        """is today (or dt argument) a bank holiday"""

        self.adapi.log(f'\tdt={dt}', level='DEBUG')

        url = 'https://www.gov.uk/bank-holidays.json'
        today = f'{dt:%Y-%m-%d}'

        is_bank_holiday = False

        resp = requests.get(url=url)
        data = resp.json() # https://requests.readthedocs.io/en/master/user/quickstart/#json-response-content

        events = data["england-and-wales"]["events"]

        for event in events:
            date_str = event["date"]
            dt = datetime.strptime(date_str, '%Y-%m-%d')

            if f'{dt.date():%Y-%m-%d}' == today:
                is_bank_holiday = True

        t = 'is not' if not is_bank_holiday else 'is'
        self.adapi.log(f'\t{t} bank holiday', level='DEBUG')

        return is_bank_holiday

# ---------------------------------------------------------------------------------------------------------

    def is_weekend(self) -> bool:
        """is today a weekend"""

        return self.dow() >= 6

# ---------------------------------------------------------------------------------------------------------

    def is_after(self, hour) -> bool:
        """is now after a certain hour"""

        dt = datetime.now()

        return dt.hour >= hour

# ---------------------------------------------------------------------------------------------------------

    def is_summer(self) -> bool:
        """is today a summer day (end of april to mid-september)"""

        (isoy, isow, isod) = arrow.now().isocalendar()  # pylint: disable=E0401 disable=E0611

        return 17 <= isow <= 37

# ---------------------------------------------------------------------------------------------------------

    def get_entity_id(self, entity_id=None): # -> tuple # FIXME
        """get entity id and volume. if testing is set, use study, else use kitchen""" # FIXME: list of speakers

        if entity_id is None:
            if self.adapi.get_state('input_boolean.alarm_testing') == 'on':
                entity_id = 'media_player.study'

                if self.adapi.now_is_between('08:00:00', '21:29:59'):
                    volume = 0.2
                elif self.adapi.now_is_between('21:30:00', '07:59:59'):
                    volume = 0.1
            else:
                entity_id = 'media_player.kitchen'
                volume = 0.5
        else:
            # just set volume
            volume = 0.25

        return (entity_id, volume)

# -------------------------------------------------------------------------------------------------

    def no_rain(self) -> bool:
        """was there more than 1mm of rain today"""

        return True if self.rain() < 1.0 else False

# ---------------------------------------------------------------------------------------------------------

    def rain(self) -> float:
        """get preciptation today"""

        result = float(self.adapi.get_state(entity_id='sensor.icambr4_precipitation_today'))
        self.adapi.log(f'\tmmrain={result}', level='DEBUG')

        return result

# ---------------------------------------------------------------------------------------------------------

    def delay(self, s) -> None:
        """sleep for s seconds if not a mock run"""

        if not self.is_mock_run():
            time.sleep(s)

# -------------------------------------------------------------------------------------------------

    def is_mock_run(self) -> bool:
        """is this a mock run"""

        return self.adapi.get_state('input_boolean.mock_run') == 'on'

# ---------------------------------------------------------------------------------------------------------

    def get_debug(self) -> bool:
        """get debug setting"""

        return self.adapi.get_state('input_boolean.debug') == 'on'

# ---------------------------------------------------------------------------------------------------------

    def get_verbose(self) -> bool:
        """get verbose setting"""

        return self.adapi.get_state('input_boolean.verbose') == 'on'


# ---------------------------------------------------------------------------------------------------------

    def get_verbose_debug(self) -> bool:
        """get verbose debug setting"""

        return self.get_verbose() and self.get_debug()

# ---------------------------------------------------------------------------------------------------------

    def get_testing(self) -> bool:
        """get testing setting"""

        return self.adapi.get_state('input_boolean.testing') == 'on'

# ---------------------------------------------------------------------------------------------------------

    def get_testing_verbose_debug(self) -> bool:
        """get verbose debug setting"""

        return self.get_testing() and self.get_verbose() and self.get_debug()

# ---------------------------------------------------------------------------------------------------------

    def get_alarm_testing(self) -> bool:
        """get alrm debug setting"""

        return self.adapi.get_state("input_boolean.alarm_testing") == "on"

# ---------------------------------------------------------------------------------------------------------

    def set_debug(self, torf) -> bool:
        """set debug setting"""

        old_state = self.adapi.get_state("input_boolean.debug")
        new_state = 'on' if torf else 'off'
        self.adapi.set_state("input_boolean.debug", state=new_state)

        return old_state == 'on'

# ---------------------------------------------------------------------------------------------------------

    def log_function_name(self, start=True) -> None:
        """log function name as log message"""

        # print(inspect.currentframe())
        # print(inspect.currentframe().f_back)

        name = inspect.currentframe().f_back.f_code.co_name

        # if self.verbose or self.debug:
        self.adapi.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

    def is_playing(self, entity_id=None) -> bool:
        """is entity id playing"""

        if entity_id is None:
            (entity_id, volume) = self.get_entity_id()

        state = self.adapi.get_state(entity_id=entity_id, attribute="state")

        return state == 'playing'

# ---------------------------------------------------------------------------------------------------------

    def interval(self, minutes) -> int:
        """return minutes as integer number """

        return int(timedelta(minutes=minutes).total_seconds())

# -------------------------------------------------------------------------------------------------

    def is_twilight(self) -> bool:
        """is it twilight"""
        # civil twilight is a sun elevation -6 degrees below horizon

        elev = self.adapi.get_state('sun.sun', attribute='elevation')
        twilight = -6 < elev < 0
        t = 'is' if twilight else 'is not'
        self.adapi.log(f'{t} twilight', level='DEBUG')

        return twilight

# ---------------------------------------------------------------------------------------------------------

    def is_night(self) -> bool:
        """is it night"""
        # civil twilight is a sun elevation -6 degrees below horizon

        elev = self.adapi.get_state('sun.sun', attribute='elevation')
        night = elev <= -6
        t = 'is' if night else 'is not'
        self.adapi.log(f'{t} night', level='DEBUG')

        return night

# ---------------------------------------------------------------------------------------------------------

    def is_below_horizon(self) -> bool:
        """is sun below the horizon"""

        elev = self.adapi.get_state('sun.sun', attribute='elevation')
        below = elev <= 0
        t = 'is' if below else 'is not'
        self.adapi.log(f'{t} below horizon')

        return below

# ---------------------------------------------------------------------------------------------------------

    def percent_to_brightness(self, percent):
        return int(255/100 * percent)

# ---------------------------------------------------------------------------------------------------------

# def helper_function():
#     print("This is a helper function.")

