"""Game buttons and utils."""

import itertools

from telethon import events, types

#COMMON
MAP = '🗺'
APPROVE = '✅'
HERO = '🧙'
MIRROW = '🪞'

#RESOURCES
ENERGY = '🪶'

#FARM_LOCATION
FIND_ENEMY = '👾️'

#TOWN
CITIZENS = '🧝'
SELLER = '💰'
BUY = '🪙'
STATUE = '🗿'
ASSIGNMENT = '🎴'
SWEAR = '🫡'
TAKEN = '⏳'
PRIZE = '🎁'
RANDOM_PRICE = '🧧'
DANGEONS = '🌋'
HOME = '🏠'
URGENT = '❗️'
REWARD = '🏆'
TARGET = '⛳️'
BACK = '⬅️'

#POTIONS
POTIONS = '🍹'
HEALTH = '❤️'
MANA = '🧿'
SLOWSHOT = '🍹'
MAX = '🎒'

#BATTLE
ATTACK = '🧿'
SKILL_DELAY = '🕐'
BUFF = '🌕️'
DEBUFF = '🌑'
ANTARAS = '💧'
VALAKAS = '🩸'
REFRESH = '🔄'
VASILISK = '🥃'
SETTINGS = '⚙️'


def get_buttons_flat(event: events.NewMessage.Event) -> list[types.TypeKeyboardButton]:
    """Get all available buttons from event message."""
    if not event.message.buttons:
        return []
    return list(itertools.chain(*event.message.buttons))
