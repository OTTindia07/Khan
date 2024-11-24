import logging
import requests
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_IP_ADDRESS, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "My Touch Panel Switch"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_IP_ADDRESS): cv.string,
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    ip_address = config.get(CONF_IP_ADDRESS)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)

    devices = [TouchPanelSwitch(ip_address, username, password)]
    add_entities(devices, True)

class TouchPanelSwitch(SwitchEntity):

    def __init__(self, ip_address, username, password):
        self._ip_address = ip_address
        self._username = username
        self._password = password
        self._name = DEFAULT_NAME
        self._state = False

    def turn_on(self, **kwargs):
        self._send_command("01XX1")
        self._state = True

    def turn_off(self, **kwargs):
        self._send_command("01XX0")
        self._state = False

    def _send_command(self, command):
        url = f"http://{self._ip_address}/api"
        data = {
            "cmd": "ST",
            "device_ID": "WL-4258BC",
            "data": command,
            "serial": 12345
        }
        response = requests.post(url, json=data, auth=(self._username, self._password))
        if response.status_code != 200:
            _LOGGER.error("Failed to send command to touch panel")

    @property
    def name(self):
        return self._name

    @property
    def is_on(self):
        return self._state

    def update(self):
        url = f"http://{self._ip_address}/api"
        data = {
            "cmd": "SS",
            "device_ID": "WL-4258BC",
            "serial": 12345
        }
        response = requests.post(url, json=data, auth=(self._username, self._password))
        if response.status_code == 200:
            self._state = "01XX1" in response.json().get("data", [])
        else:
            _LOGGER.error("Failed to update status from touch panel")
