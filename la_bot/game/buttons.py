"""Game buttons and utils."""

import itertools
import logging

from telethon import events, types
from la_bot import shared_state

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
ARROW = '🏹'
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

#CAPCHA
CAPCHA = '🔐'


def get_buttons_flat(event: events.NewMessage.Event) -> list[types.TypeKeyboardButton]:
    """Get all available buttons from event message."""
    if not event.message.buttons:
        return []

    for row in event.message.buttons:
        if isinstance(row, list):
            for wrapped_button in row:
                button = getattr(wrapped_button, 'button', wrapped_button)
                if isinstance(button, types.KeyboardButtonSimpleWebView):
                    print('KeyboardButtonSimpleWebView type:')
                    logging.info("Button attributes: %s", button.__dict__)
                    if CAPCHA in button.text and 'Перейти' in button.text:
                        shared_state.CAPCHA_URL = button.url
                elif isinstance(button, types.KeyboardButton):
                    continue
                elif isinstance(button, types.KeyboardButtonCallback):
                    continue
                else:
                    button_type = type(button).__name__
                    print(f'{button_type} type:')
                    logging.info("Button attributes:: %s", button.__dict__)

    return list(itertools.chain(*event.message.buttons))
