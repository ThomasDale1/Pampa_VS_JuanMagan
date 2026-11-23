"""
mapa.py — EL MAPA DE LA MANSIÓN COMO GRAFO.

Semana 12: "Mapa del juego representado como grafo."
Semana 13: "BFS y DFS integrados al juego."

Construye un objeto `Grafo` (grafo.py) a partir de `datos.SALAS` y
`datos.ARISTAS`, y añade la lógica propia del juego:
    - puertas cerradas que requieren un objeto o una bandera del EstadoMundo,
    - pasadizos secretos que solo aparecen con el plano de la mansión,
    - salas "descubiertas" (para no mostrar el mapa completo de golpe),
    - comandos 'mapa', 'camino' (BFS) y 'explorar' (DFS).
"""

from . import ui
from . import datos
from .grafo import Grafo


class Mapa:
    def __init__(self, estado_mundo):
        self.estado = estado_mundo
        self.grafo = Grafo(dirigido=False)
        self._construir()
        self.descubiertas = set()
        # nodos virtuales de salida (puerta principal y ventana del baño)
        for salida in datos.SALIDAS:
            self.grafo.agregar_nodo(salida)

    def _construir(self):
        for id_sala in datos.SALAS:
            self.grafo.agregar_nodo(id_sala)
        for a, b, cerradura in datos.ARISTAS:
            self.grafo.agregar_arista(a, b, cerradura)

    # ------------------------------------------------------------------
    def nombre(self, id_sala):
        if id_sala == datos.SALA_SALIDA:
            return "Portal a la calle (recibidor)"
        if id_sala == datos.SALA_VENTANA:
            return "Ventana del baño (calle)"
        return datos.SALAS.get(id_sala, {}).get("nombre", id_sala)

    def descubrir(self, id_sala):
        self.descubiertas.add(id_sala)

    def revelar_todo(self):
        self.descubiertas.update(self.grafo.nodos())

    # ---- puertas / cerraduras --------------------------------------
    def arista_transitable(self, a, b, inventario, ignorar_secretas=False):
        """
        ¿Se puede cruzar la puerta entre 'a' y 'b' con el inventario actual?
        Devuelve (bool, motivo).
        """
        cerradura = self.grafo.etiqueta(a, b)
        if cerradura is None:
            return True, ""
        if cerradura.get("secreta") and not ignorar_secretas:
            if not inventario.contiene("mapa_mansion"):
                return False, "__oculta__"       # ni siquiera se ve
        if "objeto" in cerradura:
            if not inventario.contiene(cerradura["objeto"]):
                ficha = datos.CATALOGO_OBJETOS
                nombre = next((o["nombre"] for o in ficha if o["id"] == cerradura["objeto"]),
                              cerradura["objeto"])
                return False, f"necesitas: {nombre}"
        if "flag" in cerradura:
            if not self.estado.esta_activa(cerradura["flag"]):
                return False, self._motivo_flag(cerradura["flag"])
        return True, ""

    @staticmethod
    def _motivo_flag(flag):
        return {
            "guardaespaldas_derrotado": "el guardaespaldas del salón bloquea el paso",
            "tigre_derrotado": "el tigre no te deja pasar a esa puerta",
        }.get(flag, f"falta: {flag}")

    def salidas_visibles(self, id_sala, inventario):
        """
        Lista de (sala_destino, transitable, motivo) desde 'id_sala',
        ocultando los pasadizos secretos aún no revelados.
        """
        resultado = []
        for vecino in self.grafo.vecinos(id_sala):
            ok, motivo = self.arista_transitable(id_sala, vecino, inventario)
            if motivo == "__oculta__":
                continue
            resultado.append((vecino, ok, motivo))
        return resultado

    def consumir_llave_si_procede(self, a, b, inventario, historial=None):
        cerradura = self.grafo.etiqueta(a, b)
        if cerradura and cerradura.get("consumir") and "objeto" in cerradura:
            inventario.quitar(cerradura["objeto"])

    # ---- PLANO 2D POR PISOS -----------------------------------------
    def plano_planta(self, indice, sala_actual, inventario):
        """
        Dibuja el plano 2D de una planta: cada sala es una cajita colocada en
        una rejilla (datos.PLANTAS) y entre salas vecinas se dibuja la puerta
        (═ abierta, ╌ cerrada). Abajo se listan pasadizos y escaleras a otros
        pisos. Es solo presentación; la topología real es el GRAFO.
        """
        planta = datos.PLANTAS[indice]
        salas = planta["salas"]
        max_col = max(c for c, _ in salas.values())
        max_row = max(r for _, r in salas.values())
        en = {(c, r): s for s, (c, r) in salas.items()}
        BW = 11

        def caja(sala, i):
            nom = datos.CORTO.get(sala, sala)[:BW - 2]
            aqui = sala == sala_actual
            if aqui:
                s = ("╔" + "═" * (BW - 2) + "╗" if i == 0 else
                     "║" + nom.center(BW - 2) + "║" if i == 1 else
                     "╚" + "═" * (BW - 2) + "╝")
            else:
                s = ("┌" + "─" * (BW - 2) + "┐" if i == 0 else
                     "│" + nom.center(BW - 2) + "│" if i == 1 else
                     "└" + "─" * (BW - 2) + "┘")
            return ui.c(s, "amarillo_claro" if aqui else "blanco")

        ui.escribir(f"\n  ╔═ {planta['nombre']}"
                    + ("   (estás aquí)" if datos.piso_de(sala_actual) == indice
                       or sala_actual in salas else "")
                    + " ═╗", "negrita", "cian_claro")
        for r in range(max_row + 1):
            for i in range(3):
                linea = "   "
                for cc in range(max_col + 1):
                    sala = en.get((cc, r))
                    linea += caja(sala, i) if sala else " " * BW
                    vecino = en.get((cc + 1, r))
                    if i == 1 and sala and vecino and self.grafo.hay_arista(sala, vecino):
                        ok, _ = self.arista_transitable(sala, vecino, inventario)
                        linea += ui.c("══" if ok else "╌╌", "verde" if ok else "gris")
                    else:
                        linea += "  "
                ui.escribir(linea)
            if r < max_row:
                linea = "   "
                for cc in range(max_col + 1):
                    sala, abajo = en.get((cc, r)), en.get((cc, r + 1))
                    if sala and abajo and self.grafo.hay_arista(sala, abajo):
                        ok, _ = self.arista_transitable(sala, abajo, inventario)
                        linea += " " * (BW // 2) + ui.c("║" if ok else "╎", "verde" if ok else "gris") \
                            + " " * (BW - BW // 2 - 1) + "  "
                    else:
                        linea += " " * (BW + 2)
                ui.escribir(linea)

        # puertas de este piso que no caben en la rejilla (se listan en texto)
        extra = []
        for a in salas:
            for b in self.grafo.vecinos(a):
                if b in salas and a < b:
                    ca, cb = salas[a], salas[b]
                    if abs(ca[0] - cb[0]) + abs(ca[1] - cb[1]) != 1:
                        etiq = " ⟷ ".join((datos.CORTO.get(a, a), datos.CORTO.get(b, b)))
                        cerr = self.grafo.etiqueta(a, b) or {}
                        extra.append(etiq + ("  (pasadizo secreto)" if cerr.get("secreta") else ""))
        if extra:
            ui.escribir("   otras puertas: " + " · ".join(sorted(set(extra))), "magenta")

        # escaleras / conexiones a otros pisos
        entre = set()
        for s in salas:
            for v in self.grafo.vecinos(s):
                if v in datos.SALIDAS or v in salas:
                    continue
                pv = datos.piso_de(v)
                if pv != indice:
                    entre.add(f"{datos.CORTO.get(s, s)} {'↑' if pv > indice else '↓'} "
                              f"{datos.PLANTAS[pv]['nombre'].title()}")
        if entre:
            ui.escribir("   entre pisos: " + " · ".join(sorted(entre)), "cian")
        ui.escribir("   ══ puerta abierta   ·   ╌╌/╎ puerta cerrada", "gris")

    # ---- vista de lista / matriz de adyacencia (grafo) -------------
    def mostrar(self, sala_actual, inventario):
        tiene_plano = inventario.contiene("mapa_mansion")
        ui.escribir("\nMAPA DE LA MANSIÓN (lista de adyacencia del grafo)", "negrita", "cian_claro")
        if not tiene_plano:
            ui.escribir("  (sin el plano solo ves las salas que ya visitaste)", "gris")

        visibles = self.grafo.nodos() if tiene_plano else sorted(self.descubiertas)
        for id_sala in visibles:
            if id_sala in datos.SALIDAS:
                continue
            marca = "→ " if id_sala == sala_actual else "  "
            conexiones = []
            for vecino in self.grafo.vecinos(id_sala):
                ok, motivo = self.arista_transitable(id_sala, vecino, inventario)
                if motivo == "__oculta__":
                    continue
                simbolo = "—" if ok else "×"
                conexiones.append(f"{simbolo}{self.nombre(vecino)}")
            ui.escribir(f"  {marca}{self.nombre(id_sala):28} : " + ", ".join(conexiones))

        if tiene_plano:
            self._mostrar_matriz(visibles)

    def _mostrar_matriz(self, orden_nodos):
        orden = [n for n in orden_nodos if n not in datos.SALIDAS]
        _, matriz = self.grafo.matriz_adyacencia(orden)
        ui.escribir("\nMATRIZ DE ADYACENCIA (1 = hay puerta):", "cian_claro")
        etiquetas = [n[:6] for n in orden]
        ui.escribir("        " + " ".join(f"{e:>6}" for e in etiquetas), "gris")
        for i, fila in enumerate(matriz):
            ui.escribir(f"  {etiquetas[i]:>6} " + " ".join(f"{v:>6}" for v in fila), "gris")

    # ---- comando 'camino' (BFS) --------------------------------
    def camino_mas_corto(self, origen, destino, inventario):
        """
        BFS: devuelve la lista de salas del camino MÁS CORTO (menos puertas)
        usando solo puertas ahora mismo transitables. O(V + E).
        """
        def transitable(a, b, _etiqueta):
            ok, _ = self.arista_transitable(a, b, inventario, ignorar_secretas=False)
            return ok
        return self.grafo.camino_mas_corto(origen, destino, arista_transitable=transitable)

    def explorar_dfs(self, origen):
        """DFS recursivo desde 'origen' sobre el grafo completo. O(V + E)."""
        return self.grafo.dfs_recursivo(origen)

    def bfs_niveles(self, origen):
        return self.grafo.bfs(origen)
