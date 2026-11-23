"""
main_quique.py — Main de desarrollo de QUIQUE (no es el main final del juego).

Corre SOLO las features de Quique:
    grafo.py, mapa.py, recursion.py, entidades.py, ui.py

Uso:   python main_quique.py
Las secciones que dependen de módulos de otros compañeros (datos, estado_mundo,
inventario...) se saltan con un aviso si todavía no están en tu rama.
El juego completo se corre con main.py (lo entrega Kal).
"""


def seccion(titulo, funcion):
    print("\n" + "=" * 70)
    print(titulo)
    print("=" * 70)
    try:
        funcion()
    except ImportError as e:
        print(f"  (se salta: falta un módulo de otro compañero -> {e})")


def demo_ui():
    from juego import ui
    ui.habilitar_ansi_windows()
    ui.titulo("PAMPA Y LA MAZMORRA")
    ui.caja("Despiertas en un sótano.\nTe duele todo.", "Intro")
    print(ui.barra_vida(14, 36))
    ui.tabla(["objeto", "valor"], [["Pizza fría", 2], ["Palo selfie", 9]])
    print("  normalizar('  ÁRBOL  ') ->", repr(ui.normalizar("  ÁRBOL  ")))


def demo_grafo():
    from juego.grafo import Grafo
    g = Grafo()
    for a, b in [("celda", "pasillo"), ("pasillo", "bodega"), ("pasillo", "escalera"),
                 ("escalera", "salon"), ("salon", "jardin"), ("bodega", "escalera")]:
        g.agregar_arista(a, b)
    print("  vértices:", len(g.nodos()), "| aristas:", g.num_aristas())
    orden, m = g.matriz_adyacencia()
    print("  matriz de adyacencia, orden:", orden)
    for fila in m:
        print("   ", fila)
    print("  BFS:", " -> ".join(g.bfs("celda")))
    print("  DFS iterativo:", " -> ".join(g.dfs_iterativo("celda")))
    print("  DFS recursivo:", " -> ".join(g.dfs_recursivo("celda")))
    print("  camino más corto celda->jardin:", " -> ".join(g.camino_mas_corto("celda", "jardin")))
    print("  nº de caminos simples celda->salon:", len(g.todos_los_caminos("celda", "salon")))
    print("  ¿conexo?", g.es_conexo())


def demo_recursion():
    from juego import recursion as r
    print("  factorial(6) =", r.factorial(6))
    print("  fibonacci(15) =", r.fibonacci(15), "| fibonacci_memo(50) =", r.fibonacci_memo(50))
    print("  potencia(2, 10) =", r.potencia(2, 10))
    print("  suma_lista / maximo_lista:", r.suma_lista([3, 1, 4, 1, 5]), "/", r.maximo_lista([3, 1, 4, 1, 5]))
    print("  aplanar([1,[2,[3,4]],5]) =", r.aplanar([1, [2, [3, 4]], 5]))
    print("  hanoi(3) =", r.hanoi(3))


def demo_entidades():
    from juego.entidades import Pampa, Entidad
    p = Pampa()
    rata = Entidad("Rata", vida=12, ataque=4, defensa=0, velocidad=8)
    print("  ", p, "| ataque", p.ataque, "defensa", p.defensa, "vel", p.velocidad)
    print("  Pampa golpea a la rata:", rata.recibir_dano(p.ataque), "de daño ->", rata)
    rata.aplicar_efecto("veneno", 3, 2)
    print("  efectos de la rata:", rata.descripcion_efectos())
    print("  Pampa gana 70 XP, ¿subió de nivel?", p.ganar_xp(70, "Rata"), "-> nivel", p.nivel)
    print("  curar 5:", p.curar(5), "| vida:", p.vida)


def demo_mapa():
    from juego.mapa import Mapa
    from juego.estado_mundo import EstadoMundo
    from juego.inventario import Inventario
    m = Mapa(EstadoMundo())
    m.revelar_todo()
    print("  salas:", len(m.grafo.nodos()), "| aristas:", m.grafo.num_aristas())
    print("  plano y listas del mapa:")
    m.mostrar("celda", Inventario())


def main():
    seccion("1) UI: utilidades de terminal", demo_ui)
    seccion("2) GRAFO: lista/matriz de adyacencia, BFS y DFS", demo_grafo)
    seccion("3) RECURSIÓN y divide y vencerás", demo_recursion)
    seccion("4) ENTIDADES: Pampa, vida, efectos, XP", demo_entidades)
    seccion("5) MAPA de la mansión como grafo (necesita datos, estado_mundo, inventario)", demo_mapa)


if __name__ == "__main__":
    main()
