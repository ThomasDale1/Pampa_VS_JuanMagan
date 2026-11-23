"""
main_cuchillas.py — Main de desarrollo de CUCHILLAS (no es el main final del juego).

Corre SOLO las features de Cuchillas:
    datos.py, misiones.py, estado_mundo.py, finales.py

Uso:   python main_cuchillas.py
finales.py usa NodoDecision de ia.py (Thomas): si todavía no está en tu rama,
esa sección se salta con un aviso.
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


def demo_datos():
    from juego import datos
    print("  salas:", len(datos.SALAS), "| aristas:", len(datos.ARISTAS),
          "| objetos:", len(datos.CATALOGO_OBJETOS), "| enemigos:", len(datos.ENEMIGOS))
    print("  sala inicial:", datos.SALA_INICIAL, "| salidas:", sorted(datos.SALIDAS))
    print("  enemigos:", ", ".join(e["nombre"] for e in datos.ENEMIGOS.values()))
    print("  piso de 'celda':", datos.piso_de("celda"))
    print("  --- intro ---")
    for linea in datos.INTRO:
        print("   ", linea)


def demo_estado():
    from juego.estado_mundo import EstadoMundo
    e = EstadoMundo()
    e.activar("tigre_derrotado")
    e.incrementar("bocina_usos", 3)
    e.anexar("bitacora", "entró al cuarto de Juan")
    e["tragos"] = 2
    print("  tigre_derrotado:", e.esta_activa("tigre_derrotado"),
          "| bocina_usos:", e.obtener("bocina_usos"), "| 'tragos' in e:", "tragos" in e)
    print("  como_dict:", e.como_dict())
    print("  lecturas/escrituras:", e.lecturas, "/", e.escrituras)


def demo_misiones():
    from juego.estado_mundo import EstadoMundo
    from juego.misiones import construir_arbol_misiones, DEPENDENCIAS_ZONA
    e = EstadoMundo()
    raiz = construir_arbol_misiones()
    print("  --- sin avanzar ---")
    for l in raiz.render(e):
        print("   ", l)
    e.activar("tigre_derrotado")
    e.activar("visito_cuarto_juan")
    print("  --- tras vencer al tigre y entrar al cuarto ---")
    for l in raiz.render(e):
        print("   ", l)
    print("  progreso (hechas, total):", raiz.progreso(e))
    print("  dependencias de zona:")
    for zona, reqs in DEPENDENCIAS_ZONA.items():
        print(f"    {zona:18} <- {', '.join(reqs)}")


def demo_finales():
    from juego import finales
    print("  nº de finales:", finales.contar_finales())
    for l in finales.render_arbol():
        print("   ", l)
    print("  cómo juegas -> qué final te toca:")
    for desc, ctx in finales.CONTEXTOS_EJEMPLO:
        fid = finales.clasificar(ctx)
        print(f"    {desc:40} -> {finales.FINALES[fid]['titulo']}")


def main():
    seccion("1) DATOS del mundo: salas, objetos, enemigos, narrativa", demo_datos)
    seccion("2) ESTADO DEL MUNDO: tabla hash / diccionario", demo_estado)
    seccion("3) ÁRBOL DE MISIONES y dependencias", demo_misiones)
    seccion("4) ÁRBOL DE DECISIÓN de los finales (necesita ia.py de Thomas)", demo_finales)


if __name__ == "__main__":
    main()
