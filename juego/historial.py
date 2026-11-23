"""
historial.py — PILA APLICADA: historial de acciones, retroceso y "deshacer".

Semana 5: "Pilas. Historial de acciones. Backtracking básico. Módulo de pila
          para historial o retroceso."

Se usan DOS pilas:

  1. pila_movimientos : cada vez que Pampa cambia de sala se APILA la sala de
     origen. El comando 'retroceder' DESAPILA y devuelve a Pampa allí
     (backtracking sobre el recorrido real).

  2. pila_acciones : registra acciones REVERSIBLES (recoger/soltar objeto,
     equipar) junto con la función que las deshace. El comando 'deshacer'
     DESAPILA la última y la revierte.

Complejidad: apilar / desapilar / cima -> O(1). Espacio -> O(n).
"""

from .pila import Pila


class Accion:
    """Una acción reversible: descripción + closure que la deshace."""
    def __init__(self, descripcion, deshacer):
        self.descripcion = descripcion
        self._deshacer = deshacer

    def revertir(self):
        self._deshacer()

    def __repr__(self):
        return self.descripcion


class Historial:
    def __init__(self):
        self.pila_movimientos = Pila()     # ids de sala visitados (para 'retroceder')
        self.pila_acciones = Pila()        # objetos Accion (para 'deshacer')
        self.registro = []                 # log lineal completo (solo lectura)

    # -- movimientos ---------------------------------------------------
    def registrar_movimiento(self, sala_origen):
        self.pila_movimientos.apilar(sala_origen)
        self.registro.append(f"ir: {sala_origen} ->")

    def puede_retroceder(self):
        return not self.pila_movimientos.esta_vacia()

    def retroceder(self):
        """Devuelve la sala anterior (y la quita de la pila). O(1)."""
        sala = self.pila_movimientos.desapilar()
        self.registro.append(f"retroceder -> {sala}")
        return sala

    # -- acciones reversibles ---------------------------------------
    def registrar_accion(self, descripcion, deshacer):
        self.pila_acciones.apilar(Accion(descripcion, deshacer))
        self.registro.append(f"acción: {descripcion}")

    def puede_deshacer(self):
        return not self.pila_acciones.esta_vacia()

    def deshacer(self):
        """Revierte y devuelve la última acción reversible. O(1)."""
        accion = self.pila_acciones.desapilar()
        accion.revertir()
        self.registro.append(f"deshacer: {accion.descripcion}")
        return accion

    # -- inspección ------------------------------------------------
    def ruta_recorrida(self):
        """Lista de salas en la pila de movimientos, de la más antigua a la cima."""
        return self.pila_movimientos.a_lista(desde_cima=False)

    def ultimas_acciones(self, n=8):
        return list(self.pila_acciones)[:n]

    def limpiar(self):
        self.pila_movimientos.vaciar()
        self.pila_acciones.vaciar()
