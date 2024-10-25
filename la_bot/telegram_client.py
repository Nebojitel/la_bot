"""Telegram client."""

from telethon import TelegramClient
import random
from la_bot.settings import app_settings

# Один раз выбираем устройство для текущей сессии
selected_device = random.choice(['iPhone', 'Android', 'Windows'])

# Правдоподобные параметры для каждого устройства
device_data = {
    'iPhone': {
        'system_version': '14.4',
        'app_version': '8.4',
    },
    'Android': {
        'system_version': '11',
        'app_version': '8.1.0',
    },
    'Windows': {
        'system_version': '10',
        'app_version': '3.0',
    },
}

device_model = selected_device
system_version = device_data[device_model]['system_version']
app_version = device_data[device_model]['app_version']

client = TelegramClient(
    session='.la_bot',
    api_id=app_settings.telegram_api_id,
    api_hash=app_settings.telegram_api_hash,
    auto_reconnect=True,
    connection_retries=random.randint(3, 10),
    retry_delay=random.uniform(1.0, 3.0),
    device_model=device_model,
    system_version=system_version,
    app_version=app_version,
)
