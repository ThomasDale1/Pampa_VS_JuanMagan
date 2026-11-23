"""
busqueda.py — BÚSQUEDA LINEAL y BÚSQUEDA BINARIA + justificación técnica.

Semana 11: "Búsqueda lineal, búsqueda binaria y criterios de eficiencia.
           Módulo de búsqueda y justificación técnica."

Todas las funciones devuelven una tupla (indice, comparaciones) para poder
CONTAR OPERACIONES (semana 4: conteo de operaciones) y comparar eficiencia.
`indice` es -1 si no se encontró.

Análisis de complejidad
-----------------------
    busqueda_lineal        -> mejor O(1), promedio O(n), peor O(n)   | espacio O(1)
    busqueda_binaria       -> mejor O(1), promedio O(log n), peor O(log n) | espacio O(1)
    busqueda_binaria_rec   -> O(log n) tiempo | O(log n) espacio (pila de llamadas)

Criterio de uso
---------------
    * Búsqueda LINEAL: cuando la colección NO está ordenada, es pequeña, o
      cambia constantemente (mantener el orden costaría más de lo que ahorra).
      En el juego: buscar un objeto por nombre dentro del inventario de Pampa.
    * Búsqueda BINARIA: cuando la colección está ORDENADA y se consulta muchas
      veces. Requiere acceso aleatorio O(1) (lista/array).
      En el juego: consultar el CATÁLOGO GLOBAL de objetos (ordenado por id)
      para ver la ficha de un objeto.
"""


def busqueda_lineal(lista, objetivo, clave=lambda x: x):
    """
    Recorre la lista de principio a fin comparando elemento por elemento.
    Funciona con cualquier lista (ordenada o no).
    Devuelve (indice, comparaciones).
    """
    comparaciones = 0
    for i, elemento in enumerate(lista):
        comparaciones += 1
        if clave(elemento) == objetivo:
            return i, comparaciones
    return -1, comparaciones


def busqueda_binaria(lista_ordenada, objetivo, clave=lambda x: x):
    """
    Búsqueda BINARIA iterativa. La lista DEBE venir ordenada por `clave`.
    En cada paso descarta la mitad del espacio de búsqueda -> O(log n).
    Devuelve (indice, comparaciones).
    """
    comparaciones = 0
    izquierda, derecha = 0, len(lista_ordenada) - 1
    while izquierda <= derecha:
        medio = (izquierda + derecha) // 2
        comparaciones += 1
        valor = clave(lista_ordenada[medio])
        if valor == objetivo:
            return medio, comparaciones
        if valor < objetivo:
            izquierda = medio + 1
        else:
            derecha = medio - 1
    return -1, comparaciones


def busqueda_binaria_recursiva(lista_ordenada, objetivo, clave=lambda x: x,
                               izquierda=0, derecha=None, comparaciones=0):
    """
    Versión RECURSIVA (divide y vencerás, semana 7): el problema de tamaño n
    se reduce a un subproblema de tamaño n/2.
    Devuelve (indice, comparaciones).
    """
    if derecha is None:
        derecha = len(lista_ordenada) - 1
    if izquierda > derecha:
        return -1, comparaciones
    medio = (izquierda + derecha) // 2
    comparaciones += 1
    valor = clave(lista_ordenada[medio])
    if valor == objetivo:
        return medio, comparaciones
    if valor < objetivo:
        return busqueda_binaria_recursiva(lista_ordenada, objetivo, clave,
                                          medio + 1, derecha, comparaciones)
    return busqueda_binaria_recursiva(lista_ordenada, objetivo, clave,
                                      izquierda, medio - 1, comparaciones)


JUSTIFICACION = """\
JUSTIFICACIÓN TÉCNICA DEL MÓDULO DE BÚSQUEDA
===========================================

1) Búsqueda LINEAL  ->  O(n)
   Se usa para el INVENTARIO de Pampa. El inventario:
     - es muy pequeño (<= 10 objetos): la constante oculta domina y O(n) es
       en la práctica instantáneo;
     - cambia en cada turno (se recoge/gasta/equipa): mantenerlo ordenado
       para poder aplicar binaria costaría O(n) por inserción, más caro que
       la propia búsqueda que se quiere acelerar.

2) Búsqueda BINARIA ->  O(log n)
   Se usa para el CATÁLOGO GLOBAL de objetos, que:
     - es fijo durante toda la partida (se puede ordenar UNA vez por 'id');
     - se consulta muchas veces (comando 'examinar').
   Sobre ~24 objetos, la lineal hace hasta 24 comparaciones y la binaria
   como máximo ceil(log2(24)) = 5.

3) BFS sobre el GRAFO del mapa  ->  O(V + E)
   Para "¿cuál es el camino más corto a la salida?" (comando 'camino').
   BFS explora por niveles, así que el primer camino que llega al destino
   es el de menos puertas.

4) DFS sobre el GRAFO del mapa  ->  O(V + E)
   Para "explora toda la mansión desde aquí" (comando 'explorar'): DFS se
   adentra por cada pasillo hasta el fondo antes de retroceder.
"""


def imprimir_justificacion():
    print(JUSTIFICACION)
