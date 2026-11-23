"""
cola.py — COLA (Queue), estructura FIFO (First In, First Out).

Semana 6 del curso: "Colas. Procesamiento por turnos. Eventos pendientes."

Se implementa sobre `collections.deque`, que ofrece inserción y extracción por
ambos extremos en O(1). Con una lista normal, `pop(0)` sería O(n) porque hay
que desplazar todos los elementos; por eso NO se usa una lista aquí.

También se incluye `ColaPrioridad` (montículo binario vía heapq) para el
sistema de turnos por iniciativa.

Análisis de complejidad
-----------------------
    Cola (deque):
        encolar   -> O(1)
        desencolar-> O(1)
        frente    -> O(1)
    ColaPrioridad (heap):
        encolar   -> O(log n)
        desencolar-> O(log n)
        frente    -> O(1)
    Espacio -> O(n)
"""

from collections import deque
import heapq
import itertools


class ColaVacia(Exception):
    pass


class Cola:
    """Cola FIFO clásica."""

    def __init__(self, iterable=None):
        self._datos = deque(iterable) if iterable else deque()

    def encolar(self, elemento):
        """enqueue: agrega al final. O(1)."""
        self._datos.append(elemento)

    def desencolar(self):
        """dequeue: quita y devuelve el del frente. O(1)."""
        if self.esta_vacia():
            raise ColaVacia("No se puede desencolar: la cola está vacía.")
        return self._datos.popleft()

    def frente(self):
        """Devuelve el elemento del frente sin quitarlo. O(1)."""
        if self.esta_vacia():
            raise ColaVacia("La cola está vacía.")
        return self._datos[0]

    def esta_vacia(self):
        return len(self._datos) == 0

    def __len__(self):
        return len(self._datos)

    def __iter__(self):
        return iter(self._datos)

    def __contains__(self, elemento):
        return elemento in self._datos

    def a_lista(self):
        return list(self._datos)

    def __repr__(self):
        return f"Cola(frente -> {list(self._datos)})"


class ColaPrioridad:
    """
    Cola de prioridad sobre un montículo (heapq).

    Por defecto es un min-heap: sale primero el de MENOR prioridad numérica.
    Para el sistema de turnos queremos que actúe primero quien tiene MAYOR
    iniciativa, así que al encolar se guarda la prioridad negada.
    """

    def __init__(self, max_primero=True):
        self._heap = []
        self._contador = itertools.count()  # desempata y evita comparar objetos
        self._signo = -1 if max_primero else 1

    def encolar(self, elemento, prioridad):
        """O(log n)."""
        heapq.heappush(self._heap, (self._signo * prioridad, next(self._contador), elemento))

    def desencolar(self):
        """O(log n)."""
        if not self._heap:
            raise ColaVacia("La cola de prioridad está vacía.")
        return heapq.heappop(self._heap)[2]

    def frente(self):
        if not self._heap:
            raise ColaVacia("La cola de prioridad está vacía.")
        return self._heap[0][2]

    def esta_vacia(self):
        return not self._heap

    def __len__(self):
        return len(self._heap)
