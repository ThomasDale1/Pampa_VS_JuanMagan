"""
estado_mundo.py — TABLA HASH / DICCIONARIO DE ESTADOS DEL MUNDO.

Semana 15: "Diccionario de estados del mundo del juego."
Semana 12 (tablas hash): "Acceso eficiente a estados del juego."

Toda la "memoria" del juego (qué puertas están abiertas, qué enemigos han
sido derrotados, qué objetos se recogieron, qué salas se visitaron, banderas
de historia...) vive en UN diccionario `dict` de Python, que internamente es
una tabla hash.

¿Por qué una tabla hash y no una lista?
    - Consultar / modificar un estado por su clave -> O(1) promedio.
    - Con una lista de pares (clave, valor) sería O(n) por búsqueda lineal.
El módulo `benchmark.py` mide esta diferencia de forma empírica.

Análisis de complejidad (dict / tabla hash)
-------------------------------------------
    obtener(clave)     -> O(1) promedio,  O(n) peor caso (colisiones)
    establecer(clave)  -> O(1) promedio
    eliminar(clave)    -> O(1) promedio
    "clave in dict"    -> O(1) promedio
    Espacio            -> O(n)
"""

import json


class EstadoMundo:
    """Envoltura sobre un dict para registrar y depurar el estado global."""

    def __init__(self):
        # La tabla hash central. Clave: str. Valor: cualquier cosa serializable.
        self._estados = {}
        # Contador de accesos, útil para la defensa técnica / benchmark.
        self.lecturas = 0
        self.escrituras = 0

    # -- acceso O(1) -----------------------------------------------------
    def obtener(self, clave, por_defecto=None):
        self.lecturas += 1
        return self._estados.get(clave, por_defecto)

    def establecer(self, clave, valor):
        self.escrituras += 1
        self._estados[clave] = valor

    def activar(self, bandera):
        """Marca una bandera booleana como verdadera. Ej: 'tigre_derrotado'."""
        self.establecer(bandera, True)

    def esta_activa(self, bandera):
        return bool(self.obtener(bandera, False))

    def incrementar(self, clave, cantidad=1):
        self.establecer(clave, self.obtener(clave, 0) + cantidad)
        return self._estados[clave]

    def anexar(self, clave, elemento):
        """Agrega a una lista guardada bajo 'clave' (la crea si no existe)."""
        lista = self._estados.setdefault(clave, [])
        lista.append(elemento)
        self.escrituras += 1

    def __contains__(self, clave):
        return clave in self._estados

    def __getitem__(self, clave):
        self.lecturas += 1
        return self._estados[clave]

    def __setitem__(self, clave, valor):
        self.establecer(clave, valor)

    # -- persistencia (serialización del diccionario) ------------------
    def como_dict(self):
        return dict(self._estados)

    def cargar_dict(self, datos):
        self._estados = dict(datos)

    def guardar_json(self, ruta):
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(self._estados, f, ensure_ascii=False, indent=2)

    def cargar_json(self, ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            self._estados = json.load(f)

    # -- inspección ----------------------------------------------------
    def resumen(self):
        """Devuelve una lista de (clave, valor) ordenada para mostrar."""
        return sorted(self._estados.items())

    def __repr__(self):
        return f"EstadoMundo({len(self._estados)} claves, {self.lecturas} lecturas, {self.escrituras} escrituras)"
