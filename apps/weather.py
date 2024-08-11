from datetime import datetime, timedelta
from pathlib import Path

import yaml
import json # keep for debug
import math
import aiohttp  # pylint: disable=E0401 disable=E0611
from appdaemon.plugins.hass.hassapi import Hass  # pylint: disable=E0401 disable=E0611

class Weather(Hass):
    """Weather app using tomorrow.io data"""
    def initialize(self):

        self.log('-'*72)

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

        interval = timedelta(minutes=10)
        self.run_every(self.get_weather_async, 'now', interval.total_seconds())
        self.log(f'Getting weather every {interval}')

        self.call_service('announcer/initialised', name=self.name.capitalize(), announce=False)

    async def get_weather_async(self, *args):
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

    async def publish_current_temperature(self, json_data):
        temp = json_data['timelines']['hourly'][1]['values']['temperature']
        await self.set_state(
            'sensor.weather_tomorrowio_temperature',
            state=round(temp, 1),   # one decimal place
            device_class='temperature',
        )

    async def publish_low_forecast(self, json_data):
        """Publish forecasted low over next 12 hours"""
        low_temp12 = float('inf')
        low_temp24 = float('inf')
        low_dt12 = None
        low_dt24 = None
        count = 1

        for el in json_data['timelines']['hourly']:
            # print(json.dumps(el, indent=2))
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
            count += 1

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

    async def publish_rain_forecast(self, json_data):
        """Publish forecasted rain outlook"""

        n = -2
        count = 0
        n_samples = 3
        cum_prob_3h = 0
        cum_prob_1h = json_data['timelines']['hourly'][3]['values']['precipitationProbability']

        for el in json_data['timelines']['hourly']:
            if n < 0:
                continue  # we need to skip two samples
            cum_prob_3h += el['values']['precipitationProbability']
            if count == n_samples:
                break
            count += 1

        cum_prob_3h /= n_samples

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_rain_probability_1h',
            state=cum_prob_1h,
            device_class='probability',
        )

        if cum_prob_1h >= 20:
            pct = math.floor(cum_prob_1h)
            self.call_service('announcer/announce', entity_id='media_player.study', message=f"There is a {pct} percent probability of rain in the next hour")

        await self.set_state(
            'sensor.weather_tomorrowio_forecast_rain_probability_3h',
            state=math.floor(cum_prob_3h),
            device_class='probability',
        )

    def convert_zulu(self, zulu) -> datetime:
        """Convert a Zulu based timestring to datetime"""
        utc_dt = zulu.replace("Z","UTC")
        return datetime.strptime(utc_dt, "%Y-%m-%dT%H:%M:%S%Z")
