"""
Paquete 'juego' — Proyecto final de Programación / Estructura de Datos y Algoritmos.

Juego de terminal "Pampa y la Mazmorra de Juan Magán".

Un RPG por turnos con exploración libre y 8 FINALES posibles: el desenlace
depende de por dónde salgas, a quién te enfrentes, qué uses y cuánto bebas.

Cada módulo implementa y documenta un tema del curso:

    finales.py       -> Los 8 finales + ÁRBOL DE DECISIÓN que los clasifica
    alcohol.py       -> Decisión con PROBABILIDAD y valor esperado (beber)
    pila.py          -> Pilas (LIFO)
    cola.py          -> Colas (FIFO)
    historial.py     -> Pila aplicada: historial de acciones y backtracking
    turnos.py        -> Cola aplicada: sistema de turnos y cola de eventos
    grafo.py         -> Grafos: lista/matriz de adyacencia, BFS y DFS
    mapa.py          -> El mapa de la mansión construido como grafo
    busqueda.py      -> Búsqueda lineal y binaria + justificación técnica
    ordenamiento.py  -> Burbuja, selección, inserción, quicksort, mergesort
    recursion.py     -> Recursividad y divide y vencerás
    estado_mundo.py  -> Tabla hash / diccionario de estados del mundo
    misiones.py      -> Árbol de misiones y dependencias (desbloqueos)
    ia.py            -> Árbol de decisión para el comportamiento enemigo
    inventario.py    -> Listas / estructuras lineales
    complejidad.py   -> Tablas de análisis de complejidad temporal y espacial
    benchmark.py     -> Análisis empírico de rendimiento (medición de tiempos)
    entidades.py     -> Modelado de datos: Pampa, enemigos, Juan Magán
    combate.py       -> Combate por turnos
    motor.py         -> Bucle principal y parser de comandos
    ui.py            -> Utilidades de presentación en terminal
    datos.py         -> Datos del mundo (salas, objetos, enemigos, narrativa)
"""

__version__ = "2.0"
__all__ = [
    "finales", "alcohol",
    "pila", "cola", "historial", "turnos", "grafo", "mapa", "busqueda",
    "ordenamiento", "recursion", "estado_mundo", "misiones", "ia",
    "inventario", "complejidad", "benchmark", "entidades", "combate",
    "motor", "ui", "datos",
]
