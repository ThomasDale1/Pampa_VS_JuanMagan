

"""
main.py — Punto de entrada de "Pampa y la Mazmorra de Juan Magán".

Proyecto final de Programación / Estructura de Datos y Algoritmos.

UN solo modo: un RPG por turnos donde exploras la mansión de Juan Magán con
comandos de texto. El FINAL (hay 8) depende de por dónde salgas, a quién te
enfrentes, qué recojas y uses, qué desbloquees y cuánto bebas.

Uso:
    python main.py                 jugar
    python main.py --demo          tour técnico de todas las estructuras de
                                   datos y algoritmos (incluye el árbol de
                                   decisión de los finales y la tabla del alcohol)
    python main.py --benchmark     informe empírico de rendimiento
    python main.py --complejidad   imprime solo las tablas Big-O
    python main.py --sin-color     desactiva los colores ANSI
    python main.py --historia-lenta  narra con efecto "máquina de escribir"
    python main.py --semilla=42    fija la aleatoriedad (partidas reproducibles)

Requisitos: solo la biblioteca estándar de Python 3.9+.
"""

import sys

from juego import ui
from juego import complejidad
from juego import benchmark
from juego.motor import Juego


def main(argv):
    ui.habilitar_ansi_windows()

    if "--sin-color" in argv:
        ui.COLOR = False
    if "--historia-lenta" in argv:
        ui.VELOCIDAD_TEXTO = 0.012

    semilla = None
    for a in argv:
        if a.startswith("--semilla="):
            semilla = int(a.split("=", 1)[1])

    if "--complejidad" in argv:
        complejidad.imprimir_todo()
        return
    if "--benchmark" in argv:
        benchmark.ejecutar_todo()
        return
    if "--demo" in argv:
        Juego(semilla=semilla).tour_tecnico()
        return

    try:
        Juego(semilla=semilla).jugar()
    except ui.SalirDelJuego:
        pass


if __name__ == "__main__":
    main(sys.argv[1:])
