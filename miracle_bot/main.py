"""Ponto de entrada: loop principal e orquestração."""

from __future__ import annotations

import random
import sys
import threading
import time

from miracle_bot import battle
from miracle_bot import capture
from miracle_bot import config
from miracle_bot import cycle
from miracle_bot import pause_listen
from miracle_bot import state
from miracle_bot.window import find_window_id, get_window_context, wait_for_window


def main() -> None:
    print(
        "Miracle bot — ações via xdotool na janela; visão: 1× scrot da janela inteira, crops em RAM."
    )
    if not config.USE_BATTLE_SCREENSHOT:
        print("Battle por pixel: desligado (RUNADOR_DISABLE_BATTLE_SCREENSHOT).")
    else:
        try:
            capture.require_scrot()
        except RuntimeError as e:
            print(f"ERRO: {e}")
            sys.exit(1)
        print("Battle: captura da janela inteira + recorte do battle na imagem.")

    time.sleep(2)
    ctx = wait_for_window()
    baseline = battle.load_or_calibrate_baseline(ctx)

    threading.Thread(target=pause_listen.pause_listener, daemon=True).start()

    while not state.STOP_EVENT.is_set():
        if state.PAUSED_EVENT.is_set():
            time.sleep(0.1)
            continue

        wid = find_window_id()
        if not wid:
            time.sleep(1.0)
            continue
        ctx = get_window_context(wid)
        if not ctx:
            time.sleep(1.0)
            continue

        if config.USE_BATTLE_SCREENSHOT:
            frame = capture.capture_full_window_frame(ctx)
            battle.check_safety_with_frame(ctx, frame, baseline, force=True)

        cycle.executar_ciclo(ctx)

        delay_sec = random.randint(config.RUN_MIN_DELAY_SEC, config.RUN_MAX_DELAY_SEC)
        for _ in range(delay_sec):
            if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
                break
            if config.USE_BATTLE_SCREENSHOT:
                frame = capture.capture_full_window_frame(ctx)
                battle.check_safety_with_frame(ctx, frame, baseline, force=False)
            cycle.sleep_with_pause(1.0)


def cli() -> None:
    try:
        main()
    except KeyboardInterrupt:
        state.STOP_EVENT.set()
        print("\nEncerrado pelo usuário.")
