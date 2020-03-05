"""Support for HomeKit Controller Televisions."""
import logging

from aiohomekit.model.characteristics import (
    CharacteristicsTypes,
    CurrentMediaStateValues,
    RemoteKeyValues,
    TargetMediaStateValues,
)
from aiohomekit.utils import clamp_enum_to_char

from homeassistant.components.media_player import DEVICE_CLASS_TV, MediaPlayerDevice
from homeassistant.components.media_player.const import (
    SUPPORT_PAUSE,
    SUPPORT_PLAY,
    SUPPORT_STOP,
)
from homeassistant.const import STATE_IDLE, STATE_PAUSED, STATE_PLAYING
from homeassistant.core import callback

from . import KNOWN_DEVICES, HomeKitEntity

_LOGGER = logging.getLogger(__name__)


HK_TO_HA_STATE = {
    CurrentMediaStateValues.PLAYING: STATE_PLAYING,
    CurrentMediaStateValues.PAUSED: STATE_PAUSED,
    CurrentMediaStateValues.STOPPED: STATE_IDLE,
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Homekit television."""
    hkid = config_entry.data["AccessoryPairingID"]
    conn = hass.data[KNOWN_DEVICES][hkid]

    @callback
    def async_add_service(aid, service):
        if service["stype"] != "television":
            return False
        info = {"aid": aid, "iid": service["iid"]}
        async_add_entities([HomeKitTelevision(conn, info)], True)
        return True

    conn.add_listener(async_add_service)


class HomeKitTelevision(HomeKitEntity, MediaPlayerDevice):
    """Representation of a HomeKit Controller Television."""

    def __init__(self, accessory, discovery_info):
        """Initialise the TV."""
        self._state = None
        self._features = 0
        self._supported_target_media_state = set()
        self._supported_remote_key = set()
        super().__init__(accessory, discovery_info)

    def get_characteristic_types(self):
        """Define the homekit characteristics the entity cares about."""
        return [
            CharacteristicsTypes.CURRENT_MEDIA_STATE,
            CharacteristicsTypes.TARGET_MEDIA_STATE,
            CharacteristicsTypes.REMOTE_KEY,
        ]

    def _setup_target_media_state(self, char):
        self._supported_target_media_state = clamp_enum_to_char(
            TargetMediaStateValues, char
        )

        if TargetMediaStateValues.PAUSE in self._supported_target_media_state:
            self._features |= SUPPORT_PAUSE

        if TargetMediaStateValues.PLAY in self._supported_target_media_state:
            self._features |= SUPPORT_PLAY

        if TargetMediaStateValues.STOP in self._supported_target_media_state:
            self._features |= SUPPORT_STOP

    def _setup_remote_key(self, char):
        self._supported_remote_key = clamp_enum_to_char(RemoteKeyValues, char)
        if RemoteKeyValues.PLAY_PAUSE in self._supported_remote_key:
            self._features |= SUPPORT_PAUSE | SUPPORT_PLAY

    @property
    def device_class(self):
        """Define the device class for a HomeKit enabled TV."""
        return DEVICE_CLASS_TV

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return self._features

    @property
    def state(self):
        """State of the tv."""
        homekit_state = self.get_hk_char_value(CharacteristicsTypes.CURRENT_MEDIA_STATE)
        if homekit_state is None:
            return None
        return HK_TO_HA_STATE[homekit_state]

    async def async_media_play(self):
        """Send play command."""
        if self.state == STATE_PLAYING:
            _LOGGER.debug("Cannot play while already playing")
            return

        if TargetMediaStateValues.PLAY in self._supported_target_media_state:
            characteristics = [
                {
                    "aid": self._aid,
                    "iid": self._chars["target-media-state"],
                    "value": TargetMediaStateValues.PLAY,
                }
            ]
            await self._accessory.put_characteristics(characteristics)
        elif RemoteKeyValues.PLAY_PAUSE in self._supported_remote_key:
            characteristics = [
                {
                    "aid": self._aid,
                    "iid": self._chars["remote-key"],
                    "value": RemoteKeyValues.PLAY_PAUSE,
                }
            ]
            await self._accessory.put_characteristics(characteristics)

    async def async_media_pause(self):
        """Send pause command."""
        if self.state == STATE_PAUSED:
            _LOGGER.debug("Cannot pause while already paused")
            return

        if TargetMediaStateValues.PAUSE in self._supported_target_media_state:
            characteristics = [
                {
                    "aid": self._aid,
                    "iid": self._chars["target-media-state"],
                    "value": TargetMediaStateValues.PAUSE,
                }
            ]
            await self._accessory.put_characteristics(characteristics)
        elif RemoteKeyValues.PLAY_PAUSE in self._supported_remote_key:
            characteristics = [
                {
                    "aid": self._aid,
                    "iid": self._chars["remote-key"],
                    "value": RemoteKeyValues.PLAY_PAUSE,
                }
            ]
            await self._accessory.put_characteristics(characteristics)

    async def async_media_stop(self):
        """Send stop command."""
        if self.state == STATE_IDLE:
            _LOGGER.debug("Cannot stop when already idle")
            return

        if TargetMediaStateValues.STOP in self._supported_target_media_state:
            characteristics = [
                {
                    "aid": self._aid,
                    "iid": self._chars["target-media-state"],
                    "value": TargetMediaStateValues.STOP,
                }
            ]
            await self._accessory.put_characteristics(characteristics)
