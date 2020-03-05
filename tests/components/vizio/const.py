"""Constants for the Vizio integration tests."""
import logging

from homeassistant.components.media_player import (
    DEVICE_CLASS_SPEAKER,
    DEVICE_CLASS_TV,
    DOMAIN as MP_DOMAIN,
)
from homeassistant.components.vizio.const import CONF_VOLUME_STEP
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_DEVICE_CLASS,
    CONF_HOST,
    CONF_NAME,
    CONF_PIN,
    CONF_PORT,
    CONF_TYPE,
)
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

NAME = "Vizio"
NAME2 = "Vizio2"
HOST = "192.168.1.1:9000"
HOST2 = "192.168.1.2:9000"
ACCESS_TOKEN = "deadbeef"
VOLUME_STEP = 2
UNIQUE_ID = "testid"
MODEL = "model"
VERSION = "version"

CH_TYPE = 1
RESPONSE_TOKEN = 1234
PIN = "abcd"


class MockStartPairingResponse(object):
    """Mock Vizio start pairing response."""

    def __init__(self, ch_type: int, token: int) -> None:
        """Initialize mock start pairing response."""
        self.ch_type = ch_type
        self.token = token


class MockCompletePairingResponse(object):
    """Mock Vizio complete pairing response."""

    def __init__(self, auth_token: str) -> None:
        """Initialize mock complete pairing response."""
        self.auth_token = auth_token


MOCK_PIN_CONFIG = {CONF_PIN: PIN}

MOCK_USER_VALID_TV_CONFIG = {
    CONF_NAME: NAME,
    CONF_HOST: HOST,
    CONF_DEVICE_CLASS: DEVICE_CLASS_TV,
    CONF_ACCESS_TOKEN: ACCESS_TOKEN,
}

MOCK_OPTIONS = {
    CONF_VOLUME_STEP: VOLUME_STEP,
}

MOCK_IMPORT_VALID_TV_CONFIG = {
    CONF_NAME: NAME,
    CONF_HOST: HOST,
    CONF_DEVICE_CLASS: DEVICE_CLASS_TV,
    CONF_ACCESS_TOKEN: ACCESS_TOKEN,
    CONF_VOLUME_STEP: VOLUME_STEP,
}

MOCK_TV_CONFIG_NO_TOKEN = {
    CONF_NAME: NAME,
    CONF_HOST: HOST,
    CONF_DEVICE_CLASS: DEVICE_CLASS_TV,
}

MOCK_SPEAKER_CONFIG = {
    CONF_NAME: NAME,
    CONF_HOST: HOST,
    CONF_DEVICE_CLASS: DEVICE_CLASS_SPEAKER,
}

VIZIO_ZEROCONF_SERVICE_TYPE = "_viziocast._tcp.local."
ZEROCONF_NAME = f"{NAME}.{VIZIO_ZEROCONF_SERVICE_TYPE}"
ZEROCONF_HOST = HOST.split(":")[0]
ZEROCONF_PORT = HOST.split(":")[1]

MOCK_ZEROCONF_SERVICE_INFO = {
    CONF_TYPE: VIZIO_ZEROCONF_SERVICE_TYPE,
    CONF_NAME: ZEROCONF_NAME,
    CONF_HOST: ZEROCONF_HOST,
    CONF_PORT: ZEROCONF_PORT,
    "properties": {"name": "SB4031-D5"},
}

CURRENT_INPUT = "HDMI"
INPUT_LIST = ["HDMI", "USB", "Bluetooth", "AUX"]

ENTITY_ID = f"{MP_DOMAIN}.{slugify(NAME)}"
