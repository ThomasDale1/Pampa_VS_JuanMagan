"""
recursion.py — RECURSIVIDAD y DIVIDE Y VENCERÁS aplicadas al juego.

Semana 7: "Recursividad y divide y conquista. Algoritmo recursivo aplicado
          al juego."

Se agrupan aquí los algoritmos recursivos que el juego usa de verdad:

    fibonacci(n)              -> acertijo de la Biblioteca (puerta de la
                                 estantería que pide "el n-ésimo número").
    fibonacci_memo(n)         -> misma función con memoización: muestra cómo
                                 pasar de O(2^n) a O(n).
    factorial(n)              -> cálculo de combinaciones para una cerradura.
    potencia(base, exp)       -> exponenciación rápida O(log n) (divide y vencerás).
    suma_lista(lista)         -> suma recursiva (peso total del inventario).
    contar_tesoros(sala, ...) -> recorre el árbol/grafo de salas contando objetos.
    aplanar(estructura)       -> aplana listas anidadas (mapa de pistas).
    hanoi(n, ...)             -> mini-puzzle opcional de las Torres de Hanói.

Análisis de complejidad
-----------------------
    fibonacci (ingenuo)   -> O(2^n) tiempo,  O(n) espacio (pila de llamadas)
    fibonacci_memo        -> O(n) tiempo,    O(n) espacio
    factorial             -> O(n) tiempo,    O(n) espacio
    potencia (rápida)     -> O(log n) tiempo, O(log n) espacio
    suma_lista            -> O(n) tiempo,    O(n) espacio
    hanoi                 -> O(2^n) tiempo,  O(n) espacio
"""


def factorial(n):
    """Caso base: 0! = 1! = 1. Caso recursivo: n! = n * (n-1)!."""
    if n < 0:
        raise ValueError("factorial no está definido para negativos")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    """
    Definición recursiva pura: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2).
    ¡Cuidado! Es O(2^n): recalcula los mismos valores una y otra vez.
    """
    if n < 0:
        raise ValueError("n debe ser >= 0")
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def fibonacci_memo(n, cache=None):
    """
    Misma recursión + MEMOIZACIÓN (guardar resultados ya calculados).
    Pasa de O(2^n) a O(n). Ejemplo de optimización para la defensa técnica.
    """
    cache = {} if cache is None else cache
    if n < 2:
        return n
    if n in cache:
        return cache[n]
    cache[n] = fibonacci_memo(n - 1, cache) + fibonacci_memo(n - 2, cache)
    return cache[n]


def potencia(base, exponente):
    """
    Exponenciación rápida por DIVIDE Y VENCERÁS:
        base^exp = (base^(exp/2))^2            si exp es par
        base^exp = base * base^(exp-1)         si exp es impar
    O(log n) multiplicaciones en lugar de O(n).
    """
    if exponente < 0:
        raise ValueError("exponente negativo no soportado")
    if exponente == 0:
        return 1
    if exponente % 2 == 0:
        mitad = potencia(base, exponente // 2)
        return mitad * mitad
    return base * potencia(base, exponente - 1)


def suma_lista(lista):
    """Suma recursiva: suma(l) = l[0] + suma(l[1:]). O(n)."""
    if not lista:
        return 0
    return lista[0] + suma_lista(lista[1:])


def maximo_lista(lista):
    """Máximo recursivo por reducción: compara la cabeza con el máx de la cola."""
    if len(lista) == 1:
        return lista[0]
    resto = maximo_lista(lista[1:])
    return lista[0] if lista[0] > resto else resto


def aplanar(estructura):
    """
    Aplana listas anidadas de profundidad arbitraria (recursión sobre la
    estructura). Se usa para desplegar el árbol de pistas del diario de Juan.
    """
    resultado = []
    for elemento in estructura:
        if isinstance(elemento, (list, tuple)):
            resultado.extend(aplanar(elemento))
        else:
            resultado.append(elemento)
    return resultado


def contar_objetos_alcanzables(grafo, sala_inicial, objetos_por_sala, visitadas=None):
    """
    RECURSIÓN SOBRE UN GRAFO (equivale a un DFS recursivo): cuenta cuántos
    objetos hay en todas las salas alcanzables desde 'sala_inicial'.
    Complejidad: O(V + E).
    """
    visitadas = set() if visitadas is None else visitadas
    visitadas.add(sala_inicial)
    total = len(objetos_por_sala.get(sala_inicial, []))
    for vecina in grafo.vecinos(sala_inicial):
        if vecina not in visitadas:
            total += contar_objetos_alcanzables(grafo, vecina, objetos_por_sala, visitadas)
    return total


def hanoi(n, origen="A", auxiliar="B", destino="C", movimientos=None):
    """
    Torres de Hanói: puzzle recursivo clásico. Mueve n discos de 'origen' a
    'destino'. Devuelve la lista de movimientos. O(2^n) movimientos.
    """
    movimientos = [] if movimientos is None else movimientos
    if n == 1:
        movimientos.append((origen, destino))
        return movimientos
    hanoi(n - 1, origen, destino, auxiliar, movimientos)
    movimientos.append((origen, destino))
    hanoi(n - 1, auxiliar, origen, destino, movimientos)
    return movimientos
