"""Grinding handlers."""

from functools import partial
import datetime
import logging
from math import ceil
import random
import re
from typing import Dict, List

from telethon import events, errors

from la_bot import notifications, shared_state, wait_utils
from la_bot.game import buttons, parsers
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client
from la_bot.trainer import loop

purchase_event: events.NewMessage.Event = None
battle_event: events.NewMessage.Event = None

FARM_BUTTONS = 'farm_location_buttons'
BATTLE_BUTTONS = 'battle_buttons'
TOWN_BUTTONS = 'battle_buttons'
CITIZENS_BUTTONS = 'citizens_buttons'
IDLE_CHANCE = 0.15
REWARD_CHOSEN = False
QUEST_TAKEN = False
TASK_NUMBER = 0
HAS_TASKS = False
VASILISK_USED = False
PVP_BATTLE = False
RANDOM_REWARD = str(random.randint(1, 5))

available_buttons: Dict[str, List[str]] = {
    FARM_BUTTONS: [],
    BATTLE_BUTTONS: [],
    TOWN_BUTTONS: [],
    CITIZENS_BUTTONS: [],
}


async def refresh(_: events.NewMessage.Event) -> None:
    """Set state as go to grinding zone."""
    logging.debug('Refresh')
    await wait_utils.idle_pause()
    await client.send_message(game_bot_name, '/start')


async def process_location(event: events.NewMessage.Event) -> None:
    """Изучаем локацию и что-то делаем."""
    await wait_utils.wait_for()
    found_buttons = buttons.get_buttons_flat(event)
    button_selected = False
    global QUEST_TAKEN, purchase_event
    purchase_event = None

    if found_buttons:
        if any(buttons.FIND_ENEMY in btn.text for btn in found_buttons):
            await search_monster(event)
            button_selected = True
        elif any(buttons.HOME in btn.text for btn in found_buttons):
            await update_available_buttons(event, TOWN_BUTTONS)
            shared_state.KILL_TO_STOP = -1
            shared_state.FARMING_STATE = None
            need_potions = shared_state.HEAL_TO_BUY or shared_state.MANA_TO_BUY or shared_state.SLOWSHOT_TO_BUY or shared_state.ARROWS_TO_BUY
            if need_potions:
                shared_state.FARMING_STATE = shared_state.FarmingState.need_potions

            if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
                logging.info('Мы в городе, покупаем поты')
                await handle_button_event(buttons.CITIZENS, TOWN_BUTTONS)
                button_selected = True
            elif not button_selected and not QUEST_TAKEN and any(buttons.URGENT in btn.text and buttons.CITIZENS in btn.text for btn in found_buttons):
                logging.info('Нужно взять/сдать квесты')
                await handle_button_event(buttons.CITIZENS, TOWN_BUTTONS)
                button_selected = True
            elif not button_selected:
                logging.info('Отправляемся фармить')
                shared_state.FARMING_STATE = shared_state.FarmingState.to_grinding_zone
                await open_map(event)
                button_selected = True
    else:
        logging.warning('Кнопки для категории не найдены. Инициализация не выполнена.')


async def need_to_buy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    if shared_state.FARMING_STATE is None:
        logging.info('Необходимо купить поты')
        shared_state.FARMING_STATE = shared_state.FarmingState.need_potions
        shared_state.HEAL_TO_BUY = True
        shared_state.MANA_TO_BUY = True
        shared_state.SLOWSHOT_TO_BUY = True
        if (shared_state.HERO_TYPE == 'archer'):
            shared_state.ARROWS_TO_BUY = True
        # shared_state.KILL_TO_STOP = random.randint(1, 5)
        shared_state.KILL_TO_STOP = 0


async def need_energy_potions(_: events.NewMessage.Event) -> None:
    """Set state as potions needed."""
    if shared_state.FARMING_STATE is None:
        logging.info('Необходима Энергии Эйнхасад')
        await notifications.send_custom_channel_notify('Закончилась Энергия Эйнхасад!')
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, '/hero')
        loop.exit_request()


async def pick_citizen(event: events.NewMessage.Event) -> None:
    """Выбираем жителя."""
    await update_available_buttons(event, CITIZENS_BUTTONS)
    await wait_utils.idle_pause()
    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions:
        logging.info('Выбираем торговца для покупки потов')
        await handle_button_event(buttons.SELLER, CITIZENS_BUTTONS)
    else:
        logging.info('смотрим кого выбрать')
        found_buttons = buttons.get_buttons_flat(event)
        button_selected = False

        if found_buttons:
            if any(buttons.URGENT in btn.text and buttons.SELLER in btn.text for btn in found_buttons):
                logging.info('Выбираем торговца')
                await handle_button_event(buttons.SELLER, CITIZENS_BUTTONS)
                button_selected = True
            elif not button_selected and any(buttons.URGENT in btn.text and buttons.STATUE in btn.text for btn in found_buttons):
                logging.info('Выбираем статую')
                global RANDOM_REWARD
                RANDOM_REWARD = str(random.randint(1, 5))
                await handle_button_event(buttons.STATUE, CITIZENS_BUTTONS)


async def process_citizen_buttons(event: events.NewMessage.Event, actions: list) -> None:
    """Обрабатывает кнопки на основе переданных действий."""
    logging.debug('Processing citizen buttons')
    await wait_utils.wait_for()
    message = event.message
    handled = False

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                logging.debug('Checking button: %s', btn.text)
                for condition, action in actions:
                    if condition(btn) and not handled:
                        logging.debug('Condition met for button: %s', btn.text)
                        if action == process_statue_tasks:
                            await wait_utils.wait_for()
                            await action(event)
                        else:
                            await wait_utils.wait_for()
                            await action(btn)
                        handled = True
                        logging.debug('Button action executed: %s', btn.text)
                        break
                if handled:
                    break
            if handled:
                break

    if not handled:
        logging.warning('Не понятно что тут дальше делать...')
        global purchase_event
        purchase_event = None
        await wait_utils.wait_for()
        await refresh(event)


async def handle_button_click(btn):
    """Helper function to click a button with a wait."""
    await wait_utils.wait_for()
    try:
        logging.debug('Clicking button: %s', btn.text)
        await btn.click()
        logging.debug('Button clicked successfully: %s', btn.text)
    except Exception as e:
        logging.error('Ошибка при нажатии кнопки %s: %s', btn.text, e)


async def process_seller(event: events.NewMessage.Event) -> None:
    """Обрабатывает торговца."""
    logging.debug('Обрабатываем торговца')
    found_buttons = buttons.get_buttons_flat(event)
    
    if not found_buttons:
        logging.warning('Кнопки не найдены в сообщении.')
        return

    urgent_button_exists = any(btn for btn in found_buttons if buttons.URGENT in btn.text)
    reward_button_exists = any(btn for btn in found_buttons if buttons.REWARD in btn.text)

    actions = [
        (lambda btn: buttons.URGENT in btn.text and not reward_button_exists, handle_button_click),
        (lambda btn: buttons.REWARD in btn.text, handle_button_click),
        (lambda btn: buttons.BUY in btn.text and not urgent_button_exists, handle_button_click),
        (lambda btn: buttons.POTIONS in btn.text and 'Расходники' in btn.text, handle_button_click),
        (lambda btn: buttons.HEALTH in btn.text and shared_state.HEAL_TO_BUY,
         partial(set_and_handle, 'HEAL_TO_BUY', event=event)),
        (lambda btn: buttons.MANA in btn.text and shared_state.MANA_TO_BUY,
         partial(set_and_handle, 'MANA_TO_BUY', event=event)),
        (lambda btn: buttons.SLOWSHOT in btn.text and shared_state.SLOWSHOT_TO_BUY,
         partial(set_and_handle, 'SLOWSHOT_TO_BUY', event=event)),
        (lambda btn: buttons.ARROW in btn.text and shared_state.ARROWS_TO_BUY,
         partial(set_and_handle, 'ARROWS_TO_BUY', event=event)),
        (lambda btn: buttons.MAX in btn.text, handle_button_click),
    ]

    logging.debug('Передаем события в process_citizen_buttons')
    await process_citizen_buttons(event, actions)


async def continue_purchase(_: events.NewMessage.Event) -> None:
    """Проверяет сообщение о добавлении предмета в рюкзак и обращается к сохраненному событию."""
    global purchase_event
    if purchase_event is None:
        logging.warning('Нет сохраненного события для продолжения покупки.')
        return

    try:
        logging.debug('Продолжаем покупки из сохраненного события')
        await process_seller(purchase_event)
    except Exception as e:
        logging.error('Ошибка при продолжении покупки: %s', e)


async def set_and_handle(state_var, btn, event):
    """Устанавливает состояние и обрабатывает кнопку."""
    global purchase_event
    if getattr(shared_state, state_var, None) is not None:
        setattr(shared_state, state_var, False)
        purchase_event = event
        logging.debug('State variable %s set to False, saving event for purchase', state_var)
        await handle_button_click(btn)


async def process_statue(event: events.NewMessage.Event) -> None:
    """Обрабатывает статую."""
    logging.debug('Обрабатываем статую')
    context = parsers.strip_message(event.message.message)
    global REWARD_CHOSEN, RANDOM_REWARD, QUEST_TAKEN

    found_buttons = buttons.get_buttons_flat(event)
    reward_button_exists = any(btn for btn in found_buttons if buttons.REWARD in btn.text)
    take_reward_button_exists = any(btn for btn in found_buttons if buttons.REWARD in btn.text and 'Забрать' in btn.text)
    active_quest_button_exists = any(btn for btn in found_buttons if buttons.TAKEN in btn.text)

    if active_quest_button_exists:
        QUEST_TAKEN = True

    actions = [
        (lambda btn: buttons.URGENT in btn.text and buttons.ASSIGNMENT in btn.text, handle_button_click),
        (lambda btn: buttons.REWARD in btn.text and 'Забрать' in btn.text, handle_button_click),
        (lambda btn: buttons.REWARD in btn.text and buttons.ASSIGNMENT in btn.text and not take_reward_button_exists, handle_button_click),
        (lambda btn: buttons.RANDOM_PRICE in btn.text and RANDOM_REWARD in btn.text and not REWARD_CHOSEN,
         partial(set_reward_and_handle, reward_chosen=True)),
        (lambda btn: buttons.PRIZE in btn.text, partial(set_reward_and_handle, reward_chosen=False)),
        (lambda btn: (buttons.SWEAR in btn.text and not reward_button_exists and not active_quest_button_exists and 'зачистить локацию' in context),
        lambda btn: handle_statue_task(btn, context)),
        (lambda btn: buttons.ASSIGNMENT in btn.text and not reward_button_exists and not active_quest_button_exists, process_statue_tasks),
        (lambda btn: buttons.SWEAR in btn.text and not reward_button_exists and not active_quest_button_exists and 'ты обязуешься выполнить' in context, handle_button_click),
    ]

    await process_citizen_buttons(event, actions)


async def set_reward_and_handle(btn, *, reward_chosen):
    """Устанавливает состояние для награды и обрабатывает кнопку."""
    global REWARD_CHOSEN
    REWARD_CHOSEN = reward_chosen
    await handle_button_click(btn)


async def process_statue_tasks(event: events.NewMessage.Event) -> None:
    """Обрабатывает поручения в статуе."""
    logging.debug("Получаем задания для статуи")
    await wait_utils.wait_for()
    found_buttons = buttons.get_buttons_flat(event)
    
    try:
        taken, max_tasks = parsers.get_tasks_count(event.message.message)
        logging.info(f"Количество поручений: выполнено {taken} из {max_tasks}")
    except Exception as exception:
        logging.warning(f"Не удалось получить количество поручений: {exception}")
        taken, max_tasks = None, None

    if taken is not None and max_tasks is not None:
        if taken < max_tasks:
            assignment_buttons = [
                btn for btn in found_buttons 
                if buttons.ASSIGNMENT in btn.text and buttons.TAKEN not in btn.text
            ]
            if assignment_buttons:
                chosen_task = random.choice(assignment_buttons)
                await handle_button_click(chosen_task)
            else:
                logging.info("Нет доступных кнопок для поручений.")
        elif taken == max_tasks:
            back_button = next((btn for btn in found_buttons if buttons.BACK in btn.text), None)
            if back_button:
                await handle_button_click(back_button)
            else:
                logging.warning("Кнопка 'Назад' не найдена.")
    else:
        logging.error("Не удалось определить количество выполненных поручений.")


async def handle_statue_task(btn, context) -> None:
    """Обрабатываем квест статуи."""
    match = re.search(r"зачистить локацию \((\d{1,2})\)", context)
    if match:
        shared_state.FARMING_LOCATION = match.group(1)
        logging.info(f"FARMING_LOCATION установлен в {shared_state.FARMING_LOCATION}")
    await handle_button_click(btn)


async def quest_taken(_: events.NewMessage.Event) -> None:
    """Quest taken."""
    global QUEST_TAKEN
    QUEST_TAKEN = True
    logging.debug('Квест взят.')
    # await refresh(event)


async def pvp_delay(event: events.NewMessage.Event) -> None:
    """PVP delay."""
    wait_utils.RELAXING_HUGE_STATE = True
    await search_monster(event)


async def quest_is_done(_: events.NewMessage.Event) -> None:
    """Quest is done."""
    logging.debug('Квест завершен.')
    global QUEST_TAKEN
    QUEST_TAKEN = False
    if shared_state.FARMING_STATE is None:
        logging.info('Квест завершен. Идем за наградой')
        shared_state.FARMING_STATE = shared_state.FarmingState.go_home
        shared_state.FARMING_LOCATION = app_settings.farming_location if app_settings.farming_location else '2'


async def enemy_search_started(_: events.NewMessage.Event) -> None:
    """Enemy search started."""
    global battle_event, VASILISK_USED, PVP_BATTLE
    battle_event = None
    VASILISK_USED = False
    PVP_BATTLE = False
    available_buttons[BATTLE_BUTTONS].clear()


async def pvp_started(event: events.NewMessage.Event) -> None:
    """PVP started"""
    global PVP_BATTLE
    PVP_BATTLE = True


async def enemy_found(event: events.NewMessage.Event) -> None:
    """Enemy found."""
    global battle_event, VASILISK_USED
    battle_event = event
    VASILISK_USED = False
    await update_available_buttons(event, BATTLE_BUTTONS)


async def hero_is_died(_: events.NewMessage.Event) -> None:
    """Hero is died."""
    global battle_event
    battle_event = None
    available_buttons[BATTLE_BUTTONS].clear()


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


async def open_map(event: events.NewMessage.Event) -> None:
    """Открываем карту и переходим в локацию."""
    logging.debug('Открываем карту.')
    
    if shared_state.FARMING_STATE in (shared_state.FarmingState.need_potions, shared_state.FarmingState.go_home):
        logging.info('Идем в город.')
        await wait_utils.wait_for()
        await handle_button_event(buttons.MAP, FARM_BUTTONS)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone and not shared_state.FARM_MIRROW:
        logging.info('Идем в локацию.')
        await wait_utils.wait_for()
        await update_available_buttons(event, TOWN_BUTTONS)
        await handle_button_event(buttons.MAP, TOWN_BUTTONS)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone and shared_state.FARM_MIRROW:
        logging.info('Идем в зеркальную локацию.')
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
    if shared_state.FARMING_STATE in (shared_state.FarmingState.need_potions, shared_state.FarmingState.go_home):
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.SHOP_LOCATION)
    elif shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        await wait_utils.idle_pause()
        await client.send_message(game_bot_name, shared_state.FARMING_LOCATION)
    else:
        logging.warning('Не понятно что делать.')


async def approve(event: events.NewMessage.Event, ) -> None:
    """Подтвержаем."""
    logging.debug('Подтвержаем')
    message = event.message
    context = parsers.strip_message(message.message)
    match = re.search(r"💬 отправляйся в \((\d{1,2})\).*и уничтожь", context)
    if match:
        shared_state.FARMING_LOCATION = match.group(1)
        logging.info(f"FARMING_LOCATION установлен в {shared_state.FARMING_LOCATION}")

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.APPROVE in btn.text:
                    await handle_button_click(btn)


async def search_monster(event: events.NewMessage.Event) -> None:
    """Начинаем поиск монстра."""
    now = datetime.datetime.now()

    if now.hour == 4 and 17 <= now.minute < 45:
        logging.info("Прекращаем поиск, так как время между 02:17 и 03:45.")
        loop.exit_request()
        return

    global HAS_TASKS
    context = parsers.strip_message(event.message.message)
    await update_available_buttons(event, FARM_BUTTONS)

    if 'убить' in context:
        if not HAS_TASKS:
            HAS_TASKS = True
    else:
        HAS_TASKS = False 

    if wait_utils.RELAXING_HUGE_STATE:
        await wait_utils.relaxing_huge()
        wait_utils.RELAXING_HUGE_STATE = False

    await wait_utils.idle_pause()

    if shared_state.FARMING_STATE is shared_state.FarmingState.need_potions and shared_state.KILL_TO_STOP == 0:
        await open_map(event)
        return

    if shared_state.FARMING_STATE is shared_state.FarmingState.go_home and not HAS_TASKS:
        await open_map(event)
        return

    if shared_state.FARMING_STATE is shared_state.FarmingState.to_grinding_zone:
        shared_state.FARMING_STATE = None

    if random.random() < 0.01:
        await wait_utils.relaxing()
    wait_utils.RELAXING_STATE = False
    if (shared_state.KILL_TO_STOP > 0):
        logging.info(f'Необходимо убить мобов до остановки фарма: {shared_state.KILL_TO_STOP}')
        shared_state.KILL_TO_STOP -= 1

    try:
        hp_level = parsers.get_hp_level(event.message.message)
        logging.debug('Уровень здоровья: %d%%', hp_level)
    except Exception as exception:
        hp_level = None
        logging.debug(f'Не удалось получить уровень здоровья: {exception}')

    await wait_utils.human_like_sleep(1, 3)
    await handle_button_event(buttons.FIND_ENEMY, FARM_BUTTONS)


async def vasilisk_heal(event: events.NewMessage.Event) -> None:
    """Отхиливаемся Василиском."""
    found_buttons = buttons.get_buttons_flat(event)
    await wait_utils.wait_for()

    if found_buttons:
        if any(buttons.VASILISK in btn.text for btn in found_buttons):
            logging.info('Выбираем отхил василиском')
            await handle_button_event(buttons.VASILISK, BATTLE_BUTTONS)


async def attack(event: events.NewMessage.Event) -> None:
    """Атакуем противника, проверяя доступные атаки."""
    turn_buttons: Dict[str, List[str]] = {
        'POWER': [],
        'BUFF': [],
        'DEBUFF': [],
    }
    message = event.message

    player_hp_level, enemy_hp_level = await get_health_levels(event)

    if player_hp_level is not None:
        logging.debug('Текущий уровень здоровья игрока: %d%%', player_hp_level)

    if enemy_hp_level is not None:
        logging.debug('Текущий уровень здоровья противника: %d%%', enemy_hp_level)

    vasilisk_threshold = 50
    if app_settings.is_dangeon:
        vasilisk_threshold = 84
    global battle_event, VASILISK_USED, PVP_BATTLE
    if battle_event is not None and not VASILISK_USED and player_hp_level is not None and player_hp_level < vasilisk_threshold and app_settings.use_vasilisk:
        try:
            logging.info('Делаем хил Василиском')
            await vasilisk_heal(battle_event)
            VASILISK_USED = True
        except Exception as e:
            logging.error('Ошибка при отхиливании Василиском: %s', e)

    attack_button = None
    heal_button = None
    heal_threshold = 80
    buff_threshold = 90
    buff_min_threshold = 30
    power_threshold = 93
    if app_settings.is_dangeon:
        heal_threshold = 40
        power_threshold = 30

    if message.buttons:
        for row in message.buttons:
            for btn in row:
                if buttons.SKILL_DELAY not in btn.text:
                    if buttons.BUFF in btn.text and ('Исцеление' in btn.text or 'Целебный поток' in btn.text):
                        heal_button = btn
                    elif buttons.BUFF in btn.text and ('Стойкости' in btn.text or 'Благословение' in btn.text):
                        turn_buttons['BUFF'].append(btn)
                    elif buttons.DEBUFF in btn.text and 'Немощь' in btn.text:
                        turn_buttons['DEBUFF'].append(btn)
                    elif buttons.ATTACK in btn.text and any(element in btn.text for element in ['Огненный', 'Водный', 'Электрический']):
                        turn_buttons['POWER'].append(btn)
                    elif buttons.ATTACK in btn.text:
                        attack_button = btn

    chosen_attack = None
    if player_hp_level is not None and player_hp_level <= heal_threshold and heal_button:
        logging.debug("Игрок имеет низкий уровень здоровья (<80%%), используем Исцеление.")
        chosen_attack = heal_button
    elif player_hp_level is not None and (player_hp_level <= buff_threshold or PVP_BATTLE) and player_hp_level >= buff_min_threshold and turn_buttons['BUFF']:
        logging.info("Игрок имеет низкий уровень здоровья (<90%%), используем атаку из списка BUFF.")
        chosen_attack = random.choice(turn_buttons['BUFF'])
    elif player_hp_level is not None and (player_hp_level <= power_threshold or PVP_BATTLE) and turn_buttons['POWER']:
        logging.debug("Игрок имеет низкий уровень здоровья (<90%%), используем атаку из списка POWER.")
        chosen_attack = random.choice(turn_buttons['POWER'])
    elif attack_button:
        chosen_attack = attack_button
    else:
        logging.warning("Доступных кнопок для атаки не найдено.")
        return

    if chosen_attack:
        try:
            await wait_utils.wait_for()
            await chosen_attack.click()
            logging.debug("Выполнен клик по кнопке: %s", chosen_attack.text)
        except errors.rpcerrorlist.MessageIdInvalidError:
            logging.error("Ошибка: недействительный ID сообщения или кнопка недоступна.")
        except Exception as e:
            logging.error("Неизвестная ошибка при клике по кнопке: %s", e)


async def attack2(event: events.NewMessage.Event) -> None:
    """Выбираем противника."""
    message = event.message

    if message.buttons:
        for row in message.buttons:
            btn = row[0]
            if btn:
                try:
                    await wait_utils.wait_for()
                    await btn.click()
                    logging.debug("Выполнен клик по кнопке: %s", btn.text)
                    return
                except errors.rpcerrorlist.MessageIdInvalidError:
                    logging.error("Ошибка: недействительный ID сообщения или кнопка недоступна. Кнопка: %s", btn.text)
                except Exception as e:
                    logging.error("Неизвестная ошибка при клике по кнопке '%s': %s", btn.text, e)
    else:
        logging.warning("Кнопки в сообщении отсутствуют.")


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
