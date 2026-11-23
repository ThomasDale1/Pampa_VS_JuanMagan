"""
inventario.py — ESTRUCTURAS LINEALES: el inventario de Pampa como LISTA.

Semana 2: "Arreglos, vectores, listas y estructuras lineales básicas.
          Inventario funcional y listas de entidades del juego."

El inventario es una LISTA de ids de objeto (str). Sobre ella se demuestran:
    - recorrido y conteo,
    - BÚSQUEDA LINEAL para localizar un objeto por nombre (busqueda.py),
    - ORDENAMIENTO por valor/peso/nombre (ordenamiento.py),
    - inserción O(1) al final y borrado O(n) por valor.

El CATÁLOGO global (datos.CATALOGO_OBJETOS) se mantiene ORDENADO por 'id' para
poder aplicar BÚSQUEDA BINARIA en 'examinar' (ver motor.py).

Complejidad
-----------
    agregar        -> O(1)
    quitar         -> O(n)
    contiene       -> O(n)  (búsqueda lineal)
    peso_total     -> O(n)
    ordenar_por    -> O(n log n) con quicksort/mergesort propios
"""

from . import busqueda
from . import ordenamiento
from .ui import normalizar


def coincide_nombre(texto, id_obj, nombre):
    """¿'texto' (ya normalizado) identifica al objeto (id o nombre)?
    Acepta id exacto, subcadena del id ('carnet' -> 'carnet_falso'),
    subcadena del nombre, o que TODAS las palabras del texto aparezcan en el
    nombre ('botella vino' -> 'Botella de vino')."""
    if not texto:
        return False
    nombre_n = normalizar(nombre)
    id_txt = normalizar(id_obj).replace("_", " ")
    if texto == id_obj or texto in nombre_n or texto in id_txt:
        return True
    palabras = texto.split()
    return len(palabras) > 1 and all(p in nombre_n or p in id_txt for p in palabras)


class Inventario:
    def __init__(self, capacidad=10, catalogo_por_id=None):
        self.capacidad = capacidad
        self._objetos = []                       # lista de ids (str)
        self.catalogo = catalogo_por_id or {}

    # las llaves y las notas "van en el bolsillo": no ocupan mochila
    LIBRES = ("clave", "lore")

    def _tipo(self, id_objeto):
        return self.catalogo.get(id_objeto, {}).get("tipo", "")

    def cuenta_pesada(self):
        """Nº de objetos que SÍ ocupan sitio (todo menos llaves y notas)."""
        return sum(1 for i in self._objetos if self._tipo(i) not in self.LIBRES)

    # -- operaciones lineales básicas ---------------------------------
    def agregar(self, id_objeto):
        """Inserción al final de la lista: O(1)."""
        if self._tipo(id_objeto) not in self.LIBRES and self.lleno():
            return False, "La mochila está llena (suelta algo con 'soltar')."
        self._objetos.append(id_objeto)
        return True, f"Te echás a la bolsa: {self.nombre_de(id_objeto)}."

    def quitar(self, id_objeto):
        """Borrado por valor: O(n) (hay que encontrarlo y desplazar el resto)."""
        if id_objeto in self._objetos:
            self._objetos.remove(id_objeto)
            return True
        return False

    def contiene(self, id_objeto):
        return id_objeto in self._objetos

    def contar(self, id_objeto):
        return self._objetos.count(id_objeto)

    def lleno(self):
        return self.cuenta_pesada() >= self.capacidad

    def __len__(self):
        return len(self._objetos)

    def __iter__(self):
        return iter(self._objetos)

    def ids(self):
        return list(self._objetos)

    # -- utilidades de catálogo -------------------------------------
    def ficha(self, id_objeto):
        return self.catalogo.get(id_objeto, {})

    def nombre_de(self, id_objeto):
        return self.catalogo.get(id_objeto, {}).get("nombre", id_objeto)

    # -- BÚSQUEDA LINEAL por nombre (o fragmento) ------------------
    def buscar_por_nombre(self, texto):
        """
        Devuelve (id_objeto, comparaciones) usando búsqueda LINEAL sobre la
        lista del inventario. Acepta coincidencia parcial e insensible a
        mayúsculas. Es O(n), y n <= capacidad (10) -> instantáneo.
        """
        texto = normalizar(texto)
        comparaciones = 0
        for id_obj in self._objetos:
            comparaciones += 1
            if coincide_nombre(texto, id_obj, self.nombre_de(id_obj)):
                return id_obj, comparaciones
        return None, comparaciones

    # -- ORDENAMIENTO -------------------------------------------
    def ordenar_por(self, criterio="valor", descendente=True):
        """
        Devuelve una NUEVA lista de ids ordenada por 'valor', 'peso' o 'nombre'.
        Usa quicksort propio (ordenamiento.py). No modifica el inventario real.
        """
        claves = {
            "valor": lambda i: self.ficha(i).get("valor", 0),
            "peso": lambda i: self.ficha(i).get("peso", 0),
            "nombre": lambda i: self.nombre_de(i).lower(),
        }
        clave = claves.get(criterio, claves["valor"])
        reverse = descendente and criterio != "nombre"
        ordenados, metricas = ordenamiento.ordenamiento_rapido(
            self._objetos, clave=clave, reverse=reverse)
        return ordenados, metricas

    # -- RECURSIÓN: peso total ------------------------------------
    def peso_total(self):
        pesos = [self.ficha(i).get("peso", 0) for i in self._objetos]
        from .recursion import suma_lista
        return suma_lista(pesos)

    def valor_total(self):
        from .recursion import suma_lista
        return suma_lista([self.ficha(i).get("valor", 0) for i in self._objetos])

    # -- serialización -------------------------------------------
    def como_lista(self):
        return list(self._objetos)

    def cargar_lista(self, ids):
        self._objetos = list(ids)


def catalogo_ordenado_por_id(catalogo_lista):
    """
    Devuelve el catálogo como LISTA ordenada por 'id' (una sola vez, al inicio).
    Sobre esta lista se aplica BÚSQUEDA BINARIA en el comando 'examinar'.
    """
    ordenado, _ = ordenamiento.ordenamiento_mezcla(catalogo_lista, clave=lambda o: o["id"])
    return ordenado


def buscar_en_catalogo(catalogo_ordenado, id_objeto):
    """BÚSQUEDA BINARIA en el catálogo ordenado. Devuelve (ficha|None, comparaciones)."""
    idx, comparaciones = busqueda.busqueda_binaria(
        catalogo_ordenado, id_objeto, clave=lambda o: o["id"])
    if idx == -1:
        return None, comparaciones
    return catalogo_ordenado[idx], comparaciones
