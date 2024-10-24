"""Command-line interface."""
import logging
import signal
from typing import Any, Callable

from la_bot.settings import app_settings
from la_bot.telegram_client import client
from la_bot.trainer import (
    loop,
    farming,
)

def farming_start() -> None:
    """Start farming."""
    _run(farming.main)


def _run(main_func: Callable, *args: Any, **kwargs: Any) -> None:
    _setup_logging()
    signal.signal(signal.SIGINT, loop.exit_request)
    try:
        with client:
            client.loop.run_until_complete(main_func(*args, **kwargs))
    except ConnectionError:
        loop.exit_request()


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if app_settings.debug else logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',  # noqa: WPS323
    )
