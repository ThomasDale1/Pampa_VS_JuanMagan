"""
turnos.py — COLA APLICADA: sistema de turnos y COLA DE EVENTOS pendientes.

Semana 6: "Colas. Procesamiento por turnos. Eventos pendientes. Sistema de
          turnos o eventos usando colas."

Dos usos de cola:

  1. SistemaTurnos: el orden de cada ronda se decide por INICIATIVA
     (velocidad + azar) usando una COLA DE PRIORIDAD (montículo binario,
     `cola.ColaPrioridad`); también existe el modo "ordenamiento" que usa
     ordenamiento por INSERCIÓN. Ese orden se vuelca en una COLA FIFO normal:
     tras actuar, el combatiente vuelve al final de la cola.

  2. ColaEventos: una COLA de EVENTOS PENDIENTES con cuenta atrás. Cada ronda
     se procesa: cada evento resta 1 a su contador y, al llegar a 0, se
     dispara (veneno, sangrado, fin de un buff, patrulla de Juan Magán...).

Complejidad
-----------
    Cola FIFO: encolar / desencolar    -> O(1)
    ColaPrioridad: encolar / desencolar -> O(log n)
    ordenar iniciativa (heap)          -> O(n log n)
    ordenar iniciativa (inserción)     -> O(n^2) peor, O(n) casi-ordenada; n<=4
    procesar_ronda (k eventos)         -> O(k)
"""

import random

from .cola import Cola, ColaPrioridad
from . import ordenamiento


class SistemaTurnos:
    def __init__(self, combatientes, metodo="heap"):
        """
        metodo = "heap"        -> el orden de la ronda se establece con una
                                  COLA DE PRIORIDAD (montículo), O(n log n).
               = "ordenamiento"-> se establece con ordenamiento por INSERCIÓN
                                  (útil porque la lista suele venir casi
                                  ordenada de la ronda anterior).
        Después, dentro de la ronda, se usa una COLA FIFO normal: quien actúa
        vuelve al final.
        """
        self.cola = Cola()
        self.metodo = metodo
        self.orden_inicial = []
        self._reordenar(combatientes)

    def _reordenar(self, combatientes):
        vivos = [c for c in combatientes if c.vivo]
        # iniciativa = velocidad efectiva + tirada de 1..6
        con_iniciativa = [(c, c.velocidad + random.randint(1, 6)) for c in vivos]

        if self.metodo == "heap":
            pq = ColaPrioridad(max_primero=True)     # mayor iniciativa -> antes
            for c, ini in con_iniciativa:
                pq.encolar(c, ini)
            ordenados = []
            mapa_ini = {id(c): ini for c, ini in con_iniciativa}
            while not pq.esta_vacia():
                c = pq.desencolar()
                ordenados.append((c, mapa_ini[id(c)]))
        else:
            ordenados, _ = ordenamiento.ordenamiento_insercion(
                con_iniciativa, clave=lambda par: par[1], reverse=True)

        self.orden_inicial = [(c.nombre, ini) for c, ini in ordenados]
        for c, _ini in ordenados:
            self.cola.encolar(c)

    def hay_turnos(self):
        return not self.cola.esta_vacia()

    def siguiente(self):
        return self.cola.desencolar()

    def devolver_al_final(self, combatiente):
        if combatiente.vivo:
            self.cola.encolar(combatiente)

    def agregar_combatiente(self, combatiente):
        self.cola.encolar(combatiente)

    def snapshot(self):
        return [c.nombre for c in self.cola]


class Evento:
    def __init__(self, nombre, turnos_restantes, accion, periodo=1, cargas=1):
        self.nombre = nombre
        self.turnos_restantes = turnos_restantes
        self.accion = accion            # callable() -> str | None
        self.periodo = periodo
        self.cargas = cargas            # nº de veces que aún puede dispararse

    def __repr__(self):
        return f"Evento({self.nombre}, en {self.turnos_restantes}, x{self.cargas})"


class ColaEventos:
    """COLA de eventos pendientes con cuenta atrás por rondas."""

    def __init__(self):
        self.cola = Cola()

    # -- programación -------------------------------------------------
    def programar(self, nombre, en_turnos, accion, periodo=1, cargas=1):
        self.cola.encolar(Evento(nombre, en_turnos, accion, periodo, cargas))

    def programar_veneno(self, entidad, turnos, dano_por_turno):
        entidad.aplicar_efecto("veneno", turnos, dano_por_turno)

        def tic():
            if not entidad.vivo:
                return None
            entidad.recibir_dano(dano_por_turno, ignora_defensa=True)
            for e in entidad.efectos:
                if e["tipo"] == "veneno":
                    e["turnos"] -= 1
            entidad.limpiar_efectos_expirados()
            return f"{entidad.nombre} sufre {dano_por_turno} de daño por VENENO."

        self.programar(f"veneno:{entidad.nombre}", 1, tic, periodo=1, cargas=turnos)

    def programar_sangrado(self, entidad, turnos, dano_por_turno):
        entidad.aplicar_efecto("sangrado", turnos, dano_por_turno)

        def tic():
            if not entidad.vivo:
                return None
            entidad.recibir_dano(dano_por_turno, ignora_defensa=True)
            for e in entidad.efectos:
                if e["tipo"] == "sangrado":
                    e["turnos"] -= 1
            entidad.limpiar_efectos_expirados()
            return f"{entidad.nombre} pierde {dano_por_turno} de vida por SANGRADO."

        self.programar(f"sangrado:{entidad.nombre}", 1, tic, periodo=1, cargas=turnos)

    def programar_buff_temporal(self, entidad, tipo, valor, turnos, etiqueta):
        entidad.aplicar_efecto(tipo, turnos, valor)

        def fin():
            entidad.efectos = [e for e in entidad.efectos if e["tipo"] != tipo]
            return f"El efecto de {etiqueta} se disipa en {entidad.nombre}."

        self.programar(f"buff:{tipo}:{entidad.nombre}", turnos, fin, cargas=1)

    # -- procesamiento ---------------------------------------------
    def procesar_ronda(self):
        """
        Recorre TODA la cola una vez (FIFO): resta 1 turno a cada evento; los
        que llegan a 0 se disparan y, si aún tienen cargas, se reprograman.
        Devuelve la lista de mensajes generados.
        """
        mensajes = []
        pendientes = []
        while not self.cola.esta_vacia():
            ev = self.cola.desencolar()
            ev.turnos_restantes -= 1
            if ev.turnos_restantes <= 0:
                msg = ev.accion()
                if msg:
                    mensajes.append(msg)
                ev.cargas -= 1
                if ev.cargas > 0:
                    ev.turnos_restantes = ev.periodo
                    pendientes.append(ev)
            else:
                pendientes.append(ev)
        for ev in pendientes:
            self.cola.encolar(ev)
        return mensajes

    def limpiar(self):
        self.cola = Cola()

    def __len__(self):
        return len(self.cola)
