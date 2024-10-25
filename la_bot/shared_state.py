"""Shared data variables."""

import enum

from la_bot.settings import app_settings

FARMING_LOCATION: str = app_settings.farming_location if app_settings.farming_location else '8'
SHOP_LOCATION: str = app_settings.shop_location if app_settings.shop_location else '1'
FARMING_PAUSED: bool = False


class FarmingState(enum.Enum):
    """Farming tool states."""

    need_potions = enum.auto()  # need repair
    to_grinding_zone = enum.auto()  # go to grinding zone


FARMING_STATE: FarmingState | None = None  # by default - continue grinding on current location
