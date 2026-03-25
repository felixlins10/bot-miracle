"""Um ciclo de ações no jogo (inventário, pesca, runa)."""

from __future__ import annotations

import random
import time

from miracle_bot import config
from miracle_bot import state
from miracle_bot.window import (
    WindowContext,
    mouse_click_relative,
    mouse_drag_relative,
    send_key,
)


def sleep_with_pause(seconds: float) -> None:
    end = time.monotonic() + max(0.0, seconds)
    while time.monotonic() < end:
        if state.STOP_EVENT.is_set():
            return
        if state.PAUSED_EVENT.is_set():
            while state.PAUSED_EVENT.is_set() and not state.STOP_EVENT.is_set():
                time.sleep(0.05)
            end = time.monotonic() + max(0.0, seconds)
        time.sleep(0.05)


def executar_ciclo(ctx: WindowContext) -> None:
    if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
        return

    mouse_drag_relative(
        ctx, config.BP2_PRIMEIRO_SLOT, config.MAO_ESQUERDA, duration=0.5, button=config.BTN_LEFT
    )

    if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
        return

    mouse_click_relative(
        ctx, config.PE_PERSONAGEM[0], config.PE_PERSONAGEM[1], button=config.BTN_RIGHT
    )
    sleep_with_pause(random.uniform(0.5, 1.2))

    if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
        return

    mouse_click_relative(ctx, config.SLOT_VARA[0], config.SLOT_VARA[1], button=config.BTN_RIGHT)
    sleep_with_pause(0.3)
    tile = random.choice(config.AGUA_TILES)
    mouse_click_relative(ctx, tile[0], tile[1], button=config.BTN_LEFT)

    if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
        return

    send_key(ctx, "shift+F1")
    sleep_with_pause(1.0)

    mouse_drag_relative(
        ctx, config.MAO_ESQUERDA, config.BP1_ULTIMO_SLOT, duration=0.5, button=config.BTN_LEFT
    )
