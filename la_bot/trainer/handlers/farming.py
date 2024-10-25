"""Grinding handlers."""

import logging
import random
from math import ceil
from typing import Dict, List

from telethon import events

from la_bot import notifications, shared_state, wait_utils
from la_bot.game import parsers
from la_bot.game.buttons import APPROVE, ATTACK, FIND_ENEMY, HOME, MAP, SKILL_DELAY, get_buttons_flat
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client

FARM_BUTTONS = 'farm_location_buttons'
ATTACK_BUTTONS = 'attack_buttons'
FIGHT_BUTTONS = 'fight_buttons'
TOWN_BUTTONS = 'town_buttons'
MAP_BUTTONS = 'map_buttons'
IDLE_CHANCE = 0.15

available_buttons: Dict[str, List[str]] = {
    FARM_BUTTONS: [],
    ATTACK_BUTTONS: [],
    FIGHT_BUTTONS: [],
    TOWN_BUTTONS: [],
    MAP_BUTTONS: [],
}
TOTAL_KILLED = 0


async def start_farming(event: events.NewMessage.Event) -> None:
    """Начинаем фарминг, проверяя доступные кнопки."""
    buttons = get_buttons_flat(event)

    logging.info('Farming ready event {0} {1} {2}'.format(
        shared_state.FARMING_STATE,
        shared_state.FARMING_LOCATION,
        shared_state.SHOP_LOCATION,
    ))

    if buttons:
        if any(FIND_ENEMY in btn.text for btn in buttons):
            await search_monster(event)
        elif any(HOME in btn.text for btn in buttons):
            shared_state.FARMING_STATE = shared_state.FarmingState.to_grinding_zone
            await open_map(event)
    else:
        logging.warning('Кнопки для категории не найдены. Инициализация не выполнена.')


async def need_to_buy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    logging.info('Необходимо купить поты')
    shared_state.FARMING_STATE = shared_state.FarmingState.need_potions
    await notifications.send_custom_channel_notify('Закончились поты!')


async def need_energy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    logging.info('Необходима Энергии Эйнхасад')
    await notifications.send_custom_channel_notify('Закончилась Энергия Эйнхасад!')


async def to_grinding_zone(_: events.NewMessage.Event) -> None:
    """Set state as go to grinding zone."""
    logging.info('Возвращаемся в зону гринда')
    await wait_utils.idle_pause()
    await wait_utils.idle_pause()
    await client.send_message(game_bot_name, '/start')


async def quest_is_done(_: events.NewMessage.Event) -> None:
    """Quest is done."""
    logging.info('Квест завершен.')
    await notifications.send_custom_channel_notify('Квест завершен!')


async def enemy_found(event: events.NewMessage.Event) -> None:
    """Enemy found."""
    await update_available_buttons(event, FIGHT_BUTTONS)


async def update_available_buttons(event: events.NewMessage.Event, category: str) -> None:
    """Обновляем доступные кнопки по указанной категории."""
    buttons = get_buttons_flat(event)

    if buttons:
        available_buttons[category].clear()
        for btn in buttons:
            available_buttons[category].append(btn)
        available_buttons[category] = list(set(available_buttons[category]))
    else:
        logging.warning(f'Кнопки для категории {category} не найдены. Обновление не выполнено.')


async def handle_button_event(button_symbol: str, category: str) -> bool:
    """Обрабатываем нажатие кнопки по символу из указанной категории."""
    buttons = available_buttons.get(category, [])
    button = next((btn for btn in buttons if button_symbol in btn.text), None)

    if button:
        await wait_utils.wait_for()
        await client.send_message(game_bot_name, button.text)
        return True
    logging.warning(f'Кнопка с символом "{button_symbol}" не найдена в категории {category}.')
    return False


async def open_map(event: events.NewMessage.Event, ) -> None:
    """Открываем карту и переходим в локацию."""
    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        logging.info('Открываем карту и идем за потами.')
        await handle_button_event(MAP, FARM_BUTTONS)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        logging.info('Открываем карту и идем в локацию.')
        await update_available_buttons(event, TOWN_BUTTONS)
        await handle_button_event(MAP, TOWN_BUTTONS)
    else:
        logging.warning('Не понятно что делать.')


async def go_to(event: events.NewMessage.Event) -> None:
    """Выбираем путь к локации."""
    logging.info('Выбираем путь...')
    message = event.message

    if message.buttons:
        for row in message.buttons:
            for button in row:
                if MAP in button.text and 'Указать' in button.text:
                    await wait_utils.idle_pause()
                    await wait_utils.idle_pause()
                    await button.click()


async def specify_location(_: events.NewMessage.Event, ) -> None:
    """Выбираем путь к локации."""
    logging.info('Вводим номер локации...')
    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        await wait_utils.idle_pause()
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.SHOP_LOCATION)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        await wait_utils.idle_pause()
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.FARMING_LOCATION)
    else:
        logging.warning('Не понятно что делать.')


async def approve(event: events.NewMessage.Event, ) -> None:
    """Подтвержаем путь."""
    logging.info('Подтвержаем путь...')
    message = event.message

    if message.buttons:
        for row in message.buttons:
            for button in row:
                if APPROVE in button.text:
                    await wait_utils.idle_pause()
                    await wait_utils.idle_pause()
                    await button.click()


async def search_monster(event: events.NewMessage.Event) -> None:
    """Начинаем поиск монстра."""
    global TOTAL_KILLED
    TOTAL_KILLED += 1
    await update_available_buttons(event, FARM_BUTTONS)

    await wait_utils.idle_pause()
    if random.random() < 0.01:
        await wait_utils.relaxing()

    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        await open_map(event)
        return

    if shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        shared_state.FARMING_STATE = None

    logging.info(f'Начинаем поиск противника. Убито мобов: {TOTAL_KILLED}')

    try:
        hp_level = parsers.get_hp_level(event.message.message)
        logging.info('Уровень здоровья: %d%%', hp_level)
    except Exception as exception:
        hp_level = None
        logging.warning(f'Не удалось получить уровень здоровья: {exception}')

    await wait_utils.human_like_sleep(1, 3)
    await handle_button_event(FIND_ENEMY, FARM_BUTTONS)


async def attack(event: events.NewMessage.Event) -> None:
    """Атакуем противника, проверяя доступные атаки."""
    message = event.message

    hp_player_level = None
    hp_enemy_level = None

    try:
        player_hp, enemy_hp = parsers.get_battle_hps(event.message.message)
        if player_hp[1] > 0:
            hp_player_level = ceil(player_hp[0] / player_hp[1] * 100)
        if enemy_hp[1] > 0:
            hp_enemy_level = ceil(enemy_hp[0] / enemy_hp[1] * 100)
    except (Exception, IndexError) as exception:
        logging.warning(f'Не удалось получить уровень здоровья: {exception}')

    if hp_player_level is not None:
        logging.info('Текущий уровень здоровья игрока: %d%%', hp_player_level)

    if hp_enemy_level is not None:
        logging.info('Текущий уровень здоровья противника: %d%%', hp_enemy_level)

    available_buttons[ATTACK_BUTTONS].clear()
    if message.buttons:
        for row in message.buttons:
            for button in row:
                if ATTACK in button.text and SKILL_DELAY not in button.text:
                    available_buttons[ATTACK_BUTTONS].append(button)

    if available_buttons[ATTACK_BUTTONS]:
        await wait_utils.wait_for()
        if random.random() < 0.05:
            await wait_utils.idle_pause()

        chosen_attack = random.choice(available_buttons[ATTACK_BUTTONS])
        await chosen_attack.click()
