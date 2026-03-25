"""Constantes e flags de ambiente (coordenadas, timing, paths)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Final, Tuple, TypeAlias

# Raiz do projeto = pasta que contém `runador.py` e este pacote.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

ClientRect: TypeAlias = Tuple[int, int, int, int]  # x, y, width, height (coords do cliente)

WINDOW_TITLE_REGEX: Final[str] = r"Miracle\s*7\.4"
CONTENT_INSET_XY: Final[Tuple[int, int]] = (0, 0)

MAO_ESQUERDA: Final[Tuple[int, int]] = (888, 303)
SLOT_VARA: Final[Tuple[int, int]] = (912, 335)
PE_PERSONAGEM: Final[Tuple[int, int]] = (450, 480)
BP2_PRIMEIRO_SLOT: Final[Tuple[int, int]] = (815, 235)
BP1_ULTIMO_SLOT: Final[Tuple[int, int]] = (980, 205)
BATTLE_AREA: Final[ClientRect] = (815, 65, 175, 150)

AGUA_TILES: Final[Tuple[Tuple[int, int], ...]] = (
    (410, 350),
    (450, 320),
    (350, 400),
    (300, 450),
)

USE_BATTLE_CALIBRATION: Final[bool] = True
BATTLE_BASELINE_FILE: Final[str] = str(_PROJECT_ROOT / "battle_baseline.json")
BATTLE_VAR_MULTIPLIER: Final[float] = 2.0

RUN_MIN_DELAY_SEC: Final[int] = 15
RUN_MAX_DELAY_SEC: Final[int] = 30
BATTLE_POLL_INTERVAL_SEC: Final[float] = 10.0

BTN_LEFT: Final[int] = 1
BTN_RIGHT: Final[int] = 3

SCROT_TIMEOUT_SEC: Final[int] = 15


def env_truthy(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in ("1", "true", "yes")


USE_BATTLE_SCREENSHOT: Final[bool] = not env_truthy("RUNADOR_DISABLE_BATTLE_SCREENSHOT")
