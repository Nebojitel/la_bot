"""Grinding handlers."""

import asyncio
import logging
import random
from math import ceil
from typing import Dict, List

from telethon import events

from la_bot import wait_utils
from la_bot.game import parsers
from la_bot.game.buttons import FIND_ENEMY, HOME, ATTACK, MAP, SKILL_DELAY, get_buttons_flat
from la_bot.settings import game_bot_name
from la_bot.telegram_client import client

FARM_LOCATION = 'farm_location_buttons'
ATTACK_BUTTONS = 'attack_buttons'
TOWN = 'town_buttons'
IDLE_CHANCE = 0.15
RELAX_WAIT_TIME = 3600

available_buttons: Dict[str, List[str]] = {
    FARM_LOCATION: [],
    ATTACK_BUTTONS: [],
    TOWN: [],
}
TOTAL_KILLED = 0


async def start_farming(event: events.NewMessage.Event) -> None:
    """Начинаем фарминг, проверяя доступные кнопки."""
    buttons = get_buttons_flat(event)

    if buttons:
        if any(FIND_ENEMY in btn.text for btn in buttons):
            await search_monster(event)
        elif any(HOME in btn.text for btn in buttons):
            await open_map(event)
    else:
        logging.warning('Кнопки для категории не найдены. Инициализация не выполнена.')

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

async def open_map(event: events.NewMessage.Event) -> None:
    """Открываем карту и переходим в локацию."""
    await update_available_buttons(event, TOWN)
    if any(MAP in btn.text for btn in available_buttons[TOWN]):
        logging.info('Открываем карту и идем в локацию.')
        button_to_press = next(btn for btn in available_buttons[TOWN] if MAP in btn.text)
        await handle_button_event(MAP, TOWN)  # Нажимаем на кнопку карты
    else:
        logging.warning('Не удалось найти кнопку карты.')

async def search_monster(event: events.NewMessage.Event) -> None:
    """Начинаем поиск монстра."""
    global TOTAL_KILLED
    TOTAL_KILLED += 1
    await wait_utils.idle_pause()

    logging.info(f'Начинаем поиск противника. Убито мобов: {TOTAL_KILLED}')
    await update_available_buttons(event, FARM_LOCATION)
    try:
        hp_level = parsers.get_hp_level(event.message.message)
        logging.info('Уровень здоровья: %d%%', hp_level)
    except Exception as exception:
        hp_level = None
        logging.warning(f'Не удалось получить уровень здоровья: {exception}')

    await wait_utils.wait_for(idle_chance=IDLE_CHANCE)
    await handle_button_event(FIND_ENEMY, FARM_LOCATION)

async def attack(event: events.NewMessage.Event) -> None:
    """Атакуем противника, проверяя доступные атаки."""
    await update_available_buttons(event, ATTACK_BUTTONS)
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
        chosen_attack = random.choice(available_buttons[ATTACK_BUTTONS])
        await wait_utils.wait_for()
        await chosen_attack.click()

async def relaxing(_: events.NewMessage.Event) -> None:
    """Отдыхаем, прежде чем начинать заново."""
    logging.info('Отдыхаем 1 час.')
    await asyncio.sleep(RELAX_WAIT_TIME)
    await client.send_message(game_bot_name, '/start')
