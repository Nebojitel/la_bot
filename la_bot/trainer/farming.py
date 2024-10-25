import logging
from typing import Callable

from telethon import events, types

from la_bot import stats
from la_bot.game import action, state
from la_bot.plugins import manager
from la_bot.settings import app_settings, game_bot_name
from la_bot.telegram_client import client
from la_bot.trainer import event_logging, loop
from la_bot.trainer.handlers import common, farming


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

    await client.send_message(game_bot_name, '/start')

    await _setup_handlers(game_user_id=game_user.user_id)

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
    mapping = [
        (state.common_states.is_captcha_message, common.captcha_fire_handler),
        (state.common_states.is_quest_done, common.quest_is_done),

        (state.common_states.is_start_state, farming.start_farming),
        (state.common_states.is_win_state, farming.search_monster),
        # (state.common_states.is_alive_state, farming.start_farming),
        (state.common_states.is_attack_state, farming.attack),
    ]

    for check_function, callback_function in mapping:
        if check_function(event):
            logging.debug('is %s event', check_function.__name__)
            return callback_function
    return common.skip_turn_handler
