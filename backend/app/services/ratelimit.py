"""Limitador de taxa em memória.

Suficiente para uma instância do protótipo. Em produção, substituir por Redis
(ou limitador no API Gateway) — ver docs/07-seguranca-lgpd.md.
"""

from __future__ import annotations

import threading
import time
from collections import deque


class RateLimiter:
    def __init__(self, limite: int, janela_segundos: int) -> None:
        self.limite = limite
        self.janela = janela_segundos
        self._eventos: dict[str, deque[float]] = {}
        self._trava = threading.Lock()

    def verificar(self, chave: str) -> tuple[bool, int]:
        """Retorna (permitido, segundos_para_tentar_novamente)."""
        agora = time.monotonic()
        with self._trava:
            fila = self._eventos.setdefault(chave, deque())
            while fila and agora - fila[0] > self.janela:
                fila.popleft()
            if len(fila) >= self.limite:
                espera = max(1, int(self.janela - (agora - fila[0])))
                return False, espera
            fila.append(agora)
            if len(self._eventos) > 10_000:  # higiene de memória
                for k in [k for k, v in self._eventos.items() if not v][:1000]:
                    self._eventos.pop(k, None)
            return True, 0

    def limpar(self) -> None:
        with self._trava:
            self._eventos.clear()
