"""Grinding handlers."""
from math import ceil
import logging
from typing import Dict, List

from telethon import events
import asyncio
import random

from la_bot import wait_utils
from la_bot.game import parsers
from la_bot.game.action import common
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client
from la_bot.game.buttons import FIND_ENEMY, HOME, FARM_1, SKILL_DELAY, MAGE_ATTACK_TYPES, get_buttons_flat

available_buttons: Dict[str, List[str]] = {
    'farm_location_buttons': [],
    'town_buttons': [],
}

TOTAL_KILLED = 0

async def start_farming(event: events.NewMessage.Event) -> None:
    """Начинаем."""
    buttons = get_buttons_flat(event)

    if buttons:
        if any(FIND_ENEMY in btn.text for btn in buttons):
            await search_monster(event)
        elif any(HOME in btn.text for btn in buttons):
            await go_to_farming_zone(event)
    else:
        logging.warning(f'Кнопки для категории не найдены. Инициализация не выполнена.')


async def update_available_buttons(event: events.NewMessage.Event, category: str) -> None:
    """Обновляем доступные кнопки по указанной категории."""
    global available_buttons
    buttons = get_buttons_flat(event)

    if buttons:
        if category == 'farm_location_buttons':
            for btn in buttons:
                available_buttons['farm_location_buttons'].append(btn.text)

        elif category == 'town_buttons':
            for btn in buttons:
                available_buttons['town_buttons'].append(btn.text)

        available_buttons = {key: list(set(val)) for key, val in available_buttons.items()}
    else:
        logging.warning(f'Кнопки для категории {category} не найдены. Обновление не выполнено.')


async def handle_button_event(button_symbol: str, category: str) -> bool:
    """Обрабатываем нажатие кнопки по символу из указанной категории."""
    global available_buttons
    buttons = available_buttons.get(category, [])
    button = next((btn for btn in buttons if button_symbol in btn), None)
    
    if button:
        await wait_utils.wait_for()
        await client.send_message(game_bot_name, button)
        return True
    logging.warning(f'Кнопка с символом "{button_symbol}" не найдена в категории {category}.')
    return False


async def go_to_farming_zone(event: events.NewMessage.Event) -> None:
    """Выбираем локацию для фарма"""
    await update_available_buttons(event, 'town_buttons')
    if any(FARM_1 in btn for btn in available_buttons['town_buttons']):
        logging.info('Идем в локацию.')
        await wait_utils.wait_for()
        button_to_press = next(btn for btn in available_buttons['town_buttons'] if FARM_1 in btn)
        await handle_button_event(button_to_press, 'town_buttons')
    else:
        logging.warning('Не удалось найти кнопку для перехода в локацию.')


async def search_monster(event: events.NewMessage.Event) -> None:
    """Начинаем поиск монстра."""
    global TOTAL_KILLED
    TOTAL_KILLED += 1

    logging.info(f'Начинаем поиск противника. Убито мобов: {TOTAL_KILLED}')
    await update_available_buttons(event, 'farm_location_buttons')
    await wait_utils.wait_for()
    try:
        hp_level = parsers.get_hp_level(event.message.message)
        logging.info('current HP level is %d%%', hp_level)
    except Exception as e:
        # logging.warning(f'Не удалось получить уровень здоровья: {e}')
        hp_level = None 

    

    # if hp_level is not None and hp_level <= app_settings.minimum_hp_level_for_grinding:
    if False:
        logging.info('Мало хп, отдыхаем.')
        # await relaxing(event)
        # await return_to_town()
    # elif energy_level is not None and energy_level <= 0:
    #     logging.info('Мало энергии, ждем 1 час.')
    #     await asyncio.sleep(3600)
    #     await handle_button_event(FIND_MONSTER, 'farm_location_buttons')
    else:
        await wait_utils.wait_for()
        await handle_button_event(FIND_ENEMY, 'farm_location_buttons')


async def attack(event: events.NewMessage.Event) -> None:
    """Атакуем противника."""
    message = event.message
    available_attacks = []

    try:
        player_hp, enemy_hp = parsers.get_battle_hps(event.message.message)
        hp_player_level = ceil(player_hp[0] / player_hp[1] * 100)
        hp_enemy_level = ceil(enemy_hp[0] / enemy_hp[1] * 100)
    except Exception as e:
        logging.warning(f'Не удалось получить уровень здоровья: {e}')
        hp_enemy_level = None 

    if hp_player_level is not None:
        logging.info('Текущий уровень здоровья: %d%%', hp_player_level)

    if hp_enemy_level is not None:
        logging.info('Текущий уровень здоровья противника: %d%%', hp_enemy_level)

    if message.buttons:
        for row in message.buttons:
            for button in row:
                if any(attack_type in button.text for attack_type in MAGE_ATTACK_TYPES) and SKILL_DELAY not in button.text:
                    available_attacks.append(button)

    if available_attacks:
        chosen_attack = random.choice(available_attacks)
        await wait_utils.wait_for()
        await chosen_attack.click()


async def relaxing(_: events.NewMessage.Event) -> None:
    """Отдыхаем."""
    logging.info('Отдыхаем 1 час.')
    await asyncio.sleep(3600)
    # await common.show_hero(event)
