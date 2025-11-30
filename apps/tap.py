# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing

import math

from datetime import datetime,timezone

from typing import TYPE_CHECKING, cast

import constants as const
import automationlib as _helpers  # type: ignore

from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

if TYPE_CHECKING:
    from automationlib import AutomationLib  # type: ignore

class Tap(Hass):
    """Documentation for Tap"""

    lib: "AutomationLib" = _helpers  # type: ignore

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        # runtime: get the running AutomationLib app instance (do not instantiate directly)
        self.lib = cast("AutomationLib", self.get_app('automationlib'))
        if self.lib is None:
            # defensive fallback to module if app not present (optional)
            self.lib = _helpers  # type: ignore

        self.register_service('tap/water_for', self.water_garden_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.water_garden_event, 'water_garden')
        self.listen_event(self.water_garden_for_action, "ios.action_fired", actionName='Water15', minutes=15)

        self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='on', tap_state='on')
        self.listen_state(self.set_tap_timestamp, 'switch.garden_tap', new='off', tap_state='off')

        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_1', new='on', minutes=1)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_1', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_15', new='on', minutes=15)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_15', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_20', new='on', minutes=20)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_20', new='off')
        self.listen_state(self.water_garden_for, 'input_boolean.water_garden_30', new='on', minutes=30)
        self.listen_state(self.water_garden_stop, 'input_boolean.water_garden_30', new='off')

        self.run_daily(self.water_garden_daily, 'sunset - 01:00:00')

        runtime = datetime(2024, 1, 1)
        self.run_minutely(self.check_garden_tap, runtime)

        self.set_log_level('DEBUG' if self.lib.get_debug() else 'INFO')
        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def terminate(self) -> None:
        """terminate"""

        state = self.get_state('switch.garden_tap')

        if state == 'on':
            self.call_service('switch/turn_off', entity_id='switch.garden_tap')
            self.lib.delay(5)
            state2 = self.get_state('switch.garden_tap')
            self.log(f'\tGarden tap was {state} now {state2}', level='WARNING')

# -----------------------------------------------------------------------------------

    def check_garden_tap(self, kwargs) -> None:
        """check garden tap state"""

        state = self.get_state('switch.garden_tap')

        if state == 'on':
            self.log(f'\tGarden tap is {state}', level='WARNING')
            ts = self.call_service('timestamp/get', name='tap')
            if ts is not None:
                seconds = (datetime.now() - ts).seconds
                n = math.ceil(seconds / 60)
                diff1,diff2 = divmod(seconds, 60)
                if diff1 > 0 and ((diff1 + 1) % 10) == 0:
                    self.broadcast(f'The garden tap has been on for {n} minutes')
            else:
                self.log('\tFailed to get tap timestamp', level='ERROR')

    def check_garden_tap2(self, kwargs) -> None:
        """Check garden tap state and broadcast every 10 minutes while on."""

        state = self.get_state("switch.garden_tap")

        if state != "on":
            return

        self.log("\tGarden tap is on", level="WARNING")

        try:
            ts = self.call_service("timestamp/get", name="tap")
        except (TypeError, ValueError) as e:
            self.log(f"\tFailed to call timestamp/get: {e}", level="ERROR")
            return

        if ts is None:
            self.log("\tFailed to get tap timestamp (None returned)", level="ERROR")
            return

        # Normalize ts ? aware datetime
        now = self.datetime()  # AppDaemon tz-aware "now"
        ts_dt = None
        try:
            # Accept datetime directly
            if hasattr(ts, "tzinfo"):
                ts_dt = ts
            # ISO8601 string
            elif isinstance(ts, str):
                # Home Assistant often uses UTC ISO strings
                ts_dt = self.parse_datetime(ts)  # AppDaemon helper parses ISO
            # Unix epoch seconds (int/float)
            elif isinstance(ts, (int, float)):
                ts_dt = datetime.fromtimestamp(ts, tz=timezone.utc)
            else:
                raise TypeError(f"Unsupported timestamp type: {type(ts)}")
        except (TypeError, ValueError, AttributeError) as e:
            self.log(f"\tCould not parse timestamp '{ts}': {e}", level="ERROR")
            return

        # Compute elapsed safely
        elapsed = now - ts_dt
        seconds = int(elapsed.total_seconds())
        if seconds < 0:
            # Clock skew or bad ts; bail
            self.log(f"\tTimestamp is in the future: now={now}, ts={ts_dt}", level="ERROR")
            return

        minutes = seconds // 60
        # Announce every 10 minutes (10, 20, 30, ?), but not at 0
        if minutes > 0 and minutes % 10 == 0:
            n = minutes if seconds % 60 == 0 else (minutes + 1)
            # Round up if we're between minutes
            self.broadcast(f"The garden tap has been on for {n} minutes")

# -----------------------------------------------------------------------------------

    def water_garden_service(self, namespace, domain, service, kwargs) -> None:
        """open the garage"""

        minutes = kwargs.get('minutes', None)

        if minutes:
            self.water_garden_for('','','','', {'minutes': minutes})

# -----------------------------------------------------------------------------------

    def water_garden_for(self, entity, attribute, old, new, kwargs) -> None:
        """water garden for <minutes> minutes. different switches will set 1, 15, 20, 30 minutes"""

        minutes = kwargs['minutes']

        if minutes:
            self.tap_on(minutes=minutes)
        else:
            self.error('no timer set')

# -----------------------------------------------------------------------------------

    def water_garden_for_action(self, event, data, kwargs) -> None:
        """water garden for 15 minutes as an iOS action"""

        minutes = kwargs['minutes']

        self.log(f'\twater_garden_for_action for {minutes:d} minutes')
        self.water_garden_for_n_minutes({minutes: minutes})  # was minutes=minutes

# -----------------------------------------------------------------------------------

    def water_garden_for_n_minutes(self, kwargs) -> None:
        """water garden for <minutes> minutes"""

        self.water_garden_for('', '', '', '', kwargs)

# -----------------------------------------------------------------------------------

    def water_garden_stop(self, entity, attribute, old, new, kwargs) -> None:
        """stop watering garden"""

        self.tap_off({}) # TODO: stop running thread

# -----------------------------------------------------------------------------------

    def broadcast(self, message) -> None:
        """broadcast message using announcer"""

        self.call_service('announcer/broadcast', message=message)

# -----------------------------------------------------------------------------------

    def water_garden_daily(self, kwargs) -> None:
        """water garden daily"""

        if self.lib.is_summer() and self.lib.no_rain():
            kwargs = {**kwargs, 'minutes': const.DAILY_WATERING_MINUTES}
            self.water_garden_for_n_minutes(kwargs)
            self.broadcast(f'Watering garden for {const.DAILY_WATERING_MINUTES} minutes')

# -----------------------------------------------------------------------------------

    def tap_on(self, **kwargs) -> None:
        """turn garden tap on for <minutes> minutes"""

        minutes = kwargs['minutes']

        if minutes:
            self.log(f'\ttap_on for {minutes:d} minutes', level='INFO')
            self.call_service('switch/turn_on', entity_id='switch.garden_tap')
            self.call_service('timestamp/set', name='tap')
            seconds = self.lib.interval(minutes=minutes)
            self.log(f'\tstart timer for {seconds:d}s', level='DEBUG')
            self.run_in(self.tap_off, seconds)

# -----------------------------------------------------------------------------------

    def tap_off(self, kwargs) -> None:
        """turn garden tap off"""

        self.call_service('switch/turn_off', entity_id='switch.garden_tap')
        self.broadcast('The garden tap is now off')
        self.call_service('timestamp/set', name='tap', value=None)
        self.set_state('input_boolean.water_garden_1', state='off')
        self.set_state('input_boolean.water_garden_15', state='off')
        self.set_state('input_boolean.water_garden_20', state='off')
        self.set_state('input_boolean.water_garden_30', state='off')

# -----------------------------------------------------------------------------------

    def water_garden_event(self, event, data, kwargs) -> None:

        minutes = data['minutes']
        self.water_garden_for_n_minutes({'minutes': minutes})
        self.broadcast(f'Watering garden for {minutes} minutes')

# -----------------------------------------------------------------------------------

    def status_event(self, event, data, kwargs) -> None:

        self.status('','','','',{})

# -----------------------------------------------------------------------------------

    def status(self, entity, attribute, old, new, kwargs) -> None:

        (_, week, _) = self.lib.now().isocalendar()
        state = 17 <= week <= 37

        status = f'\n\n\tweek={week}\n\tstate={state}\n'

        self.log(f'{status}')

        self.set_state('input_boolean.status', state='off')

# -----------------------------------------------------------------------------------

    def set_tap_timestamp(self, entity, attribute, old, new, kwargs) -> None:
        """set tap timestamp"""

        state = kwargs['tap_state'] == 'on'

        if state:
            self.call_service('timestamp/set', name='tap')
            self.log('Set tap timestamp', level='INFO')
        else:
            self.call_service('timestamp/set', name='tap', value=None)
            self.log('Cleared tap timestamp', level='INFO')

# -----------------------------------------------------------------------------------
