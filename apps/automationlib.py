# -*- coding: utf-8 -*-

# import inspect
# import logging

from datetime import datetime
import requests  # pylint: disable=E0401
import arrow  # pylint: disable=E0401
import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611
from appdaemon.adapi import ADAPI # pylint: disable=E0401 disable=E0611

class AutomationLib():
    """This is the documentation for AutomationLib"""

    def __init__(self, adapi: ADAPI) -> None:

        self.adapi = adapi

        message = 'AutomationLib initialised'.center(60, '-')

        # self.adapi.log(f"\t{message}", level="INFO")
        self.adapi.log(message, level="INFO")

        # self.logger = self.adapi._logging.get_child('automationlib')
        # # self.logger.log(msg=f"\t{message}", level="INFO")
        # self.logger.log(msg=message, level="INFO")


# ---------------------------------------------------------------------------------------------------------

    def dow(self) -> int:

        return arrow.now().isoweekday()

# ---------------------------------------------------------------------------------------------------------

    def is_bank_holiday(self, dt=datetime.now()) -> bool:

        self.log(f'\tdt={dt}', level="DEBUG")

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
        self.log(f'\t{t} bank holiday', level="DEBUG")

        return is_bank_holiday

# ---------------------------------------------------------------------------------------------------------

    def is_weekend(self) -> bool:

        return self.dow() >= 6

# ---------------------------------------------------------------------------------------------------------

    def is_after(self, hour) -> bool:

        dt = datetime.now()

        return dt.hour >= hour

# ---------------------------------------------------------------------------------------------------------

    def is_summer(self) -> bool:

        (isoy, isow, isod) = arrow.now().isocalendar()

        return 17 <= isow <= 37  # end of april to mid-september

# ---------------------------------------------------------------------------------------------------------

    # def log_function_name(self, start=True) -> None:

    #     name = inspect.currentframe().f_back.f_code.co_name
    #     # print(inspect.currentframe())

    #     if self.verbose or self.debug:
    #         self.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

# def helper_function():
#     print("This is a helper function.")

