from datetime import datetime, timedelta
from pathlib import Path

import math
import json # keep for debug
import yaml
import aiohttp  # type: ignore # pylint: disable=E0401 disable=E0611
from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

from automationlib import AutomationLib  # pylint: disable=E0401 disable=E0611
class Weather(Hass):
    """Weather app using tomorrow.io data"""

    request_kwargs = {}
    lib = None

# -----------------------------------------------------------------------------------

    def initialize(self):

        self.lib = AutomationLib(self)

        path = Path(f'{self.AD.config_dir}/secrets.yaml')
        path = path if path.is_file() else Path('/homeassistant/secrets.yaml') # HAOS
        with path.open('r', encoding='utf8') as f:
            apikey = yaml.safe_load(f)['tomorrow_api_key']
        self.log('API key loaded', level="DEBUG")

        lat = self.AD.sched.location.latitude
        lon = self.AD.sched.location.longitude

        self.request_kwargs = {
            'url': 'https://api.tomorrow.io/v4/weather/forecast',
            'params': {
                'apikey': apikey,
                'location': f'{lat},{lon}',
                'timesteps': '1h',
                'units': 'metric',
            },
        }

        if loc := self.args.get('location'):
            self.request_kwargs['params']['location'] = loc
            self.log(f'Updated location to {loc}', level='DEBUG')

        self.run_daily(self.frost_warning, "sunset + 00:00:00")
        self.run_daily(self.frost_warning, "sunset + 01:00:00")

        interval = timedelta(minutes=10)
        # runtime = datetime(2024, 1, 1, 0, 0, 0)

        self.run_every(self.get_weather, 'now', interval.total_seconds()) # FIXME: would be nice if on 10 minutes exactly
        self.log(f'Getting weather every {interval}', level='DEBUG')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)
        self.log('initialised', level='WARNING')

# -----------------------------------------------------------------------------------

    async def get_weather(self, *args):
        """get weather data"""

        async with aiohttp.ClientSession() as session:
            async with session.get(**self.request_kwargs) as resp:
                if resp.status == 200:
                    # self.log('Got weather async', level='DEBUG')
                    json_data = await resp.json()
                    await self.publish_current_temperature(json_data)
                    await self.publish_low_forecast(json_data)
                    await self.publish_rain_forecast(json_data)
                elif resp.status == 429:
                    self.log('Rate limited when getting weather', level='WARNING')
                else:
                    self.log(f'Error getting weather async: {resp.status}', level='ERROR')

# -----------------------------------------------------------------------------------

    async def publish_current_temperature(self, json_data):
        """Publish current temperataure"""

        temp = json_data['timelines']['hourly'][1]['values']['temperature']
        await self.set_state(
            'sensor.weather_tomorrowio_temperature',
            state=round(temp, 1),   # one decimal place
            device_class='temperature',
        )

# -----------------------------------------------------------------------------------

    async def publish_low_forecast(self, json_data):
        """Publish forecasted low over next 12 hours"""

        low_temp12 = float('inf')
        low_temp24 = float('inf')
        low_dt12 = None
        low_dt24 = None
        count = 0

        for el in json_data['timelines']['hourly']:
            count += 1
            dt = self.convert_zulu(el['time'])
            # only consider future sample times
            if dt < datetime.now():
                continue
            temp = el['values']['temperature']
            # print(f'{low_temp} {low_dt} {dt} {temp}')
            if temp < low_temp12 and count <= 12:
                low_temp12 = temp
                low_dt12 = dt
            if temp < low_temp24:
                low_temp24 = temp
                low_dt24 = dt
            if count == 24:
                break

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_low_12h',
            state=round(low_temp12,1),  # one decimal place
            device_class='temperature',
        )

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_low_24h',
            state=round(low_temp24,1),  # one decimal place
            device_class='temperature',
        )

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_low_datetime_12h',
            state=low_dt12,
            device_class='datetime',
        )

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_low_datetime_24h',
            state=low_dt24,
            device_class='datetime',
        )

# -----------------------------------------------------------------------------------

    async def publish_rain_forecast(self, json_data):
        """Publish forecasted rain outlook"""

        # print(json.dumps(json_data, indent=2))

        index = 0
        data = {}
        data[0] = json_data['timelines']['hourly'][index] # previous/current hour
        data[1] = json_data['timelines']['hourly'][index + 1] # next hour
        data[2] = json_data['timelines']['hourly'][index + 2] # hour after
        data[3] = json_data['timelines']['hourly'][index + 3] # hour after

        if self.lib.get_verbose_debug():
            print(json.dumps(data[0], indent=2))
            print(json.dumps(data[1], indent=2))
            print(json.dumps(data[2], indent=2))
            print(json.dumps(data[3], indent=2))

        code = data[0]['values']['weatherCode']
        cum_prob_1h = math.ceil((data[0]['values']['precipitationProbability'] + data[1]['values']['precipitationProbability']) / 2)
        cum_prob_3h = math.ceil((data[0]['values']['precipitationProbability'] + data[1]['values']['precipitationProbability'] +
                                 data[2]['values']['precipitationProbability'] + data[3]['values']['precipitationProbability'] ) / 4)

        self.log(f'\tprobability of rain1h={cum_prob_1h}, rain3h={cum_prob_3h}', level='DEBUG')

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_rain_probability_1h',
            state=cum_prob_1h,
            device_class='probability',
        )

        if cum_prob_1h >= 5:
            pct = math.floor(cum_prob_1h)
            if not code in (4000, 4001, 4200, 4201): # if not raining - announce
                self.call_service('announcer/announce', entity_id='media_player.study', message=f"There is a {pct} percent probability of rain in the next hour")

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_rain_probability_3h',
            state=math.floor(cum_prob_3h),
            device_class='probability',
        )

# -----------------------------------------------------------------------------------

    def convert_zulu(self, zulu) -> datetime:

        """Convert a Zulu based timestring to datetime"""
        utc_dt = zulu.replace("Z","UTC")
        return datetime.strptime(utc_dt, "%Y-%m-%dT%H:%M:%S%Z")

# -----------------------------------------------------------------------------------

    def frost_warning(self, kwargs) -> bool:

        testing = self.get_state('input_boolean.testing') == 'on'
        stemp = self.get_state(entity_id='sensor.weather_tomorrowio_forecast_low_12h')
        temp = float(stemp)
        warning = temp <= 3.0

        self.log(f'\tforecast low is {temp}', level='DEBUG')

        if warning or testing:
            self.log(f'\tfrost warning ({temp})', level='WARNING')
            self.call_service('announcer/broadcast', message='There is a chance of frost overnight')

        return warning

# -----------------------------------------------------------------------------------
