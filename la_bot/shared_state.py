"""Shared data variables."""

import enum

from la_bot.settings import app_settings

FARMING_LOCATION: str = app_settings.farming_location if app_settings.farming_location else '2'
SHOP_LOCATION: str = app_settings.shop_location if app_settings.shop_location else '1'
USER_NAME: str = 'DEFAULT'
HERO_TYPE: str = app_settings.hero_type if app_settings.hero_type else 'mage'
CAPCHA_URL: str = ''
KILL_TO_STOP: int = -1
FARM_MIRROW: bool = False
FARMING_PAUSED: bool = False

HEAL_TO_BUY: bool = False
MANA_TO_BUY: bool = False
SLOWSHOT_TO_BUY: bool = False
ARROWS_TO_BUY: bool = False

class FarmingState(enum.Enum):
    """Farming tool states."""

    need_potions = enum.auto()
    need_energy = enum.auto()
    to_grinding_zone = enum.auto()
    go_home = enum.auto()


FARMING_STATE: FarmingState | None = None
