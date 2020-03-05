"""Constants for Lovelace."""
from typing import Any

import voluptuous as vol

from homeassistant.const import CONF_ICON, CONF_TYPE, CONF_URL
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.util import slugify

DOMAIN = "lovelace"
EVENT_LOVELACE_UPDATED = "lovelace_updated"

CONF_MODE = "mode"
MODE_YAML = "yaml"
MODE_STORAGE = "storage"

LOVELACE_CONFIG_FILE = "ui-lovelace.yaml"
CONF_RESOURCES = "resources"
CONF_URL_PATH = "url_path"
CONF_RESOURCE_TYPE_WS = "res_type"

RESOURCE_TYPES = ["js", "css", "module", "html"]

RESOURCE_FIELDS = {
    CONF_TYPE: vol.In(RESOURCE_TYPES),
    CONF_URL: cv.string,
}

RESOURCE_SCHEMA = vol.Schema(RESOURCE_FIELDS)

RESOURCE_CREATE_FIELDS = {
    vol.Required(CONF_RESOURCE_TYPE_WS): vol.In(RESOURCE_TYPES),
    vol.Required(CONF_URL): cv.string,
}

RESOURCE_UPDATE_FIELDS = {
    vol.Optional(CONF_RESOURCE_TYPE_WS): vol.In(RESOURCE_TYPES),
    vol.Optional(CONF_URL): cv.string,
}

CONF_SIDEBAR = "sidebar"
CONF_TITLE = "title"
CONF_REQUIRE_ADMIN = "require_admin"

SIDEBAR_FIELDS = {
    vol.Required(CONF_ICON): cv.icon,
    vol.Required(CONF_TITLE): cv.string,
}

DASHBOARD_BASE_CREATE_FIELDS = {
    vol.Optional(CONF_REQUIRE_ADMIN, default=False): cv.boolean,
    vol.Optional(CONF_SIDEBAR): SIDEBAR_FIELDS,
}


DASHBOARD_BASE_UPDATE_FIELDS = {
    vol.Optional(CONF_REQUIRE_ADMIN): cv.boolean,
    vol.Optional(CONF_SIDEBAR): vol.Any(None, SIDEBAR_FIELDS),
}


STORAGE_DASHBOARD_CREATE_FIELDS = {
    **DASHBOARD_BASE_CREATE_FIELDS,
    vol.Required(CONF_URL_PATH): cv.string,
    # For now we write "storage" as all modes.
    # In future we can adjust this to be other modes.
    vol.Optional(CONF_MODE, default=MODE_STORAGE): MODE_STORAGE,
}

STORAGE_DASHBOARD_UPDATE_FIELDS = {
    **DASHBOARD_BASE_UPDATE_FIELDS,
}


def url_slug(value: Any) -> str:
    """Validate value is a valid url slug."""
    if value is None:
        raise vol.Invalid("Slug should not be None")
    str_value = str(value)
    slg = slugify(str_value, separator="-")
    if str_value == slg:
        return str_value
    raise vol.Invalid(f"invalid slug {value} (try {slg})")


class ConfigNotFound(HomeAssistantError):
    """When no config available."""
