"""Support for the Lovelace UI."""
import logging

import voluptuous as vol

from homeassistant.components import frontend
from homeassistant.const import CONF_FILENAME
from homeassistant.core import callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import collection, config_validation as cv
from homeassistant.util import sanitize_filename

from . import dashboard, resources, websocket
from .const import (
    CONF_ICON,
    CONF_MODE,
    CONF_REQUIRE_ADMIN,
    CONF_RESOURCES,
    CONF_SIDEBAR,
    CONF_TITLE,
    CONF_URL_PATH,
    DASHBOARD_BASE_CREATE_FIELDS,
    DOMAIN,
    MODE_STORAGE,
    MODE_YAML,
    RESOURCE_CREATE_FIELDS,
    RESOURCE_SCHEMA,
    RESOURCE_UPDATE_FIELDS,
    STORAGE_DASHBOARD_CREATE_FIELDS,
    STORAGE_DASHBOARD_UPDATE_FIELDS,
    url_slug,
)

_LOGGER = logging.getLogger(__name__)

CONF_DASHBOARDS = "dashboards"

YAML_DASHBOARD_SCHEMA = vol.Schema(
    {
        **DASHBOARD_BASE_CREATE_FIELDS,
        vol.Required(CONF_MODE): MODE_YAML,
        vol.Required(CONF_FILENAME): vol.All(cv.string, sanitize_filename),
    }
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional(DOMAIN, default={}): vol.Schema(
            {
                vol.Optional(CONF_MODE, default=MODE_STORAGE): vol.All(
                    vol.Lower, vol.In([MODE_YAML, MODE_STORAGE])
                ),
                vol.Optional(CONF_DASHBOARDS): cv.schema_with_slug_keys(
                    YAML_DASHBOARD_SCHEMA, slug_validator=url_slug,
                ),
                vol.Optional(CONF_RESOURCES): [RESOURCE_SCHEMA],
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Set up the Lovelace commands."""
    mode = config[DOMAIN][CONF_MODE]
    yaml_resources = config[DOMAIN].get(CONF_RESOURCES)

    frontend.async_register_built_in_panel(hass, DOMAIN, config={"mode": mode})

    if mode == MODE_YAML:
        default_config = dashboard.LovelaceYAML(hass, None, None)

        if yaml_resources is None:
            try:
                ll_conf = await default_config.async_load(False)
            except HomeAssistantError:
                pass
            else:
                if CONF_RESOURCES in ll_conf:
                    _LOGGER.warning(
                        "Resources need to be specified in your configuration.yaml. Please see the docs."
                    )
                    yaml_resources = ll_conf[CONF_RESOURCES]

        resource_collection = resources.ResourceYAMLCollection(yaml_resources or [])

    else:
        default_config = dashboard.LovelaceStorage(hass, None)

        if yaml_resources is not None:
            _LOGGER.warning(
                "Lovelace is running in storage mode. Define resources via user interface"
            )

        resource_collection = resources.ResourceStorageCollection(hass, default_config)

        collection.StorageCollectionWebsocket(
            resource_collection,
            "lovelace/resources",
            "resource",
            RESOURCE_CREATE_FIELDS,
            RESOURCE_UPDATE_FIELDS,
        ).async_setup(hass, create_list=False)

    hass.components.websocket_api.async_register_command(
        websocket.websocket_lovelace_config
    )
    hass.components.websocket_api.async_register_command(
        websocket.websocket_lovelace_save_config
    )
    hass.components.websocket_api.async_register_command(
        websocket.websocket_lovelace_delete_config
    )
    hass.components.websocket_api.async_register_command(
        websocket.websocket_lovelace_resources
    )

    hass.components.websocket_api.async_register_command(
        websocket.websocket_lovelace_dashboards
    )

    hass.components.system_health.async_register_info(DOMAIN, system_health_info)

    hass.data[DOMAIN] = {
        # We store a dictionary mapping url_path: config. None is the default.
        "dashboards": {None: default_config},
        "resources": resource_collection,
    }

    if hass.config.safe_mode:
        return True

    # Process YAML dashboards
    for url_path, dashboard_conf in config[DOMAIN].get(CONF_DASHBOARDS, {}).items():
        # For now always mode=yaml
        config = dashboard.LovelaceYAML(hass, url_path, dashboard_conf)
        hass.data[DOMAIN]["dashboards"][url_path] = config

        try:
            _register_panel(hass, url_path, MODE_YAML, dashboard_conf, False)
        except ValueError:
            _LOGGER.warning("Panel url path %s is not unique", url_path)

    # Process storage dashboards
    dashboards_collection = dashboard.DashboardsCollection(hass)

    async def storage_dashboard_changed(change_type, item_id, item):
        """Handle a storage dashboard change."""
        url_path = item[CONF_URL_PATH]

        if change_type == collection.CHANGE_REMOVED:
            frontend.async_remove_panel(hass, url_path)
            await hass.data[DOMAIN]["dashboards"].pop(url_path).async_delete()
            return

        if change_type == collection.CHANGE_ADDED:
            existing = hass.data[DOMAIN]["dashboards"].get(url_path)

            if existing:
                _LOGGER.warning(
                    "Cannot register panel at %s, it is already defined in %s",
                    url_path,
                    existing,
                )
                return

            hass.data[DOMAIN]["dashboards"][url_path] = dashboard.LovelaceStorage(
                hass, item
            )

            update = False
        else:
            update = True

        try:
            _register_panel(hass, url_path, MODE_STORAGE, item, update)
        except ValueError:
            _LOGGER.warning("Failed to %s panel %s from storage", change_type, url_path)

    dashboards_collection.async_add_listener(storage_dashboard_changed)
    await dashboards_collection.async_load()

    collection.StorageCollectionWebsocket(
        dashboards_collection,
        "lovelace/dashboards",
        "dashboard",
        STORAGE_DASHBOARD_CREATE_FIELDS,
        STORAGE_DASHBOARD_UPDATE_FIELDS,
    ).async_setup(hass, create_list=False)

    return True


async def system_health_info(hass):
    """Get info for the info page."""
    return await hass.data[DOMAIN]["dashboards"][None].async_get_info()


@callback
def _register_panel(hass, url_path, mode, config, update):
    """Register a panel."""
    kwargs = {
        "frontend_url_path": url_path,
        "require_admin": config[CONF_REQUIRE_ADMIN],
        "config": {"mode": mode},
        "update": update,
    }

    if CONF_SIDEBAR in config:
        kwargs["sidebar_title"] = config[CONF_SIDEBAR][CONF_TITLE]
        kwargs["sidebar_icon"] = config[CONF_SIDEBAR][CONF_ICON]

    frontend.async_register_built_in_panel(hass, DOMAIN, **kwargs)
