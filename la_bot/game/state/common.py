"""Check messages by patterns."""


from telethon import events

from la_bot.game.buttons import FIND_ENEMY, get_buttons_flat
from la_bot.game.parsers import strip_message


def is_captcha_message(event: events.NewMessage.Event) -> bool:
    """Is capch found state."""
    message = strip_message(event.message.message)
    patterns = {
        'сперва реши простой математический пример',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_start_state(event: events.NewMessage.Event) -> bool:
    """Is start state."""
    message = strip_message(event.message.message)
    patterns = {
        'заблудился?',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_town_location(event: events.NewMessage.Event) -> bool:
    """Is town state."""
    message = strip_message(event.message.message)
    patterns = {
        'глудио — это оживленный город:',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_farm_location(event: events.NewMessage.Event) -> bool:
    """Is farm location state."""
    buttons = get_buttons_flat(event)
    if not buttons:
        return False
    if any(FIND_ENEMY in btn.text for btn in buttons):
        message = strip_message(event.message.message)
        if 'ты пришел в локацию' in message:
            return True
    return False


def is_enemy_found(event: events.NewMessage.Event) -> bool:
    """Is enemy found state."""
    message = strip_message(event.message.message)
    patterns = {
        'твой противник',
        'бой начался',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_attack_state(event: events.NewMessage.Event) -> bool:
    """Is attack state."""
    message = strip_message(event.message.message)
    patterns = {
        'выбери умение для применения',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_win_state(event: events.NewMessage.Event) -> bool:
    """Is win state."""
    message = strip_message(event.message.message)
    patterns = {
        'сражение окончено победой',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_died_state(event: events.NewMessage.Event) -> bool:
    """Is win state."""
    message = strip_message(event.message.message)
    patterns = {
        'ты воскреснешь в локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_alive_state(event: events.NewMessage.Event) -> bool:
    """Is alive state."""
    message = strip_message(event.message.message)
    patterns = {
        'ты воскрес в локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_quest_done(event: events.NewMessage.Event) -> bool:
    """Is quest done state."""
    message = strip_message(event.message.message)
    patterns = {
        'успешно выполнен, не забудь забрать награду',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def need_potions(event: events.NewMessage.Event) -> bool:
    """Need to buy potions state."""
    message = strip_message(event.message.message)
    patterns = {
        'у тебя осталось',
        'отсутствия зелий в рюкзаке',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def need_energy(event: events.NewMessage.Event) -> bool:
    """Need energy state."""
    message = strip_message(event.message.message)
    patterns = {
        'когда она достигнет 0',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_map_opened_state(event: events.NewMessage.Event) -> bool:
    """Is map opened."""
    message = strip_message(event.message.message)
    patterns = {
        'следующие локации граничат',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_specify_location_state(event: events.NewMessage.Event) -> bool:
    """Is specify location."""
    message = strip_message(event.message.message)
    patterns = {
        'укажи числовой номер локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_approve_state(event: events.NewMessage.Event) -> bool:
    """Is approve state."""
    message = strip_message(event.message.message)
    patterns = {
        'твой маршрут будет следующим',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False
