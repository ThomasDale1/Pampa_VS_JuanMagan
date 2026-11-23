"""
alcohol.py — SISTEMA DE ALCOHOL: decisión con RIESGO y PROBABILIDAD creciente.

Refuerza la mecánica de decisiones estilo Henry Stickmin: cada trago es una
APUESTA. Y engancha con el análisis del curso (semana 4): probabilidad,
valor esperado y cómo un parámetro (nº de tragos) cambia la distribución de
resultados.

REGLAS
------
Pampa lleva la cuenta de `tragos`. Al beber el trago número k (k >= 1):

    magnitud    = 1 + (k - 1) // 2        -> k1-2: ±1,  k3-4: ±2,  k5-6: ±3 ... (tope 5)
    p_positivo  = clamp(0.85 - 0.075*k, 0.40, 0.85)
                  -> k1 ≈ 0.78,  k5 ≈ 0.48,  k6+ = 0.40 (PISO)
                  El piso del 40 % es a propósito: aunque beber de más siga sin
                  compensar, deja que Pampa siga apostando trago tras trago.
    estadística = 50 % ataque / 50 % defensa
    signo       = +1 con probabilidad p_positivo ; si no, -1
    efecto      = signo * magnitud  sumado (ACUMULATIVO) a esa estadística

A partir del trago 5, cada trago añade riesgo de DESMAYO:

    p_desmayo   = max(0, 0.13 * (k - 4))  -> k5: 0.13, k8: 0.52, k10: 0.78

Un desmayo = final malo "Otra Ronda" (Pampa despierta otra vez en la celda).

VALOR ESPERADO del trago k sobre la estadística elegida:
    E[efecto] = magnitud * (p_positivo * (+1) + (1 - p_positivo) * (-1))
              = magnitud * (2*p_positivo - 1)
Con k=1: 1 * (2*0.775 - 1) = +0.55   (conviene)
Con k=4: 2 * (2*0.550 - 1) = +0.20   (todavía conviene)
Con k=5: 3 * (2*0.475 - 1) = -0.15   (ya no conviene)
Con k=7: 4 * (2*0.400 - 1) = -0.80   (mala idea, pero acotada por el piso)
"""

import random


def magnitud_trago(k):
    return min(5, 1 + (k - 1) // 2)


#: probabilidad mínima de que un trago salga bueno (piso). Ver el docstring:
#: mantiene la apuesta viva aunque el valor esperado ya sea negativo.
PISO_POSITIVO = 0.40


def prob_positivo(k):
    return max(PISO_POSITIVO, min(0.85, 0.85 - 0.075 * k))


def prob_desmayo(k):
    return max(0.0, 0.13 * (k - 4))


def valor_esperado(k):
    """E[efecto] del trago k sobre la estadística que toque."""
    return magnitud_trago(k) * (2 * prob_positivo(k) - 1)


def beber(pampa, rng=None):
    """
    Aplica UN trago a Pampa. Devuelve un dict con el desglose para narrarlo:
        {trago, magnitud, estadistica, positivo, delta, desmayo,
         p_positivo, p_desmayo, atk_total, def_total}
    Modifica pampa.tragos, pampa.alcohol_atk / pampa.alcohol_def y recalcula
    las estadísticas efectivas (pampa.aplicar_equipo debe llamarse fuera si
    hace falta el catálogo; aquí ajustamos las bases directamente).
    """
    rng = rng or random
    pampa.tragos += 1
    k = pampa.tragos

    mag = magnitud_trago(k)
    p_pos = prob_positivo(k)
    p_des = prob_desmayo(k)

    estadistica = "ataque" if rng.random() < 0.5 else "defensa"
    positivo = rng.random() < p_pos
    delta = mag if positivo else -mag

    if estadistica == "ataque":
        pampa.alcohol_atk += delta
    else:
        pampa.alcohol_def += delta

    desmayo = rng.random() < p_des

    return {
        "trago": k,
        "magnitud": mag,
        "estadistica": estadistica,
        "positivo": positivo,
        "delta": delta,
        "desmayo": desmayo,
        "p_positivo": p_pos,
        "p_desmayo": p_des,
        "alcohol_atk": pampa.alcohol_atk,
        "alcohol_def": pampa.alcohol_def,
    }


def resaca(pampa):
    """Nota informativa al terminar, según lo que se bebió."""
    if pampa.tragos == 0:
        return "Ni una gota. Sobrio como cura en misa."
    if pampa.tragos <= 2:
        return "Un puntito nomás. Mañana ni te acordás de lo feo."
    if pampa.tragos <= 4:
        return "Vas alegre. La goma de mañana va a estar del terror."
    if pampa.tragos <= 6:
        return "Bien picado, maje. Ya ves todo doble."
    return "Hasta las trancas. Milagro que todavía te tenés en pie."


def tabla_probabilidades(hasta=9):
    """Devuelve filas [(k, magnitud, p_positivo%, E[efecto], p_desmayo%)]."""
    filas = []
    for k in range(1, hasta + 1):
        filas.append((
            k,
            f"±{magnitud_trago(k)}",
            f"{prob_positivo(k) * 100:.0f}%",
            f"{valor_esperado(k):+.2f}",
            f"{prob_desmayo(k) * 100:.0f}%",
        ))
    return filas
