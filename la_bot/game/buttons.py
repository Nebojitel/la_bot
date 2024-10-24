"""Game buttons and utils."""

import itertools

from telethon import events, types

#Buttons
MAP = '🗺'
HOME = '🏰'
HERO = '🧙'
FARM_1 = '🔸1'
ATTACK = '🧿'
FIND_ENEMY = '👾️'

#FIGHT MAGE
MAGE_ATTACK_TYPES = [' 🗡 Атака 🧿 2', ' 🗡 Луч 🧿 15']
SKILL_DELAY = '🕐'


def get_buttons_flat(event: events.NewMessage.Event) -> list[types.TypeKeyboardButton]:
    """Get all available buttons from event message."""
    if not event.message.buttons:
        return []
    return list(itertools.chain(*event.message.buttons))
