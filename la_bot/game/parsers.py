"""Event message parsers."""
import base64
import re
from io import BytesIO
from math import ceil

from telethon import events

from la_bot.exceptions import InvalidMessageError
from la_bot.telegram_client import client
from la_bot.settings import app_settings

_hp_level_pattern = re.compile(r'❤️(\d+)/(\d+)')
_energy_level_pattern = re.compile(r'🔋(\d+)/(\d+)')
_statue_tasks_pattern = re.compile(r'выбрано поручений: (\d+)/(\d+)')


def strip_message(original_message: str) -> str:
    """Return message content without EOL symbols."""
    return original_message.replace('\n', ' ').strip().lower()


async def get_photo_base64(event: events.NewMessage.Event) -> str | None:
    """Return message photo as base64 decoded string."""
    image_bytes = BytesIO()
    await client.download_media(
        message=event.message,
        file=image_bytes,
        thumb=-1,
    )
    image_str_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
    return image_str_base64.replace('data:image/png;', '').replace('base64,', '')


def get_hp_level(message_content: str) -> int:
    """Get current HP in percent."""
    current_level, max_level = get_character_hp(message_content)
    return ceil(int(current_level) / int(max_level) * 100)


def get_character_hp(message_content: str) -> tuple[int, int]:
    """Get character HP level."""
    found = _hp_level_pattern.search(strip_message(message_content), re.MULTILINE)
    if not found:
        raise InvalidMessageError('HP not found')

    current_level, max_level = found.group(1, 2)
    return int(current_level), int(max_level)


def get_battle_hps(message_content: str) -> tuple[tuple[int, int], tuple[int, int]]:
    """Получаем HP игрока и противника, учитывая, что app_settings.hero_name указывает на player_hp, если задан."""
    found = _hp_level_pattern.findall(strip_message(message_content))

    if not found or len(found) < 2:
        raise InvalidMessageError('HP levels not found')

    if app_settings.hero_name and app_settings.hero_name.strip():
        player_pos = message_content.find(app_settings.hero_name)

        if player_pos != -1:
            player_hp = (int(found[1][0]), int(found[1][1]))
            enemy_hp = (int(found[0][0]), int(found[0][1]))
        else:
            player_hp = (int(found[0][0]), int(found[0][1]))
            enemy_hp = (int(found[1][0]), int(found[1][1]))
    else:
        player_hp = (int(found[0][0]), int(found[0][1]))
        enemy_hp = (int(found[1][0]), int(found[1][1]))

    return player_hp, enemy_hp


def get_energy(message_content: str) -> int:
    """Get current energy."""
    current_level, _ = get_character_energy(message_content)
    return int(current_level)


def get_character_energy(message_content: str) -> tuple[int, int]:
    """Get character energy."""
    found = _energy_level_pattern.search(strip_message(message_content), re.MULTILINE)
    if not found:
        raise InvalidMessageError('Energy not found')

    current_level, max_level = found.group(1, 2)
    return int(current_level), int(max_level)


def get_tasks_count(message_content: str) -> tuple[int, int]:
    """Возвращает текущее количество поручений и максимальное."""
    taken, max = get_statue_tasks_count(message_content)
    return taken, max


def get_statue_tasks_count(message_content: str) -> tuple[int, int]:
    """Get tasks count.."""
    found = _statue_tasks_pattern.search(strip_message(message_content), re.MULTILINE)
    if not found:
        raise InvalidMessageError('Tasks count not found')

    taken, max = found.group(1, 2)
    return int(taken), int(max)
