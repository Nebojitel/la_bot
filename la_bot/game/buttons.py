"""Game buttons and utils."""

import itertools

from telethon import events, types

#Buttons
MAP = '🗺'
APPROVE = '✅'
HOME = '🏠'
HERO = '🧙'
FIND_ENEMY = '👾️'

#BATTLE
ATTACK = '🧿'
SKILL_DELAY = '🕐'
ANTARAS = '💧'
VALAKAS = '🩸'
REFRESH = '🔄'
SETTINGS = '⚙️'


def get_buttons_flat(event: events.NewMessage.Event) -> list[types.TypeKeyboardButton]:
    """Get all available buttons from event message."""
    if not event.message.buttons:
        return []
    return list(itertools.chain(*event.message.buttons))
