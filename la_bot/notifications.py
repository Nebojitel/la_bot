"""Desktop and other notifications."""

from desktop_notifier import DesktopNotifier, Urgency

from la_bot.settings import app_settings
from la_bot.telegram_client import client

notifier = DesktopNotifier(
    app_name=app_settings.trainer_name,
    app_icon=None,
)


async def send_desktop_notify(message: str, is_urgent: bool = False) -> None:
    """Send desktop notification."""
    if app_settings.notifications_enabled:
        await notifier.send(
            urgency=Urgency.Normal if is_urgent else Urgency.Low,
            title=app_settings.trainer_name,
            message=message,
            timeout=app_settings.desktop_notification_timeout,
        )


async def send_favorites_notify(message: str) -> None:
    """Send message to favorites chat in telegram."""
    if app_settings.favorites_enabled:
        me = await client.get_me()
        await client.send_message(
            me,
            message=message,
            parse_mode='markdown',
        )


async def send_custom_channel_notify(message: str, spam: str = None) -> None:
    """Send a message to a Telegram channel.

    By default, sends to the custom Telegram channel configured in settings.
    If `spam` is provided, sends the message to the spam channel defined in settings.
    """
    destination_channel = app_settings.spam_tg_channel if spam else app_settings.custom_tg_channel

    if not destination_channel:
        raise RuntimeError('No destination channel specified.')

    try:
        destination = await client.get_entity(destination_channel)
        await client.send_message(
            destination,
            message=message,
            parse_mode='markdown',
        )
    except Exception as e:
        raise RuntimeError(f'Failed to send message to channel "{destination_channel}": {e}')
