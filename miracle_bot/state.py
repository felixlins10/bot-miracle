"""Estado compartilhado entre o loop principal e a thread do Pause/Break."""

import threading

PAUSED_EVENT = threading.Event()
STOP_EVENT = threading.Event()

# Throttle da checagem do battle (monotonic seconds).
last_battle_check_mono: float = 0.0
