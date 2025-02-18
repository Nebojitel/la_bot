"""Random freezes like real-human."""

import asyncio
import enum
import logging
import random

from la_bot.settings import app_settings

RELAXING_STATE = False 
RELAXING_HUGE_STATE = False 


class WaitActions(enum.Enum):
    """
    Timings for game actions.

    Format: NAME = (min, max, min_slow_mode, max_slow_mode)
    """

    COMMON = (1, 2, 9, 19)
    ADDITIONAL_PAUSE = (2, 4, 6, 10)
    LONG_PAUSE = (200, 400, 300, 900)
    SPAM_PAUSE = (45, 100, 300, 900)
    HUGE_PAUSE = (10800, 11000, 10800, 11000)
    CAPTCHA = (1, 2, 1, 2)


async def wait_for(timing: WaitActions = WaitActions.COMMON, idle_chance: float = 0.05) -> None:
    """Let wait like human, with random pauses and behavior."""
    if app_settings.fast_mode:
        return

    min_seconds, max_seconds, min_slow_mode, max_slow_mode = timing.value
    if app_settings.slow_mode:
        sleep_time = random.randint(min_slow_mode, max_slow_mode)
    else:
        sleep_time = random.randint(min_seconds, max_seconds)

    logging.debug('wait like human %d seconds before action', sleep_time)
    await asyncio.sleep(sleep_time)

    if random.random() < idle_chance and timing == WaitActions.COMMON:
        await idle_pause()


async def idle_pause() -> None:
    """Make a random long idle pause like a human could do."""
    sleep_time = random.randint(WaitActions.ADDITIONAL_PAUSE.value[0], WaitActions.ADDITIONAL_PAUSE.value[1])
    logging.debug('idle pause for %d seconds', sleep_time)
    await asyncio.sleep(sleep_time)


async def relaxing() -> None:
    """Pause for a random time like a human taking a break before restarting."""
    global RELAXING_STATE
    RELAXING_STATE = True
    min_long_pause, max_long_pause = (
        WaitActions.LONG_PAUSE.value[:2] if not app_settings.slow_mode else WaitActions.LONG_PAUSE.value[2:]
    )
    relax_time = random.randint(min_long_pause, max_long_pause)
    minutes = relax_time // 60
    logging.info('Relaxing for %d minutes.', minutes)
    await asyncio.sleep(relax_time)


async def relaxing_spam() -> None:
    """relaxing spam"""
    sleep_time = random.randint(WaitActions.SPAM_PAUSE.value[0], WaitActions.SPAM_PAUSE.value[1])
    logging.info('Relaxing spam for %d seconds', sleep_time)
    await asyncio.sleep(sleep_time)


async def relaxing_huge() -> None:
    """relaxing huge"""
    sleep_time = random.randint(WaitActions.HUGE_PAUSE.value[0], WaitActions.HUGE_PAUSE.value[1])
    minutes = sleep_time // 60
    logging.info('Relaxing huge for %d minutes.', minutes)
    await asyncio.sleep(sleep_time)


async def human_like_sleep(min_seconds: int, max_seconds: int) -> None:
    """Random sleep with normal distribution to simulate human pauses."""
    sleep_time = random.normalvariate((min_seconds + max_seconds) / 2, (max_seconds - min_seconds) / 6)
    sleep_time = max(min_seconds, min(max_seconds, sleep_time))
    logging.debug('human-like sleep for %.2f seconds', sleep_time)
    await asyncio.sleep(sleep_time)
