"""Numbers from image captcha resolver."""

import logging

from telethon import events

from la_bot.captcha import anti_captcha_provider
from la_bot.captcha.symbol_traps_utils import replace_eng_chars
from la_bot.game.parsers import get_photo_base64

_common_pattern = 'решипростойматематическийпример'


async def image_with_numbers(message: str, event: events.NewMessage.Event) -> str | None:
    """Resolve image captcha by 3th-party service."""
    if not event.message.media:
        logging.warning('No media found in the message.')
        return None

    question = replace_eng_chars(source=message.lower().replace(' ', ''))
    if _common_pattern not in question:
        logging.info(f'Question does not match common pattern: {question}')
        return None

    image_source = await get_photo_base64(event)
    if not image_source:
        logging.warning(f'captcha event - image not found! "{image_source}"')
        return None

    try:
        answer = await anti_captcha_provider.resolve_image_to_number(image_source)
        if answer is None:
            logging.warning('Failed to resolve captcha image.')
            return None
        logging.info(f'Captcha resolved with answer: {answer}')
        return answer
    except Exception as e:
        logging.error(f'Error resolving captcha: {e}')
        return None
