"""Toggle de pausa com Pause/Break quando a janela do Miracle está em foco."""

from __future__ import annotations

import re
import subprocess
from typing import Optional

from miracle_bot import state
from miracle_bot.window import find_window_id, get_window_context, window_has_focus


def pause_listener() -> None:
    proc = subprocess.Popen(
        ["xev", "-root", "-event", "keyboard"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        bufsize=1,
    )
    event_type: Optional[str] = None
    keysym_re = re.compile(r"keysym:\s*([A-Za-z0-9_]+)")

    try:
        assert proc.stdout is not None
        for line in proc.stdout:
            if state.STOP_EVENT.is_set():
                break

            if "KeyPress" in line:
                event_type = "KeyPress"
                continue
            if "KeyRelease" in line:
                event_type = "KeyRelease"
                continue

            m = keysym_re.search(line)
            if not m or event_type != "KeyPress":
                continue

            key_sym_norm = m.group(1).strip().lower()
            is_pause = key_sym_norm == "pause" or key_sym_norm.startswith("pause")
            is_break = key_sym_norm == "break" or key_sym_norm.startswith("break")
            if not (is_pause or is_break):
                continue

            wid = find_window_id()
            if not wid:
                continue
            wctx = get_window_context(wid)
            if not wctx or not window_has_focus(wctx):
                continue

            if state.PAUSED_EVENT.is_set():
                state.PAUSED_EVENT.clear()
                print("PAUSADO: OFF")
            else:
                state.PAUSED_EVENT.set()
                print("PAUSADO: ON")
    finally:
        try:
            proc.terminate()
        except OSError:
            pass
