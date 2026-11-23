"""
main_thomas.py — Main de desarrollo de THOMAS (no es el main final del juego).

Corre SOLO las features de Thomas:
    pila.py, cola.py, historial.py, turnos.py, ia.py, combate.py

Uso:   python main_thomas.py
Las secciones que dependen de módulos de otros compañeros (ordenamiento,
ui, entidades, datos...) se saltan con un aviso si todavía no están en tu rama.
El juego completo se corre con main.py (lo entrega Kal).
"""

from types import SimpleNamespace


def seccion(titulo, funcion):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)
    try:
        funcion()
    except ImportError as e:
        print(f"  (se salta: falta un módulo de otro compañero -> {e})")


def demo_pila():
    from juego.pila import Pila
    p = Pila()
    for x in ["celda", "pasillo", "escalera", "salon"]:
        p.apilar(x)
    print("  pila (cima -> fondo):", p.a_lista())
    print("  cima:", p.cima(), "| desapilar ->", p.desapilar(), "| tamaño:", len(p))


def demo_cola():
    from juego.cola import Cola, ColaPrioridad
    c = Cola()
    for x in ["Pampa", "Rata", "Tigre"]:
        c.encolar(x)
    print("  cola FIFO:", c.a_lista(), "| desencolar ->", c.desencolar())
    pq = ColaPrioridad(max_primero=True)
    for nombre, iniciativa in [("Pampa", 9), ("Rata", 12), ("Tigre", 7)]:
        pq.encolar(nombre, iniciativa)
    orden = []
    while not pq.esta_vacia():
        orden.append(pq.desencolar())
    print("  cola de prioridad (mayor iniciativa primero):", orden)


def demo_historial():
    from juego.historial import Historial
    h = Historial()
    for sala in ["celda", "pasillo_sotano", "escalera", "salon"]:
        h.registrar_movimiento(sala)
    print("  ruta:", h.ruta_recorrida())
    print("  retroceder ->", h.retroceder(), "|", h.retroceder())
    estado = {"vida": 10}
    estado["vida"] += 5
    h.registrar_accion("curarse +5", lambda: estado.update(vida=10))
    print("  antes de deshacer:", estado, end="")
    h.deshacer()
    print(" | después:", estado)


def demo_ia():
    from juego import ia
    jefe = SimpleNamespace(vida=10, vida_max=70, tipo="jefe",
                           habilidad={"nombre": "x"}, habilidad_furia=None)
    pampa = SimpleNamespace(vida=30, vida_max=36)
    for turno, vida in [(1, 70), (2, 10)]:
        jefe.vida = vida
        traza = []
        accion = ia.decidir_accion(jefe, pampa, turno, traza=traza)
        print(f"  jefe con {vida}/70 de vida, turno {turno}:")
        print("    camino:", " | ".join(traza))
        print("    acción:", accion)


class _Combatiente:
    """Combatiente mínimo para probar turnos sin depender de entidades.py (Quique)."""
    def __init__(self, nombre, velocidad, vida=20):
        self.nombre, self.velocidad, self.vida, self.efectos = nombre, velocidad, vida, []

    @property
    def vivo(self):
        return self.vida > 0

    def aplicar_efecto(self, tipo, turnos, valor=0):
        self.efectos.append({"tipo": tipo, "turnos": turnos, "valor": valor})

    def recibir_dano(self, cantidad, ignora_defensa=False):
        self.vida = max(0, self.vida - cantidad)

    def limpiar_efectos_expirados(self):
        self.efectos = [e for e in self.efectos if e["turnos"] > 0]


def demo_turnos():
    from juego.turnos import SistemaTurnos, ColaEventos
    import random
    random.seed(1)
    cs = [_Combatiente("Pampa", 6), _Combatiente("Rata", 8), _Combatiente("Tigre", 7)]
    st = SistemaTurnos(cs)
    print("  orden de iniciativa:", st.orden_inicial)
    actor = st.siguiente()
    st.devolver_al_final(actor)
    print("  actúa", actor.nombre, "-> cola ahora:", st.snapshot())
    ev = ColaEventos()
    ev.programar_veneno(cs[0], turnos=2, dano_por_turno=3)
    for ronda in (1, 2, 3):
        print(f"  ronda {ronda}:", ev.procesar_ronda() or "sin eventos", "| vida Pampa:", cs[0].vida)


def demo_combate():
    from juego import ui, datos
    from juego.entidades import Pampa, Enemigo
    from juego.inventario import Inventario
    from juego.estado_mundo import EstadoMundo
    from juego.combate import Combate
    catalogo = {o["id"]: o for o in datos.CATALOGO_OBJETOS}
    pampa, inv, estado = Pampa(), Inventario(catalogo_por_id=catalogo), EstadoMundo()
    guion = iter(["2", "1"] + ["1"] * 20)
    ui.ENTRADA = lambda _p: next(guion)
    try:
        c = Combate(pampa, [Enemigo.desde_id("guardaespaldas")], inv, catalogo, estado)
        print("  resultado del combate de ejemplo:", c.ejecutar())
    except ui.SalirDelJuego:
        print("  (combate interrumpido)")
    finally:
        ui.ENTRADA = None


def main():
    seccion("1) PILA (LIFO)", demo_pila)
    seccion("2) COLA (FIFO) y COLA DE PRIORIDAD", demo_cola)
    seccion("3) HISTORIAL: pila de movimientos y deshacer", demo_historial)
    seccion("4) ÁRBOL DE DECISIÓN de la IA enemiga", demo_ia)
    seccion("5) SISTEMA DE TURNOS y COLA DE EVENTOS (necesita ordenamiento.py)", demo_turnos)
    seccion("6) COMBATE por turnos (necesita ui, entidades, datos, inventario)", demo_combate)


if __name__ == "__main__":
    main()
