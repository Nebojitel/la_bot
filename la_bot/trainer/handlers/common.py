"""Common handlers."""
import logging

from telethon import events

from la_bot import notifications, stats, shared_state, wait_utils
from la_bot.captcha import resolvers
from la_bot.game import action
from la_bot.settings import app_settings
from la_bot.trainer import loop


async def skip_turn_handler(_: events.NewMessage.Event) -> None:
    """Just skip event."""
    logging.info('skip event')
    await wait_utils.wait_for()


async def captcha_fire_handler(event: events.NewMessage.Event) -> None:
    """Try to solve captcha."""
    logging.warning('captcha event shot!')

    stats.collector.inc_value('captcha-s')
    await notifications.send_custom_channel_notify(f'Capcha!!! Solve math task {shared_state.USER_NAME}')

    if app_settings.captcha_solver_enabled:
        captcha_answer = await resolvers.try_resolve(event)
        logging.info(f'captcha answer {captcha_answer}')

        if captcha_answer.answer:
            await action.common_actions.captcha_answer(event, captcha_answer.answer)
        else:
            await notifications.send_custom_channel_notify('captcha not solved!')

    elif app_settings.stop_if_captcha_fire:
        loop.exit_request()


async def button_fire_handler(event: events.NewMessage.Event) -> None:
    """Press the button captcha."""
    logging.warning('press the button event shot!')

    stats.collector.inc_value('captcha-s')
    await notifications.send_custom_channel_notify(f'Capcha!!! Press the button for {shared_state.USER_NAME}!!!')
