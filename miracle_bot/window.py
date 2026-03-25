"""Descoberta da janela X11 e entrada (xdotool: mouse/teclas)."""

from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
from typing import Optional, Tuple

from miracle_bot import config
from miracle_bot import state


@dataclass(frozen=True)
class WindowContext:
    """Janela X11 + inset do conteúdo do jogo em relação ao frame da janela."""

    wid: str
    win_x: int
    win_y: int
    win_w: int
    win_h: int
    inset_x: int
    inset_y: int

    def client_to_window_pixels(self, client_x: int, client_y: int) -> Tuple[int, int]:
        return (client_x + self.inset_x, client_y + self.inset_y)


def _run_xdotool(args: list[str], *, timeout_s: float = 5.0) -> str:
    out = subprocess.check_output(["xdotool", *args], text=True, timeout=timeout_s)
    return out.strip()


def get_active_window_id() -> Optional[str]:
    try:
        wid = _run_xdotool(["getactivewindow"], timeout_s=2.0)
        return wid or None
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None


def find_window_id() -> Optional[str]:
    try:
        out = _run_xdotool(
            ["search", "--onlyvisible", "--name", config.WINDOW_TITLE_REGEX],
            timeout_s=2.0,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

    if not out:
        return None
    matches = [line.strip() for line in out.splitlines() if line.strip()]
    if not matches:
        return None

    active = get_active_window_id()
    if active and active in matches:
        return active
    return matches[0]


def get_window_context(wid: str) -> Optional[WindowContext]:
    try:
        out = _run_xdotool(["getwindowgeometry", "--shell", wid], timeout_s=2.0)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return None

    values: dict[str, int] = {}
    for line in out.splitlines():
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip()
        if key in {"X", "Y", "WIDTH", "HEIGHT"}:
            values[key] = int(val)

    if not {"X", "Y", "WIDTH", "HEIGHT"}.issubset(values.keys()):
        return None

    ix, iy = config.CONTENT_INSET_XY
    return WindowContext(
        wid=wid,
        win_x=values["X"],
        win_y=values["Y"],
        win_w=values["WIDTH"],
        win_h=values["HEIGHT"],
        inset_x=ix,
        inset_y=iy,
    )


def window_has_focus(ctx: WindowContext) -> bool:
    active = get_active_window_id()
    return bool(active and active == ctx.wid)


def mouse_move_relative(ctx: WindowContext, x: int, y: int) -> None:
    wx, wy = ctx.client_to_window_pixels(x, y)
    _run_xdotool(["mousemove", "--window", ctx.wid, str(wx), str(wy)], timeout_s=2.0)


def mouse_click_relative(ctx: WindowContext, x: int, y: int, *, button: int) -> None:
    mouse_move_relative(ctx, x, y)
    _run_xdotool(["click", "--window", ctx.wid, str(button)], timeout_s=2.0)


def mouse_drag_relative(
    ctx: WindowContext,
    start_xy: Tuple[int, int],
    end_xy: Tuple[int, int],
    *,
    duration: float = 0.5,
    steps: int = 6,
    button: int = config.BTN_LEFT,
) -> None:
    steps = max(steps, 2)
    sx, sy = start_xy
    ex, ey = end_xy
    mouse_move_relative(ctx, sx, sy)
    _run_xdotool(["mousedown", "--window", ctx.wid, str(button)], timeout_s=2.0)

    for i in range(1, steps + 1):
        if state.STOP_EVENT.is_set() or state.PAUSED_EVENT.is_set():
            break
        t = i / steps
        cx = int(sx + (ex - sx) * t)
        cy = int(sy + (ey - sy) * t)
        mouse_move_relative(ctx, cx, cy)
        time.sleep(duration / steps)

    _run_xdotool(["mouseup", "--window", ctx.wid, str(button)], timeout_s=2.0)


def send_key(ctx: WindowContext, keysequence: str) -> None:
    _run_xdotool(["key", "--window", ctx.wid, "--clearmodifiers", keysequence], timeout_s=2.0)


def wait_for_window() -> WindowContext:
    while not state.STOP_EVENT.is_set():
        wid = find_window_id()
        if wid:
            ctx = get_window_context(wid)
            if ctx:
                return ctx
        time.sleep(1.0)
    raise RuntimeError("Interrompido antes de encontrar a janela do Miracle.")
