"""Detecção do battle a partir de um frame já capturado (crop + variância)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from typing import Any

from PIL import Image, ImageStat

from miracle_bot import config
from miracle_bot import state
from miracle_bot import capture
from miracle_bot.window import WindowContext, send_key


def battle_danger_from_crop(crop: Image.Image, baseline: dict[str, Any]) -> bool:
    cur_var = capture.grayscale_variance_rgb(crop)
    base_var = float(baseline["var"])
    mult = float(baseline.get("multiplier_used", config.BATTLE_VAR_MULTIPLIER))
    return cur_var > base_var * mult


def check_safety_with_frame(
    ctx: WindowContext,
    frame: Image.Image,
    baseline: dict[str, Any],
    *,
    force: bool,
) -> None:
    if not config.USE_BATTLE_SCREENSHOT:
        return
    if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
        return

    now = time.monotonic()
    if (
        not force
        and config.BATTLE_POLL_INTERVAL_SEC > 0
        and (now - state.last_battle_check_mono) < config.BATTLE_POLL_INTERVAL_SEC
    ):
        return
    state.last_battle_check_mono = now

    battle_crop = capture.crop_client_region(frame, ctx, config.BATTLE_AREA)
    if battle_danger_from_crop(battle_crop, baseline):
        _trigger_danger_logout(ctx)


def _trigger_danger_logout(ctx: WindowContext) -> None:
    print("!!! PERIGO DETECTADO (battle) !!!")
    try:
        send_key(ctx, "ctrl+l")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, OSError):
        pass
    subprocess.Popen(
        ["mplayer", "/usr/share/sounds/freedesktop/stereo/alarm-clock-elapsed.oga"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    state.STOP_EVENT.set()
    sys.exit(0)


def calibrate_battle_baseline(ctx: WindowContext) -> dict[str, Any]:
    print("Calibrando detecção de battle (uma captura da janela inteira + crop do battle).")
    print("1) Deixe o battle VAZIO (sem player/monstro).")
    input("2) Quando estiver pronto, pressione Enter aqui no terminal...")

    frame = capture.capture_full_window_frame(ctx)
    battle_crop = capture.crop_client_region(frame, ctx, config.BATTLE_AREA)
    stat = ImageStat.Stat(battle_crop.convert("L"))
    return {
        "mean": float(stat.mean[0]),
        "var": float(stat.var[0]),
        "multiplier_used": config.BATTLE_VAR_MULTIPLIER,
        "window_title_regex": config.WINDOW_TITLE_REGEX,
    }


def load_or_calibrate_baseline(ctx: WindowContext) -> dict[str, Any]:
    if not config.USE_BATTLE_SCREENSHOT:
        return {"var": 999999.0, "multiplier_used": config.BATTLE_VAR_MULTIPLIER, "disabled": True}

    if not config.USE_BATTLE_CALIBRATION:
        return {"var": 999999.0, "multiplier_used": config.BATTLE_VAR_MULTIPLIER}

    try:
        if os.path.exists(config.BATTLE_BASELINE_FILE):
            with open(config.BATTLE_BASELINE_FILE, encoding="utf-8") as f:
                data = json.load(f)
            if "var" in data:
                return data
    except (OSError, json.JSONDecodeError):
        pass

    baseline = calibrate_battle_baseline(ctx)
    try:
        with open(config.BATTLE_BASELINE_FILE, "w", encoding="utf-8") as f:
            json.dump(baseline, f, indent=2)
    except OSError:
        pass
    return baseline
