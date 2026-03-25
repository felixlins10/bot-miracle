"""Captura da janela com scrot e recortes em coordenadas do cliente."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageStat

from miracle_bot import config
from miracle_bot.config import ClientRect
from miracle_bot.window import WindowContext


def require_scrot() -> None:
    if not shutil.which("scrot"):
        raise RuntimeError(
            "Comando 'scrot' não encontrado no PATH. Instale com: sudo apt install scrot "
            "ou use RUNADOR_DISABLE_BATTLE_SCREENSHOT=1."
        )


def capture_screen_rectangle(left: int, top: int, width: int, height: int) -> Image.Image:
    """Uma captura scrot do retângulo de tela; PNG temporário removido após leitura."""
    if width <= 0 or height <= 0:
        raise ValueError("Largura/altura da captura devem ser positivas.")
    require_scrot()

    geo = f"{width}x{height}+{left}+{top}"
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    try:
        proc = subprocess.run(
            ["scrot", "-z", "-a", geo, path],
            check=False,
            timeout=config.SCROT_TIMEOUT_SEC,
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            msg = (proc.stderr or proc.stdout or "").strip()
            raise RuntimeError(f"scrot falhou ({proc.returncode}): {msg or 'sem mensagem'}")
        return Image.open(path).convert("RGB")
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def capture_full_window_frame(ctx: WindowContext) -> Image.Image:
    """Captura a janela inteira (outer geometry do xdotool) em uma única imagem."""
    return capture_screen_rectangle(ctx.win_x, ctx.win_y, ctx.win_w, ctx.win_h)


def crop_client_region(frame: Image.Image, ctx: WindowContext, region: ClientRect) -> Image.Image:
    """
    Recorta região em coords do cliente a partir do frame da janela inteira
    (origem do frame = canto superior esquerdo da janela X11).
    """
    rx, ry, rw, rh = region
    x0, y0 = ctx.client_to_window_pixels(rx, ry)
    x1, y1 = x0 + rw, y0 + rh
    fw, fh = frame.size
    if x0 < 0 or y0 < 0 or x1 > fw or y1 > fh:
        raise ValueError(
            f"Região do cliente fora do frame da janela: frame={frame.size}, "
            f"crop em pixels de janela=({x0},{y0})-({x1},{y1})"
        )
    return frame.crop((x0, y0, x1, y1))


def grayscale_variance_rgb(image: Image.Image) -> float:
    stat = ImageStat.Stat(image.convert("L"))
    return float(stat.var[0])
