"""
ia.py — ÁRBOL DE DECISIÓN para el comportamiento de los enemigos.

Semana 14: "Árboles, árboles de decisión y dependencias."

El "cerebro" de cada enemigo es un ÁRBOL DE DECISIÓN binario:
    - los nodos internos son PREGUNTAS (condiciones sobre el estado del combate),
    - las hojas son ACCIONES ("atacar", "habilidad", "defender", "invocar").

Se recorre desde la raíz: en cada nodo se evalúa la condición y se baja por la
rama 'si' o 'no' hasta llegar a una hoja. Recorrido: O(h), con h = altura del
árbol (aquí h <= 4).

Árbol usado por los enemigos:

                      ¿mi vida < 25%?
                     /              \\
                   sí                no
                  /  \\              /      \\
        ¿soy jefe?    defender   ¿jugador malherido?
        /     \\                   /            \\
   invocar   habilidad          habilidad     ¿turno par?
                                              /         \\
                                        habilidad     atacar
"""

import random


class NodoDecision:
    """Nodo interno: una condición y dos ramas."""
    def __init__(self, condicion, rama_si, rama_no, etiqueta=""):
        self.condicion = condicion      # función(contexto) -> bool
        self.rama_si = rama_si
        self.rama_no = rama_no
        self.etiqueta = etiqueta

    def decidir(self, contexto, traza=None):
        resultado = self.condicion(contexto)
        if traza is not None:
            traza.append(f"{self.etiqueta} -> {'sí' if resultado else 'no'}")
        rama = self.rama_si if resultado else self.rama_no
        if isinstance(rama, NodoDecision):
            return rama.decidir(contexto, traza)
        return rama                      # hoja: string de acción


def _construir_arbol_enemigo():
    # Hojas (acciones posibles)
    ATACAR, HABILIDAD, DEFENDER, INVOCAR = "atacar", "habilidad", "defender", "invocar"

    turno_par = NodoDecision(
        lambda ctx: ctx["turno"] % 2 == 0,
        rama_si=HABILIDAD, rama_no=ATACAR,
        etiqueta="¿turno par?")

    jugador_malherido = NodoDecision(
        lambda ctx: ctx["jugador_vida_pct"] < 0.30,
        rama_si=HABILIDAD, rama_no=turno_par,
        etiqueta="¿jugador malherido?")

    soy_jefe = NodoDecision(
        lambda ctx: ctx["es_jefe"] and not ctx["hay_invocados"] and ctx["puede_invocar"],
        rama_si=INVOCAR, rama_no=HABILIDAD,
        etiqueta="¿jefe sin refuerzos?")

    vida_critica = NodoDecision(
        lambda ctx: ctx["mi_vida_pct"] < 0.25,
        rama_si=soy_jefe, rama_no=jugador_malherido,
        etiqueta="¿mi vida crítica?")

    return vida_critica


ARBOL_ENEMIGO = _construir_arbol_enemigo()


def decidir_accion(enemigo, jugador, turno, hay_invocados=False, traza=None):
    """
    Evalúa el ÁRBOL DE DECISIÓN y devuelve una de:
        "atacar" | "habilidad" | "defender" | "invocar"
    'traza' (lista opcional) recoge el camino recorrido para poder mostrarlo.
    """
    contexto = {
        "mi_vida_pct": enemigo.vida / enemigo.vida_max if enemigo.vida_max else 0,
        "jugador_vida_pct": jugador.vida / jugador.vida_max if jugador.vida_max else 0,
        "turno": turno,
        "es_jefe": enemigo.tipo == "jefe",
        "puede_invocar": enemigo.tipo == "jefe",
        "hay_invocados": hay_invocados,
    }
    accion = ARBOL_ENEMIGO.decidir(contexto, traza)

    # Coherencia: si no tiene habilidad definida, ataca normal.
    if accion == "habilidad" and not (enemigo.habilidad or enemigo.habilidad_furia):
        accion = "atacar"
    if accion == "invocar" and enemigo.tipo != "jefe":
        accion = "habilidad"
    return accion


def objetivo_area(combatientes_jugador):
    """Para habilidades de área (Perreo intenso): devuelve todos los aliados vivos."""
    return [c for c in combatientes_jugador if c.vivo]


def tirada(probabilidad):
    """Auxiliar: True con la probabilidad dada (0..1)."""
    return random.random() < probabilidad
