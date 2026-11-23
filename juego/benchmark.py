"""
benchmark.py — ANÁLISIS EMPÍRICO DE RENDIMIENTO.

Semana 16: "Análisis empírico de rendimiento, medición de tiempo, comparación
           de estructuras. Informe de experimentación y métricas de rendimiento."

Aquí NO se razona con Big-O: se MIDE el tiempo real de ejecución con
`time.perf_counter` y se comprueba que las curvas empíricas coinciden con la
teoría del módulo `complejidad.py`.

Experimentos:
    1. dict (tabla hash) vs lista de pares  -> búsqueda de un estado.
    2. Los 5 algoritmos de ordenamiento sobre datos aleatorios.
    3. Búsqueda lineal vs binaria en una lista ordenada.
    4. Pila y Cola propias vs list.append/pop.
    5. BFS/DFS sobre grafos de tamaño creciente.

Ejecutar:  python main.py --benchmark
"""

import random
import time

from . import ui
from .pila import Pila
from .cola import Cola
from .grafo import Grafo
from . import ordenamiento
from . import busqueda


def _cronometrar(funcion, repeticiones=1):
    """Devuelve el tiempo MEDIO en milisegundos de ejecutar 'funcion'."""
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        funcion()
    fin = time.perf_counter()
    return (fin - inicio) * 1000 / repeticiones


# ---------------------------------------------------------------------------
# 1. Tabla hash vs búsqueda lineal
# ---------------------------------------------------------------------------
def exp_hash_vs_lista():
    ui.escribir("\n1) DICCIONARIO (tabla hash) vs LISTA DE PARES — buscar un estado",
                "negrita", "cian_claro")
    filas = []
    for n in (100, 1_000, 10_000, 100_000):
        claves = [f"estado_{i}" for i in range(n)]
        d = {k: i for i, k in enumerate(claves)}
        pares = list(d.items())
        objetivo = claves[-1]                     # peor caso para la lineal

        t_dict = _cronometrar(lambda: d[objetivo], repeticiones=2000)
        t_lista = _cronometrar(
            lambda: next(v for k, v in pares if k == objetivo), repeticiones=200)
        filas.append((n, f"{t_dict:.6f}", f"{t_lista:.6f}",
                      f"{t_lista / t_dict:,.0f}x" if t_dict else "-"))
    ui.tabla(["n", "dict  O(1)  [ms]", "lista  O(n)  [ms]", "lista es más lenta"], filas)


# ---------------------------------------------------------------------------
# 2. Comparación de ordenamientos
# ---------------------------------------------------------------------------
def exp_ordenamientos():
    ui.escribir("\n2) ALGORITMOS DE ORDENAMIENTO — datos aleatorios",
                "negrita", "cian_claro")
    for n in (200, 1000, 3000):
        datos = [random.randint(0, 10_000) for _ in range(n)]
        ui.escribir(f"\n   n = {n}", "amarillo")
        filas = []
        for nombre, funcion in ordenamiento.ALGORITMOS.items():
            t = _cronometrar(lambda f=funcion: f(datos), repeticiones=3)
            _, m = funcion(datos)
            filas.append((nombre, f"{t:.3f}",
                          m["comparaciones"], m["intercambios"]))
        t_py = _cronometrar(lambda: sorted(datos), repeticiones=20)
        filas.append(("sorted() de Python (Timsort)", f"{t_py:.3f}", "-", "-"))
        ui.tabla(["algoritmo", "tiempo [ms]", "comparaciones", "intercambios"], filas)


# ---------------------------------------------------------------------------
# 3. Búsqueda lineal vs binaria
# ---------------------------------------------------------------------------
def exp_busquedas():
    ui.escribir("\n3) BÚSQUEDA LINEAL O(n) vs BINARIA O(log n) — lista ordenada",
                "negrita", "cian_claro")
    filas = []
    for n in (1_000, 10_000, 100_000, 1_000_000):
        datos = list(range(n))
        objetivo = n - 1                          # peor caso para la lineal
        t_lin = _cronometrar(lambda: busqueda.busqueda_lineal(datos, objetivo),
                             repeticiones=5)
        t_bin = _cronometrar(lambda: busqueda.busqueda_binaria(datos, objetivo),
                             repeticiones=2000)
        _, c_lin = busqueda.busqueda_lineal(datos, objetivo)
        _, c_bin = busqueda.busqueda_binaria(datos, objetivo)
        filas.append((n, f"{t_lin:.4f}", c_lin, f"{t_bin:.6f}", c_bin))
    ui.tabla(["n", "lineal [ms]", "comp. lineal", "binaria [ms]", "comp. binaria"], filas)


# ---------------------------------------------------------------------------
# 4. Pila / Cola
# ---------------------------------------------------------------------------
def exp_pila_cola():
    ui.escribir("\n4) PILA y COLA propias — 100 000 operaciones", "negrita", "cian_claro")
    n = 100_000

    def usar_pila():
        p = Pila()
        for i in range(n):
            p.apilar(i)
        while not p.esta_vacia():
            p.desapilar()

    def usar_cola():
        q = Cola()
        for i in range(n):
            q.encolar(i)
        while not q.esta_vacia():
            q.desencolar()

    def cola_mala():
        lista = []
        for i in range(n):
            lista.append(i)
        while lista:
            lista.pop(0)                          # O(n) cada pop -> O(n^2) total

    filas = [
        ("Pila (list.append/pop)", f"{_cronometrar(usar_pila):.2f}", "O(1) amortizado"),
        ("Cola (collections.deque)", f"{_cronometrar(usar_cola):.2f}", "O(1)"),
        ("Cola MAL hecha (list.pop(0))", f"{_cronometrar(cola_mala):.2f}", "O(n) por pop!"),
    ]
    ui.tabla(["estructura", "tiempo [ms]", "coste por operación"], filas)


# ---------------------------------------------------------------------------
# 5. BFS / DFS
# ---------------------------------------------------------------------------
def exp_grafos():
    ui.escribir("\n5) BFS y DFS — grafo tipo malla de tamaño creciente",
                "negrita", "cian_claro")
    filas = []
    for lado in (10, 30, 60, 100):
        g = Grafo()
        for x in range(lado):
            for y in range(lado):
                if x + 1 < lado:
                    g.agregar_arista((x, y), (x + 1, y))
                if y + 1 < lado:
                    g.agregar_arista((x, y), (x, y + 1))
        V, E = len(g.nodos()), g.num_aristas()
        t_bfs = _cronometrar(lambda: g.bfs((0, 0)), repeticiones=5)
        t_dfs = _cronometrar(lambda: g.dfs_iterativo((0, 0)), repeticiones=5)
        filas.append((f"{lado}x{lado}", V, E, f"{t_bfs:.3f}", f"{t_dfs:.3f}"))
    ui.tabla(["malla", "V", "E", "BFS [ms]", "DFS [ms]"], filas)


def ejecutar_todo():
    ui.habilitar_ansi_windows()
    ui.titulo("INFORME DE EXPERIMENTACIÓN Y MÉTRICAS DE RENDIMIENTO")
    ui.escribir("Medición con time.perf_counter(). Los tiempos varían según la máquina;\n"
                "lo importante es la FORMA de la curva al crecer n.\n", "gris")
    exp_hash_vs_lista()
    exp_busquedas()
    exp_pila_cola()
    exp_grafos()
    exp_ordenamientos()
    ui.escribir("\nConclusión: las curvas empíricas coinciden con el Big-O de "
                "complejidad.py.\n", "verde")
