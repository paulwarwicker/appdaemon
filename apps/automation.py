# -*- coding: utf-8 -*-
# **************************
# *** use vscode instead ***
# **************************

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import asyncio
# import adbase


import inspect
import time
import json
import re
import random
import math
import traceback
from datetime import datetime, timedelta
# from requests import get, put
import requests.adapters
import urllib3
from uuid import uuid4
from json import dumps as json_dumps
from base64 import b64decode
from typing import Dict
from pprint import pprint

BASE_URL = "https://api.starlingbank.com/api/v2"
BASE_URL_SANDBOX = "https://api-sandbox.starlingbank.com/api/v2"
# SPENDING_CATEGORIES = ['BIKE', 'BILLS_AND_SERVICES', 'BUCKET_LIST', 'CAR', 'CASH', 'CELEBRATION', 'CHARITY', 'CHILDREN', 'CLOTHES', 'COFFEE', 'DEBT_REPAYMENT', 'DIY', 'DRINKS', 'EATING_OUT', 'EDUCATION', 'EMERGENCY', 'ENTERTAINMENT', 'ESSENTIAL_SPEND', 'EXPENSES', 'FAMILY', 'FITNESS', 'FUEL', 'GAMBLING', 'GAMING', 'GARDEN', 'GENERAL', 'GIFTS', 'GROCERIES', 'HOBBY', 'HOLIDAYS', 'HOME', 'IMPULSE_BUY', 'INCOME', 'INSURANCE', 'INVESTMENTS', 'LIFESTYLE', 'MAINTENANCE_AND_REPAIRS', 'MEDICAL', 'MORTGAGE', 'NON_ESSENTIAL_SPEND', 'PAYMENTS', 'PERSONAL_CARE', 'PERSONAL_TRANSFERS', 'PETS', 'PROJECTS', 'RELATIONSHIPS', 'RENT', 'SAVING', 'SHOPPING', 'SUBSCRIPTIONS', 'TAKEAWAY', 'TAXI', 'TRANSPORT', 'TREATS', 'WEDDING', 'WELLBEING', 'NONE', 'REVENUE', 'OTHER_INCOME', 'CLIENT_REFUNDS', 'INVENTORY', 'STAFF', 'TRAVEL', 'WORKPLACE', 'REPAIRS_AND_MAINTENANCE', 'ADMIN', 'MARKETING', 'BUSINESS_ENTERTAINMENT', 'INTEREST_PAYMENTS', 'BANK_CHARGES', 'OTHER', 'FOOD_AND_DRINK', 'EQUIPMENT', 'PROFESSIONAL_SERVICES', 'PHONE_AND_INTERNET', 'VEHICLES', 'DIRECTORS_WAGES', 'VAT', 'CORPORATION_TAX', 'SELF_ASSESSMENT_TAX', 'INVESTMENT_CAPITAL', 'TRANSFERS', 'LOAN_PRINCIPAL', 'PERSONAL', 'DIVIDENDS']

import yaml
import requests  # pylint: disable=E0401

import arrow  # pylint: disable=E0401
import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611
import appdaemon.adbase as ad  # pylint: disable=E0401,E0611
from ics import Calendar  # pylint: disable=E0401

class Automation(hass.Hass):
    """This is the documentation for Automation"""
    override = False
    kitchen_timer = None
    kitchen_long_timer = None
    kitchen_floor_timer = None
    utility_timer = None
    utility_long_timer = None
    stairs_timer = None
    early_alarm_callback = None
    normal_alarm_callback = None
    test_alarm_callback = None
    upstairs_ts = datetime.now()
    downstairs_ts = datetime.now()
    prev_upstairs_ts = datetime.now()
    general_announce_ts = datetime.now() + timedelta(minutes=-15)
    travel_announce_ts = datetime.now() + timedelta(minutes=-15)
    garage_announce_ts = datetime.now()
    vacuum_announce_ts = datetime.now()
    karoq_announce_ts = datetime.now()
    initialise_ts = datetime.now()
    tap_ts = None
    downstairs_motion_flag = False
    default_early_alarm_schedule = 'daily'  # weekday|daily|none
    log_level = ''
    handlers = {}
    locations = {
        'proximity.ds_smith_fordham': 'DS Smith Fordham',
        'proximity.ds_smith_warboys': 'DS Smith Warboys',
        'proximity.pilates': 'Pilates',
        'proximity.pilates2': 'Pilates Bar Hill',
        'proximity.pilates3': 'Pilates Nothstowe',
        'proximity.karen_wax': 'Karen waxing',
        'proximity.karen_smith': 'Karen Smith',
        'proximity.karen_nail': 'Karen nails',
        'proximity.indian_ocean': 'Indian Ocean',
        'proximity.newmarket': 'Newmarket junction',
        'proximity.bar_hill': 'Bar Hill junction',
        'proximity.village': 'Max is in the village',
        'proximity.sainsbury_eddington': 'Sainsburys Eddington',
        'proximity.waitrose_trumpington': 'Waitrose Trumpington',
        'proximity.morrisons_stives': 'Morrisons St Ives',
        'proximity.gay_kellaway_racing': 'Gay Kellaway Racing',
        'proximity.martyn_tracey': 'Martyn and Tracey',
        'proximity.papworth': 'Papworh',
    }
    garage_entity_id = 'cover.remootio_device_host_192_168_1_13_s_n_30c92235df30xupwfafu_none'
    karoq_entity_id = 'binary_sensor.tmbkr7nu5p5079987_doors_locked'
    max_entity_id = 'device_tracker.maxine_iphone'
    paul_entity_id = 'device_tracker.paulw_iphone'
    verbose = False
    debug = False
    testing = False
    announce_start = 8
    announce_end = 21
    starling = None
    rota = []
    task = None
    messages = []

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""
        self.log('-'*72)

        self.pre_init()

        self.log('\tregistration start')

        self.listen_event(self.lights_off, "ios.action_fired", actionName='Lights')
        self.listen_event(self.water_garden_for_action, "ios.action_fired", actionName='Water15', minutes=15)
        self.listen_event(self.delete_calendar_events, 'delete_calendar_events')
        self.listen_event(self.add_calendar_events, 'add_calendar_events')
        self.listen_event(self.set_all_state_event, 'set_all_state')
        self.listen_event(self.status_event, 'status')
        # self.listen_event(self._announce_listener, 'announce')

        # self.listen_state(self.paul_home, Automation.paul_entity_id)
        self.listen_state(self.garage_door_open, Automation.paul_entity_id, old='not_home', new='home')
        self.listen_state(self.garage_door_close, Automation.paul_entity_id, old='home', new='not_home')
        self.listen_state(self.max_home, Automation.max_entity_id, new='Home')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Village', name='Village', location='proximity.village')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='DS_Smith_Fordham', name='DS_Smith_Fordham', location='proximity.ds_smith_fordham')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='DS_Smith_Fordham', name='DS_Smith_Fordham', location='proximity.ds_smith_fordham')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='DS_Smith_Warboys', name='DS_Smith_Warboys', location='proximity.ds_smith_warboys')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='DS_Smith_Warboys', name='DS_Smith_Warboys', location='proximity.ds_smith_warboys')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Pilates', name='Pilates', location='proximity.pilates')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Pilates', name='Pilates', location='proximity.pilates')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Pilates_Class', name='Pilates_Class', location='proximity.pilates_class')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Pilates_Class', name='Pilates_Class', location='proximity.pilates_class')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Indian_Ocean', name='Indian_Ocean', location='proximity.indian_ocean', duration=10)
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Indian_Ocean', name='Indian_Ocean', location='proximity.indian_ocean')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Karen_Wax', name='Karen_Wax', location='proximity.karen_wax', duration=10)
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Karen_Wax', name='Karen_Wax', location='proximity.karen_wax')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Karen_Nails', name='Karen_Nails', location='proximity.karen_nails')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Bar_Hill', name='Bar_Hill', location='proximity.bar_hill')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Newmarket', name='Newmarket', location='proximity.newmarket')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Karen_Smith', name='Karen_Smith', location='proximity.karen_smith')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Karen_Smith', name='Karen_Smith', location='proximity.karen_smith')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Sainsburys_Eddington', name='Sainsburys_Eddington', location='proximity.sainsburys_eddington')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Sainsburys_Eddington', name='Sainsburys_Eddington', location='proximity.sainsburys_eddington')
        # self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Waitrose_Trumpington', name='Waitrose_Trumpington', location='proximity.waitrose_trumpington')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Waitrose_Trumpington', name='Waitrose_Trumpington', location='proximity.waitrose_trumpington')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Morrisons_StIves', name='Morrisons_StIves', location='proximity.morrisons_stives')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Morrisons_StIves', name='Morrisons_StIves', location='proximity.morrisons_stives')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, new='Gay_Kellaway_Racing', name='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Gay_Kellaway_Racing', name='Gay_Kellaway_Racing', location='proximity.gay_kellaway_racing')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Martyn_Tracey', name='Martyn_Tracey', location='proximity.martyn_tracey')
        self.listen_state(self.max_location_detect, Automation.max_entity_id, old='Papworth', name='Papworth', location='proximity.papworth')
        self.log('\tmax_* registered')

        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_1', new='on', minutes=1)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_1', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_15', new='on', minutes=15)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_15', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_20', new='on', minutes=20)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_20', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_30', new='on', minutes=30)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_30', new='off')
        self.log('\twater_* registered')

        self.listen_state(self.garage_door_announce_opening, Automation.garage_entity_id, new='opening')
        self.listen_state(self.garage_door_announce_closing, Automation.garage_entity_id, new='closing')
        self.listen_state(self.garage_door_announce_open, Automation.garage_entity_id, new='open')
        self.listen_state(self.garage_door_announce_closed, Automation.garage_entity_id, new='closed')
        self.listen_state(self.garage_door_debug, Automation.garage_entity_id)
        self.log('\tgarage_door_* registered')

        self.listen_state(self.set_early_alarm, 'input_boolean.early_alarm', new='on', action='set')
        self.listen_state(self.set_early_alarm, 'input_boolean.early_alarm', new='off', action='cancel')
        self.listen_state(self.set_normal_alarm, 'input_boolean.normal_alarm', new='on', action='set')
        self.listen_state(self.set_normal_alarm, 'input_boolean.normal_alarm', new='off', action='cancel')
        self.listen_state(self.set_test_alarm, 'input_boolean.test_alarm', new='on', action='set')
        self.listen_state(self.set_test_alarm, 'input_boolean.test_alarm', new='off', action='cancel')
        self.log('\t*_alarm registered')

        self.listen_state(self.set_console_log_level, 'input_boolean.verbose', new='on')
        self.listen_state(self.set_console_log_level, 'input_boolean.verbose', new='off')

        self.listen_state(self.front_door_ding, 'binary_sensor.front_door_ding', old='off', new='on')
        self.log('\tfront_door_ding registered')

        self.listen_state(self.kitchen_motion, 'binary_sensor.kitchen_sensor_motion', old='off', new='on', timer=300, location='kitchen')
        self.listen_state(self.utility_motion, 'binary_sensor.utility_room_motion_sensor_motion', old='off', new='on', timer=300, location='utility')
        self.listen_state(self.downstairs_motion, 'binary_sensor.downstairs_sensor_motion', old='off', new='on', timer=300, check_override=True, location='downstairs')
        self.listen_state(self.upstairs_motion, 'binary_sensor.upstairs_sensor_motion', old='off', new='on', timer=600, check_override=False, location='upstairs')
        self.log('\t*_motion registered')

        self.listen_state(self.reset_test1, 'input_boolean.test_1', new='on')
        self.listen_state(self.reset_test2, 'input_boolean.test_2', new='on')
        self.listen_state(self.reset_alarms, 'input_boolean.reset_alarms', new='on')
        self.log('\treset* registered')

        self.listen_state(self.set_utility_motion_test, 'input_boolean.test_utility_motion', new='on', action='set')
        self.listen_state(self.set_utility_motion_test, 'input_boolean.test_utility_motion', new='off', action='cancel')
        self.listen_state(self.set_bins_test, 'input_boolean.test_bins_announce', new='on', action='set')
        self.listen_state(self.set_bins_test, 'input_boolean.test_bins_announce', new='off', action='cancel')
        self.listen_state(self.set_frost_warning_test, 'input_boolean.test_frost_warning', new='on', action='set')
        self.listen_state(self.set_frost_warning_test, 'input_boolean.test_frost_warning', new='off', action='cancel')
        self.listen_state(self.set_notification_test, 'input_boolean.test_notification', new='on', action='set')
        self.listen_state(self.set_notification_test, 'input_boolean.test_notification', new='off', action='cancel')
        self.listen_state(self.set_announcement_test, 'input_boolean.test_announcement', new='on', action='set')
        self.listen_state(self.set_announcement_test, 'input_boolean.test_announcement', new='off', action='cancel')
        self.listen_state(self.set_max_home_test, 'input_boolean.test_max_home', new='on', action='set')
        self.listen_state(self.set_max_home_test, 'input_boolean.test_max_home', new='off', action='cancel')
        self.listen_state(self.set_front_door_ding_test, 'input_boolean.test_front_door_ding', new='on', action='set')
        self.listen_state(self.set_front_door_ding_test, 'input_boolean.test_front_door_ding', new='off', action='cancel')
        self.listen_state(self.set_front_door_light_on_test, 'input_boolean.test_front_door_light_on', new='on', action='set')
        self.listen_state(self.set_front_door_light_on_test, 'input_boolean.test_front_door_light_on', new='off', action='cancel')
        self.listen_state(self.test_test_alarm_test, 'input_boolean.test_early_alarm', new='on')
        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='on', action='set')
        self.listen_state(self.set_test_test, 'input_boolean.test_test', new='off', action='cancel')
        self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='on', action='set')
        self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='off', action='cancel')
        # self.listen_state(self.set_shift, 'input_boolean.early_shift', new='on') # FIXME: remove ?
        # self.listen_state(self.set_shift, 'input_boolean.early_shift', new='off')
        self.log('\tset* (for input_booleans) registered')

        self.listen_state(self.status, 'input_boolean.status', new='on')
        self.listen_state(self.set_debug_flag, 'input_boolean.debug')
        self.listen_state(self.set_verbose_flag, 'input_boolean.verbose')
        self.listen_state(self.vacuum_debug, 'vacuum.s7_max_ultra')

        # daily reset including booleans
        self.run_daily(self.reset, '04:00:00')

        # set state
        self.run_daily(self.set_all_state, '21:00:10') # pre-set - make sure before max retires (to bed)
        self.run_daily(self.set_all_state, '00:00:10') # re-set - possibly dodgy as won't be confirmed before max retires

        self.run_daily(self.downstairs_off, '02:00:00')

        # set for 07:00
        # self.run_daily(self.sonos_configure1a, '06:59:55') # kitchen, bedroom, bedroom2
        self.run_daily(self.sonos_configure2b, '06:59:55')
        # set for 07:45
        # bedroom, bedroom2, bathroom
        self.run_daily(self.sonos_configure2b, '07:44:55')
        # set for 09:00
        self.run_daily(self.sonos_configure2a, '08:59:55')
        # set for 10:00
        self.run_daily(self.sonos_configure2a, '09:59:55')
        self.log('\tsonos_configure* registered')

        self.run_daily(self.frost_warning, "sunset + 00:00:00")
        self.run_daily(self.frost_warning, "sunset + 01:00:00")
        self.log('\tfrost_warning registered')

        self.run_daily(self.backup, '23:30:00')
        self.log('\tbackup registered')

        self.run_daily(self.stairs_on, "sunset + 00:00:00")
        self.log('\tstairs_on registered')

        self.run_daily(self.radiator_on, "sunset + 00:10:00")
        self.log('\tradiator_on registered')

        self.run_daily(self.bedtime, "23:30:00")
        self.log('\tbedtime registered')

        self.run_daily(self.front_door_battery, "19:29:00")
        self.log('\tfront_door_battery registered')

        self.run_daily(self.bins_preannounce, '19:30:00')
        self.run_daily(self.bins_announce1, '17:30:00')
        self.run_daily(self.bins_announce2, '19:30:00')
        self.run_daily(self.vouchers_announce, '17:29:00')
        self.log('\t*announce* registered')

        self.run_daily(self.water_garden_daily, '19:30:00')  # , 'minutes': 10)
        self.log('\twater_garden_* registered')

        self.run_daily(self.outside_lights_off, "21:30:00")
        self.log('\toutside_lights_off registered')

        # self.run_daily(self.rearm_kitchen_alarm, '07:00:30')
        # self.run_daily(self.wardrobe_on, '07:00:00')
        self.log('\trun_daily registered')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.max_travel_time_to_home, runtime)
        self.run_minutely(self.check_garden_tap, runtime)
        self.run_minutely(self.check_garage_door, runtime)
        self.run_minutely(self.check_karoq_door, runtime)
        self.log('\trun_minutely registered')

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.update_openweathermap, runtime)
        self.run_hourly(self.check_roborock, runtime)
        self.run_hourly(self.add_starling_calendar_events, runtime)
        self.log('\trun_hourly registered')

        self.run_every(self.update_openweathermap, "now", 5 * 60)
        self.log('\trun_every registered')

        self.log('\tregistration end')


        # adapi = self.get_ad_api()
        # print(adapi)
        # task =
        # self.create_task(self.main())

        self.post_init()

# -------------------------------------------------------------------------------------------------

    def pre_init(self):
        self.debug = True if self.get_state('input_boolean.default_debug_state') == 'on' else False
        self.verbose = True if self.get_state('input_boolean.default_verbose_state') == 'on' else False
        self.testing = True if self.get_state('input_boolean.default_testing_state') == 'on' else False

        self.rota = self.generate_rota(datetime(2024, 5, 16).date(), 12)

# -------------------------------------------------------------------------------------------------

    # async def main(self):
    #     for message in self.messages:
    #         await self.send_notification(message)
    #         await asyncio.sleep(1)

    # async def send_notification(self, message):
    #     print(message)
    #     await self.call_service('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id='media_player.study', return_result=True)
    #     # await self.adapi.call_service("send/alert", message=message, return_result=True)


    def post_init(self):
        self.set_all_state()
        # self.run_in_thread(self.backup, 0)
        self.set_console_log_level()
        self.int_set_log_level("DEBUG")

        self.starling = StarlingHelper('eyJhbGciOiJQUzI1NiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAA_31Ty5KjMAz8lSnOoykgJDbc5rY_sB8gZDlxDdiUbbI7tbX_vkqAPHaq5oYtd0vdLf4ULqWiK3BybyljHJw_9ug_3iiMxWuR5l6K9aGs6z1ZUFb30FBJoNvSgO7bslWklLE7ecy_p6JrtNqrtq4O6rVwmIuuUnVZVXp_uUCiMPv8IwyG409nhLs5NKrfG4RDbQiaWhrgYW-gVcra3U41VauFO4cP9gtC1VyXfduDLncamhJlmlLVgPum4UppxdgLQhS9E3FKd5S2RFD1poVG4Q6w1ATMLWrTtpZ0eRFMYWJ5PuEnM7gRj9xFRvOCOSOdRvZ5OSc8i1UJjgEHyBF9shzXEp3YzAMbEJY7YqG8PkXKLviVeM6nEF0SNnDeuLMzMw5LLTKxm3L3K7rMLyNnNJixIynK-QvV4wUbl19G9ALgzvDAApCApYH0CVH832jQmCg2LYjrkMsnzSmHcRNFwVsXR7yQQ7BgZ2_SUrrNtTDEYN2weXe9evRqm2VdBThddwHy58QPNt0mfkReyzyiG1ZazlkazdNq5DOjiM2r3e5uUY8DetoyXZUvAjEaEJU5ho3_wnDJDyidn3rcEevMT5ofo1vJ71STsd8t0JbJfduW7BdXvgC392nCm6jVBmcE7azbAhQGGAJtPv7nlsdxxW87s839uDFPyMGlb_-FJcLi7z8CO9KdYwQAAA.UHuebVjVW021Ad_7N__22UwU_6nt_fsXazoKRQEUilYYQVW29ryGzMRW5Gzuhwwb4_ZnmJ02NN3KgKEtQnyxfs1w4IrozXfCypdzISFCxTjbwtxfYRdqgmkpuRpDrFlgWhnoZpXirUY9KKDeg8F7w0g74TUOOT8CCgo-Pr67wW6Ru5U77Gb876295azO_kz9sdZMCe5pplaKhpVySi-LOUe5-2IjH1B6Bt6AW7UcUIJNAMAAyzIInEHXB5HSs6FMcHVphOaIIsj-sSX0MdJ6_flNCJoXZf_bXWXsGMtCBgtdo5McLmcM0R2s8o_BSUy4W-w1umod6LLRB5CMqVBeQHgZmy_-By3ct5AIqZF9aSneEQgUKIsBEuZL4nC7Ohqz9-GRqBmOS24Yth9LqaI7dfQT2uFxLd66WjjDEorCdMgIHntwRfpkQSxWzRgWoVbH12vKaXCiZndKuSLShCD3EdMx1uwPpEx3Ih_r_pJGw6zMAxDRz2rnkVltKhR411LnQyV6-KNrsESXvSrbU5NXGUlxSbT7-bkyHz_FVXwcG4rqAUEXxdLSFo5eRvQ7MJ8jwX-BH8Sn1Q8fiPOgycJHV8qkUoOqgsfh6kA6xmY6Q5oVaZOPh3LOA5ilvWP4oXOMZEr6-j62ApFgfpA0WFQSVXChm5mgKnT2R7otEooCWYc', update=True)

        self.fire_event('refresh_calendar_events')
        # self.int_set_log_level("DEBUG")

        # self.run_in_thread(self.show_starling_account, 0)
        self.run_in_thread(self.add_starling_calendar_events, 0)
        # self.run_in_thread(self.add_shift_calendar_events, 0)

        # print(self.get_callback_entries())
        self.announce(delay=4, message='Initialised', entity_id='media_player.study')
        # self.messages.append("foo")
        # self.messages.append("bar")

        # print(self.messages)

# -------------------------------------------------------------------------------------------------

    def show_starling_account(self, kwargs={}):

        account = self.starling.account()
        account.update()

        print(account)
        account.show_standing_orders()
        account.show_direct_debits()

        # goal = helper.find_savings_goal('Tax')

# -------------------------------------------------------------------------------------------------

    def add_shift_calendar_events(self, kwargs={}):

        # print(self.rota)
        for a_date, shift in self.rota:
            # print(f'{date} {shift}')
            if shift != 'Off':
                end_date = a_date + timedelta(days=1)
                self.call_service('calendar/create_event', entity_id='calendar.shifts', summary=shift, description=shift, start_date=str(a_date), end_date=str(end_date))

# -------------------------------------------------------------------------------------------------

    def add_starling_calendar_events(self, kwargs={}):

        self.log_function_name()
        helper = self.starling
        account = helper.account()
        account_uid = account.account_uid
        default_category_uid = account.default_category_uid

        state = self.get_state('sensor.starling_events', attribute='scheduled_events')
        # self.log(state)

        data = helper.get_request("/direct-debit/mandates")

        for el in data["mandates"]:
            add = True
            dd = DirectDebit(el)
            next_date = dd.next_date
            last_date = dd.last_date
            summary = f'{dd.originator_name} - {dd.reference}'

            if (dd.cancelled is not None) or (next_date is None and last_date is None):
                continue

            for el in state["calendar.starling"]["events"]:
                match=next_date == el["start"] and summary == el["summary"]
                # self.log(f'dd {match} next_date={next_date} last_date={last_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}', level='WARNING')
                if match:
                    add = False
                    self.log(f'\t\tSkip previously entered DD next_date={next_date} summary={summary}', level='WARNING')
                    break

                match = last_date == el["start"] and summary == el["summary"]
                # self.log(f'dd {match} next_date={next_date} last_date={last_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}', level='WARNING')
                if match:
                    add = False
                    self.log(f'\t\tSkip previously entered DD last_date={last_date} summary={summary}', level='WARNING')
                    break

            if add:
                self.add_starling_dd_calendar_event(dd)


        data = helper.get_request(f"/payments/local/account/{account_uid}/category/{default_category_uid}/standing-orders")

        for el in data["standingOrders"]:
            add = True
            so = StandingOrder(helper, el)

            next_date = so.next_date
            summary = f'{so.payee_name} - {so.reference}'

            if (so.cancelled_at is not None) or (next_date is None):
                continue

            for el in state["calendar.starling"]["events"]:
                match=next_date == el["start"] and summary == el["summary"]
                # print(f'so {match} next_date={next_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}')
                if match:
                    add = False
                    self.log(f'\t\tSkip previously entered SO next_date={next_date} summary={summary}', level='WARNING')
                    break

            if add:
                self.add_starling_so_calendar_event(so)

        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def add_starling_dd_calendar_event(self, dd):

        amount = dd.amount
        currency = dd.currency
        reference = dd.reference
        last_date = dd.last_date
        originator = dd.originator_name
        summary = f'{originator} - {reference}'
        description=f"{currency} {amount:.2f} payable to {originator} : Reference {reference} : Last payment was on {last_date}"

        if dd.next_date is not None:
            start_date = datetime.strptime(dd.next_date, '%Y-%m-%d').date()
            end_date = start_date + timedelta(days=1)
            self.call_service('calendar/create_event', entity_id='calendar.starling', summary=summary, description=description, start_date=str(start_date), end_date=str(end_date))
            self.log('future direct debit added', level='WARNING')

        if dd.last_date is not None:
            start_date = datetime.strptime(dd.last_date, '%Y-%m-%d').date()
            end_date = start_date + timedelta(days=1)
            self.call_service('calendar/create_event', entity_id='calendar.starling', summary=summary, description=description, start_date=str(start_date), end_date=str(end_date))
            self.log('past direct debit added', level='WARNING')

# -------------------------------------------------------------------------------------------------

    def add_starling_so_calendar_event(self, so):

        start_date = datetime.strptime(so.start_date, '%Y-%m-%d').date()
        end_date = start_date + timedelta(days=1)
        summary = f'{so.payee_name} - {so.reference}'
        frequency = so.frequency.lower().title()
        category = so.spending_category.lower().title()
        description=f"{so.currency} {so.amount} payable to {so.payee_name} : Frequency {frequency} x{so.interval} : Category {category}"
        # self.log(f'start_date={start_date} end_date={end_date} summary={summary} description={description}')
        self.call_service('calendar/create_event', entity_id='calendar.starling', summary=summary, description=description, start_date=str(start_date), end_date=str(end_date))
        self.log('future standing order added', level='WARNING')

# -------------------------------------------------------------------------------------------------

    def dummy(self):
        self.log_function_name()
        # self.log(f'\ttest')
        # self.log(f'\ttest', level='DEBUG')
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def set_all_state(self, kwargs={}):
        self.log_function_name()

        dow = self.dow()
        day = datetime.now().date()

        if self.now_is_between('03:00:01', '23:59:59'):
            day += timedelta(days=1) # check for tomorrow

        shift = self.check_shift(day)
        self.log(f'\t{shift} shift', level='WARNING')

        # is_weekday = self.is_weekday()
        # self.log_debug(f'\tdow={dow} is_weekday={is_weekday}')

        delay = 0 if self.is_mock_run() else 5

        early_alarm_time = self.get_state('input_datetime.early_alarm_time')

        if early_alarm_time != "04:58:00" and early_alarm_time != "05:25:00":
            # must be set specifically
            hour = self.get_state('input_datetime.early_alarm_time', attribute='hour')
            minute = self.get_state('input_datetime.early_alarm_time', attribute='minute')
        else:
            if shift == 'Night':
                hour = 5
                minute = 25
            else:
                hour = 4
                minute = 58

            self.set_state('input_datetime.early_alarm_time', state=f"{hour:02d}:{minute:02d}:00", hour=hour, minute=minute, second=0)

        # (21-00 on tuesday or friday/saturday) or (00-03 on wednesday or saturday/sunday) -> set alarm later
        later = (self.now_is_between('21:00:00', '23:59:59') and ((dow == 2) or (5 <= dow <= 6))) or (self.now_is_between('00:00:00', '03:00:00') and ((dow == 3) or (6 <= dow <= 7)))

        if later:
            self.set_state('input_datetime.normal_alarm_time', state="10:00:00", hour=10, minute=0, second=0)
        else:
            self.set_state('input_datetime.normal_alarm_time', state="07:45:00", hour=7, minute=45, second=0)

        booleans = {
            # !!! do NOT include debug/verbose/testing !!!
            'early_alarm', 'normal_alarm', 'test_alarm', 'lumie', 'test_1', 'test_2', 'test_3', 'sonos',
            'water_garden_1', 'water_garden_15', 'water_garden_20', 'water_garden_30', 'bedtime',
            'reset_alarms', 'test_utility_motion', 'test_kitchen_motion', 'test_bins_announce', 'test_frost_warning', 'test_notification',
            'test_announcement', 'test_max_home', 'test_reset', 'test_front_door_ding', 'test_front_door_light_on', 'test_test',
            'test_early_alarm', 'mock_run', 'alarm_debug'
        }

        for boolean in booleans:
            self.set_state(f'input_boolean.{boolean}', state='off')

        self.set_default_state()

        # # if Automation.default_early_alarm_schedule in ('weekday', 'daily'):
        # #     if not is_weekday or (dow == 5 and self.is_after(Automation.announce_start)):
        # #         state = 'off'
        # #     if self.is_sunday():
        # #         state = 'on'
        # # else:
        # #     state = 'off'

        state = 'off' if shift == 'Off' else 'on'

        self.set_state('input_boolean.early_alarm', state=state)

        message = f'The early morning alarm is set to {hour:02d}:{minute:02d}' if state == 'on' else 'The early morning alarm is cancelled'
        diff = (datetime.now() - Automation.initialise_ts).seconds

        if diff > 60:
            self.announce(delay=delay, message=message, entity_id='media_player.study')
        else:
            self.desktop_notification(message)

        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def set_console_log_level(self, entity='input_boolean.debug', attribute='state', old='off', new='on', kwargs={}):
        if self.get_debug():
            self.int_set_log_level("DEBUG")
        else:
            self.int_set_log_level("INFO")

# -------------------------------------------------------------------------------------------------

    def set_debug_flag(self, entity, attribute, old, new, kwargs={}):
        Automation.debug = True if new == 'on' else False
        self.log(f'\tdebug now {Automation.debug}', level='INFO')
        self.set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def set_testing_flag(self, entity, attribute, old, new, kwargs={}):
        Automation.testing = True if new == 'on' else False
        self.log(f'\ttesting now {Automation.testing}', level='INFO')
        self.set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def set_verbose_flag(self, entity, attribute, old, new, kwargs={}):
        Automation.verbose = True if new == 'on' else False
        self.log(f'\tverbose now {Automation.verbose}', level='INFO')
        self.set_console_log_level()

# -------------------------------------------------------------------------------------------------

    def int_set_log_level(self, level):
        if Automation.log_level != level:
            self.log(f'\tchanging log level to {level}', level='INFO')
            self.set_log_level(level)
            Automation.log_level = level
        else:
            self.log(f'\tlog level unchanged ({level})', level='INFO')

# -------------------------------------------------------------------------------------------------

    # def set_shift(self, entity, attribute, old, new, kwargs={}): # FIXME: remove ?
    #     self.set_all_state()

# -------------------------------------------------------------------------------------------------

    def reset_test1(self, entity, attribute, old, new, kwargs={}):
        self.delay(0.5)
        self.set_state('input_boolean.test_1', state='off')

# -------------------------------------------------------------------------------------------------

    def reset_test2(self, entity, attribute, old, new, kwargs={}):
        self.delay(0.5)
        self.set_state('input_boolean.test_2', state='off')

# -------------------------------------------------------------------------------------------------

    def reset_test3(self, entity, attribute, old, new, kwargs={}):
        self.delay(0.5)
        self.set_state('input_boolean.test_3', state='off')

# -------------------------------------------------------------------------------------------------

    def reset_alarms(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.cancel_timer2(Automation.early_alarm_callback, 'early alarm')
        self.cancel_timer2(Automation.normal_alarm_callback, 'normal alarm')
        self.cancel_timer2(Automation.test_alarm_callback, 'test alarm')

        self.set_state('input_boolean.early_alarm', state=self.get_state('input_boolean.default_early_alarm_state'))
        self.set_state('input_boolean.normal_alarm', state=self.get_state('input_boolean.default_normal_alarm_state'))

        self.set_state('input_boolean.alarm_debug', state='off')
        self.set_state('input_boolean.reset_alarms', state='off')
        enabled = self.get_state('input_boolean.early_alarm') == 'on'

        if enabled:
            # self.set_state('input_datetime.early_alarm_time', state="05:25:00", hour=5, minute=25, second=0)
            self.set_state('input_datetime.early_alarm_time', state="07:00:00", hour=7, minute=0, second=0)
        else:
            # self.set_state('input_datetime.early_alarm_time', state="04:59:00", hour=4, minute=59, second=0)
            # self.set_state('input_datetime.early_alarm_time', state="06:50:00", hour=6, minute=50, second=0)
            self.set_state('input_datetime.early_alarm_time', state="07:00:00", hour=7, minute=0, second=0)

        self.set_state('input_datetime.normal_alarm_time', state="07:45:00", hour=7, minute=45, second=0)

        self.set_alarms()
        # self.delay(0.5)
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def set_default_state(self):

        self.set_state('input_boolean.early_alarm', state=self.get_state('input_boolean.default_early_alarm_state'))
        self.set_state('input_boolean.normal_alarm', state=self.get_state('input_boolean.default_normal_alarm_state'))
        self.set_state('input_boolean.lumie', state=self.get_state('input_boolean.default_lumie_state'))
        self.set_state('input_boolean.debug', state=self.get_state('input_boolean.default_debug_state'))
        self.set_state('input_boolean.verbose', state=self.get_state('input_boolean.default_verbose_state'))
        self.set_state('input_boolean.testing', state=self.get_state('input_boolean.default_testing_state'))

# -------------------------------------------------------------------------------------------------

    def register_test(self, callback, entity_id='input_boolean.test_1', **kwargs):
        handler = self.listen_state(callback, entity_id, **kwargs)
        self.log(f'\tcallback {callback.__name__} registered on {entity_id}', level='WARNING')
        Automation.handlers[entity_id] = handler

# -------------------------------------------------------------------------------------------------

    def deregister_test(self, entity_id, **kwargs):
        handler = Automation.handlers[entity_id] if entity_id in Automation.handlers else None
        if handler is not None:
            self.log(f'\tcallback {handler} deregistered on {entity_id}', level='WARNING')
            self.cancel_listen_state(handler, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_1(self, callback, entity_id='input_boolean.test_1', **kwargs):
        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_2(self, callback, entity_id='input_boolean.test_2', **kwargs):
        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def register_test_3(self, callback, entity_id='input_boolean.test_3', **kwargs):
        self.register_test(callback, entity_id, **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_1(self, **kwargs):
        self.deregister_test('input_boolean.test_1', **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_2(self, **kwargs):
        self.deregister_test('input_boolean.test_2', **kwargs)

# -------------------------------------------------------------------------------------------------

    def deregister_test_3(self, **kwargs):
        self.deregister_test('input_boolean.test_3', **kwargs)
        self.set_state('input_boolean.test_3', state='off')

# ---------------------------------------------------------------------------------------------------------

    def test_test(self, entity, attribute, old, new, kwargs):
        self.log_function_name()
        self.run_in(self.test, 0)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def test(self, kwargs={}):
        self.log_function_name()
        traceback.print_stack() # leave
        # future_time = self.parse_time('07:00:00')
        # self.log(future_time)
        # self.log(future_time.hour)
        # self.log(future_time.minute)
        # self.log(future_time.second)
        # self.set_all_state()
        state = self.get_state(entity_id='media_player.kitchen', attribute="all")
        self.log(f'{state}')
        attributes = state['attributes']
        self.log(f'{attributes}')
        media_content_id = attributes.get('media_content_id', '')
        media_content_type = attributes.get('media_content_type', '')
        muted = attributes.get('is_volume_muted', True)
        self.log(f'{media_content_type} {media_content_id} {muted}')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def test_kwargs(self, **kwargs):
        self.log_function_name()
        self.log(kwargs['test'])
        self.log(kwargs['alarm_type'])
        self.log(kwargs['foo'])
        self.log(kwargs['__thread_id'])
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------



    def reset(self, kwargs={}):
        self.log_function_name()

        self.reset_downstairs_motion_flag()
        self.sonos_unjoin_all({})
        self.sonos_configure1({})  # failsafe for bank holiday

        self.set_state('input_boolean.sonos', state='off')
        self.set_state('input_boolean.test_1', state='off')
        self.set_state('input_boolean.test_2', state='off')
        self.set_state('input_boolean.test_3', state='off')
        self.log('\treset')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def log_function_name(self, start=True):
        name = inspect.currentframe().f_back.f_code.co_name
        if self.get_verbose() or self.get_debug():
            self.log(('\t>>> begin' if start else '\t<<< end') +
                     f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

    def delay(self, s):
        if not self.is_mock_run():
            time.sleep(s)

# -------------------------------------------------------------------------------------------------

    def notification_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.run_in(self.int_notification_test, 0)
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def int_notification_test(self, kwargs={}):
        self.log_function_name()
        self.notification('testing notifications', title='title here')
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def notification(self, message, log=False, title=''):
        self.log_function_name()
        if log or self.get_debug():
            self.log(f'\tmessage="{message}" title="{title}"')
        # self.call_service('notify/lg_webos_tv_oled65c7v', message=message) # FIXME: renable TV notification
        self.call_service('notify/disc0rd', title=title, message=message, target="1250932196613685313") # target="1250945771071602851") #
        # swap over and use non-default title if supplied
        message, title = title, message
        # self.call_service('notify/pushbullet', title=title, message=message)
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def desktop_notification(self, message):
        self.log_function_name()
        if self.get_debug():
            self.log(f'\tmessage={message}')
        self.call_service('notify/disc0rd', title='Deferred notification', message=message, target="1250932196613685313")
        # self.call_service('notify/pushbullet', title='Deferred notification', message=message)
        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def announce_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.announce(delay=3, message='testing announcements')
        self.log_function_name(False)

    # def _announce_listener(self, event, data, kwargs={}): # delay, message, timestamp=None, entity_id=None):
    #     self.log_function_name()
    #     self.run_in_thread(self.announce_announcer, 0, **data)
    #     self.log_function_name(False)

    # def announce_announcer(self, data):  # announce to a single device
    #     self.log_function_name()
    #     delay = data['delay2']
    #     message = data['message']
    #     timestamp = data['timestamp']
    #     entity_id = data['entity_id']

    #     print(f'{delay} {message}')
    #     self.log_function_name(False)

        # if entity_id is not None:
        #     volume = 0.3
        # else:
        #     entity_id, volume = self.get_entity_id()

        # # state = self.get_state(entity_id=entity_id, attribute="all")
        # # not_playing = state['state'] != 'playing'

        # if self.announceable():
        #     self.call_service('sonos/snapshot', entity_id=entity_id, with_group=True)
        #     self.int_announce(entity_id=entity_id, volume=volume, delay=delay, message=message)
        #     self.call_service('sonos/restore', entity_id=entity_id, with_group=True)
        #     if timestamp is not None:
        #         ts = datetime.now()
        #         # match timestamp:
        #         #     case None:
        #         #         pass
        #         #     case "travel":
        #         #         Automation.travel_announce_ts = ts
        #         #     case "garage":
        #         #         Automation.garage_announce_ts = ts
        #         #     case "karoq":
        #         #         Automation.karoq_announce_ts = ts
        #         #     case "tap":
        #         #         Automation.tap_ts = ts
        #         #     case "general":
        #         #         Automation.general_announce_ts = ts
        #         #     case _:
        #         #         pass
        #         if timestamp == "travel":
        #             Automation.travel_announce_ts = ts
        #         elif timestamp == "garage":
        #             Automation.garage_announce_ts = ts
        #         elif timestamp == "karoq":
        #             Automation.karoq_announce_ts = ts
        #         elif timestamp == "tap":
        #             Automation.tap_ts = ts
        #         elif timestamp == "general":
        #             Automation.general_announce_ts = ts
        # else:
        #     self.log(f'\tannouncement disabled - {message}', level='WARNING')
        #     self.desktop_notification(message)

        # # if restart:
        # #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)
        # #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)

        # self.log_function_name(False)

    @ ad.app_lock
    def _announce(self, delay, message, timestamp=None, entity_id=None):  # announce to a single device
        self.log_function_name()
        # state = self.get_state(entity_id=entity_id, attribute="all")
        # attributes = state['attributes']
        # media_content_id = attributes['media_content_id']
        # media_content_type = attributes['media_content_type']
        # self.log(f'media id={media_content_id} type={media_content_type}')
        # restart = state['state'] == 'playing'

        if entity_id is not None:
            volume = 0.25
        else:
            entity_id, volume = self.get_entity_id()

        # state = self.get_state(entity_id=entity_id, attribute="all")
        # not_playing = state['state'] != 'playing'

        if self.announceable():
            self.call_service('sonos/snapshot', entity_id=entity_id, with_group=True)
            self.int_announce(entity_id=entity_id, volume=volume, delay=delay, message=message)
            self.call_service('sonos/restore', entity_id=entity_id, with_group=True)
            if timestamp is not None:
                ts = datetime.now()
                # match timestamp:
                #     case None:
                #         pass
                #     case "travel":
                #         Automation.travel_announce_ts = ts
                #     case "garage":
                #         Automation.garage_announce_ts = ts
                #     case "karoq":
                #         Automation.karoq_announce_ts = ts
                #     case "tap":
                #         Automation.tap_ts = ts
                #     case "general":
                #         Automation.general_announce_ts = ts
                #     case _:
                #         pass
                if timestamp == "travel":
                    Automation.travel_announce_ts = ts
                elif timestamp == "garage":
                    Automation.garage_announce_ts = ts
                elif timestamp == "karoq":
                    Automation.karoq_announce_ts = ts
                elif timestamp == "tap":
                    Automation.tap_ts = ts
                elif timestamp == "general":
                    Automation.general_announce_ts = ts
        else:
            self.log(f'\t\tannouncement disabled - {message}', level='WARNING')
            self.desktop_notification(message)

        # if restart:
        #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)
        #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)

        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    @ ad.app_lock
    def announce(self, delay, message, timestamp=None, entity_id=None):  # announce to a single device
        self.log_function_name()
        # state = self.get_state(entity_id=entity_id, attribute="all")
        # attributes = state['attributes']
        # media_content_id = attributes['media_content_id']
        # media_content_type = attributes['media_content_type']
        # self.log(f'media id={media_content_id} type={media_content_type}')
        # restart = state['state'] == 'playing'

        # self.fire_event("announce", delay2=delay, message=message, timestamp=timestamp, entity_id=entity_id)

        self.submit_to_executor(self._announce, delay, message, timestamp, entity_id)

        # if entity_id is not None:
        #     volume = 0.3
        # else:
        #     entity_id, volume = self.get_entity_id()

        # # state = self.get_state(entity_id=entity_id, attribute="all")
        # # not_playing = state['state'] != 'playing'

        # if self.announceable():
        #     self.call_service('sonos/snapshot', entity_id=entity_id, with_group=True)
        #     self.int_announce(entity_id=entity_id, volume=volume, delay=delay, message=message)
        #     self.call_service('sonos/restore', entity_id=entity_id, with_group=True)
        #     if timestamp is not None:
        #         ts = datetime.now()
        #         # match timestamp:
        #         #     case None:
        #         #         pass
        #         #     case "travel":
        #         #         Automation.travel_announce_ts = ts
        #         #     case "garage":
        #         #         Automation.garage_announce_ts = ts
        #         #     case "karoq":
        #         #         Automation.karoq_announce_ts = ts
        #         #     case "tap":
        #         #         Automation.tap_ts = ts
        #         #     case "general":
        #         #         Automation.general_announce_ts = ts
        #         #     case _:
        #         #         pass
        #         if timestamp == "travel":
        #             Automation.travel_announce_ts = ts
        #         elif timestamp == "garage":
        #             Automation.garage_announce_ts = ts
        #         elif timestamp == "karoq":
        #             Automation.karoq_announce_ts = ts
        #         elif timestamp == "tap":
        #             Automation.tap_ts = ts
        #         elif timestamp == "general":
        #             Automation.general_announce_ts = ts
        # else:
        #     self.log(f'\tannouncement disabled - {message}', level='WARNING')
        #     self.desktop_notification(message)

        # # if restart:
        # #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)
        # #     self.call_service('media_player/media_play', entity_id=entity_id, media_content_id=media_content_id, media_content_type=media_content_type)

        self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def int_announce(self, entity_id, volume, delay, message, setvol=True):
        self.log_function_name()

        mute_delay = 1
        state = self.get_state(entity_id=entity_id, attribute="all")
        attributes = state.get('attributes', {})
        media_content_id = attributes.get('media_content_id', '')
        media_content_type = attributes.get('media_content_type', '')
        muted = attributes.get('is_volume_muted', True)

        if self.is_mock_run():
            delay = 0
            mute_delay = 0

        self.log_verbose(f"\tmessage={message}")
        self.log_debug(f"\tdelay={delay} volume={volume} setvol={setvol} attributes={attributes}")
        self.log_debug(f'\tmuted={muted} media id={media_content_id} type={media_content_type}')

        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=True)
        self.delay(mute_delay)

        if setvol:
            self.log_verbose(f'\tset new volume {volume:3.2f} on {entity_id}')
            self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume)
            self.delay(mute_delay)

        self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
        self.delay(mute_delay)

        if muted:
            self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)

        # https://www.home-assistant.io/integrations/google_translate/
        #
        # self.call_service('tts/google_translate_say', entity_id=entity_id, message=message)
        self.call_service('tts/speak', entity_id='tts.google_en_co_uk', cache=True, message=message, media_player_entity_id=entity_id)
        self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')

        Automation.general_announce_ts = datetime.now()
        self.notification(message, log=False)  # tv and pushbullet
        self.delay(delay)  # wait for message to complete
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    @ ad.app_lock
    def broadcast(self, volume, message):  # broadcast to multiple devices
        self.log_function_name()

        broadcast = ['media_player.kitchen', 'media_player.bathroom', 'media_player.dining_room']
        other = ['media_player.study', 'media_player.bedroom_2']
        # other = ['media_player.living_room', 'media_player.study', 'media_player.bedroom_2']

        self.call_service('sonos/snapshot', entity_id='all')
        self.call_service('media_player/join', entity_id=broadcast[0], group_members=broadcast[1:])

        for e in broadcast:
            self.call_service('media_player/volume_set', entity_id=e, volume_level=volume)

        for e in other:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=True)

        self.int_announce(entity_id=broadcast[0], delay=3, volume=volume, message=message, setvol=True)
        self.call_service('sonos/restore', entity_id='all')

        for e in broadcast + other:
            self.call_service('media_player/volume_mute', entity_id=e, is_volume_muted=False)

        self.log_function_name(False)

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

    def is_playing(self, entity_id=None):

        if entity_id is None:
            entity_id, volume = self.get_entity_id()

        state = self.get_state(entity_id=entity_id, attribute="state")
        return state == 'playing'

# ---------------------------------------------------------------------------------------------------------

    def announceable(self):
        dt = datetime.now()
        start = Automation.announce_start
        end = Automation.announce_end
        # end = 23
        return (start <= dt.hour <= (end - 1)) or (dt.hour == end and dt.minute <= 29)

# ---------------------------------------------------------------------------------------------------------

    def is_mock_run(self):
        return self.get_state('input_boolean.mock_run') == 'on'

# ---------------------------------------------------------------------------------------------------------

    def is_summer(self):
        (isoy, isow, isod) = arrow.now().isocalendar()
        return 17 <= isow <= 37  # end of april to mid-september

# ---------------------------------------------------------------------------------------------------------

    def is_garage_door_closed(self):
        state = self.get_state(Automation.garage_entity_id)
        return state == 'closed'

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

    def turn_on_if_off(self, entity_id, brightness=64):
        prev_state = self.get_state(entity_id)
        prev_brightness = self.get_state(entity_id, attribute="brightness")
        debug = self.get_debug()

        if prev_state == 'off':
            if debug:
                self.log(f'\tturn on {entity_id} brightness={brightness}', level='DEBUG')
            self.call_service('light/turn_on', entity_id=entity_id, brightness=brightness)
        else:
            if debug:
                self.log(f'\tignored - {entity_id} already on brightness={prev_brightness}', level='DEBUG')
        return prev_state

# ---------------------------------------------------------------------------------------------------------

    def rearm_kitchen_alarm(self, kwargs={}):
        # self.log_function_name()
        self.call_service('switch/turn_on', entity_id='switch.sonos_alarm_1392')
        # self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def reset_downstairs_motion_flag(self):
        # self.log_function_name()
        self.log(f'\tdownstairs_motion_flag was {self.downstairs_motion_flag} now False')
        self.downstairs_motion_flag = False
        # self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def any_light_on_full(self, entity_ids):
        for entity_id in entity_ids:
            brightness = self.get_state(entity_id=entity_id, attribute="brightness")
            if brightness is not None and brightness >= 250:
                return True
        return False

# ---------------------------------------------------------------------------------------------------------

    def light_entities(self, name, count=1):
        entities = []
        for entity in range(1, count+1):
            entities.append(f'light.{name}_{entity}')
        return entities

# ---------------------------------------------------------------------------------------------------------

    def cancel_timer2(self, timer, message=None):
        if timer is not None:
            self.cancel_timer(timer, True)
            timer = None
            if message is not None:
                self.log(f'\t{message} cancelled', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def log_debug(self, message):
        if self.get_debug():
            self.log(f'\t{message}', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def log_verbose(self, message):
        if self.get_verbose() or self.get_debug():
            self.log(f'\t{message}', level='INFO')

# ---------------------------------------------------------------------------------------------------------

    def get_debug(self):
        return Automation.debug

# ---------------------------------------------------------------------------------------------------------

    def get_verbose(self):
        return Automation.verbose

# ---------------------------------------------------------------------------------------------------------

    def get_testing(self):
        return False # fixme:
        # return Automation.testing

# ---------------------------------------------------------------------------------------------------------

    def get_alarm_debug(self):
        return self.get_state("input_boolean.alarm_debug") == "on"

# ---------------------------------------------------------------------------------------------------------

    def get_sun_elevation(self):
        elev = self.get_state('sun.sun', attribute='elevation')
        self.log(f'\telev={elev:2.2f}', level='DEBUG')
        return elev

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

    def max_travel_time_to_home(self, kwargs={}):
        # verbose = self.get_verbose()
        # debug = self.get_debug()
        testing = self.get_testing()
        diff = (datetime.now() - Automation.travel_announce_ts).seconds
        minutes = int(self.get_state('sensor.google_travel_time'))
        direction = self.get_state('sensor.max_dir_of_travel')
        state = self.get_state('sensor.maxine_iphone_activity')

        if state == "Automotive":
            self.set_state('sensor.max_driving_status', state='Driving')
        else:
            self.set_state('sensor.max_driving_status', state='Not Driving')

        announce = self.now_is_between('10:00:00', '00:30:00') and (10 <= minutes <= 15) and (diff >= 4 * 60) and direction in ('towards', 'unknown', None)

        message = f'Max is {minutes} minutes away'

        if announce or testing or self.is_mock_run():
            if self.is_playing('media_player.study'):
                self.desktop_notification(message)
                Automation.travel_announce_ts = datetime.now()
            else:
                self.log(f'\tmessage={message} ts={Automation.travel_announce_ts.ctime()} ({Automation.travel_announce_ts.timestamp():6.3f})', level='DEBUG')
                self.announce(delay=5, message=message, timestamp='travel', entity_id='media_player.study')

# ---------------------------------------------------------------------------------------------------------

    def max_location_announce(self, entity_id, state, kwargs={}):
        self.log_function_name()

        announce = True
        delay = 0 if self.is_mock_run() else 10
        village = entity_id == 'proximity.village'
        direction = self.get_state("proximity.home", attribute="dir_of_travel")
        self.log(f'\tdirection={direction}', level='DEBUG')

        name = Automation.locations[entity_id]
        self.log(f'\tentity_id={entity_id} state={state} name={name}')

        if village:
            if direction != 'towards':
                announce = False
            message = name
        else:
            if state == 'arrive':
                message = f'Max has arrived at {name}'
            else:
                message = f'Max has left {name}'

        if announce:
            self.announce(delay=delay, message=message, entity_id='media_player.study')

        if village:
            self.max_home('', '', '', '', {})

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def max_location_detect(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        name = kwargs['name']
        location = kwargs['location']
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} name={name} location={location}', level='INFO')
        if new == name:
            self.max_location_announce(location, 'arrive', kwargs)
        elif old == name:
            self.max_location_announce(location, 'leave', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def max_village_announce_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.set_state('input_boolean.debug', state='on')
        self.int_max_village_announce(entity, attribute, old, new, kwargs)
        self.set_state('input_boolean.debug', state='off')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def force_debug(self, callback, entity='', attribute='', old='', new='', kwargs={}):
        self.int_set_log_level("DEBUG")

        try:
            callback(entity, attribute, old, new, kwargs)
        except Exception:
            self.log('\texception in force_debug')
        finally:
            self.int_set_log_level("INFO")

# ---------------------------------------------------------------------------------------------------------

    def max_home_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.max_home(entity, attribute, old, new, kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def max_home(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()

        if self.is_dusk():
            self.call_service('light/turn_on', entity_id=['light.standard_lamp_1'], brightness=128)
            self.call_service('light/turn_on', entity_id=['light.front_door_1'], brightness=128)
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)
            self.front_door_light_on()
            seconds = 10*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.front_door_light_off, seconds)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def paul_home_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.paul_home(entity, attribute, old, new, kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def paul_home(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new}')  # kwargs={kwargs}')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def scene_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()

        self.activate_scene(entity, attribute, old, new, kwargs)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def activate_scene(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()

        scene = kwargs['scene']
        entity_id = kwargs['entity_id']

        if scene:
            scene = 'scene.'+scene
            if new == 'on':
                self.turn_on(scene)
            else:
                self.turn_off(scene)

        if entity_id:
            self.delay(1)
            self.set_state(entity_id, state='off')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    # def tap_test(self, entity, attribute, old, new, kwargs={}):
    #     self.log_function_name()
    #     self.log(f'\t{kwargs}', level='DEBUG')
    #     self.water_garden_for(entity, attribute, old, new, minutes=1)
    #     self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        minutes = kwargs['minutes']
        if minutes:
            self.tap_on(minutes=minutes)
        else:
            self.error('no timer set')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_action(self, event, data, kwargs={}):
        self.log_function_name()
        minutes = kwargs['minutes']
        self.log(f'\twater_garden_for_action for {minutes:d} minutes')
        self.water_garden_for_n_minutes({minutes: minutes})  # was minutes=minutes
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_for_n_minutes(self, kwargs={}):
        self.log_function_name()
        self.water_garden_for('', '', '', '', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_stop(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.tap_off()
        # TODO: stop running thread
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def water_garden_daily(self, kwargs={}):
        self.log_function_name()
        if self.is_summer():
            if self.no_rain():
                minutes = 20
                kwargs = {**kwargs, 'minutes': minutes}
                self.water_garden_for_n_minutes(kwargs)
                self.announce(delay=5, message=f'Watering garden for {minutes} minutes')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def tap_on(self, **kwargs):
        self.log_function_name()
        minutes = kwargs['minutes']
        if minutes:
            self.log(f'\ttap_on for {minutes:d} minutes')
            self.call_service('switch/turn_on', entity_id='switch.garden_tap')
            Automation.tap_ts = datetime.now()
            seconds = 60*minutes
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.tap_off, seconds)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def tap_off(self, kwargs={}):
        self.log_function_name()
        self.call_service('switch/turn_off', entity_id='switch.garden_tap')
        self.announce(delay=6, message='The garden tap is now off')
        Automation.tap_ts = None
        self.set_state('input_boolean.water_garden_1', state='off')
        self.set_state('input_boolean.water_garden_15', state='off')
        self.set_state('input_boolean.water_garden_20', state='off')
        self.set_state('input_boolean.water_garden_30', state='off')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def check_garden_tap(self, kwargs):
        state = self.get_state('switch.garden_tap')
        if state == 'on':
            self.log(f'\tGarden tap is {state}', level='WARNING')
            seconds = (datetime.now() - Automation.tap_ts).seconds
            n = math.ceil(seconds / 60)
            diff1,diff2 = divmod(seconds, 60)
            self.log(f'\t\t{diff1} {diff2}')
            if diff1 > 0 and ((diff1 + 1) % 10) == 0:
                self.announce(delay=6, message=f'The garden tap has been on for {n} minutes', timestamp=None) # don't update timestamp

# ---------------------------------------------------------------------------------------------------------

    def check_garage_door(self, kwargs={}):
        state = self.get_state(Automation.garage_entity_id)
        if state != 'closed':
            self.log(f'\tGarage door is {state} garage_announce_ts={Automation.garage_announce_ts}', level='WARNING')
            diff = (datetime.now() - Automation.garage_announce_ts).seconds
            if diff >= 60 * 60:
                self.garage_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    def check_karoq_door(self, kwargs={}):
        state = self.get_state(Automation.karoq_entity_id)

        if state == 'unavailable':
            self.log(f'\tkaroq_door_state={state}', level='WARNING')
            return

        lock_state = 'locked' if state == 'off' else 'unlocked'
        # self.log(f'\tstate={state} karoq_announce_ts={Automation.karoq_announce_ts}', level='WARNING')

        if state != 'off':
            if self.is_after(19):
                self.call_service('lock/lock', entity_id='lock.tmbkr7nu5p5079987_door_locked')
                state = self.get_state(Automation.karoq_entity_id)
                self.log(f'\tThe car door lock request has been sent. state={state}', level='WARNING')
                # do not announce self.karoq_door_announce(state=state)
                return  # check again in a minute

            self.log(f'\tThe car door is {lock_state} karoq_announce_ts={Automation.karoq_announce_ts}', level='WARNING')
            diff = (datetime.now() - Automation.karoq_announce_ts).seconds
            if diff > 60 * 60:
                self.karoq_door_announce(state=state)

# ---------------------------------------------------------------------------------------------------------

    def garage_door(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        is_dusk = self.is_dusk()
        if new == 'opening':
            if is_dusk:
                self.garage_door_lights(on=True)
        # elif old == 'open' and new == 'closing':
        #     pass
        elif new == 'closed':
            if is_dusk:
                seconds = 60
                self.log(f'\tstart garage_door_light timer for {seconds:d}s', level='DEBUG')
                self.run_in(self.garage_door_lights_off, seconds)
        self.garage_door_announce(state=new)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def get_entity_id(self):
        if self.get_testing():
            entity_id = 'media_player.study'
            volume = 0.2
        else:
            entity_id = 'media_player.kitchen'
            volume = 0.5
        return (entity_id, volume)

# ---------------------------------------------------------------------------------------------------------

    def karoq_door_announce(self, **kwargs):

        state = kwargs['state']

        if state == 'off':
            message = 'The car door is locked'
        elif state == 'on':
            message = 'The car door is unlocked'

        self.announce(delay=5.0, message=message, timestamp='karoq')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce(self, **kwargs):
        state = kwargs['state']

        if state == 'opening':
            message = 'The garage door is opening'
        elif state == 'closing':
            message = 'The garage door is closing'
        elif state == 'closed':
            message = 'The garage door is closed'
        elif state == 'open':
            message = 'The garage door is open'
        elif state == 'unavailable':
            return
        # else:
        #     state = self.get_state(Automation.garage_entity_id)
        #     message = f'The garage door is {state}'

        self.announce(delay=5.0, message=message, timestamp='garage')

# ---------------------------------------------------------------------------------------------------------

    def garage_door_open(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.call_service('cover/open_cover', entity_id=Automation.garage_entity_id)
        if self.is_dusk():
            self.garage_door_lights(on=True)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_close(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.call_service('cover/close_cover', entity_id=Automation.garage_entity_id)
        if self.is_dusk():
            self.garage_door_lights(on=False)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_opening(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.garage_door(Automation.garage_entity_id, 'state', 'closed', 'opening')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closing(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.garage_door(Automation.garage_entity_id, 'state', 'open', 'closing')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_open(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.garage_door(Automation.garage_entity_id, 'state', 'opening', 'open')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_announce_closed(self, entity='', attribute='', old='', new='', kwargs={}):
        self.log_function_name()
        self.garage_door(Automation.garage_entity_id, 'state', 'closing', 'closed')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_debug(self, entity, attribute, old, new, kwargs={}):
        state = self.get_state(Automation.garage_entity_id)
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights(self, **kwargs):
        self.log_function_name()
        entities = {'light.garage_2', 'light.garage_1'}
        on = kwargs['on'] is True

        if on:
            for entity_id in entities:
                self.call_service('light/turn_on', entity_id=entity_id)
        else:
            self.run_in(self.garage_door_lights, 300, on=False)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def garage_door_lights_off(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.garage_door_lights(on=False)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def vacuum_debug(self, entity, attribute, old, new, kwargs={}):
        state = self.get_state('vacuum.s7_max_ultra')
        self.log(f'\tentity={entity} attribute={attribute} old={old} new={new} state={state}', level='INFO')  # kwargs={kwargs}

# ---------------------------------------------------------------------------------------------------------

    def bins_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.run_in(self.bins_preannounce, 0)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def bins_announce(self, announce_type, force=False):
        self.log_function_name()
        # https://www.scambs.gov.uk/recycling-and-bins/find-your-household-bin-collection-day#id=100091416947
        # baseurl = 'https://refusecalendarapi.azurewebsites.net/calendar/ical/'
        baseurl = 'https://servicelayer3c.azure-api.net/wastecalendar/calendar/ical/'
        url = baseurl+'100091416947'  # was '100091416948'
        bins = []
        dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow

        if announce_type == 'preannounce':
            dow = arrow.now().floor('day').shift(hours=6).shift(days=2)  # 6am day after tomorrow
        else:
            dow = arrow.now().floor('day').shift(hours=6).shift(days=1)  # 6am tomorrow

        loop = True
        pattern = r'^Rate limit is exceeded. Try again in (\d+) seconds.$'

        while loop:
            r = requests.get(url)
            t = r.text
            if t[0] == '{':
                y = json.loads(t)
                a = re.search(pattern, y['message'])
                s = a.groups(1)[0]
                self.delay(int(s))
            else:
                loop = False

        c = Calendar(t)

        for e in iter(c.timeline.overlapping(dow, dow)):
            bins.append(e.name.split()[0].lower())

        if force:
            bins = ['orange']

        if len(bins) > 0:
            if len(bins) > 1:
                bins.insert(1, 'and')
                bins.append('bins')
            else:
                bins.append('bin')

            if announce_type == 'preannounce':
                phrase = ' '.join(['It', 'is', 'the', ' '.join(bins), 'this', 'week'])
            elif announce_type == 'announce1':
                phrase = ' '.join(['Can', 'you', 'put', 'the', ' '.join(bins), 'out', 'please'])
            elif announce_type == 'announce2':
                phrase = ' '.join(['Have', 'you', 'put', 'the', ' '.join(bins), 'out'])

            self.announce(delay=5.0, message=phrase)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def bins_preannounce(self, kwargs={}):
        self.log_function_name()
        if self.get_testing():
            self.bins_announce('preannounce', True)
        else:
            self.bins_announce('preannounce')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def bins_announce1(self, kwargs={}):
        self.log_function_name()
        self.bins_announce('announce1')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def bins_announce2(self, kwargs={}):
        self.log_function_name()
        self.bins_announce('announce2')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def vouchers_announce(self, kwargs={}):
        self.log_function_name()

        dow = arrow.now().isoweekday()

        with open('/homeassistant/data.yaml', 'r', encoding="utf-8") as stream:
            try:
                data = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                print(e)

        vouchers = data['vouchers']
        force = vouchers['force']
        value = vouchers['value']
        expiry = vouchers['expiry']

        mock_run = self.is_mock_run()

        if mock_run:
            value = 1
            expiry = 'whenever'

        if dow == 2 or force or mock_run:
            if value > 0:
                phrase = ' '.join([str(value), 'pounds', 'of', 'vouchers', 'expiring', 'end', 'of', expiry])
                self.log(f'\tphrase={phrase}')
                self.announce(delay=6, message=phrase)
            else:
                self.log('\tno expiring vouchers', level='WARNING')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_unjoin1(self, kwargs={}):
        self.log_function_name()

        if arrow.now().isoweekday() >= 6:
            self.log('\tis weekend', level='DEBUG')
        else:
            speakers = ['media_player.bathroom', 'media_player.study', 'media_player.bedroom', 'media_player.bedroom_2']
            self.call_service('media_player/unjoin', entity_id=speakers)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_unjoin2(self, kwargs={}):
        self.log_function_name()
        speakers = ['media_player.bathroom', 'media_player.study', 'media_player.bedroom', 'media_player.bedroom_2']
        self.call_service('media_player/unjoin', entity_id=speakers)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_unjoin_all_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.sonos_unjoin_all(kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_unjoin_all(self, kwargs={}):
        self.log_function_name()
        # self.call_service('media_player/unjoin', entity_id="all")

        speakers = [
            'media_player.kitchen', 'media_player.bathroom', 'media_player.bedroom', 'media_player.bedroom_2', 'media_player.study', 'media_player.dining_room'
        ]
        volume = {
            'media_player.kitchen': 0.0,
            'media_player.bathroom': 0.0,
            'media_player.bedroom': 0.0,
            'media_player.bedroom_2': 0.0,
            'media_player.study': 0.0,
            'media_player.dining_room': 0.0
        }

        self.sonos_configure(speakers, volume, True, 0, False, False)
        self.downstairs_motion_flag = False

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure(self, speakers, volume, unjoin, delay, join, check_downstairs_motion):

        self.log_function_name()

        if unjoin:
            self.log(f"\tunjoin {speakers}", level='DEBUG')
            self.call_service('media_player/unjoin', entity_id=speakers)

        if join:
            self.log(f"\tjoin {speakers}", level='DEBUG')
            self.call_service('media_player/join', entity_id=speakers[0], group_members=speakers[1:])

        # assume bank holiday and mute
        for speaker in speakers:
            self.call_service('media_player/volume_mute', entity_id=speaker, is_volume_muted=True)

        if not self.is_mock_run():
            self.delay(delay)

        is_not_bank_holiday = not self.is_bank_holiday()
        no_downstairs_motion = True
        if check_downstairs_motion:
            no_downstairs_motion = not self.downstairs_motion_flag
        self.log_debug(f"\tis_not_bank_holiday={is_not_bank_holiday} no_downstairs_motion={no_downstairs_motion}")

        if is_not_bank_holiday and no_downstairs_motion:
            for speaker in speakers:
                self.log_debug(f'\tsetting speaker volume to {volume[speaker]} for {speaker}')
                self.call_service('media_player/volume_set', entity_id=speaker, volume_level=volume[speaker])
                self.call_service('media_player/volume_mute', entity_id=speaker, is_volume_muted=False)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure1_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        if self.get_state(entity_id='input_boolean.sonos') == 'on':
            self.sonos_configure1a(kwargs)
        else:
            self.log('\tignored', level='DEBUG')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure1(self, kwargs={}):

        self.log_function_name()

        speakers = [
            'media_player.kitchen', 'media_player.bedroom', 'media_player.bedroom_2'
        ]
        volume = {
            'media_player.kitchen': 0.05, 'media_player.bedroom': 0.05, 'media_player.bedroom_2': 0.3
        }

        sonos = self.get_state(entity_id='input_boolean.sonos')
        state = self.get_state(entity_id='input_boolean.test_1')

        if sonos == 'off':
            self.sonos_configure(speakers, volume, True, 0, True, True)
        else:
            self.log(f'\t{state}', level='DEBUG')
            if state == 'on':
                self.sonos_configure(speakers, volume, True, 0, True, True)
            else:
                self.call_service('media_player/unjoin', entity_id=speakers)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure1a(self, kwargs={}):

        self.log_function_name()

        speakers = [
            'media_player.kitchen', 'media_player.bedroom', 'media_player.bedroom_2'
        ]
        volume = {
            'media_player.kitchen': 0.05, 'media_player.bedroom': 0.05, 'media_player.bedroom_2': 0.3
        }

        self.sonos_configure(speakers, volume, True, 7, True, True)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure2_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        if self.get_state(entity_id='input_boolean.sonos') == 'on':
            self.sonos_configure2a(kwargs)
        else:
            self.log('\tignored', level='DEBUG')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure2a(self, kwargs={}):

        self.log_function_name()

        speakers = [
            'media_player.bedroom', 'media_player.bathroom', 'media_player.bedroom_2', ]
        volume = {
            'media_player.bedroom': 0.01, 'media_player.bathroom': 0.3, 'media_player.bedroom_2': 0.3
        }

        # don't bother to check downstairs_motion_flag but mute for bank holiday - checked in sonos_configure
        self.sonos_configure(speakers, volume, True, 7, True, False)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def sonos_configure2b(self, kwargs={}):

        self.log_function_name()

        speakers = ['media_player.bedroom']
        volume = { 'media_player.bedroom': 0.01 }

        # don't bother to check downstairs_motion_flag but mute for bank holiday - checked in sonos_configure
        self.sonos_configure(speakers, volume, True, 7, True, False)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def lights_off(self, event, data, kwargs={}):

        self.call_service('light/turn_off', entity_id=['light.hallway_1', 'light.hallway_2', 'light.front_door_1', 'light.garage_1', 'light.garage_2']) # not light.standard_lamp_1 !!

# ---------------------------------------------------------------------------------------------------------

    def delete_calendar_events(self, event, data, kwargs={}):

        self.log_function_name()
        state = self.get_state('sensor.starling_events', attribute='scheduled_events')
        for el in state["calendar.starling"]["events"]:
            print(el)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def add_calendar_events(self, event, data, kwargs={}):

        self.log_function_name()
        self.add_starling_calendar_events()
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def set_all_state_event(self, event, data, kwargs={}):

        self.log_function_name()
        self.set_all_state()
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def stairs_on(self, kwargs={}):

        self.call_service('light/turn_on', entity_id='light.hallway_3', brightness=5)

# ---------------------------------------------------------------------------------------------------------

    def radiator_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        elev = self.get_state('sun.sun', 'elevation')
        self.log(f'\telev={elev}', level='DEBUG')
        self.run_in(self.radiator_on, 0)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def radiator_on(self, kwargs={}):
        # self.log_function_name()
        self.call_service('light/turn_on', entity_id='light.radiator')
        # self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def living_room_lights_off(self, kwargs={}):

        self.call_service('light/turn_off', entity_id='light.radiator')
        self.call_service('light/turn_off', entity_id='light.standard_lamp_1')
        self.call_service('light/turn_off', entity_id='light.table_lamp_1')
        # try again - wasn't switching off
        self.call_service('light/turn_off', entity_id='light.standard_lamp_1')

# ---------------------------------------------------------------------------------------------------------

    def bedtime_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.bedtime(kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def bedtime(self, kwargs={}):

        self.living_room_lights_off(kwargs)

# ---------------------------------------------------------------------------------------------------------

    def outside_lights_off(self, kwargs={}):
        self.call_service('light/turn_off', entity_id='light.front_door_1')
        self.call_service('light/turn_off', entity_id='light.garage_1')
        self.log('\toutside lights off')

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_on(self, kwargs={}):

        if 'dow' in kwargs:
            dow = kwargs['dow']
        else:
            dow = arrow.now().isoweekday()

        turn_on = (not (dow == 3 or dow >= 6)) and self.sun_down()

        if turn_on:
            self.log('\tturn on wardrobe')
            self.call_service('switch/turn_on', entity_id='switch.wardrobe')
            s = 15*60
            self.log(f'\tstart wardrobe timer for {s:d}s')
            # self.run_at(self.wardrobe, 'sunrise + 00:30:00')
            self.run_in(self.wardrobe_off, s)

# ---------------------------------------------------------------------------------------------------------

    def wardrobe_off(self, kwargs={}):

        self.call_service('switch/turn_off', entity_id='switch.wardrobe')

# ---------------------------------------------------------------------------------------------------------

    def hallway_on(self, kwargs={}):

        # Turn on hallway lights when dark after 6am

        if self.sun_down():
            self.log('\tsun down - turn on hallway light', level='DEBUG')
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)
            self.log('\thallway off')
            self.log('\tset timer for hallway light', level='DEBUG')
            self.run_at(self.hallway_off, 'sunrise + 00:10:00')

# ---------------------------------------------------------------------------------------------------------

    def hallway_off(self, kwargs={}):

        self.call_service('light/turn_off', entity_id='light.hallway_1')
        self.call_service('light/turn_off', entity_id='light.hallway_2')
        self.log('\thallway off')

# ---------------------------------------------------------------------------------------------------------

    def upstairs_motion_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        kwargs = {**kwargs, 'timer': 20, 'check_override': False, 'location': 'upstairs test'}
        self.upstairs_motion('binary_sensor.downstairs_sensor_motion', 'attribute', 'off', 'on', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def upstairs_motion(self, entity, attribute, old, new, kwargs={}):

        Automation.prev_upstairs_ts = Automation.upstairs_ts
        Automation.upstairs_ts = datetime.now()

        diff1 = (Automation.upstairs_ts - Automation.downstairs_ts).seconds
        diff2 = (Automation.upstairs_ts - Automation.prev_upstairs_ts).seconds
        self.log(f'\tdiff1={diff1} diff2={diff2}', level='DEBUG')

        if diff1 <= 300:
            timer = 600 # 5m timer for bannister
            if self.now_is_between('00:00:00', '03:00:00'):
                self.call_service('light/turn_on', entity_id='light.lumie', brightness=5)
        elif diff1 > 300 and diff2 <= 120:
            timer = 10
        else:
            timer = 120

        if self.now_is_between('22:00:00', 'sunrise') or self.get_state(entity_id='input_boolean.test_2'):
            kwargs = {**kwargs, 'timer': timer, 'check_override': False, 'location': 'upstairs'}
        self.stairs_motion(**kwargs)

# ---------------------------------------------------------------------------------------------------------

    def downstairs_motion_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        # kwargs |= {'timer': 60, 'check_override': True, 'location': 'downstairs'} # 3.9+
        kwargs = {**kwargs, 'timer': 60, 'check_override': True, 'location': 'downstairs'}
        self.downstairs_motion('binary_sensor.downstairs_sensor_motion', 'attribute', 'off', 'on', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def downstairs_motion(self, entity, attribute, old, new, kwargs={}):

        self.downstairs_motion_flag = True
        self.log(f'\tdownstairs_motion_flag={self.downstairs_motion_flag}', level='DEBUG')
        Automation.downstairs_ts = datetime.now()
        # Automation.count = 2
        self.stairs_motion(**kwargs)
        if self.now_is_between('05:00:00', '07:00:00'):
            self.sonos_unjoin2(kwargs)
        # self.cancel_alarm_if_set('switch.sonos_alarm_1392', '07:00:00')  # 07:00 alarm
        self.cancel_alarm_if_set('input_boolean.early_alarm', '07:00:00', '06:00:00')

# ---------------------------------------------------------------------------------------------------------

    def cancel_alarm_if_set(self, entity_id, end_time, start_time='05:00:00'):

        if self.now_is_between(start_time, end_time):
            self.log(f'\tmotion detected between {start_time} and {end_time}')
            state = self.get_state(entity_id=entity_id, attribute="state")
            if state == 'on':
                self.set_state(entity_id, state="off")
        else:
            self.log('\tmotion detected but outside time window')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_motion_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.kitchen_motion('binary_sensor.kitchen_sensor_motion', 'attribute', 'off', 'on', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def kitchen_motion(self, entity, attribute, old, new, kwargs={}):

        self.cancel_kitchen_timers()
        # self.kitchen_floor_on()

        seconds = 5 * 60
        self.log(f'\tstart kitchen floor timer for {seconds:d}s', level='INFO')
        Automation.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)

        # if self.sun_down():
        if self.now_is_between('sunset + 00:15:00', 'sunrise + 00:30:00'):
            self.log('\tsun down - turn_on_if_off kitchen_1/4/5/6', level='INFO')
            self.turn_on_if_off('light.kitchen_1')
            self.turn_on_if_off('light.kitchen_4')
            self.turn_on_if_off('light.kitchen_5')
            self.turn_on_if_off('light.kitchen_6')
            seconds = 5 * 60
            self.log(f'\tstart short kitchen timer for {seconds:d}s', level='INFO')
            Automation.kitchen_timer = self.run_in(self.kitchen_off, seconds, **kwargs)
            seconds = 10 * 60
            self.log(f'\tstart long kitchen timer for {seconds:d}s', level='INFO')
            Automation.kitchen_long_timer = self.run_in(self.kitchen_all_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    def cancel_kitchen_timers(self):

        self.cancel_timer2(Automation.kitchen_timer, 'short kitchen timer')
        self.cancel_timer2(Automation.kitchen_long_timer, 'long kitchen timer')
        self.cancel_timer2(Automation.kitchen_floor_timer, 'floor kitchen timer')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_floor_on(self):

        if self.now_is_between('08:00:00', '22:00:00'):
            self.call_service('light/turn_on', entity_id='light.kitchen_floor', brightness=255)
        if self.now_is_between('22:00:00', '08:00:00'):
            self.call_service('light/turn_on', entity_id='light.kitchen_floor', brightness=128)

# ---------------------------------------------------------------------------------------------------------

    def utility_motion_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.utility_motion('binary_sensor.utility_room_motion_sensor_motion', 'attribute', 'off', 'on', kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def utility_motion(self, entity, attribute, old, new, kwargs={}):

        entity_id = 'light.utility_room_1'
        # state = self.get_state(entity_id=entity_id)
        brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        self.log(f'\tbrightness={brightness} st={Automation.utility_timer} lt={Automation.utility_long_timer}', level='DEBUG')

        # new motion detected - restart timers
        self.cancel_utility_timers(timer_type='both')

        if self.now_is_between('sunset + 00:15:00', 'sunrise'):
            prev_state = self.turn_on_if_off(entity_id, brightness=64)
            self.log(f'\tprev_state={prev_state}', level='DEBUG')
            seconds = 5 * 60
            self.log(f'\tstart short utility timer for {seconds:d}s', level='DEBUG')
            Automation.utility_timer = self.run_in(self.utility_off, seconds, timer_type='short')
            seconds = 10 * 60
            self.log(f'\tstart long utility timer for {seconds:d}s', level='DEBUG')
            Automation.utility_long_timer = self.run_in(self.utility_off, seconds, timer_type='long')

# ---------------------------------------------------------------------------------------------------------

    def utility_off(self, kwargs={}):

        entity_id = 'light.utility_room_1'
        timer_type = kwargs['timer_type']
        brightness = self.get_state(entity_id=entity_id, attribute="brightness")
        state = self.get_state(entity_id=entity_id, attribute="state")
        self.log(f'\ttimer_type={timer_type} brightness={brightness} state={state} st={Automation.utility_timer} lt={Automation.utility_long_timer}', level='DEBUG')
        self.cancel_utility_timers(timer_type='short')
        # (timer_type == 'long' or (brightness is not None and brightness <= 130)):
        if state == 'on' and timer_type == 'long':
            self.call_service('light/turn_off', entity_id=entity_id)
        else:
            self.log('\tlong timer running or brightness >= 130', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def cancel_utility_timers(self, **kwargs):

        timers = kwargs['timer_type']

        if timers in ('both', 'short'):
            self.cancel_timer2(Automation.utility_timer, 'short utility timer')

        if timers in ('both', 'long'):
            self.cancel_timer2(Automation.utility_long_timer, 'long utility timer')

# ---------------------------------------------------------------------------------------------------------

    def stairs_motion(self, **kwargs):

        self.log(f'\tts1={Automation.downstairs_ts.ctime()} ({Automation.downstairs_ts.timestamp():6.3f})', level='DEBUG')
        self.log(f'\tts2={Automation.upstairs_ts.ctime()} ({Automation.upstairs_ts.timestamp():6.3f})', level='DEBUG')

        if self.is_predusk():
            seconds = kwargs['timer']
            self.cancel_timer2(Automation.stairs_timer, 'stairs timer')
            Automation.override = not kwargs['check_override']
            self.bannister_on()
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            Automation.stairs_timer = self.run_in(self.bannister_off, seconds, **kwargs)

# ---------------------------------------------------------------------------------------------------------

    def bannister_on(self, kwargs={}):

        self.call_service('light/turn_on', entity_id='light.bannister', brightness=77)
        elev = self.get_state('sun.sun', 'elevation')
        if elev < 5 and not self.now_is_between('01:30:00', 'sunrise'):
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64)

# ---------------------------------------------------------------------------------------------------------

    def bannister_off(self, kwargs={}):

        check = kwargs['check_override']
        location = kwargs['location']
        if (check and not Automation.override) or not check:
            self.log(f'\tturn off bannister - {location}')
            self.call_service('light/turn_off', entity_id='light.bannister')
            self.call_service('light/turn_off', entity_id='light.hallway_1')
            Automation.override = False
            Automation.stairs_timer = None
        else:
            self.log(f'\tskip turn off bannister - {location}')

# ---------------------------------------------------------------------------------------------------------

    def downstairs_off(self, kwargs={}):

        self.call_service('light/turn_off', entity_id='light.upstairs')
        self.call_service('light/turn_off', entity_id='light.downstairs')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_floor_off(self, kwargs={}):

        self.call_service('light/turn_off', entity_id='light.kitchen_floor')
        Automation.kitchen_floor_timer = None

# ---------------------------------------------------------------------------------------------------------

    def kitchen_off(self, kwargs={}):

        entity_ids = self.light_entities('kitchen', 6)
        if not self.any_light_on_full(entity_ids):
            self.kitchen_all_off(kwargs)
        else:
            self.log('\tdeferring - kitchen lights high', level='DEBUG')

# ---------------------------------------------------------------------------------------------------------

    def kitchen_all_off(self, kwargs={}):

        self.cancel_kitchen_timers()
        self.kitchen_floor_on()
        seconds = 60
        Automation.kitchen_floor_timer = self.run_in(self.kitchen_floor_off, seconds)
        self.log(f'\tstart {seconds}s timer floor lights', level='DEBUG')
        for e in [1, 2, 3, 4, 5, 6, 1, 2, 3, 4, 5, 6]:
            self.call_service('light/turn_off', entity_id=f'light.kitchen_{e}')

# ---------------------------------------------------------------------------------------------------------

    def front_door_ding_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        self.front_door_ding('binary_sensor.front_door_ding', 'state', 'off', 'on', {})
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def front_door_ding(self, entity, attribute, old, new, kwargs={}):

        self.int_front_door_ding(entity, attribute, old, new, kwargs)

# ---------------------------------------------------------------------------------------------------------

    def int_front_door_ding(self, entity, attribute, old, new, kwargs={}):

        self.tapo_siren_on()
        self.front_door_announce()
        self.ding_front_door_light()
        self.ding_hallway_light()

# ---------------------------------------------------------------------------------------------------------

    def tapo_siren_on(self, kwargs={}):

        self.call_service('siren/turn_on', entity_id='siren.tapo_hub_siren')
        seconds = 5
        self.log(f'\tstart timer for{seconds:d}s', level='DEBUG')
        self.run_in(self.tapo_siren_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def tapo_siren_off(self, kwargs={}):

        self.call_service('siren/turn_off', entity_id='siren.tapo_hub_siren')

# ---------------------------------------------------------------------------------------------------------

    def front_door_announce(self, kwargs={}):

        message = 'Someone is at the front door' if not self.get_testing() else 'just testing'
        self.broadcast(volume=0.5, message=message)

# ---------------------------------------------------------------------------------------------------------

    def ding_front_door_light(self, kwargs={}):
        # Turn on front door light when dark when someone calls
        # see also front_door_light_on/off

        if self.now_is_between('sunset', 'sunrise'):
            # TODO: return to previous level if was previously on
            brightness = self.get_state('light.front_door_1', attribute='brightness')
            state = self.get_state('light.front_door_1')
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
            self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=192, transition=10)
            # self.turn_on('scene.front_door_ding_2') # FIXME: not working - scenes dont allow transitiona
            seconds = 12*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            # FIXME:, brightness=brightness) # state=state??
            self.run_in(self.front_door_light_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def ding_hallway_light(self, kwargs={}):
        # Turn on hallway light when dark

        if self.is_dusk():  # dusk till dawn
            self.call_service('light/turn_on', entity_id='light.hallway_1', brightness=64, transition=5)
            seconds = 10*60
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.hallway_off, seconds)

# ---------------------------------------------------------------------------------------------------------

    def front_door_battery_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        self.run_in(self.front_door_battery, 0)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def front_door_battery(self, kwargs={}):

        level = int(self.get_state('sensor.front_door_battery'))
        message = None
        if level <= 50:
            battery = ''
            if level <= 20:
                battery = ' - CRITICAL'
                message = 'Please replace the front door battery immediately'
            elif level <= 25:
                battery = ' - dangerously low'
                message = 'Please replace the front door battery as soon as possible'
            elif level <= 30:
                battery = ' - low'
                message = 'Please charge the second front door battery'
            if message:
                self.announce(delay=5, message=message)
            self.notification(f'Recharge front door battery ({level:d}%{battery})')

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_on(self, kwargs={}):

        self.run_in(self.int_front_door_light_on, 0)

# ---------------------------------------------------------------------------------------------------------

    def int_front_door_light_on(self, kwargs={}):

        if self.now_is_between('sunset', 'sunrise + 1:00:00'):
            if self.is_dusk():
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=0)
                self.call_service('light/turn_on', entity_id='light.front_door_1', brightness=128, transition=10)
                self.call_service('light/turn_on', entity_id='light.garage_1', brightness=128, transition=10)
            else:
                self.run_in(self.int_front_door_light_on, 60)  # respawn self in 60s

# ---------------------------------------------------------------------------------------------------------

    def front_door_light_off(self, kwargs={}):

        # scene = 'scene.front_door_ding_2'
        # self.log(f'\tscene={scene}', level='DEBUG')
        # self.turn_off(scene) # TODO: not working
        self.call_service('light/turn_off', entity_id='light.hallway_1', transition=10)
        self.call_service('light/turn_off', entity_id='light.front_door_1', transition=10)

# ---------------------------------------------------------------------------------------------------------

    def frost_warning_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        self.frost_warning(kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def frost_warning(self, kwargs={}):

        testing = self.get_testing()
        stemp = self.get_state(entity_id='sensor.openweathermap_forecast_temperature_low')

        if stemp is None or stemp == 'unavailable':
            self.log(f'\tforecast low is {stemp}', level='WARNING')
            return False

        temp = float(stemp)
        self.log(f'\tforecast low is {temp}', level='DEBUG')
        warning = temp <= 3.0

        if warning or testing:
            self.log('\tfrost warning', level='WARNING')
            self.announce(delay=5, message='There is a chance of frost overnight')

        return warning

# ---------------------------------------------------------------------------------------------------------

    def update_available_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        self.update_available(entity, attribute, old, new, kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def update_available(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def early_alarm_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.run_in(self.int_alarm, 0, alarm_type='test')
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def set_early_alarm(self, entity='', attribute='', old='', new='', kwargs={}):
        self.cancel_timer2(Automation.early_alarm_callback, 'early alarm')
        Automation.early_alarm_callback = self.set_alarm(alarm_type='early', action=kwargs['action'])

# ---------------------------------------------------------------------------------------------------------

    def set_normal_alarm(self, entity='', attribute='', old='', new='', kwargs={}):
        self.cancel_timer2(Automation.normal_alarm_callback, 'normal alarm')
        Automation.normal_alarm_callback = self.set_alarm(alarm_type='normal', action=kwargs['action'])

# ---------------------------------------------------------------------------------------------------------

    def set_test_alarm(self, entity='', attribute='', old='', new='', kwargs={}):
        self.cancel_timer2(Automation.test_alarm_callback, 'test alarm')

        n=1 # 0
        t = datetime.now() - timedelta(hours=n) + timedelta(minutes=7)
        tt = f'{t.hour:02d}:{t.minute:02d}:00'  # {t.second:02d}'
        # self.log(f'\tt={t} tt={tt}', level='INFO')
        self.set_state('input_datetime.test_alarm_time', state=tt, hour=t.hour, minute=t.minute, second=0)

        Automation.test_alarm_callback = self.set_alarm(alarm_type='test', action=kwargs['action'])

# ---------------------------------------------------------------------------------------------------------

    def set_alarms(self):
        self.log_function_name()
        if self.get_state('input_boolean.early_alarm') == 'on':
            self.set_early_alarm('', '', '', '', {'action': 'set'})

        if self.get_state('input_boolean.normal_alarm') == 'on':
            self.set_normal_alarm('', '', '', '', {'action': 'set'})

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def set_alarm(self, **kwargs):
        # if self.get_debug():
        #     traceback.print_stack()
        #     self.log(80*'=')

        alarm = None
        action = kwargs['action']
        alarm_type = kwargs['alarm_type']
        entity_id = f'input_datetime.{alarm_type}_alarm_time'

        if alarm_type == 'test':
            enabled = True
        else:
            enabled = self.get_state(f'input_boolean.{alarm_type}_alarm') == 'on'

        self.log(f"\t{alarm_type} alarm enabled", level='DEBUG')
        self.log(f"\taction={action}", level='DEBUG')

        debug = self.get_alarm_debug()

        if action == 'set':
            state = self.get_state(entity_id, attribute="attributes")
            if debug:
                now = datetime.now()
                self.log(f"\t{now}", level='DEBUG')
                # FIXME: hour +1 ??
                alarm_time = f"{now.hour+1:02d}:{(now.minute+1):02d}:00"
                self.set_state(entity_id, state=alarm_time, hour=now.hour, minute=now.minute+1, second=0)
                state = self.get_state(entity_id, attribute="attributes")
            else:
                d = datetime.now() + timedelta(days=1)
                t = datetime(d.year, d.month, d.day, state['hour'], state['minute'], 0, 0) + timedelta(minutes=-5)
                alarm_time = f"{t.hour:02d}:{t.minute:02d}:00"
            kwargs.pop('action', None)  # del kwargs['action']
            alarm = self.run_daily(self.alarm, alarm_time, **kwargs)
            self.log_debug(f'\t{alarm_type} alarm set for {alarm_time} using {entity_id}')
            self.desktop_notification(f'The {alarm_type} alarm is set to {alarm_time}')
        elif action == 'cancel':
            if alarm_type == 'early':
                alarm = Automation.early_alarm_callback
            elif alarm_type == 'normal':
                alarm = Automation.normal_alarm_callback
            elif alarm_type == 'test':
                alarm = Automation.test_alarm_callback
            self.cancel_timer2(alarm, f'{alarm_type} alarm')
        else:
            self.log(f"\tUnexpected alarm action {action}", level='WARNING')

        return alarm

# ---------------------------------------------------------------------------------------------------------

    def alarm(self, kwargs={}):
        self.log_function_name()
        self.run_in(self.lumie_alarm, 0, **kwargs)
        # self.log(f'{kwargs}')

        if kwargs['alarm_type'] == 'test':
            s = 30
        else:
            s = 5*60

        self.run_in(self.int_alarm, s, **kwargs)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def select_alarm(self, **kwargs):

        if kwargs['alarm_type'] == 'normal':
            ids = [
                'x-rincon-mp3radio://http://prem2.di.fm:80/melodicprogressive_hi?5fba91be81f6da5b573f89c1',
                'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
            ]
        elif kwargs['alarm_type'] == 'test':
            ids = [
                'aac://http://prem2.di.fm:80/progressive?5fba91be81f6da5b573f89c1',
            ]
        else:
            ids = [
                # birdsong spring morning
                'x-sonos-spotify:spotify%3atrack%3a5VFk26TzgwqX18dFhRmbSM?sid=9&flags=8224&sn=1',
                # birdsong garden morning
                'x-sonos-spotify:spotify%3atrack%3a3K3cxx8ntQp8DZbPpltwr4?sid=9&flags=8224&sn=1',
                # a gentle thunderstorm
                'x-sonos-spotify:spotify%3atrack%3a1r4QKeqpv1ov8FkrgKDxQ7?sid=9&flags=8224&sn=1',

                # 'x-sonos-spotify:spotify%3atrack%3a2T5Lipk1QTtvt76Xjcwrxc?sid=9&flags=8224&sn=1', # heavy thunderstorm sounds
                # 'x-sonos-spotify:spotify%3atrack%3a1E0jvxVMYcnZbjvrs03Yay?sid=9&flags=8224&sn=1', # thunderstorm sounds with rain and loud claps of thunder for all isomniacs
                # 'x-sonos-spotify:spotify%3atrack%3a49kbhMUlsVPp0fOdTOCgNM?sid=9&flags=8224&sn=1', # extreme thunderstorm soubnds with torrential rain & very loud thunder claps
                #
                # 'x-sonos-spotify:spotify%3atrack%3a2cwKtKEhPn6ZnJmlzbmpLQ?sid=9&flags=8224&sn=1', # the early morning rain
                #
                # 'x-sonos-spotify:spotify%3atrack%3a4G6Lz9Et6dhLKydPyY4N9a?sid=9&flags=8224&sn=1', # rain drops dancing on a tin roof
                # 'x-sonos-spotify:spotify%3atrack%3a16D3zoIJWuEbXFfkzXSIqs?sid=9&flags=8224&sn=1', # an angry thunderstorm
                # 'x-sonos-spotify:spotify%3atrack%3a6H5aGE9xZEPkpeEAn4f7b8?sid=9&flags=8224&sn=1', # thunderstorm
                # 'x-sonos-spotify:spotify%3atrack%3a3UdClX9rDMiYUOIl6JWaRo?sid=9&flags=8224&sn=1', # heavy thunderstorm
            ]

        return ids[random.randint(0, len(ids) - 1)]  # randomise choice.

# ---------------------------------------------------------------------------------------------------------

    def play_normal_alarm(self, dow=None):
        if dow is None:
            dow = arrow.now().isoweekday()
        bank_holiday = self.is_bank_holiday()
        return self.get_state(entity_id='input_boolean.normal_alarm') == 'on' and (not bank_holiday) and dow <= 5 and dow != 3

# ---------------------------------------------------------------------------------------------------------

    def int_alarm(self, kwargs={}):
        self.log_function_name()

        alarm_type = kwargs['alarm_type']
        test = alarm_type == 'test'
        debug = self.get_alarm_debug()
        entity_id = 'media_player.bedroom'

        if test:
            play = True
            entity_id = 'media_player.study'
        else:
            play = alarm_type == 'early' or alarm_type == 'normal' # (alarm_type == 'normal' and self.play_normal_alarm())

        self.log(f'\talarm_type={alarm_type} debug={debug} play={play}')

        if play:
            media_content_id = self.select_alarm(alarm_type=alarm_type)
            self.log(f'\tmedia_content_id={media_content_id}')
            self.log(f'\tentity_id={entity_id}', level='DEBUG')
            self.call_service('media_player/volume_mute', entity_id=entity_id, is_volume_muted=False)
            self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=0)
            self.delay(1)
            self.call_service('media_player/play_media', entity_id=entity_id, media_content_type="music", media_content_id=media_content_id)
            self.call_service('media_player/repeat_set', entity_id=entity_id, repeat='off')

            target_volume = 50  # deal in integers for convenience
            if test:
                span = 12
            else:
                span = 60
            volume = 0
            incr_volume = target_volume * (5/100.0)  # 5% increase in volume
            sleeptime = span/12

            while volume < target_volume:
                volume += incr_volume
                self.call_service('media_player/volume_set', entity_id=entity_id, volume_level=volume/100.0)
                self.delay(sleeptime)

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def lumie_alarm_test(self, entity, attribute, old, new, kwargs={}):
        self.log_function_name()
        self.run_in(self.lumie_alarm, 0, test=True)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def lumie_alarm(self, kwargs={}):
        self.log_function_name()
        test = 'test' in kwargs
        seconds = 5*60 if 'test' not in kwargs else 10
        elev = self.get_state('sun.sun', 'elevation')
        enabled = self.get_state('input_boolean.lumie') == 'on' and elev < 5
        dow = arrow.now().isoweekday()
        holiday = self.is_bank_holiday()

        if not holiday and enabled and dow <= 5 and dow != 3 or test:
            # TODO: record handles?
            self.run_in_thread(self.lumie_phase1, 0, brightness=100,transition=seconds, rgb_color=[255, 180, 10])  # now
            if self.now_is_between('06:00:00', '08:00:00'):
                self.run_in_thread(self.lumie_phase2, seconds, brightness=250, transition=seconds, rgb_color=[250, 250, 250]) # +5m
            self.run_in_thread(self.lumie_phase3, 4*seconds)  # +20m
        else:
            self.log(f'\tskipping lumie alarm holiday={holiday} enabled={enabled} dow={dow}', level='INFO')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase1(self, kwargs={}):
        if self.get_state('input_boolean.lumie') == 'off':
            return
        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']
        self.call_service('light/turn_on', entity_id='light.lumie', brightness=brightness, transition=transition, rgb_color=rgb_color)

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase2(self, kwargs={}):
        if self.get_state('input_boolean.lumie') == 'off':
            return
        brightness = kwargs['brightness']
        transition = kwargs['transition']
        rgb_color = kwargs['rgb_color']
        self.call_service('light/turn_on', entity_id='light.lumie', brightness=brightness, transition=transition, rgb_color=rgb_color)
        kwargs['alarm_type'] = 'normal'

# ---------------------------------------------------------------------------------------------------------

    def lumie_phase3(self, kwargs={}):
        self.call_service('light/turn_off', entity_id='light.lumie')

# ---------------------------------------------------------------------------------------------------------

    def set_utility_motion_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.utility_motion_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_kitchen_motion_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.kitchen_motion_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_bins_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.bins_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_frost_warning_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.frost_warning_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_notification_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.notification_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_announcement_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.announce_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_max_home_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            # self.register_test_3(self.max_home_test)
            self.register_test_3(self.max_village_announce)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_front_door_ding_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.front_door_ding_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_front_door_light_on_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.front_door_light_on_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_test_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.test_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_early_alarm_test(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            self.register_test_3(self.test_early_alarm_test)
        elif action == 'cancel':
            self.deregister_test_3()

# ---------------------------------------------------------------------------------------------------------

    def set_tap_timestamp(self, entity, attribute, old, new, kwargs={}):
        action = kwargs['action']
        if action == 'set':
            Automation.tap_ts = datetime.now()
        elif action == 'cancel':
            Automation.tap_ts = None

# ---------------------------------------------------------------------------------------------------------

    def test_test_alarm_test(self, entity, attribute, old, new, kwargs={}):

        self.log_function_name()

        if Automation.test_alarm_callback is not None:
            self.cancel_timer2(Automation.test_alarm_callback, 'test alarm')

        t = datetime.now() + timedelta(minutes=1)
        self.log(f'\t{t}', level='DEBUG')
        tt = f'{t.hour:02d}:{t.minute:02d}:00'  # {t.second:02d}'
        self.log(f'\t{tt}', level='INFO')
        self.set_state('input_datetime.test_alarm_time', state=tt, hour=t.hour, minute=t.minute, second=0)

        Automation.test_alarm_callback = self.set_alarm(alarm_type='test', action='set')

        self.log_function_name(False)

# ---------------------------------------------------------------------------------

    def cancel_alarm(self, entity, attribute, old, new, kwargs={}):

        self.set_state('input_boolean.early_alarm', state='off')

# ---------------------------------------------------------------------------------

    def backup(self, entity='', attribute='', old='', new='', kwargs={}):

        self.log_function_name()
        self.call_service('hassio/backup_full', compressed=True, homeassistant_exclude_database=True)
        self.log_function_name(False)

# ---------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs={}):

        self.status('','','','')

# ---------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs={}):

        status = f'\n\n\tkitchen_timer={Automation.kitchen_timer}\n'
        status += f'\tkitchen_long_timer={Automation.kitchen_long_timer}\n'
        status += f'\tkitchen_floor_timer={Automation.kitchen_floor_timer}\n'
        status += f'\tutility_timer={Automation.utility_timer}\n'
        status += f'\tutility_timer={Automation.utility_long_timer}\n'
        status += f'\tstairs_timer={Automation.stairs_timer}\n'
        status += f'\n\tearly_alarm_callback={Automation.early_alarm_callback}\n'
        status += f'\tnormal_alarm_callback={Automation.normal_alarm_callback}\n'
        status += f'\n\tupstairs_ts={Automation.upstairs_ts}\n'
        status += f'\tdonstairs_ts={Automation.downstairs_ts}\n'
        status += f'\tprev_upstairs_ts={Automation.prev_upstairs_ts}\n'
        status += f'\tgeneral_announce_ts={Automation.general_announce_ts}\n'
        status += f'\ttravel_announce_ts={Automation.travel_announce_ts}\n'
        status += f'\tgarage_announce_ts={Automation.garage_announce_ts}\n'
        status += f'\ttap_ts={Automation.tap_ts}\n'
        status += f'\n\tdownstairs_motion_flag={Automation.downstairs_motion_flag}\n'
        status += f'\n\tdefault_early_alarm_schedule={Automation.default_early_alarm_schedule}\n'
        state = self.get_state('input_boolean.default_early_alarm_state')
        status += f'\tdefault_early_alarm_state={state}\n'
        state = self.get_state('input_boolean.default_normal_alarm_state')
        status += f'\tdefault_normal_alarm_state={state}\n'
        state = self.get_state('input_boolean.default_lumie_state')
        status += f'\tdefault_lumie_state={state}\n'
        state = self.get_state('input_boolean.default_debug_state')
        status += f'\tdefault_debug_state={state}\n'
        state = self.get_state('input_boolean.default_verbose_state')
        status += f'\tdefault_verbose_state={state}\n'
        state = self.get_state('input_boolean.default_testing_state')
        status += f'\tdefault_testing_state={state}\n'
        status += f'\n\tdebug={Automation.debug}\n'
        status += f'\tverbose={Automation.verbose}\n'
        status += f'\ttesting={Automation.testing}\n'

        self.log(f'{status}')

        # account = self.starling.account()
        self.show_starling_account()

        self.set_state('input_boolean.status', state='off')

# ---------------------------------------------------------------------------------

    def update_openweathermap(self, kwargs):

        self.call_service('homeassistant/update_entity', entity_id='weather.openweathermap')

# ---------------------------------------------------------------------------------

    def check_roborock(self, kwargs):

        state = self.get_state('sensor.s7_max_ultra_dock_error')

        if state == 'ok':
            return

        if state == "duct_blockage":
            message = 'Vacuum duct blockage'
        elif state == "water_empty":
            message = 'Vacuum clean water tank empty or not installed'
        elif state == "waste_water_tank_full":
            message = 'Vacuum waste water tank full'
        elif state == "cleaning_tank_full_or_blocked":
            message = 'Vacuum cleaning tank full or blocked'
        elif state == "maintenance_brush_jammed":
            message = 'Vacuum maintenance brush jammed'
        elif state == "dirty_tank_latch_open":
            message = 'Vacuum dirty tank latch open'
        elif state == "no_dustbin":
            message = 'Vacuum has no dustbin'
        else:
            self.desktop_notification(f'Roborock has an unknown error {state}')
            return

        diff = (datetime.now() - Automation.vacuum_announce_ts).seconds

        if diff > ( 3 * 60 ):
            self.announce(delay=8, message=message)
            Automation.vacuum_announce_ts = datetime.now()

# ---------------------------------------------------------------------------------

    def generate_rota(self, start_date, num_cycles):

        # Shift pattern: 3 days on, 1 day off, 3 days on, 3 days off, 4 days on (night shift), 7 days off, 3 days on, 4 days off
        pattern = [
            (3, 'Day'),
            (1, 'Off'),
            (3, 'Day'),
            (3, 'Off'),
            (4, 'Night'),
            (7, 'Off'),
            (3, 'Night'),
            (4, 'Off')
        ]

        rota = []
        current_date = start_date

        for cycle in range(num_cycles):
            for days, shift in pattern:
                for _ in range(days):
                    rota.append((current_date, shift))
                    current_date += timedelta(days=1)

        return rota

# ---------------------------------------------------------------------------------

    def check_shift(self, date_to_check):

        for date, status in self.rota:
            if date == date_to_check:
                return status

        return "Date out of range"

# ---------------------------------------------------------------------------------

class StarlingHelper:
    """Helper class"""

    def __init__(self, api_token: str, update: bool = False, sandbox: bool = False) -> None:
        """Call to initialise a StarlingHelper object."""

        self._api_token = api_token
        self._sandbox = sandbox
        self._update = update
        self._auth_headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

        retry = urllib3.Retry(respect_retry_after_header=True)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry)
        session = requests.Session()
        session.mount("https://", adapter)

        self._session = session
        self._account = StarlingAccount(self)

        # if update:
        #     self._account.update()

    def account(self) -> None:
        if self._account is None:
            self._account = StarlingAccount(self)

        return self._account

    def get_request(self, endpoint: str) -> None:

        url = self.url(endpoint)
        response = self._session.get(url, headers=self._auth_headers)
        # print(response.status_code, response.headers)
        response.raise_for_status()
        data = response.json()
        return data

    def put_request(self, endpoint: str, data: str) -> None:

        url = self.url(endpoint)
        response = self._session.put(url, headers=self._auth_headers, data=json_dumps(data))
        # print(response.status_code, response.headers)
        response.raise_for_status()
        return

    def url(self, endpoint: str) -> str:
        """Build a URL from the API's base URLs."""

        if self._sandbox is True:
            url = BASE_URL_SANDBOX
        else:
            url = BASE_URL
        return "{0}{1}".format(url, endpoint)

    def get_payee(self, uid: str):

        json = self.get_request(f"/payees/{uid}")
        return json["payeeName"]

    def show_savings_goals(self):

        for uid, goal in self.account.savings_goals.items():
            if goal.target_minor_units is not None:
                print(f'{uid} - {goal.name} = {goal.target_currency}{goal.total_saved_minor_units:6.2f} ({goal.target_currency}{goal.target_minor_units:6.2f})')
            else:
                print(f'{uid} - {goal.name} = {goal.total_saved_minor_units:6.2f}')

    def find_savings_goal(self, name):

        for uid, goal in self.account.savings_goals.items():
            if goal.name == name:
                return goal
class DirectDebit:
    """Representation of a Direct Debit."""

    def __init__(self, dd: Dict) -> None:

        self.uid = dd.get("uid", None)
        self.reference = dd.get("reference", None)
        self.status = dd.get("status", None)
        self.source = dd.get("source", None)
        self.created = dd.get("created", None)
        self.cancelled = dd.get("cancelled", None)
        self.next_date = dd.get("nextDate", None)
        self.last_date = dd.get("lastDate", None)
        self.originator_name = dd.get("originatorName", None)
        self.originator_uid  = dd.get("originatorUid", None)
        self.merchant_uid = dd.get("merchantUid", None)
        self.last_payment = dd.get("lastPayment", None)
        if self.last_payment is not None:
            amount = self.last_payment.get("lastAmount", None)
            if amount is not None:
                self.currency = amount["currency"]
                self.amount = amount["minorUnits"] / 100.0
        self.account_uid = dd.get("accountUid", None)
        self.category_uid = dd.get("categoryUid", None)

    def __repr__(self):
        attrs = vars(self)
        return 'DirectDebit:\n'+'\n'.join("\t%s: %s" % item for item in attrs.items())+'\n'

    def __str__(self):
        attrs = vars(self)
        return 'DirectDebit('+', '.join("%s: %s" % item for item in attrs.items())+')'


class StandingOrder:
    """Representation of a Standing Order."""

    def __init__(self, helper, so: Dict) -> None:

        # print(so)
        # print('-----')
        self.payment_order_uid = so.get("paymentOrderUid", None)
        amount = so.get("amount", None)
        self.currency = amount["currency"]
        self.amount = amount["minorUnits"] / 100.0
        self.reference = so.get("reference", None)
        self.payee_uid = so.get("payeeUid", None)
        self.payee_account_uid = so.get("payeeAccountUid", None)
        self.payee_name = helper.get_payee(self.payee_uid)
        self.standing_order_recurrence = so.get("standingOrderRecurrence", None)
        self.start_date = self.standing_order_recurrence['startDate']
        self.frequency = self.standing_order_recurrence['frequency']
        self.interval = self.standing_order_recurrence.get('interval', None)
        self.count = self.standing_order_recurrence.get('count', None)
        self.until_date = self.standing_order_recurrence.get('untilDate', None)
        self.next_date = so.get("nextDate", None)
        self.cancelled_at = so.get("cancelledAt", None)
        self.updated_at = so.get("updatedAt", None)
        self.spending_category = so.get("spendingCategory", None)
        self.category_uid = so.get("categoryUid", None)

    def __repr__(self):

        attrs = vars(self)
        return 'StandingOrder:\n'+'\n'.join("\t%s: %s" % item for item in attrs.items())+'\n'

    def __str__(self):

        attrs = vars(self)
        return 'StandingOrder('+', '.join("%s: %s" % item for item in attrs.items())+')'

class SavingsGoal:
    """Representation of a Savings Goal."""

    def __init__(self, helper, uid) -> None:

        self._helper = helper
        self.uid = uid
        self.name = None
        self.target_currency = None
        self.target_minor_units = None
        self.total_saved_currency = None
        self.total_saved_minor_units = None

    def __repr__(self):

        attrs = vars(self)
        return 'SavingsGoal:\n'+'\n'.join("\t%s: %s" % item for item in attrs.items())+'\n'

    def __str__(self):

        attrs = vars(self)
        return 'SavingsGoal('+', '.join("%s: %s" % item for item in attrs.items())+')'

    def update(self, goal: Dict = None) -> None:
        """Update a single savings goals data."""

        if goal is None:
            goal = self._helper.get_request(f"/account/{self._helper.account.account_uid}/savings-goals/{self.uid}")

        # self.uid = goal.get("savingsGoalUid")
        self.name = goal.get("name")

        target = goal.get("target", {})
        self.target_currency = target.get("currency", None)

        value = target.get("minorUnits", None)
        if value is not None:
            self.target_minor_units = value / 100.0

        total_saved = goal.get("totalSaved", {})
        self.total_saved_currency = total_saved.get("currency", None)

        value = total_saved.get("minorUnits", None)
        if value is not None:
            self.total_saved_minor_units = value / 100.0

    def deposit(self, deposit_minor_units: int) -> None:
        """Add funds to a savings goal."""

        url = f"/account/{self._helper.account.account_uid}/savings-goals/{self.uid}/add-money/{uuid4()}"
        json = {
            "amount": {
                "currency": self.total_saved_currency,
                "minorUnits": deposit_minor_units,
            }
        }

        self._helper.put_request(url, json)
        self.update()

    def withdraw(self, withdraw_minor_units: int) -> None:
        """Withdraw funds from a savings goal."""

        url = f"/account/{self._helper.account.account_uid}/savings-goals/{self.uid}/withdraw-money/{uuid4()}"
        json = {
            "amount": {
                "currency": self.total_saved_currency,
                "minorUnits": withdraw_minor_units,
            }
        }

        self._helper.put_request(url, json)
        self.update()

    def get_image(self, filename: str = None) -> None:
        """Download the photo associated with a Savings Goal."""

        if filename is None:
            filename = "{0}.png".format(self.name)

        json = self._helper.get_request(f"/account/{self._helper.account.account_uid}/savings-goals/{self.uid}/photo")

        base64_image = json["base64EncodedPhoto"]

        with open(filename, "wb") as file:
            file.write(b64decode(base64_image))

class StarlingAccount:
    """Representation of a Starling Account."""

    def __init__(self, helper) -> None:
        """Call to initialise a StarlingAccount object."""

        self._helper = helper

        json = helper.get_request("/accounts")

        # Assume there will be only 1 account as this is the case with personal access.
        account = json["accounts"][0]

        self.account_uid = account["accountUid"]
        self.default_category_uid = account["defaultCategory"]
        self.currency = account["currency"]
        self.created_at = account["createdAt"]

        json = helper.get_request(f"/accounts/{self.account_uid}/identifiers")

        self.account_identifier = json.get("accountIdentifier")
        self.bank_identifier = json.get("bankIdentifier")
        self.iban = json.get("iban")
        self.bic = json.get("bic")

        # Account Data
        # self.account_identifier = None
        # self.bank_identifier = None
        # self.iban = None
        # self.bic = None
        self.default_category = None

        # Balance Data
        self.cleared_balance = None
        self.effective_balance = None
        self.pending_transactions = None
        self.accepted_overdraft = None
        self.total_cleared_balance = None
        self.total_effective_balance = None

        # Savings Goals Data
        self.savings_goals = {}  # type: Dict[str, SavingsGoal]
        self.direct_debits = [] # type list
        self.standing_orders = [] # type list

        self.update_balance_data()
        self.update_savings_goal_data()

    # def __repr__(self):

    #         attrs = vars(self)
    #         return 'SavingsGoal:\n'+'\n'.join("\t%s: %s" % item for item in attrs.items())+'\n'

    def __str__(self):

        # attrs = vars(self)
        # return 'SavingsGoal('+', '.join("%s: %s" % item for item in attrs.items())+')'

        string = "StarlingAccount:\n"
        string += f'\taccount identifier={self.account_identifier}\n'
        string += f'\tbank identifier={self.bank_identifier}\n'
        string += f'\tbic={self.bic}\n'
        string += f'\tiban={self.iban}\n'
        string += f'\teffective balance={self.effective_balance:6.2f}\n'
        string += f'\tcleared balance={self.cleared_balance:6.2f}\n'
        string += f'\ttransactions={self.pending_transactions:6.2f}\n'
        string += f'\toverdraft={self.accepted_overdraft:6.2f}\n'
        string += f'\ttotal effective balance={self.total_effective_balance:6.2f}\n'
        string += f'\ttotal cleared balance={self.total_cleared_balance:6.2f}\n'

        return string

    def update_balance_data(self) -> None:
        """Get the latest balance information for the account."""

        helper = self._helper
        json = helper.get_request(f"/accounts/{self.account_uid}/balance")

        self.cleared_balance = json["clearedBalance"]["minorUnits"] / 100.0
        self.effective_balance = json["effectiveBalance"]["minorUnits"] / 100.0
        self.total_cleared_balance = json["totalClearedBalance"]["minorUnits"] / 100.0
        self.total_effective_balance = json["totalEffectiveBalance"]["minorUnits"] / 100.0
        self.pending_transactions = json["pendingTransactions"]["minorUnits"] / 100.0
        self.accepted_overdraft = json["acceptedOverdraft"]["minorUnits"] / 100.0

    def update_savings_goal_data(self) -> None:
        """Get the latest savings goal information for the account."""

        helper = self._helper
        json = helper.get_request(f"/account/{self.account_uid}/savings-goals")

        response_savings_goals = json.get("savingsGoalList", {})
        returned_uids = []

        # New / Update
        for goal in response_savings_goals:
            uid = goal.get("savingsGoalUid")
            returned_uids.append(uid)

            # Intiialise new _SavingsGoal object if new
            if uid not in self.savings_goals:
                self.savings_goals[uid] = SavingsGoal(helper, uid)

            self.savings_goals[uid].update(goal)

        # Forget about savings goals if the UID isn't returned by Starling
        for uid in list(self.savings_goals):
            if uid not in returned_uids:
                self.savings_goals.pop(uid)

    def update(self) -> None:

        if self._helper._update:
            self.update_balance_data()
            self.update_savings_goal_data()
            # self.show_direct_debits()
            # self.show_standing_orders()

    def show_direct_debits(self) -> None:
        """Get direct debits for the account."""

        json = self._helper.get_request("/direct-debit/mandates")

        # print(response["mandates"].__class__.__name__)
        # print(len(response["mandates"]))

        for el in json["mandates"]:
            dd = DirectDebit(el)
            # self.direct_debits.append(dd)
            print(dd.__repr__())

    def show_standing_orders(self) -> None:
        """Get standing orders for the account."""

        json = self._helper.get_request(f"/payments/local/account/{self.account_uid}/category/{self.default_category_uid}/standing-orders")

        for el in json["standingOrders"]:
            so = StandingOrder(self._helper, el)
            # so = StandingOrder(el, self._sandbox, self._auth_headers)
            # self.standing_orders.append(so)
            print(so.__repr__())

        # description=f"\n{so.currency}{so.amount} - {so.payee_name}\n{so.interval} {so.frequency}\n"
        # self.log(f'start_date={start_date} end_date={end_date} summary={summary} description={description}')
        # self.call_service('calendar/create_event', entity_id='calendar.starling', summary=summary, description=description, start_date=str(start_date), end_date=str(end_date))
