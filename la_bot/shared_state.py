"""Shared data variables."""

import enum

from la_bot.settings import app_settings

FARMING_LOCATION: str = app_settings.farming_location if app_settings.farming_location else '9'
SHOP_LOCATION: str = app_settings.shop_location if app_settings.shop_location else '1'
KILL_TO_STOP: int = -1
FARMING_PAUSED: bool = False
BATTLE_TIMER = None

HEAL_TO_BUY: bool = False
MANA_TO_BUY: bool = False
SLOWSHOT_TO_BUY: bool = False

class FarmingState(enum.Enum):
    """Farming tool states."""

    need_potions = enum.auto()  # need repair
    need_energy = enum.auto()  # need energy
    to_grinding_zone = enum.auto()  # go to grinding zone


FARMING_STATE: FarmingState | None = None
