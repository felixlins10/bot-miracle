#!/usr/bin/env python3
"""
Entrada do projeto: delega para o pacote `miracle_bot`.

Estrutura:
- miracle_bot/config.py     — constantes e flags de ambiente
- miracle_bot/state.py      — eventos de pausa/parada (threads)
- miracle_bot/window.py     — janela X11 + xdotool (mouse/teclas)
- miracle_bot/capture.py    — scrot + recortes na imagem
- miracle_bot/battle.py     — baseline e checagem do battle
- miracle_bot/cycle.py      — ciclo de ações no jogo
- miracle_bot/pause_listen.py — Pause/Break via xev
- miracle_bot/main.py       — loop principal

Também pode rodar: python3 -m miracle_bot
"""

from miracle_bot.main import cli

if __name__ == "__main__":
    cli()
