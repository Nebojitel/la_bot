import asyncio
from datetime import datetime, timedelta
import logging
from typing import Callable

from telethon import events, types

from la_bot import notifications, stats, wait_utils
from la_bot.game import state
from la_bot.plugins import manager
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client
from la_bot.trainer import event_logging, loop
from la_bot.trainer.handlers import common, farming

last_event_time = None 
CHECK_INTERVAL_SECONDS = 60
INACTIVITY_LIMIT_MINUTES = 3


async def check_last_event_time() -> None:
    """Проверка времени последнего события каждые CHECK_INTERVAL_SECONDS секунд."""
    while True:
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

        if last_event_time is not None and (datetime.now() - last_event_time) > timedelta(minutes=INACTIVITY_LIMIT_MINUTES) and not wait_utils.RELAXING_STATE:
            logging.warning("Не было событий в течение %d минут. Выполняем действия...", INACTIVITY_LIMIT_MINUTES)
            await handle_no_events()


async def handle_no_events() -> None:
    """Обработчик бездействия при отсутствии событий."""
    await notifications.send_custom_channel_notify('бот завис')


async def main(execution_limit_minutes: int | None = None) -> None:
    """Farming runner."""
    local_settings = {
        'execution_limit_minutes': execution_limit_minutes or 'infinite',
        'notifications_enabled': app_settings.notifications_enabled,
        'slow_mode': app_settings.slow_mode,
    }
    logging.info(f'start farming ({local_settings})')

    logging.info('auth as %s', (await client.get_me()).username)

    game_user: types.InputPeerUser = await client.get_input_entity(game_bot_name)
    logging.info('game user is %s', game_user)

    await wait_utils.idle_pause()
    # await client.send_message(game_bot_name, '/start')

    await _setup_handlers(game_user_id=game_user.user_id)

    asyncio.create_task(check_last_event_time())

    await loop.run_wait_loop(execution_limit_minutes)
    logging.info('end farming')


async def _setup_handlers(game_user_id: int) -> None:
    if app_settings.self_manager_enabled:
        manager.setup(client)

    client.add_event_handler(
        callback=_message_handler,
        event=events.NewMessage(
            incoming=True,
            from_users=(game_user_id,),
        ),
    )
    client.add_event_handler(
        callback=_message_handler,
        event=events.MessageEdited(
            incoming=True,
            from_users=(game_user_id,),
        ),
    )


async def _message_handler(event: events.NewMessage.Event) -> None:
    await event_logging.log_event_information(event)
    stats.collector.inc_value('events')

    await event.message.mark_read()

    select_callback = _select_action_by_event(event)

    await select_callback(event)


def _select_action_by_event(event: events.NewMessage.Event) -> Callable:
    global last_event_time
    last_event_time = datetime.now()

    mapping = [
        # (state.common_states.is_captcha_message, common.captcha_fire_handler),

        # (state.common_states.is_quest_completed, farming.quest_is_done),
        # (state.common_states.is_win_message, farming.search_monster),
        # (state.common_states.is_death_message, farming.hero_is_died),
        # (state.common_states.is_attack_message, farming.attack),
        # (state.common_states.is_enemy_found_message, farming.enemy_found),
        # (state.common_states.is_search_started_message, farming.enemy_search_started),

        # (state.common_states.is_low_on_potions, farming.need_to_buy_potions),
        # (state.common_states.is_energy_depleted, farming.need_energy_potions),
        # (state.common_states.is_refresh_message, farming.refresh),

        # (state.common_states.is_at_location, farming.process_location),        

        # (state.common_states.is_map_opened_message, farming.go_to),
        # (state.common_states.is_specify_location_message, farming.specify_location),
        # (state.common_states.need_to_approve_state, farming.approve),

        # (state.common_states.is_citizens_message, farming.pick_citizen),
        # (state.common_states.is_seller_message, farming.process_seller),
        # (state.common_states.is_statue_message, farming.process_statue),
        # (state.common_states.is_quest_taken, farming.quest_taken),
    ]

    for check_function, callback_function in mapping:
        if check_function(event):
            logging.debug('is %s event', check_function.__name__)
            return callback_function
    return common.skip_turn_handler
