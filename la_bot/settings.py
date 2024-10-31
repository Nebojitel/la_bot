"""Application settings."""
import os
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings

APP_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
    ),
)


class AppSettings(BaseSettings):
    """Application settings class."""

    # required customer settings
    telegram_api_id: int = 123456
    telegram_api_hash: str = 'u_api_hash'

    # optional customer settings
    minimum_hp_level_for_grinding: int = Field(default=60, ge=1, le=100)
    notifications_enabled: bool = False
    favorites_enabled: bool = True
    custom_tg_channel: str = ''
    self_manager_enabled: bool = False
    stop_if_captcha_fire: bool = False
    captcha_solver_enabled: bool = True
    shop_location: str = ''
    farming_location: str = ''
    use_vasilisk: bool = False

    # advanced customer settings
    anti_captcha_com_apikey: str = Field(default='', description='see https://anti-captcha.com for more information')
    anti_captcha_com_timeout: int = 15
    anti_captcha_com_create_task_tries: int = 3
    anti_captcha_com_create_task_throttling: int = 15
    anti_captcha_com_get_task_tries: int = 20
    anti_captcha_com_get_task_throttling: int = 5

    # developer section
    fast_mode: bool = Field(default=False)
    slow_mode: bool = Field(default=False, description='Used for fresh telegram accounts.')
    ping_commands: str = ',.-+=/0'
    game_username: str = 'lineage2_telegram_bot'
    hero_name: str = ''
    tlg_client_retries: int = 30
    tlg_client_retry_delay: int = 15
    trainer_name: str = 'La Trainer'
    debug: bool = Field(default=False)
    message_log_limit: int = 1000
    wait_loop_iteration_seconds: int = 3
    show_stats_every_seconds: int = 30 * 60
    desktop_notification_timeout: int = 10

app_settings = AppSettings(
    _env_file=os.path.join(APP_PATH, '.env'),  # type: ignore
)

game_bot_name = app_settings.game_username
