"""
complejidad.py — TABLAS DE ANÁLISIS DE COMPLEJIDAD TEMPORAL Y ESPACIAL.

Semana 4: "Análisis de algoritmos, conteo de operaciones, complejidad
          temporal y espacial básica. Tabla inicial de análisis de complejidad."

Este módulo NO tiene lógica de juego: solo reúne, en un único lugar, el
análisis Big-O de cada estructura y algoritmo que el proyecto utiliza, para
poder mostrarlo con el comando 'complejidad' y usarlo en la defensa técnica.
"""

from . import ui

# (estructura, operación, mejor, promedio, peor, espacio, dónde se usa)
TABLA_ESTRUCTURAS = [
    ("Lista (inventario)", "acceso por índice", "O(1)", "O(1)", "O(1)", "O(n)", "leer objeto equipado"),
    ("Lista (inventario)", "buscar por nombre", "O(1)", "O(n)", "O(n)", "O(1)", "comando 'usar'/'tomar'"),
    ("Lista (inventario)", "insertar al final", "O(1)", "O(1)", "O(1)", "O(1)", "recoger objeto"),
    ("Lista (inventario)", "eliminar por valor", "O(n)", "O(n)", "O(n)", "O(1)", "gastar poción"),
    ("Pila (historial)", "apilar / desapilar", "O(1)", "O(1)", "O(1)", "O(n)", "moverse / retroceder"),
    ("Cola (turnos)", "encolar / desencolar", "O(1)", "O(1)", "O(1)", "O(n)", "orden de combate"),
    ("Cola de prioridad", "encolar / desencolar", "O(1)", "O(log n)", "O(log n)", "O(n)", "iniciativa por velocidad"),
    ("Diccionario (estado)", "obtener / establecer", "O(1)", "O(1)", "O(n)", "O(n)", "banderas del mundo"),
    ("Grafo lista adyacencia", "vecinos de un nodo", "O(1)", "O(1)", "O(1)", "O(V+E)", "salidas de una sala"),
    ("Grafo matriz adyacencia", "¿hay arista a-b?", "O(1)", "O(1)", "O(1)", "O(V^2)", "vista de matriz del mapa"),
    ("Árbol de misiones", "recorrer / evaluar", "O(n)", "O(n)", "O(n)", "O(h)", "desbloqueos y objetivos"),
    ("Árbol de decisión (finales)", "clasificar el final", "O(1)", "O(h)", "O(h)", "O(h)", "elegir cuál de los 8 finales"),
]

# (algoritmo, tiempo mejor, promedio, peor, espacio, dónde se usa)
TABLA_ALGORITMOS = [
    ("Búsqueda lineal", "O(1)", "O(n)", "O(n)", "O(1)", "buscar en inventario"),
    ("Búsqueda binaria", "O(1)", "O(log n)", "O(log n)", "O(1)", "catálogo de objetos ('examinar')"),
    ("Búsqueda binaria recursiva", "O(1)", "O(log n)", "O(log n)", "O(log n)", "idem, versión recursiva"),
    ("BFS (grafo)", "O(V+E)", "O(V+E)", "O(V+E)", "O(V)", "camino más corto ('camino')"),
    ("DFS (grafo)", "O(V+E)", "O(V+E)", "O(V+E)", "O(V)", "explorar mansión ('explorar')"),
    ("Ordenamiento burbuja", "O(n)", "O(n^2)", "O(n^2)", "O(1)", "comparativa ('ranking')"),
    ("Ordenamiento selección", "O(n^2)", "O(n^2)", "O(n^2)", "O(1)", "comparativa"),
    ("Ordenamiento inserción", "O(n)", "O(n^2)", "O(n^2)", "O(1)", "ordenar iniciativa (listas casi ordenadas)"),
    ("Quicksort", "O(n log n)", "O(n log n)", "O(n^2)", "O(log n)", "ranking de enemigos por XP"),
    ("Mergesort", "O(n log n)", "O(n log n)", "O(n log n)", "O(n)", "ranking estable por XP"),
    ("Fibonacci recursivo", "O(2^n)", "O(2^n)", "O(2^n)", "O(n)", "acertijo de la biblioteca"),
    ("Fibonacci con memoización", "O(n)", "O(n)", "O(n)", "O(n)", "solución optimizada del acertijo"),
    ("Exponenciación rápida", "O(log n)", "O(log n)", "O(log n)", "O(log n)", "cerradura por combinaciones"),
    ("Torres de Hanói", "O(2^n)", "O(2^n)", "O(2^n)", "O(n)", "puzzle opcional"),
]

NOTACION = """\
RECORDATORIO DE NOTACIÓN
    n = tamaño de la entrada (nº de objetos, nodos, combatientes...)
    V = nº de vértices (salas) ; E = nº de aristas (puertas) ; h = altura del árbol
    O(1)      constante   — no depende del tamaño
    O(log n)  logarítmica — se parte el problema por la mitad (binaria, heap)
    O(n)      lineal      — se recorre la entrada una vez
    O(n log n) casi lineal — ordenamientos eficientes
    O(n^2)    cuadrática  — dobles bucles anidados (ordenamientos simples)
    O(2^n)    exponencial — recursión que se ramifica sin memoria (fib, hanoi)
"""


def imprimir_tabla_estructuras():
    ui.escribir("\nCOMPLEJIDAD DE LAS ESTRUCTURAS DE DATOS", "negrita", "cian_claro")
    ui.tabla(
        ["Estructura", "Operación", "Mejor", "Prom.", "Peor", "Espacio", "Uso en el juego"],
        [list(fila) for fila in TABLA_ESTRUCTURAS],
    )


def imprimir_tabla_algoritmos():
    ui.escribir("\nCOMPLEJIDAD DE LOS ALGORITMOS", "negrita", "cian_claro")
    ui.tabla(
        ["Algoritmo", "Mejor", "Prom.", "Peor", "Espacio", "Uso en el juego"],
        [list(fila) for fila in TABLA_ALGORITMOS],
    )


def imprimir_todo():
    ui.titulo("TABLA DE ANÁLISIS DE COMPLEJIDAD")
    print(NOTACION)
    imprimir_tabla_estructuras()
    imprimir_tabla_algoritmos()
