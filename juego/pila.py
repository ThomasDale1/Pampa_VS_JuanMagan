"""
pila.py — PILA (Stack), estructura LIFO (Last In, First Out).

Semana 5 del curso: "Pilas. Historial de acciones. Backtracking básico."

Implementación propia sobre una lista de Python. Se usa una lista porque
`append` y `pop` al final son O(1) amortizado, que es justo lo que necesita
una pila.

Análisis de complejidad
-----------------------
    apilar (push)   -> O(1) amortizado
    desapilar (pop) -> O(1)
    cima (peek)     -> O(1)
    esta_vacia      -> O(1)
    tamaño          -> O(1)
    buscar / __contains__ -> O(n)   (recorre todos los elementos)
    Espacio         -> O(n)
"""


class PilaVacia(Exception):
    """Se lanza al desapilar o mirar la cima de una pila sin elementos."""


class Pila:
    def __init__(self, iterable=None):
        self._datos = list(iterable) if iterable else []

    # -- operaciones fundamentales -----------------------------------------
    def apilar(self, elemento):
        """push: agrega 'elemento' en la cima. O(1) amortizado."""
        self._datos.append(elemento)

    def desapilar(self):
        """pop: quita y devuelve el elemento de la cima. O(1)."""
        if self.esta_vacia():
            raise PilaVacia("No se puede desapilar: la pila está vacía.")
        return self._datos.pop()

    def cima(self):
        """peek: devuelve la cima SIN quitarla. O(1)."""
        if self.esta_vacia():
            raise PilaVacia("No hay cima: la pila está vacía.")
        return self._datos[-1]

    # -- consultas --------------------------------------------------------
    def esta_vacia(self):
        return len(self._datos) == 0

    def __len__(self):
        return len(self._datos)

    def __iter__(self):
        """Itera desde la cima hacia el fondo (orden LIFO)."""
        return reversed(self._datos)

    def __contains__(self, elemento):
        return elemento in self._datos

    def a_lista(self, desde_cima=True):
        """Copia el contenido a una lista. Por defecto, cima primero."""
        return list(self._datos[::-1]) if desde_cima else list(self._datos)

    def vaciar(self):
        self._datos.clear()

    def __repr__(self):
        return f"Pila(cima -> {self._datos[::-1]})"
