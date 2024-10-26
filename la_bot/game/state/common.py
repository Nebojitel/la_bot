"""Check messages by patterns."""


from telethon import events

from la_bot.game.parsers import strip_message


def is_captcha_message(event: events.NewMessage.Event) -> bool:
    """Capcha found message."""
    message = strip_message(event.message.message)
    patterns = {
        'сперва реши простой математический пример',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_refresh_message(event: events.NewMessage.Event) -> bool:
    """Refresh message."""
    message = strip_message(event.message.message)
    patterns = {
        'заблудился?',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_at_location(event: events.NewMessage.Event) -> bool:
    """Came to location message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты пришел в локацию',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_citizens_message(event: events.NewMessage.Event) -> bool:
    """Citizens message."""
    message = strip_message(event.message.message)
    patterns = {
        'жители поселения готовы тебе помочь',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_seller_message(event: events.NewMessage.Event) -> bool:
    """Seller message."""
    message = strip_message(event.message.message)
    patterns = {
        'я их куплю по самой выгодной цене',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_buy_message(event: events.NewMessage.Event) -> bool:
    """Buy message."""
    message = strip_message(event.message.message)
    patterns = {
        'сколько ты хочешь купить',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def successfull_trade_message(event: events.NewMessage.Event) -> bool:
    """Successfull trade message."""
    message = strip_message(event.message.message)
    patterns = {
        'добавлены в твой рюкзак',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_search_started_message(event: events.NewMessage.Event) -> bool:
    """Enemy search started message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты начал поиск монстров',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_enemy_found_message(event: events.NewMessage.Event) -> bool:
    """Enemy found message."""
    message = strip_message(event.message.message)
    patterns = {
        'твой противник',
        'бой начался',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_attack_message(event: events.NewMessage.Event) -> bool:
    """Attack state message."""
    message = strip_message(event.message.message)
    patterns = {
        'выбери умение для применения',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_win_message(event: events.NewMessage.Event) -> bool:
    """Win message."""
    message = strip_message(event.message.message)
    patterns = {
        'сражение окончено победой',
        'ты одержал доблестную победу',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_death_message(event: events.NewMessage.Event) -> bool:
    """Death state message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты воскреснешь в локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_resurrection_message(event: events.NewMessage.Event) -> bool:
    """Alive state message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты воскрес в локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_action_failed_message(event: events.NewMessage.Event) -> bool:
    """Stacked state message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты не можешь выполнить это действие',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_quest_completed(event: events.NewMessage.Event) -> bool:
    """Quest completed message."""
    message = strip_message(event.message.message)
    patterns = {
        'успешно выполнен, не забудь забрать награду',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_low_on_potions(event: events.NewMessage.Event) -> bool:
    """Need to buy potions message."""
    message = strip_message(event.message.message)
    patterns = {
        'у тебя осталось менее',
        'отсутствия зелий в рюкзаке',
        'соулшотов менее',
        'он не был применен и твоя атака не увеличилась',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_energy_depleted(event: events.NewMessage.Event) -> bool:
    """Need energy message."""
    message = strip_message(event.message.message)
    patterns = {
        'у тебя закончилась',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_map_opened_message(event: events.NewMessage.Event) -> bool:
    """Map opened message."""
    message = strip_message(event.message.message)
    patterns = {
        'следующие локации граничат',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_specify_location_message(event: events.NewMessage.Event) -> bool:
    """Specify location message."""
    message = strip_message(event.message.message)
    patterns = {
        'укажи числовой номер локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def need_to_approve_state(event: events.NewMessage.Event) -> bool:
    """Aprove state."""
    message = strip_message(event.message.message)
    patterns = {
        'твой маршрут будет следующим',
        'ты можешь докупить',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False
