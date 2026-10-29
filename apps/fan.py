# -*- coding: utf-8 -*-

# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.run_in
# https://appdaemon.readthedocs.io/en/latest/AD_API_REFERENCE.html#appdaemon.adapi.ADAPI.get_state

# https://nickwhyte.com/appdaemon-testing
# https://github.com/nickw444/appdaemon-testing


# from typing import TYPE_CHECKING, cast

import constants as const # pylint: disable=unused-import

# from hassapi import Hass  # type: ignore # pylint: disable=E0401 disable=E0611

from automationbase import AutomationBase

class Fan(AutomationBase):
    """Documentation for Fan"""

    DEFAULT_TIMEOUT = 2*60

# -----------------------------------------------------------------------------------

    def initialize(self) -> None:
        """initialise"""

        super().initialize()

        self.register_service('fan/fan_on', self.fan_on_service)
        self.register_service('fan/fan_off', self.fan_off_service)
        self.register_service('fan/light_on', self.light_on_service)
        self.register_service('fan/light_off', self.light_off_service)
        self.register_service('fan/study_purifier_on', self.study_purifier_on_service)
        self.register_service('fan/study_purifier_off', self.study_purifier_off_service)
        self.register_service('fan/bedroom_purifier_on', self.bedroom_purifier_on_service)
        self.register_service('fan/bedroom_purifier_off', self.bedroom_purifier_off_service)

        self.listen_event(self.status_event, 'status')
        self.listen_event(self.study_purifier_on_event, 'study_purifier_on')
        self.listen_event(self.study_purifier_off_event, 'study_purifier_off')
        self.listen_event(self.bedroom_purifier_on_event, 'bedroom_purifier_on')
        self.listen_event(self.bedroom_purifier_off_event, 'bedroom_purifier_off')

        self.set_state('input_boolean.actual_fan_low', state='off')
        self.set_state('input_boolean.actual_fan_medium', state='off')
        self.set_state('input_boolean.actual_fan_high', state='off')

        self.listen_state(self.fan_on, 'input_boolean.fan_low', new='on', level='low')
        self.listen_state(self.fan_on, 'input_boolean.fan_medium', new='on', level='medium')
        self.listen_state(self.fan_on, 'input_boolean.fan_high', new='on', level='high')
        self.listen_state(self.fan_off, 'input_boolean.fan', new='off')
        self.listen_state(self.fan_off, 'input_boolean.fan_low', new='off', level='low')
        self.listen_state(self.fan_off, 'input_boolean.fan_medium', new='off', level='medium')
        self.listen_state(self.fan_off, 'input_boolean.fan_high', new='off', level='high')
        self.listen_state(self.light_on, 'input_boolean.fan_light', new='on')
        self.listen_state(self.light_off, 'input_boolean.fan_light', new='off')

        self.call_service('announcer/initialised', name=self.name.lower(), announce=False)

# -----------------------------------------------------------------------------------

    def fan_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom fan"""

        self._log_function_name(start=True)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_off_service(self, namespace, domain, service, data) -> None:
        """turn off bedroom fan"""

        self._log_function_name(start=True)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom fan light"""

        self._log_function_name(start=True)

        self.set_state('input_boolean.fan_light', state='on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_off_service(self, namespace, domain, service, data) -> None:

        self._log_function_name(start=True)

        self.set_state('input_boolean.fan_light', state='off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_purifier_on_service(self, namespace, domain, service, data) -> None:
        """turn on study purifier"""

        self._log_function_name(start=True)

        self.turn_on('fan.study_purifier_fan')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_purifier_off_service(self, namespace, domain, service, data) -> None:
        """turn off study purifier"""

        self._log_function_name(start=True)

        self.turn_off('fan.study_purifier_fan')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_purifier_on_service(self, namespace, domain, service, data) -> None:
        """turn on bedroom purifier"""

        self._log_function_name(start=True)

        self.turn_on('fan.bedroom_purifier_fan')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_purifier_off_service(self, namespace, domain, service, data) -> None:
        """turn off bedroom purifier"""

        self._log_function_name(start=True)

        self.turn_off('fan.bedroom_purifier_fan')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def status_event(self, event_name, data, kwargs) -> None:
        """status event"""

        self._log_function_name(start=True)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_purifier_on_event(self, event_name, data, kwargs) -> None:
        """study purifier on event"""

        self._log_function_name(start=True)

        self.call_service('fan/study_purifier_on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def study_purifier_off_event(self, event_name, data, kwargs) -> None:
        """study purifier off event"""

        self._log_function_name(start=True)
        self.call_service('fan/study_purifier_off')
        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_purifier_on_event(self, event_name, data, kwargs) -> None:
        """bedroom purifier on event"""

        self._log_function_name(start=True)

        self.call_service('fan/bedroom_purifier_on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def bedroom_purifier_off_event(self, event_name, data, kwargs) -> None:
        """bedroom purifier off event"""

        self._log_function_name(start=True)

        self.call_service('fan/bedroom_purifier_off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_on(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan on with level"""

        self._log_function_name(start=True)

        level = kwargs.get('level', 'low')

        self.toggle_state(level, 'on')
        # self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command=level)
        print(f"Fan level: {level} - on")

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def fan_off(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan off with level"""

        self._log_function_name(start=True)

        level = kwargs.get('level', 'low')

        self.toggle_state(level, 'off')
        # self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command=level)
        print(f"Fan level: {level} - off")

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def toggle_state(self, level, state) -> None:
        """toggle state of fan level input booleans"""

        self._log_function_name(start=True)

        other_state = 'off' if state == 'on' else 'on'

        if level == 'low':
            self.set_state('input_boolean.actual_fan_low', state=state)
            self.set_state('input_boolean.actual_fan_medium', state=other_state)
            self.set_state('input_boolean.actual_fan_high', state=other_state)
            self.set_state('input_boolean.fan_medium', state=other_state)
            self.set_state('input_boolean.fan_high', state=other_state)
        elif level == 'medium':
            self.set_state('input_boolean.actual_fan_low', state=other_state)
            self.set_state('input_boolean.actual_fan_medium', state=state)
            self.set_state('input_boolean.actual_fan_high', state=other_state)
            self.set_state('input_boolean.fan_low', state=other_state)
            self.set_state('input_boolean.fan_high', state=other_state)
        elif level == 'high':
            self.set_state('input_boolean.actual_fan_low', state=other_state)
            self.set_state('input_boolean.actual_fan_medium', state=other_state)
            self.set_state('input_boolean.actual_fan_high', state=state)
            self.set_state('input_boolean.fan_low', state=other_state)
            self.set_state('input_boolean.fan_medium', state=other_state)

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------


        # if level == 'low':
        #     self.set_state('input_boolean.fan_low', state='on')
        #     self.set_state('input_boolean.fan_medium', state='off')
        #     self.set_state('input_boolean.fan_high', state='off')
        # elif level == 'medium':
        #     self.set_state('input_boolean.fan_low', state='off')
        #     self.set_state('input_boolean.fan_medium', state='on')
        #     self.set_state('input_boolean.fan_high', state='off')
        # elif level == 'high':
        #     self.set_state('input_boolean.fan_low', state='off')
        #     self.set_state('input_boolean.fan_medium', state='off')
        #     self.set_state('input_boolean.fan_high', state='on')

        self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='off')

        self.set_state('input_boolean.fan_low', state='off')
        self.set_state('input_boolean.fan_medium', state='off')
        self.set_state('input_boolean.fan_high', state='off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_on(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan light on"""

        self._log_function_name(start=True)

        # self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')
        self.set_state('input_boolean.fan_light', state='on')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------

    def light_off(self, entity, attribute, old, new, kwargs) -> None:
        """bedroom fan light off"""

        self._log_function_name(start=True)

        # self.call_service('remote/send_command', entity_id='remote.broadlink', device='fan', command='light')
        self.set_state('input_boolean.fan_light', state='off')

        self._log_function_name(start=False)

# -----------------------------------------------------------------------------------
