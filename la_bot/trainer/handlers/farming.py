"""Grinding handlers."""

import logging
import random
from math import ceil
from typing import Dict, List

from telethon import events

from la_bot import notifications, shared_state, wait_utils
from la_bot.game import buttons, parsers
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client
from la_bot.trainer import loop

FARM_BUTTONS = 'farm_location_buttons'
ATTACK_BUTTONS = 'attack_buttons'
FIGHT_BUTTONS = 'fight_buttons'
TOWN_BUTTONS = 'town_buttons'
CITIZENS_BUTTONS = 'citizens_buttons'
MAP_BUTTONS = 'map_buttons'
IDLE_CHANCE = 0.15

available_buttons: Dict[str, List[str]] = {
    FARM_BUTTONS: [],
    ATTACK_BUTTONS: [],
    FIGHT_BUTTONS: [],
    TOWN_BUTTONS: [],
    CITIZENS_BUTTONS: [],
    MAP_BUTTONS: [],
}


async def refresh(_: events.NewMessage.Event) -> None:
    """Set state as go to grinding zone."""
    logging.debug('Refresh')
    await wait_utils.idle_pause()
    await client.send_message(game_bot_name, '/start')


async def process_location(event: events.NewMessage.Event) -> None:
    """Изучаем локацию и что-то делаем."""
    found_buttons = buttons.get_buttons_flat(event)

    if found_buttons:
        if any(buttons.FIND_ENEMY in btn.text for btn in found_buttons):
            await search_monster(event)
        elif any(buttons.HOME in btn.text for btn in found_buttons):
            shared_state.KILL_TO_STOP = -1
            shared_state.FARMING_STATE = None
            need_potions = shared_state.HEAL_TO_BUY or shared_state.MANA_TO_BUY or shared_state.SLOWSHOT_TO_BUY
            if need_potions:
                shared_state.FARMING_STATE = shared_state.FarmingState.need_potions

            if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
                logging.debug('Мы в городе, покупаем поты')
                await update_available_buttons(event, TOWN_BUTTONS)
                await handle_button_event(buttons.CITIZENS, TOWN_BUTTONS)
            else:
                logging.debug('Отправляемся фармить')
                shared_state.FARMING_STATE = shared_state.FarmingState.to_grinding_zone
                await open_map(event)
    else:
        logging.warning('Кнопки для категории не найдены. Инициализация не выполнена.')


async def need_to_buy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    if shared_state.FARMING_STATE is None:
        logging.debug('Необходимо купить поты')
        shared_state.FARMING_STATE = shared_state.FarmingState.need_potions
        shared_state.HEAL_TO_BUY = True
        shared_state.MANA_TO_BUY = True
        shared_state.SLOWSHOT_TO_BUY = True
        shared_state.KILL_TO_STOP = random.randint(1, 5)


async def need_energy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    if shared_state.FARMING_STATE is None:
        logging.info('Необходима Энергии Эйнхасад')
        shared_state.FARMING_STATE = shared_state.FarmingState.need_energy
        shared_state.KILL_TO_STOP = random.randint(1, 5)
        await notifications.send_custom_channel_notify('Закончилась Энергия Эйнхасад!')


async def pick_seller(event: events.NewMessage.Event) -> None:
    """Выбираем торговца."""
    logging.debug('Выбираем торговца')
    await update_available_buttons(event, CITIZENS_BUTTONS)
    await wait_utils.idle_pause()
    await handle_button_event(buttons.SELLER, CITIZENS_BUTTONS)


async def process_seller(event: events.NewMessage.Event) -> None:
    """Обрабатываем торговца."""
    logging.debug('Обрабатываем торговца')
    message = event.message
    handled = False

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.BUY in btn.text and not handled:
                    await handle_button_click(btn)
                    handled = True
                elif buttons.POTIONS in btn.text and 'Расходники' in btn.text and not handled:
                    await handle_button_click(btn)
                    handled = True
                elif buttons.HEALTH in btn.text and shared_state.HEAL_TO_BUY and not handled:
                    shared_state.HEAL_TO_BUY = False
                    await handle_button_click(btn)
                    handled = True
                elif buttons.MANA in btn.text and shared_state.MANA_TO_BUY and not handled:
                    shared_state.MANA_TO_BUY = False
                    await handle_button_click(btn)
                    handled = True
                elif buttons.SLOWSHOT in btn.text and shared_state.SLOWSHOT_TO_BUY and not handled:
                    shared_state.SLOWSHOT_TO_BUY = False
                    await handle_button_click(btn)
                    handled = True
                elif buttons.MAX in btn.text and not handled:
                    await handle_button_click(btn)
                    handled = True

    if not handled:
        logging.warning('Не понятно что делать.')


async def quest_is_done(_: events.NewMessage.Event) -> None:
    """Quest is done."""
    logging.debug('Квест завершен.')
    await notifications.send_custom_channel_notify('Квест завершен!')


async def enemy_search_started(_: events.NewMessage.Event) -> None:
    """Enemy search started."""
    available_buttons[FIGHT_BUTTONS].clear()


async def enemy_found(event: events.NewMessage.Event) -> None:
    """Enemy found."""
    await update_available_buttons(event, FIGHT_BUTTONS)


async def hero_is_died(_: events.NewMessage.Event) -> None:
    """Hero is died."""
    available_buttons[FIGHT_BUTTONS].clear()


async def update_available_buttons(event: events.NewMessage.Event, category: str) -> None:
    """Обновляем доступные кнопки по указанной категории."""
    found_buttons = buttons.get_buttons_flat(event)

    if found_buttons:
        available_buttons[category].clear()
        for btn in found_buttons:
            available_buttons[category].append(btn)
        available_buttons[category] = list(set(available_buttons[category]))
    else:
        logging.warning(f'Кнопки для категории {category} не найдены. Обновление не выполнено.')


async def handle_button_event(button_symbol: str, category: str) -> bool:
    """Обрабатываем нажатие кнопки по символу из указанной категории."""
    found_buttons = available_buttons.get(category, [])
    btn = next((btn for btn in found_buttons if button_symbol in btn.text), None)

    if btn:
        await wait_utils.wait_for()
        await client.send_message(game_bot_name, btn.text)
        return True
    logging.warning(f'Кнопка с символом "{button_symbol}" не найдена в категории {category}.')
    return False


async def handle_button_click(btn):
    """Helper function to click a button with a wait."""
    await wait_utils.wait_for()
    await btn.click()


async def open_map(event: events.NewMessage.Event) -> None:
    """Открываем карту и переходим в локацию."""
    logging.debug('Открываем карту.')
    
    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        logging.info('Идем за потами.')
        await handle_button_event(buttons.MAP, FARM_BUTTONS)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        logging.info('Идем в локацию.')
        await update_available_buttons(event, TOWN_BUTTONS)
        await handle_button_event(buttons.MAP, TOWN_BUTTONS)
    else:
        logging.warning('Не понятно что делать.')


async def go_to(event: events.NewMessage.Event) -> None:
    """Выбираем путь к локации."""
    logging.debug('Выбираем путь...')
    message = event.message

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.MAP in btn.text and 'Указать' in btn.text:
                    await wait_utils.idle_pause()
                    await btn.click()


async def specify_location(_: events.NewMessage.Event, ) -> None:
    """Вводим номер локации."""
    logging.debug('Вводим номер локации...')
    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.SHOP_LOCATION)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.FARMING_LOCATION)
    else:
        logging.warning('Не понятно что делать.')


async def approve(event: events.NewMessage.Event, ) -> None:
    """Подтвержаем путь."""
    logging.debug('Подтвержаем путь...')
    message = event.message

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.APPROVE in btn.text:
                    await handle_button_click(btn)


async def search_monster(event: events.NewMessage.Event) -> None:
    """Начинаем поиск монстра."""
    await update_available_buttons(event, FARM_BUTTONS)

    await wait_utils.idle_pause()

    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions and shared_state.KILL_TO_STOP == 0:
        await open_map(event)
        return

    if shared_state.FARMING_STATE is shared_state.FarmingState.need_energy and shared_state.KILL_TO_STOP == 0:
        await client.send_message(game_bot_name, '/hero')
        loop.exit_request()

    if shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        shared_state.FARMING_STATE = None

    if random.random() < 0.01:
        await wait_utils.relaxing()
    
    if (shared_state.KILL_TO_STOP > 0):
        logging.info(f'Необходимо убить мобов до остановки фарма: {shared_state.KILL_TO_STOP}')
        shared_state.KILL_TO_STOP -= 1

    try:
        hp_level = parsers.get_hp_level(event.message.message)
        logging.debug('Уровень здоровья: %d%%', hp_level)
    except Exception as exception:
        hp_level = None
        logging.warning(f'Не удалось получить уровень здоровья: {exception}')

    await wait_utils.human_like_sleep(1, 3)
    await handle_button_event(buttons.FIND_ENEMY, FARM_BUTTONS)


async def attack(event: events.NewMessage.Event) -> None:
    """Атакуем противника, проверяя доступные атаки."""
    message = event.message

    player_hp_level, enemy_hp_level = await get_health_levels(event)

    if player_hp_level is not None:
        logging.debug('Текущий уровень здоровья игрока: %d%%', player_hp_level)

    if enemy_hp_level is not None:
        logging.debug('Текущий уровень здоровья противника: %d%%', enemy_hp_level)

    available_buttons[ATTACK_BUTTONS].clear()
    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.ATTACK in btn.text and buttons.SKILL_DELAY not in btn.text:
                    available_buttons[ATTACK_BUTTONS].append(btn)

    if available_buttons[ATTACK_BUTTONS]:
        await wait_utils.wait_for()
        chosen_attack = random.choice(available_buttons[ATTACK_BUTTONS])
        await chosen_attack.click()


async def get_health_levels(event: events.NewMessage.Event):
    """Получаем уровни здоровья игрока и противника."""
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
    
    return hp_player_level, hp_enemy_level
