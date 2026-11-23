"""
ordenamiento.py — ALGORITMOS DE ORDENAMIENTO + comparación.

Semana 10: "Ordenamiento: burbuja, selección, inserción, quicksort o
           mergesort. Ranking ordenado y comparación de algoritmos."

Cada función:
    - NO modifica la lista original (trabaja sobre una copia),
    - devuelve (lista_ordenada, metricas) donde metricas es un dict con
      'comparaciones' e 'intercambios' (conteo de operaciones, semana 4),
    - acepta `clave` para ordenar por un campo, y `reverse` para descendente.

Análisis de complejidad
-----------------------
    Algoritmo    | Mejor      | Promedio   | Peor       | Espacio  | Estable
    -------------|------------|------------|------------|----------|--------
    Burbuja      | O(n)       | O(n^2)     | O(n^2)     | O(1)     | Sí
    Selección    | O(n^2)     | O(n^2)     | O(n^2)     | O(1)     | No
    Inserción    | O(n)       | O(n^2)     | O(n^2)     | O(1)     | Sí
    Quicksort    | O(n log n) | O(n log n) | O(n^2)     | O(log n) | No
    Mergesort    | O(n log n) | O(n log n) | O(n log n) | O(n)     | Sí

En el juego se usan para:
    - ordenar por INICIATIVA a los combatientes (sistema de turnos),
    - el RANKING de enemigos derrotados por XP (comando 'ranking'),
    - ordenar el inventario por valor/peso (comando 'inventario ordenar').
"""


def _preparar(lista, clave):
    return [(clave(x), i, x) for i, x in enumerate(lista)]  # i desempata -> estable


def ordenamiento_burbuja(lista, clave=lambda x: x, reverse=False):
    """Compara pares adyacentes y los intercambia si están desordenados."""
    datos = list(lista)
    n = len(datos)
    comp = interc = 0
    for i in range(n - 1):
        hubo_cambio = False
        for j in range(n - 1 - i):
            comp += 1
            a, b = clave(datos[j]), clave(datos[j + 1])
            if (a > b) != reverse and a != b:
                datos[j], datos[j + 1] = datos[j + 1], datos[j]
                interc += 1
                hubo_cambio = True
        if not hubo_cambio:            # ya está ordenada -> O(n) en el mejor caso
            break
    return datos, {"comparaciones": comp, "intercambios": interc}


def ordenamiento_seleccion(lista, clave=lambda x: x, reverse=False):
    """Busca el mínimo (o máximo) del resto y lo coloca en su lugar."""
    datos = list(lista)
    n = len(datos)
    comp = interc = 0
    for i in range(n - 1):
        elegido = i
        for j in range(i + 1, n):
            comp += 1
            if (clave(datos[j]) < clave(datos[elegido])) != reverse:
                elegido = j
        if elegido != i:
            datos[i], datos[elegido] = datos[elegido], datos[i]
            interc += 1
    return datos, {"comparaciones": comp, "intercambios": interc}


def ordenamiento_insercion(lista, clave=lambda x: x, reverse=False):
    """Inserta cada elemento en su posición dentro de la parte ya ordenada."""
    datos = list(lista)
    comp = interc = 0
    for i in range(1, len(datos)):
        actual = datos[i]
        j = i - 1
        while j >= 0:
            comp += 1
            if (clave(datos[j]) > clave(actual)) != reverse:
                datos[j + 1] = datos[j]
                interc += 1
                j -= 1
            else:
                break
        datos[j + 1] = actual
    return datos, {"comparaciones": comp, "intercambios": interc}


def ordenamiento_rapido(lista, clave=lambda x: x, reverse=False):
    """
    QUICKSORT (divide y vencerás, semana 7).
    Elige un pivote, particiona en menores/iguales/mayores y ordena recursivamente.
    """
    metricas = {"comparaciones": 0, "intercambios": 0}

    def quick(seq):
        if len(seq) <= 1:
            return seq
        pivote = clave(seq[len(seq) // 2])
        menores, iguales, mayores = [], [], []
        for elem in seq:
            metricas["comparaciones"] += 1
            k = clave(elem)
            if k == pivote:
                iguales.append(elem)
            elif (k < pivote) != reverse:
                menores.append(elem)
            else:
                mayores.append(elem)
        metricas["intercambios"] += len(menores) + len(mayores)
        return quick(menores) + iguales + quick(mayores)

    return quick(list(lista)), metricas


def ordenamiento_mezcla(lista, clave=lambda x: x, reverse=False):
    """
    MERGESORT (divide y vencerás, semana 7).
    Divide la lista por la mitad, ordena cada mitad recursivamente y las
    MEZCLA en O(n). Complejidad garantizada O(n log n).
    """
    metricas = {"comparaciones": 0, "intercambios": 0}

    def mezclar(izq, der):
        resultado = []
        i = j = 0
        while i < len(izq) and j < len(der):
            metricas["comparaciones"] += 1
            if (clave(izq[i]) <= clave(der[j])) != reverse:
                resultado.append(izq[i]); i += 1
            else:
                resultado.append(der[j]); j += 1
            metricas["intercambios"] += 1
        resultado.extend(izq[i:])
        resultado.extend(der[j:])
        return resultado

    def merge_sort(seq):
        if len(seq) <= 1:
            return seq
        medio = len(seq) // 2
        return mezclar(merge_sort(seq[:medio]), merge_sort(seq[medio:]))

    return merge_sort(list(lista)), metricas


ALGORITMOS = {
    "burbuja": ordenamiento_burbuja,
    "seleccion": ordenamiento_seleccion,
    "insercion": ordenamiento_insercion,
    "rapido": ordenamiento_rapido,
    "mezcla": ordenamiento_mezcla,
}


def comparar(lista, clave=lambda x: x, reverse=False):
    """
    Ejecuta TODOS los algoritmos sobre la misma lista y devuelve una tabla
    [(nombre, comparaciones, intercambios, ¿resultado correcto?), ...].
    """
    referencia = sorted(lista, key=clave, reverse=reverse)
    filas = []
    for nombre, funcion in ALGORITMOS.items():
        ordenada, m = funcion(lista, clave=clave, reverse=reverse)
        ok = [clave(x) for x in ordenada] == [clave(x) for x in referencia]
        filas.append((nombre, m["comparaciones"], m["intercambios"], "sí" if ok else "NO"))
    return filas
