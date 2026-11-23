"""
grafo.py — GRAFOS: nodos, aristas, lista y matriz de adyacencia + BFS y DFS.

Semana 12: "Grafos: nodos, aristas, conexiones, matriz/lista de adyacencia."
Semana 13: "BFS y DFS. Recorridos sobre grafos."

El mapa de la mansión de Juan Magán se modela como un GRAFO NO DIRIGIDO:
    - cada SALA es un nodo (vértice),
    - cada PUERTA / PASILLO es una arista.

Se guarda como LISTA DE ADYACENCIA (un dict: nodo -> lista de vecinos), que es
la representación eficiente cuando el grafo es "disperso" (pocas aristas por
nodo), como ocurre en el mapa de una casa. También se puede generar la MATRIZ
DE ADYACENCIA bajo demanda para enseñar el concepto.

Análisis de complejidad  (V = nº de vértices, E = nº de aristas)
---------------------------------------------------------------
    agregar_nodo / agregar_arista        -> O(1)
    vecinos(n)                            -> O(1) para obtener la lista
    lista de adyacencia (espacio)        -> O(V + E)
    matriz de adyacencia (espacio)       -> O(V^2)
    BFS (recorrido completo)             -> O(V + E)
    DFS (recorrido completo)             -> O(V + E)
    BFS para camino más corto (sin peso) -> O(V + E)
"""

from collections import deque


class Grafo:
    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        # LISTA DE ADYACENCIA: nodo -> dict(vecino -> etiqueta_de_arista)
        self.adyacencia = {}

    # -- construcción --------------------------------------------------
    def agregar_nodo(self, nodo):
        self.adyacencia.setdefault(nodo, {})

    def agregar_arista(self, a, b, etiqueta=None):
        self.agregar_nodo(a)
        self.agregar_nodo(b)
        self.adyacencia[a][b] = etiqueta
        if not self.dirigido:
            self.adyacencia[b][a] = etiqueta

    # -- consultas ----------------------------------------------------
    def nodos(self):
        return list(self.adyacencia.keys())

    def vecinos(self, nodo):
        """Devuelve la lista de nodos adyacentes. O(1) para acceder al dict."""
        return list(self.adyacencia.get(nodo, {}).keys())

    def hay_arista(self, a, b):
        return b in self.adyacencia.get(a, {})

    def etiqueta(self, a, b):
        return self.adyacencia.get(a, {}).get(b)

    def num_aristas(self):
        total = sum(len(v) for v in self.adyacencia.values())
        return total if self.dirigido else total // 2

    # -- matriz de adyacencia ---------------------------------------
    def matriz_adyacencia(self, orden=None):
        """
        Construye la MATRIZ DE ADYACENCIA (lista de listas de 0/1).
        Espacio O(V^2). Devuelve (orden_de_nodos, matriz).
        """
        orden = orden or sorted(self.adyacencia.keys())
        indice = {nodo: i for i, nodo in enumerate(orden)}
        n = len(orden)
        matriz = [[0] * n for _ in range(n)]
        for a in orden:
            for b in self.adyacencia[a]:
                if b in indice:
                    matriz[indice[a]][indice[b]] = 1
        return orden, matriz

    # -- BFS: Búsqueda en Anchura ----------------------------------
    def bfs(self, inicio):
        """
        Recorrido en ANCHURA. Usa una COLA (deque).
        Devuelve la lista de nodos en el orden en que fueron visitados.
        Complejidad: O(V + E).
        """
        if inicio not in self.adyacencia:
            return []
        visitados = {inicio}
        orden = []
        cola = deque([inicio])
        while cola:
            actual = cola.popleft()          # FIFO -> explora por niveles
            orden.append(actual)
            for vecino in self.adyacencia[actual]:
                if vecino not in visitados:
                    visitados.add(vecino)
                    cola.append(vecino)
        return orden

    def camino_mas_corto(self, inicio, fin, arista_transitable=None):
        """
        BFS para hallar el CAMINO MÁS CORTO (menos puertas) entre dos salas.
        En un grafo sin pesos, BFS garantiza el camino mínimo en aristas.

        `arista_transitable(a, b, etiqueta) -> bool` permite ignorar puertas
        cerradas. Si es None, todas las aristas se consideran transitables.

        Devuelve la lista [inicio, ..., fin] o None si no hay camino.
        Complejidad: O(V + E).
        """
        if inicio == fin:
            return [inicio]
        if inicio not in self.adyacencia:
            return None
        previo = {inicio: None}
        cola = deque([inicio])
        while cola:
            actual = cola.popleft()
            for vecino, etiqueta in self.adyacencia[actual].items():
                if vecino in previo:
                    continue
                if arista_transitable and not arista_transitable(actual, vecino, etiqueta):
                    continue
                previo[vecino] = actual
                if vecino == fin:
                    return self._reconstruir(previo, fin)
                cola.append(vecino)
        return None

    @staticmethod
    def _reconstruir(previo, fin):
        camino = [fin]
        while previo[camino[-1]] is not None:
            camino.append(previo[camino[-1]])
        camino.reverse()
        return camino

    # -- DFS: Búsqueda en Profundidad ----------------------------
    def dfs_iterativo(self, inicio):
        """
        Recorrido en PROFUNDIDAD con PILA explícita.
        Devuelve la lista de nodos visitados. Complejidad: O(V + E).
        """
        if inicio not in self.adyacencia:
            return []
        visitados = set()
        orden = []
        pila = [inicio]
        while pila:
            actual = pila.pop()             # LIFO -> se adentra lo más posible
            if actual in visitados:
                continue
            visitados.add(actual)
            orden.append(actual)
            # se apilan en orden inverso para visitarlos alfabéticamente
            for vecino in sorted(self.adyacencia[actual], reverse=True):
                if vecino not in visitados:
                    pila.append(vecino)
        return orden

    def dfs_recursivo(self, inicio, visitados=None, orden=None):
        """
        Misma idea que dfs_iterativo pero con RECURSIÓN (la pila es la pila de
        llamadas del sistema). Ver semana 7: "Recursividad".
        Complejidad: O(V + E).
        """
        visitados = set() if visitados is None else visitados
        orden = [] if orden is None else orden
        visitados.add(inicio)
        orden.append(inicio)
        for vecino in sorted(self.adyacencia.get(inicio, {})):
            if vecino not in visitados:
                self.dfs_recursivo(vecino, visitados, orden)
        return orden

    def es_conexo(self):
        if not self.adyacencia:
            return True
        return len(self.bfs(next(iter(self.adyacencia)))) == len(self.adyacencia)

    # -- todos los caminos (recursión / backtracking) -----------
    def todos_los_caminos(self, inicio, fin, camino=None):
        """
        Enumera TODOS los caminos simples entre 'inicio' y 'fin' por
        backtracking recursivo. Complejidad exponencial en el peor caso:
        O(V!) — se usa solo con fines didácticos sobre el mapa pequeño.
        """
        camino = (camino or []) + [inicio]
        if inicio == fin:
            return [camino]
        resultado = []
        for vecino in self.adyacencia.get(inicio, {}):
            if vecino not in camino:
                resultado.extend(self.todos_los_caminos(vecino, fin, camino))
        return resultado
