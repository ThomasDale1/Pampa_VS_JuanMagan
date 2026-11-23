"""
misiones.py — ÁRBOL DE MISIONES Y DEPENDENCIAS (desbloqueos).

Semana 14: "Árboles, árboles de decisión y dependencias. Árbol de misiones o
           desbloqueos."

Los objetivos del juego forman un ÁRBOL: una misión padre solo se completa
cuando TODAS sus submisiones (hijos) están completas. La raíz es "Escapar de
la mansión".

                        [ Escapar de la mansión ]
                         /          |               \\
          [Vencer a Juan Magán]  [Pistola de portal]  [Llegar al recibidor]
              /            \\
   [Vencer al tigre]   [Entrar al cuarto de Juan]

Cada hoja se marca como completada desde el motor cuando ocurre el evento
correspondiente (derrotar a un enemigo, recoger un objeto, entrar a una sala).
El árbol se evalúa de forma RECURSIVA (post-orden): O(n) sobre los nodos.
"""


class NodoMision:
    def __init__(self, id_mision, titulo, descripcion="", condicion=None, oculta=False):
        self.id = id_mision
        self.titulo = titulo
        self.descripcion = descripcion
        # condicion(estado_mundo) -> bool  (solo para hojas)
        self.condicion = condicion
        self.oculta = oculta                 # no se muestra hasta desbloquearse
        self.hijos = []
        self.completada_manual = False

    def agregar(self, *hijos):
        self.hijos.extend(hijos)
        return self

    # -- evaluación RECURSIVA (post-orden) --------------------------
    def completada(self, estado):
        """
        Una misión con hijos se completa si TODOS sus hijos se completan.
        Una hoja se completa si su condición es verdadera (o se marcó a mano).
        """
        if self.hijos:
            return all(h.completada(estado) for h in self.hijos)
        if self.completada_manual:
            return True
        return bool(self.condicion and self.condicion(estado))

    def desbloqueada(self, estado):
        """Una misión oculta se desbloquea cuando sus 'hermanos previos' avanzan.
        Aquí simplificamos: se desbloquea si su padre no está aún completo y
        al menos un hijo previo del árbol está hecho. El motor pasa el estado."""
        return not self.oculta or estado.esta_activa(f"mision_vista_{self.id}")

    # -- utilidades de recorrido -------------------------------
    def recorrer(self):
        """Pre-orden: devuelve todos los nodos del subárbol."""
        yield self
        for h in self.hijos:
            yield from h.recorrer()

    def progreso(self, estado):
        """Devuelve (completadas, total) de las HOJAS del subárbol."""
        hojas = [n for n in self.recorrer() if not n.hijos]
        hechas = sum(1 for h in hojas if h.completada(estado))
        return hechas, len(hojas)

    def render(self, estado, nivel=0, lineas=None):
        """Dibuja el árbol con marcas [x]/[ ] de forma recursiva."""
        lineas = [] if lineas is None else lineas
        if self.oculta and not estado.esta_activa(f"mision_vista_{self.id}"):
            marca = "[?]"
            titulo = "??? (misión oculta)"
        else:
            marca = "[x]" if self.completada(estado) else "[ ]"
            titulo = self.titulo
        lineas.append("   " * nivel + f"{marca} {titulo}")
        for h in self.hijos:
            h.render(estado, nivel + 1, lineas)
        return lineas


def construir_arbol_misiones():
    """Crea y devuelve la raíz del árbol de misiones del juego."""
    m_tigre = NodoMision(
        "vencer_tigre", "Derrotar al Tigre de Juan Magán",
        condicion=lambda e: e.esta_activa("tigre_derrotado"))
    m_entrar_cuarto = NodoMision(
        "entrar_cuarto", "Entrar en el cuarto de Juan Magán",
        condicion=lambda e: e.esta_activa("visito_cuarto_juan"))
    m_juan = NodoMision(
        "vencer_juan", "Vencer a Juan Magán").agregar(m_tigre, m_entrar_cuarto)

    m_juan_muerto = NodoMision(
        "juan_derrotado", "Juan Magán derrotado",
        condicion=lambda e: e.esta_activa("juan_derrotado"))

    m_portal = NodoMision(
        "pistola_portal", "Conseguir la pistola de portal",
        condicion=lambda e: e.esta_activa("tiene_pistola_portal"))
    m_recibidor = NodoMision(
        "llegar_recibidor", "Llegar al recibidor",
        condicion=lambda e: e.esta_activa("visito_recibidor"))

    raiz = NodoMision(
        "escapar", "ESCAPAR DE LA MANSIÓN",
        "Abre un portal a la calle y sal con vida."
    ).agregar(m_juan, m_juan_muerto, m_portal, m_recibidor)
    return raiz


# --- ÁRBOL DE DESBLOQUEOS / DEPENDENCIAS DE ZONAS -----------------------
# (qué necesitas para poder ACCEDER a cada zona; se muestra con 'objetivos')
DEPENDENCIAS_ZONA = {
    "pasillo_sotano": ["forzar la puerta de la celda con el carné falso"],
    "estudio": ["la llave del candado de la bici (bodega)"],
    "pasillo_alto": ["derrotar al guardaespaldas del salón"],
    "cuarto_juan": ["derrotar al tigre del jardín"],
    "puerta_principal": ["la pistola de portal (estudio)"],
}
