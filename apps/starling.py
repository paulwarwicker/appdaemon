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

# import asyncio
# import adbase

import inspect
from datetime import datetime, timedelta
# import pytz
# from requests import get, put
import requests  # pylint: disable=E0401
# import requests.adapters
# from requests import requests, adapters
import urllib3

BASE_URL = "https://api.starlingbank.com/api/v2"
BASE_URL_SANDBOX = "https://api-sandbox.starlingbank.com/api/v2"
# SPENDING_CATEGORIES = ['BIKE', 'BILLS_AND_SERVICES', 'BUCKET_LIST', 'CAR', 'CASH', 'CELEBRATION', 'CHARITY', 'CHILDREN', 'CLOTHES', 'COFFEE', 'DEBT_REPAYMENT', 'DIY', 'DRINKS', 'EATING_OUT', 'EDUCATION', 'EMERGENCY', 'ENTERTAINMENT', 'ESSENTIAL_SPEND', 'EXPENSES', 'FAMILY', 'FITNESS', 'FUEL', 'GAMBLING', 'GAMING', 'GARDEN', 'GENERAL', 'GIFTS', 'GROCERIES', 'HOBBY', 'HOLIDAYS', 'HOME', 'IMPULSE_BUY', 'INCOME', 'INSURANCE', 'INVESTMENTS', 'LIFESTYLE', 'MAINTENANCE_AND_REPAIRS', 'MEDICAL', 'MORTGAGE', 'NON_ESSENTIAL_SPEND', 'PAYMENTS', 'PERSONAL_CARE', 'PERSONAL_TRANSFERS', 'PETS', 'PROJECTS', 'RELATIONSHIPS', 'RENT', 'SAVING', 'SHOPPING', 'SUBSCRIPTIONS', 'TAKEAWAY', 'TAXI', 'TRANSPORT', 'TREATS', 'WEDDING', 'WELLBEING', 'NONE', 'REVENUE', 'OTHER_INCOME', 'CLIENT_REFUNDS', 'INVENTORY', 'STAFF', 'TRAVEL', 'WORKPLACE', 'REPAIRS_AND_MAINTENANCE', 'ADMIN', 'MARKETING', 'BUSINESS_ENTERTAINMENT', 'INTEREST_PAYMENTS', 'BANK_CHARGES', 'OTHER', 'FOOD_AND_DRINK', 'EQUIPMENT', 'PROFESSIONAL_SERVICES', 'PHONE_AND_INTERNET', 'VEHICLES', 'DIRECTORS_WAGES', 'VAT', 'CORPORATION_TAX', 'SELF_ASSESSMENT_TAX', 'INVESTMENT_CAPITAL', 'TRANSFERS', 'LOAN_PRINCIPAL', 'PERSONAL', 'DIVIDENDS']


import appdaemon.plugins.hass.hassapi as hass  # pylint: disable=E0401 disable=E0611
import appdaemon.adbase as ad  # pylint: disable=E0401,E0611

class Starling(hass.Hass):
    """This is the documentation for Automation"""

    starling = None

# -------------------------------------------------------------------------------------------------

    def initialize(self):
        """."""

        self.log('-'*72)

        self.listen_event(self.delete_calendar_events, 'delete_calendar_events')
        self.listen_event(self.add_calendar_events, 'add_calendar_events')
        self.listen_event(self.check_feed, 'check_feed')
        self.listen_event(self.check_starling_balance, 'check_starling_balance')
        self.listen_event(self.status_event, 'status')

        runtime = datetime(2024, 1, 1, 0, 0, 0)
        self.run_hourly(self.add_starling_calendar_events, runtime)

        self.starling = StarlingHelper('eyJhbGciOiJQUzI1NiIsInppcCI6IkdaSVAifQ.H4sIAAAAAAAA_31Ty5KjMAz8lSnOoykgJDbc5rY_sB8gZDlxDdiUbbI7tbX_vkqAPHaq5oYtd0vdLf4ULqWiK3BybyljHJw_9ug_3iiMxWuR5l6K9aGs6z1ZUFb30FBJoNvSgO7bslWklLE7ecy_p6JrtNqrtq4O6rVwmIuuUnVZVXp_uUCiMPv8IwyG409nhLs5NKrfG4RDbQiaWhrgYW-gVcra3U41VauFO4cP9gtC1VyXfduDLncamhJlmlLVgPum4UppxdgLQhS9E3FKd5S2RFD1poVG4Q6w1ATMLWrTtpZ0eRFMYWJ5PuEnM7gRj9xFRvOCOSOdRvZ5OSc8i1UJjgEHyBF9shzXEp3YzAMbEJY7YqG8PkXKLviVeM6nEF0SNnDeuLMzMw5LLTKxm3L3K7rMLyNnNJixIynK-QvV4wUbl19G9ALgzvDAApCApYH0CVH832jQmCg2LYjrkMsnzSmHcRNFwVsXR7yQQ7BgZ2_SUrrNtTDEYN2weXe9evRqm2VdBThddwHy58QPNt0mfkReyzyiG1ZazlkazdNq5DOjiM2r3e5uUY8DetoyXZUvAjEaEJU5ho3_wnDJDyidn3rcEevMT5ofo1vJ71STsd8t0JbJfduW7BdXvgC392nCm6jVBmcE7azbAhQGGAJtPv7nlsdxxW87s839uDFPyMGlb_-FJcLi7z8CO9KdYwQAAA.UHuebVjVW021Ad_7N__22UwU_6nt_fsXazoKRQEUilYYQVW29ryGzMRW5Gzuhwwb4_ZnmJ02NN3KgKEtQnyxfs1w4IrozXfCypdzISFCxTjbwtxfYRdqgmkpuRpDrFlgWhnoZpXirUY9KKDeg8F7w0g74TUOOT8CCgo-Pr67wW6Ru5U77Gb876295azO_kz9sdZMCe5pplaKhpVySi-LOUe5-2IjH1B6Bt6AW7UcUIJNAMAAyzIInEHXB5HSs6FMcHVphOaIIsj-sSX0MdJ6_flNCJoXZf_bXWXsGMtCBgtdo5McLmcM0R2s8o_BSUy4W-w1umod6LLRB5CMqVBeQHgZmy_-By3ct5AIqZF9aSneEQgUKIsBEuZL4nC7Ohqz9-GRqBmOS24Yth9LqaI7dfQT2uFxLd66WjjDEorCdMgIHntwRfpkQSxWzRgWoVbH12vKaXCiZndKuSLShCD3EdMx1uwPpEx3Ih_r_pJGw6zMAxDRz2rnkVltKhR411LnQyV6-KNrsESXvSrbU5NXGUlxSbT7-bkyHz_FVXwcG4rqAUEXxdLSFo5eRvQ7MJ8jwX-BH8Sn1Q8fiPOgycJHV8qkUoOqgsfh6kA6xmY6Q5oVaZOPh3LOA5ilvWP4oXOMZEr6-j62ApFgfpA0WFQSVXChm5mgKnT2R7otEooCWYc', update=True)

        self.fire_event('refresh_calendar_events')
        self.run_in_thread(self.add_starling_calendar_events, 0)
        self.call_service("announcer/announce", entity_id='media_player.study', message='Starling initialised')

# -------------------------------------------------------------------------------------------------

    def show_starling_account(self, kwargs={}):

        account = self.starling.account()
        account.update()

        print(account)
        account.show_standing_orders()
        account.show_direct_debits()

        # goal = helper.find_savings_goal('Tax')

# -------------------------------------------------------------------------------------------------

    def add_starling_calendar_events(self, kwargs={}):

        # self.log_function_name()
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

        # self.log_function_name(False)

# -------------------------------------------------------------------------------------------------

    def check_starling_balance(self, event, data, kwargs={}):

        self._check_starling_balance()

# -------------------------------------------------------------------------------------------------

    def _check_starling_balance(self, kwargs={}):

        helper = self.starling
        account = helper.account()
        account_uid = account.account_uid
        default_category_uid = account.default_category_uid

        state = self.get_state('sensor.starling_events', attribute='scheduled_events')
        # self.log(state)

        now=(datetime.now() - timedelta(days=4)).strftime("%Y-%m-%dT%H:%M:%SZ")
        data = helper.get_request(f"/feed/account/{account_uid}/category/{default_category_uid}?changesSince={now}")
        # print(data)

        date_format = '%Y-%m-%dT%H:%M:%S.%fZ'

        for el in data["feedItems"]:
            if el['status'] == 'SETTLED':
                continue
            print(f'{el}\n\n')
            feed_uid = el['feedItemUid']
            category_uid = el['categoryUid']
            amount = el['amount']
            currency = amount['currency']
            value = amount['minorUnits'] / 100
            source_amount = el['sourceAmount']
            direction = el['direction']
            updated_at = el['updatedAt'] # '2024-07-18T23:30:10.217Z',
            transaction_time = el['transactionTime']
            source = el['source']
            status = el['status']
            to = el['counterPartyName']
            reference = el['reference']
            country = el['country']
            spending_category = el['spendingCategory']

            print(f'to={to}, reference={reference}, amount={amount}, currency={currency}, value={value}, direction={direction}, transaction_time={transaction_time}, updated_at={updated_at}')
            print(f'feed_uid={feed_uid}, category_uid={category_uid}, status={status}, spending_category={spending_category}')

            # date_obj = datetime.strptime(transaction_time, date_format)
            date_obj = datetime.fromisoformat(transaction_time)
            print(date_obj)


            # Calling the now() function to get
            # current date and time
            date_time = datetime.now()

            # Calling the utcoffset() function
            # over the above initialized datetime
            print(date_time.utcoffset())
            # 'sourceAmount' 'counterPartyType'             'counterPartyUid'             'counterPartySubEntityUid'             'hasAttachment'             'hasReceipt'             'batchPaymentDetails'



# {'feedItems': [{'feedItemUid': 'c008be25-4484-4fd7-9818-73d4603cf3ff', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 6286}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 6286}, 'direction': 'OUT', 'updatedAt': '2024-07-18T23:30:10.217Z', 'transactionTime': '2024-07-21T23:30:00.000Z', 'source': 'DIRECT_DEBIT', 'status': 'UPCOMING', 'counterPartyType': 'MERCHANT', 'counterPartyUid': 'da587da2-390e-49b0-8f34-690430a2ac27', 'counterPartyName': 'Creation', 'counterPartySubEntityUid': '92c4714c-9625-4a17-b1f4-d932bdf456cb', 'reference': 'Y9484673/R086501', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'c2b7daff-f3d5-43f3-9e92-f4d3c9aa915e', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 30000}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 30000}, 'direction': 'OUT', 'updatedAt': '2024-07-18T23:19:07.974Z', 'transactionTime': '2024-07-18T23:19:06.957Z', 'settlementTime': '2024-07-18T23:19:07.917Z', 'source': 'FASTER_PAYMENTS_OUT', 'status': 'SETTLED', 'transactingApplicationUserUid': '260225cf-7f8b-4c0c-890d-8b9097c77df3', 'counterPartyType': 'PAYEE', 'counterPartyUid': '44f74be6-ee8f-4590-8617-b1007dfe4854', 'counterPartyName': 'Paul Warwicker', 'counterPartySubEntityUid': '44f7176a-badc-4ba1-b1fd-f8436c0eed86', 'counterPartySubEntityName': 'Account', 'counterPartySubEntityIdentifier': '040625', 'counterPartySubEntitySubIdentifier': '03296368', 'reference': '6699a1c982d4374555', 'country': 'GB', 'spendingCategory': 'SAVING', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'bd151308-877c-42e6-bdeb-488022ad6381', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 15898}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 15898}, 'direction': 'IN', 'updatedAt': '2024-07-18T23:08:27.698Z', 'transactionTime': '2024-07-18T23:01:00.000Z', 'settlementTime': '2024-07-18T23:06:31.255Z', 'source': 'DIRECT_CREDIT', 'status': 'SETTLED', 'counterPartyType': 'MERCHANT', 'counterPartyUid': '21ef8556-071e-477d-b8a4-2c338fcf6cbd', 'counterPartyName': 'Seccl Custody Limi', 'counterPartySubEntityUid': '2cd97cf6-f733-456a-beb2-285b75851df5', 'reference': 'CHIP1-02188B5', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'bd15a3ea-2022-4720-9f23-435b3e5e849f', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 12827}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 12827}, 'direction': 'IN', 'updatedAt': '2024-07-18T23:11:16.148Z', 'transactionTime': '2024-07-18T23:01:00.000Z', 'settlementTime': '2024-07-18T23:08:47.441Z', 'source': 'DIRECT_CREDIT', 'status': 'SETTLED', 'counterPartyType': 'MERCHANT', 'counterPartyUid': '21ef8556-071e-477d-b8a4-2c338fcf6cbd', 'counterPartyName': 'Seccl Custody Limi', 'counterPartySubEntityUid': '2cd97cf6-f733-456a-beb2-285b75851df5', 'reference': 'CHIP1-02188B5', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}]}{'feedItems': [{'feedItemUid': 'c008be25-4484-4fd7-9818-73d4603cf3ff', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 6286}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 6286}, 'direction': 'OUT', 'updatedAt': '2024-07-18T23:30:10.217Z', 'transactionTime': '2024-07-21T23:30:00.000Z', 'source': 'DIRECT_DEBIT', 'status': 'UPCOMING', 'counterPartyType': 'MERCHANT', 'counterPartyUid': 'da587da2-390e-49b0-8f34-690430a2ac27', 'counterPartyName': 'Creation', 'counterPartySubEntityUid': '92c4714c-9625-4a17-b1f4-d932bdf456cb', 'reference': 'Y9484673/R086501', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'c2b7daff-f3d5-43f3-9e92-f4d3c9aa915e', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 30000}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 30000}, 'direction': 'OUT', 'updatedAt': '2024-07-18T23:19:07.974Z', 'transactionTime': '2024-07-18T23:19:06.957Z', 'settlementTime': '2024-07-18T23:19:07.917Z', 'source': 'FASTER_PAYMENTS_OUT', 'status': 'SETTLED', 'transactingApplicationUserUid': '260225cf-7f8b-4c0c-890d-8b9097c77df3', 'counterPartyType': 'PAYEE', 'counterPartyUid': '44f74be6-ee8f-4590-8617-b1007dfe4854', 'counterPartyName': 'Paul Warwicker', 'counterPartySubEntityUid': '44f7176a-badc-4ba1-b1fd-f8436c0eed86', 'counterPartySubEntityName': 'Account', 'counterPartySubEntityIdentifier': '040625', 'counterPartySubEntitySubIdentifier': '03296368', 'reference': '6699a1c982d4374555', 'country': 'GB', 'spendingCategory': 'SAVING', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'bd151308-877c-42e6-bdeb-488022ad6381', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 15898}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 15898}, 'direction': 'IN', 'updatedAt': '2024-07-18T23:08:27.698Z', 'transactionTime': '2024-07-18T23:01:00.000Z', 'settlementTime': '2024-07-18T23:06:31.255Z', 'source': 'DIRECT_CREDIT', 'status': 'SETTLED', 'counterPartyType': 'MERCHANT', 'counterPartyUid': '21ef8556-071e-477d-b8a4-2c338fcf6cbd', 'counterPartyName': 'Seccl Custody Limi', 'counterPartySubEntityUid': '2cd97cf6-f733-456a-beb2-285b75851df5', 'reference': 'CHIP1-02188B5', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}, {'feedItemUid': 'bd15a3ea-2022-4720-9f23-435b3e5e849f', 'categoryUid': 'bc269593-0740-4062-afd0-75212f43c025', 'amount': {'currency': 'GBP', 'minorUnits': 12827}, 'sourceAmount': {'currency': 'GBP', 'minorUnits': 12827}, 'direction': 'IN', 'updatedAt': '2024-07-18T23:11:16.148Z', 'transactionTime': '2024-07-18T23:01:00.000Z', 'settlementTime': '2024-07-18T23:08:47.441Z', 'source': 'DIRECT_CREDIT', 'status': 'SETTLED', 'counterPartyType': 'MERCHANT', 'counterPartyUid': '21ef8556-071e-477d-b8a4-2c338fcf6cbd', 'counterPartyName': 'Seccl Custody Limi', 'counterPartySubEntityUid': '2cd97cf6-f733-456a-beb2-285b75851df5', 'reference': 'CHIP1-02188B5', 'country': 'GB', 'spendingCategory': 'PAYMENTS', 'hasAttachment': False, 'hasReceipt': False, 'batchPaymentDetails': None}]}
# https://api.starlingbank.com/api       /v2/feed/account/d9c51e1d-4e86-474d-b9a8-e56eef13df37/category/bc269593-0740-4062-afd0-75212f43c025?changesSince=2024-07-18T00%3A00%3A00Z
# https://api.starlingbank.com/api/v2/api/v2/feed/account/d9c51e1d-4e86-474d-b9a8-e56eef13df37/category/bc269593-0740-4062-afd0-75212f43c025?changesSince=2024-07-19T01:45:25Z
# https://api.starlingbank.com/api/v2/v2/api/api/v2/feed/account/d9c51e1d-4e86-474d-b9a8-e56eef13df37/category/bc269593-0740-4062-afd0-75212f43c025?changesSince=2024-07-19T01:51:43Z
        # data = helper.get_request("/direct-debit/mandates")

        # for el in data["mandates"]:
        #     add = True
        #     dd = DirectDebit(el)
        #     next_date = dd.next_date
        #     last_date = dd.last_date
        #     summary = f'{dd.originator_name} - {dd.reference}'

        #     if (dd.cancelled is not None) or (next_date is None and last_date is None):
        #         continue

        #     for el in state["calendar.starling"]["events"]:
        #         match=next_date == el["start"] and summary == el["summary"]
        #         # self.log(f'dd {match} next_date={next_date} last_date={last_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}', level='WARNING')
        #         if match:
        #             add = False
        #             self.log(f'\t\tSkip previously entered DD next_date={next_date} summary={summary}', level='WARNING')
        #             break

        #         match = last_date == el["start"] and summary == el["summary"]
        #         # self.log(f'dd {match} next_date={next_date} last_date={last_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}', level='WARNING')
        #         if match:
        #             add = False
        #             self.log(f'\t\tSkip previously entered DD last_date={last_date} summary={summary}', level='WARNING')
        #             break

        #     if add:
        #         self.add_starling_dd_calendar_event(dd)


        # data = helper.get_request(f"/payments/local/account/{account_uid}/category/{default_category_uid}/standing-orders")

        # for el in data["standingOrders"]:
        #     add = True
        #     so = StandingOrder(helper, el)

        #     next_date = so.next_date
        #     summary = f'{so.payee_name} - {so.reference}'

        #     if (so.cancelled_at is not None) or (next_date is None):
        #         continue

        #     for el in state["calendar.starling"]["events"]:
        #         match=next_date == el["start"] and summary == el["summary"]
        #         # print(f'so {match} next_date={next_date} summary={summary}  -  start={el["start"]} summary={el["summary"]}')
        #         if match:
        #             add = False
        #             self.log(f'\t\tSkip previously entered SO next_date={next_date} summary={summary}', level='WARNING')
        #             break

        #     if add:
        #         self.add_starling_so_calendar_event(so)

# -------------------------------------------------------------------------------------------------

    def check_feed(self, event, data, kwargs={}):

        self._check_feed()

# -------------------------------------------------------------------------------------------------

    def _check_feed(self):

        self.log_function_name()
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

    def log_function_name(self, start=True):

        name = inspect.currentframe().f_back.f_code.co_name

        self.log(('\t>>> begin' if start else '\t<<< end') + f' {name}', level='INFO')

# -------------------------------------------------------------------------------------------------

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

    def status_event(self, event, data, kwargs={}):

        status = f'\n\n'

        self.log(f'{status}')

        # self.show_starling_account()

        self.set_state('input_boolean.status', state='off')

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

    def __init__(self, dd) -> None:

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

    def __init__(self, helper, so) -> None:

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

    def update(self, goal=None) -> None:
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
