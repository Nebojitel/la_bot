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


def is_checking_message(event: events.NewMessage.Event) -> bool:
    """Checking found message."""
    message = strip_message(event.message.message)
    patterns = {
        'тебе нужно пройти проверку нажав кнопку ниже',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_update_message(event: events.NewMessage.Event) -> bool:
    """Checking found message."""
    message = strip_message(event.message.message)
    patterns = {
        'игровой мир обновляется',
        'в связи с обновлением сервера',
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
        'заблудился?',
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
        'сколько ты хочешь купить',
        'список доступных квестов',
        '🏆 выполнен',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_purchase_message(event: events.NewMessage.Event) -> bool:
    """Alive state message."""
    message = strip_message(event.message.message)
    patterns = {
        'добавлены в твой рюкзак',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_statue_message(event: events.NewMessage.Event) -> bool:
    """Statue message."""
    message = strip_message(event.message.message)
    patterns = {
        'статуя эйнхасад предстает перед тобой',
        'иначе она пропадет, а поручения обновятся',
        'выбери одну из дополнительных наград',
        'ты обязуешься выполнить',
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


def is_refresh_message(event: events.NewMessage.Event) -> bool:
    """Alive state message."""
    message = strip_message(event.message.message)
    patterns = {
        'ты воскрес в локации',
        'ты не можешь выполнить это действие',
        'квест успешно принят',
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
        'ты выполнил поручение, успей забрать награду',
        'ты выполнил ежедневное задание',
        'ты сегодня больше не можешь искать монстров в зеркальной локации',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False


def is_quest_taken(event: events.NewMessage.Event) -> bool:
    """Quest taken message."""
    message = strip_message(event.message.message)
    patterns = {
        'клятва принята',
        'квест успешно принят',
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
        'в твоём рюкзаке закончились',
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


def is_energy_recovered(event: events.NewMessage.Event) -> bool:
    """Energy Recovered message."""
    message = strip_message(event.message.message)
    patterns = {
        'запас твоей энергии эйнхасад восстановлен',
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
        '🙂 новый ⛳️ цель',
    }
    for pattern in patterns:
        if pattern in message:
            return True
    return False
