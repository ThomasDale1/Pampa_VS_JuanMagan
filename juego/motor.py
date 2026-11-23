"""
motor.py — BUCLE PRINCIPAL DEL JUEGO (interfaz de UNA SOLA TECLA).

El juego NO se escribe: se pulsa una tecla.
    números  -> ir a una salida
    letras   -> agarrar objetos y elegir opciones de las pantallas
    I mochila · M mapa · L mirar · T objetivos · P Pampa · R volver · G guardar

Cada acción "toca" una o varias estructuras del curso:
    ir / retroceder   -> GRAFO + PILA (historial de movimientos)
    agarrar / usar    -> LISTA (inventario) + BÚSQUEDA LINEAL
    examinar objeto   -> BÚSQUEDA BINARIA sobre el catálogo ordenado
    mapa              -> GRAFO: lista y matriz de adyacencia
    trazar ruta       -> BFS (camino más corto)
    explorar          -> DFS (recorrido en profundidad, recursivo)
    objetivos         -> ÁRBOL de misiones + DICCIONARIO de estados (tabla hash)
    Pampa / ranking   -> ORDENAMIENTOS (comparación)
    acertijo          -> RECURSIVIDAD (Fibonacci)
    (combate)         -> COLA de turnos + COLA de eventos + ÁRBOL de decisión
    guardar / cargar  -> serialización del diccionario de estado
    (final)           -> ÁRBOL DE DECISIÓN de finales.py
"""

import json
import os
import random
import time

from . import ui
from . import datos
from . import busqueda
from . import ordenamiento
from . import recursion
from . import complejidad
from . import benchmark
from .entidades import Pampa, Enemigo
from .estado_mundo import EstadoMundo
from .inventario import (Inventario, catalogo_ordenado_por_id, buscar_en_catalogo,
                         coincide_nombre)
from .historial import Historial
from .mapa import Mapa
from .misiones import construir_arbol_misiones, DEPENDENCIAS_ZONA
from .combate import Combate
from . import alcohol
from . import finales

RUTA_PROGRESO = os.path.join(os.path.dirname(os.path.dirname(__file__)), "progreso.json")


class Juego:
    def __init__(self, guion=None, semilla=None):
        if semilla is not None:
            random.seed(semilla)
        self.catalogo_por_id = {o["id"]: o for o in datos.CATALOGO_OBJETOS}
        # LISTA ordenada por 'id' -> permite BÚSQUEDA BINARIA en 'examinar'
        self.catalogo_ordenado = catalogo_ordenado_por_id(datos.CATALOGO_OBJETOS)

        self.pampa = Pampa()
        self.pampa.aplicar_equipo(self.catalogo_por_id)
        self.estado = EstadoMundo()                    # DICCIONARIO / tabla hash
        # LISTA. Mochila deliberadamente apretada: 8 objetos "pesados" (las llaves
        # y las notas no cuentan). Obliga a elegir qué cargar, pero sobra de sobra
        # para cualquiera de los 8 finales (ninguno pide llevar más de 3-4 cosas).
        self.inv = Inventario(capacidad=8, catalogo_por_id=self.catalogo_por_id)
        self.historial = Historial()                   # PILAS
        self.mapa = Mapa(self.estado)                  # GRAFO
        self.misiones = construir_arbol_misiones()     # ÁRBOL

        self.sala_actual = datos.SALA_INICIAL
        self.turno_mundo = 0
        self.terminado = False
        self.final_id = None
        self.contexto_final = {}
        self.inicio_tiempo = time.perf_counter()
        self.progreso = self._cargar_progreso()
        self._recien_cargado = False

        self.objetos_en_sala = {s: list(d.get("objetos", [])) for s, d in datos.SALAS.items()}
        self.enemigo_en_sala = {s: d.get("enemigo") for s, d in datos.SALAS.items()}

        self._guion = list(guion) if guion else None
        self._guion_iter = iter(self._guion) if self._guion else None
        if self._guion_iter is not None:
            ui.ENTRADA = self._siguiente_guion

    def _siguiente_guion(self, _prompt):
        return next(self._guion_iter)

    # ==================================================================
    #  ARRANQUE
    # ==================================================================
    def jugar(self):
        try:
            self._intro()
            if not self._recien_cargado:
                self._entrar_sala(self.sala_actual, primera=True)
            else:
                self._describir_sala()
            while not self.terminado:
                self._turno_sala()
        except ui.SalirDelJuego:
            ui.escribir("\n(se acabó la partida)", "gris")
        except KeyboardInterrupt:
            ui.escribir("\n\nDejaste a Pampa botado donde el Juan. Qué mal cheró. Adiós.", "gris")
            return
        self._final()

    def _intro(self):
        ui.habilitar_ansi_windows()
        print(ui.c(datos.ARTE_TITULO, "cian"))
        for linea in datos.INTRO:
            ui.escribir("  " + linea, "blanco")
        ui.escribir()
        vistos = len(self.progreso.get("finales", []))
        ui.caja(
            "Esto se juega con UNA sola tecla, sin escribir nada:\n"
            "  · números  -> ir a una salida\n"
            "  · letras   -> agarrar objetos y elegir opciones\n"
            "  · [I] mochila  [M] mapa por pisos  [L] mirar  [T] objetivos  [P] Pampa\n"
            "  · [R] volver   [G] guardar  [?] manual  [Q] salir\n"
            f"Hay {finales.contar_finales()} finales distintos; llevás "
            f"{vistos}/{finales.contar_finales()} vistos.",
            "CÓMO SE JUEGA", "cian")
        if ui.ENTRADA is None:
            k = ui.elegir("", [("s", "Sí, mostrame el manual completo")], permitir_esc=True,
                          prompt="  ¿Querés leer el manual de cómo jugar?  [S] sí   ·   [Enter] no:")
            if k == "s":
                self._manual()
            if os.path.exists(self._ruta_guardado("partida")):
                k = ui.elegir("", [("c", "Seguir la partida guardada")], permitir_esc=True,
                              prompt="  [C] cargar la partida guardada   ·   [Enter] empezar de cero:")
                if k == "c":
                    self._cargar()
                    return
        ui.pausa()

    def _manual(self):
        ui.escribir("\n  MANUAL — TODO SE HACE CON UNA TECLA", "negrita", "cian_claro")
        ui.escribir("  (una sola pulsación; no hay que darle a Enter)\n", "gris")
        secciones = [
            ("MOVERSE", [
                ("1 – 9", "ir a la salida con ese número (aparecen abajo en el menú)"),
                ("R", "volver a la sala anterior — usa la PILA de movimientos"),
                ("L", "volver a mirar / leer la sala"),
            ]),
            ("OBJETOS", [
                ("A – H", "agarrar el objeto con esa letra (lo mejor se equipa solo)"),
                ("", "   la mochila aguanta 8 cosas 'pesadas'; llaves y notas no cuentan"),
                ("I", "abrir la mochila: ahí elegís una letra y luego"),
                ("", "   [U] usar/consumir · [B] beber · [E] equipar/quitar · [S] soltar"),
                ("", "   [1] ordenar (quicksort) · [2] lineal vs binaria · [3] deshacer"),
            ]),
            ("MAPA (tecla M)", [
                ("M", "plano 2D del piso donde estás"),
                ("1/2/3", "ver el plano de otro piso (sótano / noble / alta)"),
                ("A", "lista y matriz de adyacencia (el grafo de verdad)"),
                ("C / X", "ruta más corta (BFS) / recorrer todo (DFS) — con el plano"),
            ]),
            ("EN CADA SALA", [
                ("V", "beber un trago (arriesgado: ver Pampa [P])"),
                ("X", "probar el estante del acertijo (Fibonacci)"),
                ("J", "calentar el brazo en el beer pong (comedor)"),
                ("Z", "tirar de la alarma de incendios (planta alta)"),
                ("K", "quedarte con la mansión (después de vencer a Juan)"),
            ]),
            ("CON UN ENEMIGO DELANTE", [
                ("1", "pelear (combate por turnos)"),
                ("2 / 3", "la salida sin bronca: sobornar/cantar/retar · colarse/bailar"),
                ("4", "tirar de la alarma (solo con Juan)"),
                ("9", "alejarte por donde viniste"),
            ]),
            ("EN COMBATE", [
                ("1", "atacar    ·    2  habilidad / hechizo"),
                ("3", "usar un objeto (¡acá curás con las pociones!)"),
                ("4", "defender  ·    5  huir"),
            ]),
            ("OTRAS", [
                ("T", "objetivos (árbol de misiones) y estado del mundo"),
                ("P", "ficha de Pampa y ranking de enemigos"),
                ("G / Q", "guardar la partida / salir"),
                ("Esc", "cerrar cualquier pantalla y volver"),
            ]),
        ]
        for titulo, filas in secciones:
            ui.escribir(f"  ── {titulo} ──", "amarillo_claro")
            for tecla, desc in filas:
                ui.escribir(f"     {tecla:8} {desc}" if tecla else f"     {'':8} {desc}")
            ui.escribir()
        ui.pausa()

    # -- progreso entre partidas (serialización del diccionario) --------
    def _cargar_progreso(self):
        try:
            with open(RUTA_PROGRESO, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, ValueError):
            return {"finales": []}

    def _guardar_progreso(self):
        vistos = sorted(set(self.progreso.get("finales", [])) | {self.final_id})
        self.progreso = {"finales": vistos}
        try:
            with open(RUTA_PROGRESO, "w", encoding="utf-8") as fh:
                json.dump(self.progreso, fh, ensure_ascii=False, indent=2)
        except OSError:
            pass

    # ==================================================================
    #  SALAS (GRAFO) y menú por teclas
    # ==================================================================
    def _entrar_sala(self, id_sala, primera=False, por_retroceso=False):
        self.sala_actual = id_sala
        self.mapa.descubrir(id_sala)
        self.estado.activar(f"visito_{id_sala}")
        self.estado.anexar("bitacora", id_sala)

        sala = datos.SALAS.get(id_sala, {})
        texto_primera = sala.get("primera_visita")
        if texto_primera and not self.estado.esta_activa(f"narrado_{id_sala}"):
            ui.caja(texto_primera, "···", "magenta")
        self.estado.activar(f"narrado_{id_sala}")
        self._describir_sala()

    def _describir_sala(self):
        sala = datos.SALAS.get(self.sala_actual, {})
        ui.regla("═")
        ui.escribir("  " + self.mapa.nombre(self.sala_actual).upper(), "negrita", "cian_claro")
        ui.escribir("  " + sala.get("descripcion", ""), "blanco")
        objetos = self.objetos_en_sala.get(self.sala_actual, [])
        if objetos:
            ui.escribir("  Tirado por acá: " +
                        ", ".join(self.catalogo_por_id[o]["nombre"] for o in objetos),
                        "amarillo_claro")
        eid = self.enemigo_en_sala.get(self.sala_actual)
        if eid:
            ui.escribir("  ¡" + datos.ENEMIGOS[eid]["nombre"] +
                        " está acá y no te quita el ojo de encima!", "rojo_claro")
        ui.regla("═")

    def _marco(self):
        p = self.pampa
        col = "verde" if p.vida > p.vida_max * 0.4 else "amarillo" if p.vida > p.vida_max * 0.2 else "rojo"
        estado = ui.c(f"vida {p.vida}/{p.vida_max}", col)
        if p.tragos:
            estado += ui.c(f"  ·  tragos {p.tragos}", "magenta")
        return ui.c(f"── {self.mapa.nombre(self.sala_actual).upper()} ──", "cian_claro") + "   " + estado

    # ---- turno normal (sin enemigo) --------------------------------
    def _turno_sala(self):
        enemigo_id = self.enemigo_en_sala.get(self.sala_actual)
        if enemigo_id:
            self._turno_enemigo(enemigo_id)
            return

        acciones = {}
        obj_l, sal_l, ext_l = [], [], []

        for i, oid in enumerate(self.objetos_en_sala.get(self.sala_actual, [])[:8]):
            t = chr(ord("a") + i)
            acciones[t] = (lambda o=oid: self._agarrar(o))
            obj_l.append((t, "Agarrar: " + self.catalogo_por_id[oid]["nombre"], "amarillo_claro"))

        for i, (destino, ok, motivo) in enumerate(self.mapa.salidas_visibles(self.sala_actual, self.inv), 1):
            t = str(i)
            acciones[t] = (lambda d=destino: self._ir_a(d))
            etq = "Ir a: " + self.mapa.nombre(destino) + ("" if ok else f"   (cerrado: {motivo})")
            sal_l.append((t, etq, "verde" if ok else "gris"))

        fuente = self._fuente_trago()
        if fuente:
            acciones["v"] = self._beber
            ext_l.append(("v", f"Beber un trago — {self._describir_fuente(fuente)} (arriesgado)", "magenta"))
        if self.sala_actual == "comedor" and not self.estado.esta_activa("calienta_brazo"):
            acciones["j"] = self._cmd_beerpong
            ext_l.append(("j", "Calentar el brazo con el beer pong", "cian"))
        sala_d = datos.SALAS.get(self.sala_actual, {})
        if "acertijo" in sala_d and not self.estado.esta_activa(f"acertijo_{self.sala_actual}"):
            acciones["x"] = self._acertijo
            ext_l.append(("x", "Probar el estante del acertijo (Fibonacci)", "magenta"))
        if self.sala_actual == "pasillo_alto":
            acciones["z"] = self._cmd_alarma
            ext_l.append(("z", "Tirar de la alarma de incendios", "rojo"))
        if self.sala_actual == "cuarto_juan" and self.estado.esta_activa("juan_derrotado"):
            acciones["k"] = self._cmd_quedarse
            ext_l.append(("k", "Quedarte con el cantón de Juan Magán", "amarillo_claro"))

        acciones.update({
            "i": self._pantalla_inventario, "m": self._pantalla_mapa,
            "l": self._describir_sala, "t": self._pantalla_objetivos,
            "p": self._pantalla_pampa, "r": self._retroceder,
            "g": self._guardar, "?": self._manual, "q": self._pedir_salir,
        })

        ui.escribir()
        ui.escribir("  " + self._marco())
        for t, etq, col in obj_l + sal_l + ext_l:
            ui.escribir(f"    [{t.upper()}] {etq}", col)
        ui.escribir("    " + ui.c("[I]", "cian") + " Mochila  " + ui.c("[M]", "cian") + " Mapa  "
                    + ui.c("[L]", "cian") + " Mirar  " + ui.c("[T]", "cian") + " Objetivos  "
                    + ui.c("[P]", "cian") + " Pampa", "gris")
        ui.escribir("    " + ui.c("[R]", "cian") + " Volver   " + ui.c("[G]", "cian") + " Guardar  "
                    + ui.c("[?]", "cian") + " Manual  " + ui.c("[Q]", "cian") + " Salir", "gris")
        ui.escribir("  Pulsá una tecla:", "amarillo_claro")

        ui.CONTEXTO_MENU = "sala"
        k = ui.leer_tecla()
        fn = acciones.get(k)
        if fn:
            fn()
        elif k in ("ESC", "ENTER"):
            self._describir_sala()
        else:
            ui.escribir("  Esa tecla no hace nada acá. (pulsá ? para la ayuda)", "rojo")

    # ---- turno con enemigo (la decisión clave: a quién enfrentás) --
    def _turno_enemigo(self, enemigo_id):
        nombre = datos.ENEMIGOS[enemigo_id]["nombre"]
        ui.escribir()
        ui.escribir("  " + self._marco())
        ui.escribir(f"  ⚔  {nombre} te cierra el paso.", "rojo_claro")

        entradas, acciones = [("1", "Pelear", "rojo")], {"1": lambda: self._combate(enemigo_id)}

        def bloqueada(motivo):
            return lambda m=motivo: ui.escribir(f"  Todavía no podés: {m}.", "rojo")

        if enemigo_id == "guardaespaldas":
            if self.inv.contiene("botella_tequila"):
                entradas.append(("2", "Invitarle a chupitos hasta que se le olvide su trabajo"))
                acciones["2"] = self._cmd_sobornar
            else:
                entradas.append(("2", "Invitarle a chupitos  (necesitás una botella)", "gris"))
                acciones["2"] = bloqueada("no cargás botella (hay en la bodega)")
            if self.pampa.tragos >= 2:
                entradas.append(("3", "Colártela: '¡soy el DJ de refuerzo!'"))
                acciones["3"] = self._cmd_colarse
            else:
                entradas.append(("3", "Colártela de DJ  (necesitás aplomo: 2 tragos)", "gris"))
                acciones["3"] = bloqueada("te falta aplomo (2 tragos)")
        elif enemigo_id == "tigre":
            if self.estado.esta_activa("leyo_diario"):
                entradas.append(("2", "Cantarle el estribillo de Juan Magán"))
                acciones["2"] = self._cmd_cantar
            else:
                entradas.append(("2", "Cantarle el estribillo  (leé antes el diario)", "gris"))
                acciones["2"] = bloqueada("no te sabés el estribillo (leé el diario del estudio)")
        elif enemigo_id == "juan_magan":
            entradas.append(("2", "Retarlo a un duelo de chupitos"))
            acciones["2"] = self._cmd_retar
            if self.pampa.tragos >= 3 or self.estado.esta_activa("calienta_brazo"):
                entradas.append(("3", "Batalla de perreo"))
                acciones["3"] = self._cmd_bailar
            else:
                entradas.append(("3", "Batalla de perreo  (soltura: 3 tragos o calentar brazo)", "gris"))
                acciones["3"] = bloqueada("te falta soltura (3 tragos, o calentá brazo en el comedor)")
            entradas.append(("4", "Tirar de la alarma de incendios"))
            acciones["4"] = self._cmd_alarma

        entradas.append(("9", "Alejarte por donde viniste"))
        acciones["9"] = self._retroceder

        k = ui.elegir("¿Qué hacés?", entradas, permitir_esc=False)
        acciones.get(k, lambda: None)()

    # ==================================================================
    #  OBJETOS: LISTA + BÚSQUEDA LINEAL + PILA de acciones
    # ==================================================================
    def _agarrar(self, oid):
        objetos = self.objetos_en_sala.get(self.sala_actual, [])
        if oid not in objetos:
            ui.escribir("  Eso ya no está acá.", "gris")
            return
        # BÚSQUEDA LINEAL sobre la lista de objetos de la sala (didáctico)
        pos = objetos.index(oid) + 1
        ok, msg = self.inv.agregar(oid)
        ui.escribir("  " + msg, "verde" if ok else "rojo")
        if not ok:
            return
        objetos.remove(oid)
        ui.escribir(f"  (búsqueda lineal: estaba en la posición {pos})", "gris")
        sala = self.sala_actual
        self.historial.registrar_accion(
            f"agarrar {self.catalogo_por_id[oid]['nombre']}",
            deshacer=lambda o=oid, s=sala: (self.inv.quitar(o), self.objetos_en_sala[s].append(o)))
        self._al_obtener(oid)
        self._avanzar_mundo()

    def _al_obtener(self, oid):
        if oid == "pistola_portal":
            self.estado.activar("tiene_pistola_portal")
        elif oid == "mapa_mansion":
            self.estado.activar("tiene_plano")
            ui.escribir("  Ya podés trazar rutas (BFS) y explorar (DFS) desde el mapa [M].", "cian")
        elif oid == "diario_juan":
            self.estado.activar("mision_vista_juan_derrotado")
            self._leer_diario()
        elif oid == "postit":
            ui.escribir("  Leés el papelito: " +
                        self.catalogo_por_id["postit"]["descripcion"], "gris")
        # el alcohol trae sus tragos "de fábrica": (re)carga la cuenta al recogerlo
        cargas = self.catalogo_por_id[oid].get("efecto", {}).get("alcohol")
        if cargas:
            self.estado.establecer(f"alcohol_{oid}", cargas)
            cuenta = "1 trago" if cargas == 1 else f"{cargas} tragos"
            ui.escribir(f"  Trae {cuenta}. Pulsá [V] (o [I] y luego [B]) para pegarte uno.", "gris")
        # auto-equipar si es arma/armadura y mejora lo que llevás
        f = self.catalogo_por_id[oid]
        if f["tipo"] in ("arma", "armadura"):
            slot = "arma" if f["tipo"] == "arma" else "armadura"
            actual = getattr(self.pampa, slot)
            if not actual or self.catalogo_por_id[actual].get("valor", 0) < f.get("valor", 0):
                setattr(self.pampa, slot, oid)
                self.pampa.aplicar_equipo(self.catalogo_por_id)
                ui.escribir(f"  Pampa se pone {f['nombre']} de una vez.  "
                            f"ATQ {self.pampa.ataque} · DEF {self.pampa.defensa}", "cian")

    def _leer_diario(self):
        ui.escribir("\n  DIARIO DE JUAN MAGÁN", "negrita", "magenta")
        for linea in datos.DIARIO_TEXTO:
            ui.escribir("   " + linea, "blanco")
        self.estado.activar("leyo_diario")
        ui.escribir("   Te aprendés el estribillo que amansa al tigre "
                    "(opción 'Cantar' en el jardín).", "cian")
        pistas = ["salida:", ["recibidor", ["pistola_portal", "estudio"]], "jefe:", ["cuarto_juan"]]
        ui.escribir("   pistas (aplanadas recursivamente): " +
                    " · ".join(recursion.aplanar(pistas)), "gris")

    # ==================================================================
    #  MOVIMIENTO: GRAFO + PILA
    # ==================================================================
    def _ir_a(self, destino):
        ok, motivo = self.mapa.arista_transitable(self.sala_actual, destino, self.inv)
        if not ok:
            ui.escribir(f"  Esa puerta está cerrada: {motivo}.", "rojo")
            return
        if destino == datos.SALA_VENTANA:
            if self.pampa.tragos >= 6:
                ui.escribir("  Sacás medio cuerpo por la ventana... y ahí te quedás trabado.\n"
                            "  Con lo que llevás bebido no pasás. Te bajás, maje.", "rojo")
                return
            self._terminar(salida="ventana")
            return
        if destino == datos.SALA_SALIDA:
            ui.escribir("  Alzás la pistola de portal en el zaguán, apuntás a la pared y apretás el gatillo.", "verde")
            self._terminar(salida="puerta", juan=self.estado.obtener("juan_via"))
            return
        self.historial.registrar_movimiento(self.sala_actual)   # PILA
        self.mapa.consumir_llave_si_procede(self.sala_actual, destino, self.inv)
        self._avanzar_mundo()
        self._entrar_sala(destino)

    def _retroceder(self):
        if not self.historial.puede_retroceder():
            ui.escribir("  No hay de dónde venís todavía.", "rojo")
            return
        anterior = self.historial.retroceder()          # PILA (backtracking)
        if self.mapa.grafo.hay_arista(self.sala_actual, anterior):
            ok, motivo = self.mapa.arista_transitable(self.sala_actual, anterior, self.inv)
            if not ok:
                ui.escribir(f"  No podés devolverte por ahí ahora: {motivo}.", "rojo")
                self.historial.pila_movimientos.apilar(anterior)
                return
        ui.escribir(f"  Te devolvés a {self.mapa.nombre(anterior)}.", "cian")
        self._avanzar_mundo()
        self._entrar_sala(anterior, por_retroceso=True)

    # ==================================================================
    #  RECURSIVIDAD: acertijo de Fibonacci (opción múltiple)
    # ==================================================================
    def _acertijo(self):
        sala = datos.SALAS.get(self.sala_actual, {})
        ac = sala.get("acertijo")
        if not ac or self.estado.esta_activa(f"acertijo_{self.sala_actual}"):
            ui.escribir("  Acá no hay ningún acertijo pendiente.", "gris")
            return
        ui.escribir("\n  " + ac["pregunta"], "magenta")
        ui.escribir("  Sucesión: 0, 1, 1, 2, 3, 5, 8, 13, 21, ...  (contá hasta el décimo)", "gris")
        correcto = recursion.fibonacci_memo(9)          # = 34
        opciones = [21, correcto, 55, 89]
        if ui.ENTRADA is None:                           # en modo guion no barajamos
            random.shuffle(opciones)
        letras = ["a", "b", "c", "d"]
        k = ui.elegir("¿Qué número marcás?",
                      [(letras[i], str(v)) for i, v in enumerate(opciones)])
        if k == "ESC":
            return
        ui.escribir(f"  (el motor lo verifica con fibonacci_memo(9) = {correcto})", "gris")
        if opciones[letras.index(k)] == correcto:
            self.estado.activar(f"acertijo_{self.sala_actual}")
            ui.escribir("  " + ac["exito"], "verde")
            for oid in ac["recompensa"]:
                self.objetos_en_sala.setdefault(self.sala_actual, []).append(oid)
            ui.escribir("  Cae botín en la sala.", "amarillo_claro")
        else:
            ui.escribir("  El estante suelta una chispa y no se mueve. Ese número no es, cerote.", "rojo")
        self._avanzar_mundo()

    # ==================================================================
    #  PANTALLA: MOCHILA (LISTA + búsquedas + ordenamiento + PILA)
    # ==================================================================
    def _pantalla_inventario(self):
        while True:
            ids = self.inv.ids()
            if not ids:
                ui.escribir("  La mochila está pelada.", "gris")
                return
            ui.escribir(f"\n  MOCHILA  ({self.inv.cuenta_pesada()}/{self.inv.capacidad}"
                        f"  ·  las llaves y notas no ocupan)", "negrita", "amarillo_claro")
            entradas = []
            for i, oid in enumerate(ids[:18]):
                f = self.catalogo_por_id[oid]
                tag = "  *equipada" if oid in (self.pampa.arma, self.pampa.armadura) else ""
                entradas.append((chr(ord("a") + i), f"{f['nombre']:32} {f['tipo']}{tag}"))
            entradas += [("1", "Ordenar la mochila por valor (quicksort)"),
                         ("2", "Comparar búsqueda lineal vs binaria"),
                         ("3", "Deshacer la última acción (PILA)")]
            ui.escribir("  Elegí la LETRA de un objeto para usarlo, equipártelo o soltarlo.", "gris")
            k = ui.elegir("¿Qué querés ver?", entradas)
            if k == "ESC":
                return
            if k == "1":
                self._inv_ordenar()
            elif k == "2":
                self._inv_comparar_busquedas()
            elif k == "3":
                self._deshacer()
            else:
                idx = ord(k) - ord("a")
                if 0 <= idx < len(ids):
                    self._inv_objeto(ids[idx])

    def _inv_objeto(self, oid):
        f = self.catalogo_por_id[oid]
        # BÚSQUEDA BINARIA sobre el catálogo ordenado por 'id'
        _, comps = buscar_en_catalogo(self.catalogo_ordenado, oid)
        ui.escribir(f"\n  {f['nombre']}  ({f['tipo']})", "negrita", "cian_claro")
        ui.escribir("  " + f["descripcion"])
        ui.escribir(f"  valor {f['valor']}  ·  peso {f['peso']}  ·  efecto {f.get('efecto', {})}", "gris")
        ui.escribir(f"  (BÚSQUEDA BINARIA en el catálogo de {len(self.catalogo_ordenado)}: "
                    f"{comps} comparaciones; la lineal haría hasta {len(self.catalogo_ordenado)})", "gris")
        entradas = []
        if f["tipo"] == "consumible":
            entradas.append(("u", "Usar / consumir"))
        if "alcohol" in f.get("efecto", {}):
            entradas.append(("b", f"Pegarte un trago  (quedan {self._cargas_alcohol(oid)})"))
        if f["tipo"] in ("arma", "armadura"):
            equip = oid in (self.pampa.arma, self.pampa.armadura)
            entradas.append(("e", "Quitártelo" if equip else "Equipártelo"))
        if oid == "diario_juan":
            entradas.append(("r", "Releerlo"))
        entradas.append(("s", "Soltarlo acá"))
        k = ui.elegir("", entradas)
        if k == "u":
            self._usar_item(oid)
        elif k == "b":
            self._beber(forzar_objeto=oid)
        elif k == "e":
            self._equipar_item(oid)
        elif k == "r":
            self._leer_diario()
        elif k == "s":
            self._soltar_item(oid)

    def _usar_item(self, oid):
        ficha = self.catalogo_por_id[oid]
        tipo, efecto = ficha["tipo"], ficha.get("efecto", {})
        if tipo == "clave":
            self._usar_clave(oid, ficha)
            return
        if tipo in ("arma", "armadura"):
            self._equipar_item(oid)
            return
        if "curar" in efecto:
            got = self.pampa.curar(efecto["curar"])
            ui.escribir(f"  Usás {ficha['nombre']}. Recuperás {got} de vida "
                        f"({self.pampa.vida}/{self.pampa.vida_max}).", "verde_claro")
        if efecto.get("cura_estado"):
            self.pampa.quitar_efectos_negativos()
        if efecto.get("revelar"):
            ui.escribir("  Alumbrás los rincones... acá no hay nada escondido.", "gris")
        if not efecto:
            ui.escribir(f"  No pasa nada especial con {ficha['nombre']}.", "gris")
            return
        if tipo == "consumible":
            self.inv.quitar(oid)
        self._avanzar_mundo()

    def _usar_clave(self, oid, ficha):
        if oid == "carnet_falso":
            if self.sala_actual == "celda":
                self.estado.activar("puerta_celda_forzada")
                ui.escribir("  Metés el carné entre los barrotes, hacés palanquita... *clinc*.\n"
                            "  La chapa cede. Gracias, DUI trucho: nunca me fallaste.", "verde")
            else:
                ui.escribir("  Acá no hay ninguna chapa barata que forzar.", "gris")
        elif "abre" in ficha:
            ui.escribir(f"  {ficha['nombre']}: se usa solita al cruzar la puerta que le toca.", "gris")
        else:
            ui.escribir(f"  Ves {ficha['nombre']} y no sabés ni pa' qué te va a servir.", "gris")

    def _equipar_item(self, oid):
        ficha = self.catalogo_por_id[oid]
        if ficha["tipo"] not in ("arma", "armadura"):
            ui.escribir(f"  {ficha['nombre']} no se equipa.", "rojo")
            return
        slot = "arma" if ficha["tipo"] == "arma" else "armadura"
        anterior = getattr(self.pampa, slot)
        nuevo = None if anterior == oid else oid
        setattr(self.pampa, slot, nuevo)
        self.pampa.aplicar_equipo(self.catalogo_por_id)
        verbo = "se quita" if nuevo is None else "se equipa"
        ui.escribir(f"  Pampa {verbo} {ficha['nombre']}.  "
                    f"ATQ {self.pampa.ataque} · DEF {self.pampa.defensa} · VEL {self.pampa.velocidad}", "cian")
        self.historial.registrar_accion(
            f"equipar {ficha['nombre']}",
            deshacer=lambda: (setattr(self.pampa, slot, anterior),
                              self.pampa.aplicar_equipo(self.catalogo_por_id)))

    def _soltar_item(self, oid):
        self.inv.quitar(oid)
        sala = self.sala_actual
        self.objetos_en_sala.setdefault(sala, []).append(oid)
        ui.escribir(f"  Dejás {self.catalogo_por_id[oid]['nombre']} tirado en el suelo.", "cian")
        self.historial.registrar_accion(
            f"soltar {self.catalogo_por_id[oid]['nombre']}",
            deshacer=lambda: (self.objetos_en_sala[sala].remove(oid), self.inv.agregar(oid)))

    def _deshacer(self):
        if not self.historial.puede_deshacer():
            ui.escribir("  No hay ninguna acción reversible en la PILA.", "rojo")
            return
        accion = self.historial.deshacer()
        ui.escribir(f"  Deshecho: {accion.descripcion}.", "cian")

    def _inv_ordenar(self):
        ordenados, m = self.inv.ordenar_por("valor", descendente=True)
        ui.escribir(f"\n  MOCHILA por valor (quicksort: {m['comparaciones']} comparaciones, "
                    f"{m['intercambios']} intercambios):", "cian_claro")
        for oid in ordenados:
            f = self.catalogo_por_id[oid]
            ui.escribir(f"    {f['valor']:>3}  {f['nombre']}")
        ui.pausa()

    def _inv_comparar_busquedas(self):
        objetivo = random.choice(self.inv.ids())
        lista = self.catalogo_ordenado
        t0 = time.perf_counter()
        i_lin, c_lin = busqueda.busqueda_lineal(lista, objetivo, clave=lambda o: o["id"])
        t_lin = (time.perf_counter() - t0) * 1e6
        t0 = time.perf_counter()
        i_bin, c_bin = busqueda.busqueda_binaria(lista, objetivo, clave=lambda o: o["id"])
        t_bin = (time.perf_counter() - t0) * 1e6
        _, c_rec = busqueda.busqueda_binaria_recursiva(lista, objetivo, clave=lambda o: o["id"])
        ui.escribir(f"\n  Buscando '{self.catalogo_por_id[objetivo]['nombre']}' en el catálogo "
                    f"({len(lista)} objetos, ordenado por id):", "cian_claro")
        ui.tabla(["algoritmo", "comparaciones", "tiempo (µs)", "O()"],
                 [["lineal", c_lin, f"{t_lin:.1f}", "O(n)"],
                  ["binaria", c_bin, f"{t_bin:.1f}", "O(log n)"],
                  ["binaria recursiva", c_rec, "-", "O(log n)"]])
        ui.escribir("  El inventario (n<=14, cambia cada turno) usa LINEAL a propósito.", "gris")
        ui.pausa()

    # ==================================================================
    #  PANTALLA: MAPA (GRAFO + BFS + DFS + PILA)
    # ==================================================================
    def _pantalla_mapa(self):
        piso = datos.piso_de(self.sala_actual)
        while True:
            self.mapa.plano_planta(piso, self.sala_actual, self.inv)
            tiene = self.inv.contiene("mapa_mansion")
            entradas = [("1", "Ver el SÓTANO"), ("2", "Ver la PLANTA NOBLE"),
                        ("3", "Ver la PLANTA ALTA"),
                        ("a", "Ver la lista y la matriz de adyacencia (grafo)")]
            if tiene:
                entradas += [("c", "Trazar la ruta más corta a una sala (BFS)"),
                             ("x", "Recorrer toda la mansión (DFS y BFS)")]
            else:
                entradas.append(("y", "Conseguí el plano en la biblioteca para BFS/DFS", "gris"))
            entradas.append(("h", "Ver la PILA de movimientos y de acciones"))
            k = ui.elegir("Plano — [1/2/3] cambiar de piso", entradas)
            if k in ("ESC", "y"):
                return
            if k in "123":
                piso = int(k) - 1
            elif k == "a":
                self.mapa.mostrar(self.sala_actual, self.inv)
                ui.pausa()
            elif k == "c" and tiene:
                self._trazar_camino()
            elif k == "x" and tiene:
                self._explorar()
            elif k == "h":
                self._ver_historial()

    def _trazar_camino(self):
        salas = [s for s in datos.SALAS if s != self.sala_actual]
        entradas = [(chr(ord("a") + i), self.mapa.nombre(s)) for i, s in enumerate(salas[:20])]
        k = ui.elegir("¿A qué sala trazo la ruta?", entradas)
        if k == "ESC":
            return
        destino = salas[ord(k) - ord("a")]
        camino = self.mapa.camino_mas_corto(self.sala_actual, destino, self.inv)
        if not camino:
            ui.escribir("  No hay ruta transitable ahora mismo (puertas cerradas).", "amarillo")
        else:
            ui.escribir(f"\n  BFS — ruta más corta ({len(camino)-1} puertas):", "negrita", "cian_claro")
            ui.escribir("   " + "  →  ".join(self.mapa.nombre(s) for s in camino), "verde")
            ui.escribir("  BFS explora por niveles con una COLA: el primero que llega es el mínimo.", "gris")
        ui.pausa()

    def _explorar(self):
        g = self.mapa.grafo
        orden_dfs = self.mapa.explorar_dfs(self.sala_actual)
        orden_bfs = self.mapa.bfs_niveles(self.sala_actual)
        ui.escribir(f"\n  DFS (profundidad, recursivo) desde {self.mapa.nombre(self.sala_actual)}:",
                    "negrita", "cian_claro")
        ui.escribir("   " + " → ".join(self.mapa.nombre(s) for s in orden_dfs if s not in datos.SALIDAS), "verde")
        ui.escribir("  DFS (iterativo con PILA): " +
                    " → ".join(self.mapa.nombre(s) for s in g.dfs_iterativo(self.sala_actual)
                               if s not in datos.SALIDAS), "gris")
        ui.escribir(f"\n  BFS (anchura, con COLA) desde {self.mapa.nombre(self.sala_actual)}:",
                    "negrita", "cian_claro")
        ui.escribir("   " + " → ".join(self.mapa.nombre(s) for s in orden_bfs if s not in datos.SALIDAS), "cian")
        ui.pausa()

    def _ver_historial(self):
        ui.escribir("\n  PILA DE MOVIMIENTOS (cima = más reciente)", "negrita", "cian_claro")
        ruta = self.historial.pila_movimientos.a_lista(desde_cima=True)
        ui.escribir("   " + (" ← ".join(self.mapa.nombre(s) for s in ruta) if ruta else "(vacía)"))
        ui.escribir("\n  PILA DE ACCIONES REVERSIBLES (cima = próxima en 'Deshacer')", "negrita", "cian_claro")
        acciones = self.historial.ultimas_acciones()
        for a in (acciones or [None]):
            ui.escribir("   - " + (a.descripcion if a else "(vacía)"))
        ui.pausa()

    # ==================================================================
    #  PANTALLA: OBJETIVOS (ÁRBOL de misiones + DICCIONARIO de estado)
    # ==================================================================
    def _pantalla_objetivos(self):
        if self.estado.esta_activa("tigre_derrotado"):
            self.estado.activar("mision_vista_juan_derrotado")
        ui.escribir("\n  ÁRBOL DE MISIONES  (se evalúa recursivamente, post-orden)", "negrita", "cian_claro")
        for linea in self.misiones.render(self.estado):
            color = "verde" if "[x]" in linea else "gris" if "[?]" in linea else "blanco"
            ui.escribir("  " + linea, color)
        hechas, total = self.misiones.progreso(self.estado)
        ui.escribir(f"\n  Progreso: {hechas}/{total} objetivos de hoja completados.", "amarillo_claro")

        ui.escribir("\n  ZONAS (qué necesitás para entrar):", "cian_claro")
        for zona, reqs in DEPENDENCIAS_ZONA.items():
            marca = "✓" if self.estado.esta_activa(f"visito_{zona}") else " "
            ui.escribir(f"   [{marca}] {self.mapa.nombre(zona):28} <- {', '.join(reqs)}")

        ui.escribir("\n  DICCIONARIO DE ESTADOS DEL MUNDO (tabla hash, acceso O(1)):", "cian_claro")
        for clave, valor in self.estado.resumen():
            if clave.startswith(("visito_", "narrado_", "bitacora")):
                continue
            ui.escribir(f"   {clave:30} = {valor}")
        ui.escribir(f"   {self.estado}", "gris")
        ui.pausa()

    # ==================================================================
    #  PANTALLA: PAMPA (stats + ranking con ORDENAMIENTOS)
    # ==================================================================
    def _pantalla_pampa(self):
        p = self.pampa
        ui.escribir("\n  PAMPA", "negrita", "cian_claro")
        ui.escribir("   Vida     " + ui.barra_vida(p.vida, p.vida_max))
        ui.escribir(f"   Nivel    {p.nivel}   (XP {p.xp}/{p.nivel*30})")
        ui.escribir(f"   Ataque   {p.ataque}    Defensa {p.defensa}    Velocidad {p.velocidad}")
        ui.escribir(f"   Arma     {self.catalogo_por_id.get(p.arma, {}).get('nombre', '—')}")
        ui.escribir(f"   Armadura {self.catalogo_por_id.get(p.armadura, {}).get('nombre', '—')}")
        ui.escribir(f"   Tragos   {p.tragos}  (mod. ATQ {p.alcohol_atk:+d}, DEF {p.alcohol_def:+d})")
        ui.escribir(f"   {alcohol.resaca(p)}", "gris")

        if p.enemigos_vencidos:
            ui.escribir("\n  RANKING DE ENEMIGOS DERROTADOS (por XP)", "cian_claro")
            ordenados, m = ordenamiento.ordenamiento_mezcla(
                list(p.enemigos_vencidos), clave=lambda r: r["xp"], reverse=True)
            for i, r in enumerate(ordenados, 1):
                ui.escribir(f"   {i}. {r['nombre']:26} {r['xp']} XP")
            ui.escribir(f"   (mergesort: {m['comparaciones']} comparaciones, {m['intercambios']} mezclas)", "gris")
            filas = ordenamiento.comparar(list(p.enemigos_vencidos), clave=lambda r: r["xp"], reverse=True)
            ui.tabla(["algoritmo", "comparaciones", "intercambios", "correcto"], [list(f) for f in filas])
        ui.pausa()

    # ==================================================================
    #  ALCOHOL (probabilidad con piso 40%; ver alcohol.py) + trago LIMITADO:
    #  cada barra de sala (datos.BARRA_SALAS) y cada botella de la mochila
    #  (efecto {"alcohol": N}) tiene cargas contadas en el diccionario de estado.
    # ==================================================================
    def _cargas_alcohol(self, oid):
        """Tragos que le quedan a un objeto de alcohol que Pampa carga."""
        maximo = self.catalogo_por_id.get(oid, {}).get("efecto", {}).get("alcohol", 0)
        return self.estado.obtener(f"alcohol_{oid}", maximo)

    def _barra_restante(self, sala):
        return self.estado.obtener(f"barra_{sala}", datos.BARRA_SALAS.get(sala, 0))

    def _fuente_trago(self, forzar_objeto=None):
        """De dónde sale el próximo trago: ('sala', id) | ('objeto', id) | None.
        La barra fija de la sala se gasta antes que las botellas de la mochila."""
        if forzar_objeto is not None:
            return ("objeto", forzar_objeto) if self._cargas_alcohol(forzar_objeto) > 0 else None
        if self._barra_restante(self.sala_actual) > 0:
            return ("sala", self.sala_actual)
        for oid in self.inv.ids():
            if "alcohol" in self.catalogo_por_id.get(oid, {}).get("efecto", {}) and self._cargas_alcohol(oid) > 0:
                return ("objeto", oid)
        return None

    def _describir_fuente(self, fuente):
        tipo, ref = fuente
        if tipo == "sala":
            return f"barra de la sala, quedan {self._barra_restante(ref)}"
        return f"{self.catalogo_por_id[ref]['nombre']}, quedan {self._cargas_alcohol(ref)}"

    def _beber(self, forzar_objeto=None):
        if self.enemigo_en_sala.get(self.sala_actual) and self.sala_actual != "cuarto_juan":
            ui.escribir("  Con ese ahí viéndote feo no es hora de ponerte a chupitear.", "rojo")
            return
        fuente = self._fuente_trago(forzar_objeto)
        if not fuente:
            ui.escribir("  Ya no queda nada bebible por aquí, maje. Buscá una botella.", "gris")
            return

        tipo, ref = fuente
        if tipo == "sala":
            restante = self._barra_restante(ref) - 1
            self.estado.establecer(f"barra_{ref}", restante)
            origen = "de la barra"
        else:
            restante = self._cargas_alcohol(ref) - 1
            self.estado.establecer(f"alcohol_{ref}", restante)
            origen = f"de {self.catalogo_por_id[ref]['nombre']}"

        r = alcohol.beber(self.pampa)
        self.pampa.aplicar_equipo(self.catalogo_por_id)
        ui.escribir(f"  Trago nº {r['trago']} ({origen})  ·  P(que salga bueno) = {r['p_positivo']*100:.0f}%", "gris")
        color = "verde_claro" if r["positivo"] else "rojo"
        verbo = "SE TE SUBE" if r["positivo"] else "SE TE BAJA"
        ui.escribir(f"  Salud. Tu {r['estadistica'].upper()} {verbo} {abs(r['delta'])}   ->   "
                    f"ATQ {self.pampa.ataque} · DEF {self.pampa.defensa}", color)

        nombre = self.catalogo_por_id[ref]["nombre"] if tipo == "objeto" else None
        if tipo == "objeto" and restante <= 0:
            self.inv.quitar(ref)
            ui.escribir(f"  Se acabó {nombre}. A la basura.", "gris")
        elif tipo == "objeto":
            cola = "le queda 1 trago" if restante == 1 else f"le quedan {restante} tragos"
            ui.escribir(f"  A {nombre} {cola}.", "gris")
        elif restante <= 0:
            ui.escribir("  Con ese dejaste la barra de esta sala pelada.", "gris")

        self._avanzar_mundo()
        if r["desmayo"]:
            ui.escribir("  El techo se pone a dar vueltas, las patas no responden...", "magenta")
            self._terminar(desmayo=True)

    def _cmd_alarma(self):
        if self.sala_actual not in ("cuarto_juan", "pasillo_alto"):
            ui.escribir("  No hallás ninguna alarma de incendios por aquí, maje.", "gris")
            return
        ui.escribir("  Jalás la palanca roja. Se prenden todas las luces de un solo,\n"
                    "  la música se corta en seco y a Juan casi le da un soponcio.", "amarillo_claro")
        self._terminar(salida="alarma")

    def _cmd_retar(self):
        if self.sala_actual != "cuarto_juan" or not self.enemigo_en_sala.get("cuarto_juan"):
            ui.escribir("  Acá no hay a quién retar a nada, cerote.", "gris")
            return
        ui.escribir("\n  DUELO DE CHUPITOS CONTRA JUAN MAGÁN", "negrita", "amarillo_claro")
        ui.escribir("  —El último en pie gana. Salú. —Y Juan sirve dos vasos hasta el tope.", "blanco")
        juan_tragos = 0
        while True:
            juan_tragos += 1
            r = alcohol.beber(self.pampa)
            self.pampa.aplicar_equipo(self.catalogo_por_id)
            ui.escribir(f"  Ronda {juan_tragos}: te empujás el trago nº {r['trago']} "
                        f"(lo aguantás al {(1 - r['p_desmayo']) * 100:.0f}%)", "gris")
            if r["desmayo"]:
                ui.escribir("  Te vas de jeta al piso. Juan levanta su vaso, ni despeinado.", "rojo")
                self._terminar(desmayo=True)
                return
            p_juan = max(0.0, 0.17 * (juan_tragos - 3))   # Juan aguanta peor que vos
            ui.escribir(f"  Juan se empuja el suyo (prob. de que se caiga: {p_juan * 100:.0f}%)", "gris")
            if random.random() < p_juan or juan_tragos >= 12:
                ui.escribir("  Juan ve el vaso, dice 'este me lo guardo' y se va resbalando al suelo.", "verde")
                self.estado.activar("juan_derrotado")
                self.estado.establecer("juan_via", "duelo")
                self.enemigo_en_sala["cuarto_juan"] = None
                self._terminar(juan="duelo")
                return

    def _cmd_bailar(self):
        if self.sala_actual != "cuarto_juan" or not self.enemigo_en_sala.get("cuarto_juan"):
            ui.escribir("  Acá no hay pista ni con quién menearse.", "gris")
            return
        if not (self.pampa.tragos >= 3 or self.estado.esta_activa("calienta_brazo")):
            ui.escribir("  Lo intentás sobrio y sin calentar: te enredás en el primer paso.\n"
                        "  Te falta soltura (3 tragos, o calentá brazo en el comedor).", "rojo")
            return
        base = min(0.85, 0.40 + 0.08 * min(self.pampa.tragos, 4) +
                   (0.12 if self.estado.esta_activa("calienta_brazo") else 0.0))
        ui.escribir("\n  BATALLA DE PERREO  (3 rondas, tenés que ganar 2)", "negrita", "magenta")
        aciertos = 0
        for ronda in range(1, 4):
            ui.escribir(f"  Ronda {ronda}/3 — pulsá un paso (1/2/3):", "amarillo_claro")
            ui.CONTEXTO_MENU = "baile"
            ui.leer_tecla()
            if random.random() < base:
                aciertos += 1
                ui.escribir("  ¡CABAL AL RITMO! La gente se vuelve loca.", "verde")
            else:
                ui.escribir("  Se te fue el compás, maje.", "rojo")
        if aciertos >= 2:
            ui.escribir(f"  {aciertos}/3. Juan Magán se rinde entre aplausos y silbidos.", "verde_claro")
            self.estado.activar("juan_derrotado")
            self.estado.activar("juan_amigo")
            self.estado.establecer("juan_via", "baile")
            self.enemigo_en_sala["cuarto_juan"] = None
            self._terminar(juan="baile")
        else:
            ui.escribir(f"  {aciertos}/3. No pegó; Juan te deja probar otra vuelta.", "rojo")

    def _cmd_cantar(self):
        if self.sala_actual != "jardin" or not self.enemigo_en_sala.get("jardin"):
            ui.escribir("  Acá no hay a quién cantarle, cerote.", "gris")
            return
        if not self.estado.esta_activa("leyo_diario"):
            ui.escribir("  Cantás pero te inventás la letra. El tigre capta que le estás\n"
                        "  vacilando al dueño y se pone más arrecho. Mejor peleá o corré.", "rojo")
            return
        ui.escribir("  Cantás el estribillo tal cual venía en el diario. El tigre para las\n"
                    "  orejas, mueve la cola y se echa panza arriba pa' que le sobés la guata.", "verde")
        self.estado.activar("tigre_derrotado")
        self.estado.activar("tigre_amigo")
        self.enemigo_en_sala["jardin"] = None
        self._describir_sala()

    def _cmd_beerpong(self):
        if self.sala_actual != "comedor" or self.estado.esta_activa("calienta_brazo"):
            ui.escribir("  Ya calentaste bastante. Guardá la muñeca pa' lo que viene.", "gris")
            return
        ui.escribir("  Tirás unas cuantas a los vasos y metés tres seguidas, de a peluche.\n"
                    "  Sentís la muñeca suelta: te va a servir en una batalla de perreo.", "cian")
        self.estado.activar("calienta_brazo")
        self._avanzar_mundo()

    def _cmd_quedarse(self):
        if self.sala_actual != "cuarto_juan" or not self.estado.esta_activa("juan_derrotado"):
            ui.escribir("  Acá no hay ningún cantón que reclamar (todavía).", "gris")
            return
        self._terminar(se_queda=True, juan=self.estado.obtener("juan_via", "pelea"))

    def _cmd_sobornar(self):
        if not self.inv.contiene("botella_tequila"):
            ui.escribir("  No cargás nada con qué convidarle. Hay botellas en la bodega.", "gris")
            return
        ui.escribir("  Le pasás la botella. Se la empuja. Y otra. A la cuarta ya anda llorando\n"
                    "  y contándote que su papá nunca lo llevó al circo. Pasás de puntillas.", "verde")
        self.inv.quitar("botella_tequila")
        self.estado.activar("guardaespaldas_derrotado")
        self.estado.activar("guardaespaldas_evitado")
        self.enemigo_en_sala["salon"] = None

    def _cmd_colarse(self):
        if self.pampa.tragos < 2:
            ui.escribir("  —Soy... el DJ de refuerzo... —Lo decís tan bajito que ni vos te la creés.", "rojo")
            return
        ui.escribir("  —¡SOY EL DJ DE REFUERZO, ME HABLÓ EL JUAN! —Lo soltás con tal seguridad\n"
                    "  que el ropero se hace a un lado. —Haberlo dicho antes, maje. Pasá.", "verde")
        self.estado.activar("guardaespaldas_derrotado")
        self.estado.activar("guardaespaldas_evitado")
        self.enemigo_en_sala["salon"] = None

    # ==================================================================
    #  GUARDAR / CARGAR (serialización del DICCIONARIO)
    # ==================================================================
    def _ruta_guardado(self, nombre="partida"):
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), nombre + ".json")

    def _guardar(self):
        d = {
            "sala_actual": self.sala_actual, "turno_mundo": self.turno_mundo,
            "pampa": {"vida": self.pampa.vida, "vida_max": self.pampa.vida_max,
                      "nivel": self.pampa.nivel, "xp": self.pampa.xp,
                      "arma": self.pampa.arma, "armadura": self.pampa.armadura,
                      "tragos": self.pampa.tragos, "alcohol_atk": self.pampa.alcohol_atk,
                      "alcohol_def": self.pampa.alcohol_def,
                      "enemigos_vencidos": self.pampa.enemigos_vencidos},
            "inventario": self.inv.como_lista(),
            "estado": self.estado.como_dict(),
            "objetos_en_sala": self.objetos_en_sala,
            "enemigo_en_sala": self.enemigo_en_sala,
            "descubiertas": sorted(self.mapa.descubiertas),
            "pila_movimientos": self.historial.pila_movimientos.a_lista(desde_cima=False),
        }
        with open(self._ruta_guardado(), "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        ui.escribir("  Partida guardada (el diccionario de estado -> JSON).", "verde")
        ui.pausa()

    def _cargar(self):
        ruta = self._ruta_guardado()
        if not os.path.exists(ruta):
            return
        with open(ruta, "r", encoding="utf-8") as f:
            d = json.load(f)
        self.sala_actual = d["sala_actual"]
        self.turno_mundo = d.get("turno_mundo", 0)
        pj = d["pampa"]
        self.pampa.vida, self.pampa.vida_max = pj["vida"], pj["vida_max"]
        self.pampa.nivel, self.pampa.xp = pj["nivel"], pj["xp"]
        self.pampa.arma, self.pampa.armadura = pj["arma"], pj["armadura"]
        self.pampa.tragos = pj.get("tragos", 0)
        self.pampa.alcohol_atk = pj.get("alcohol_atk", 0)
        self.pampa.alcohol_def = pj.get("alcohol_def", 0)
        self.pampa.enemigos_vencidos = pj["enemigos_vencidos"]
        self.pampa.aplicar_equipo(self.catalogo_por_id)
        self.inv.cargar_lista(d["inventario"])
        self.estado.cargar_dict(d["estado"])
        self.objetos_en_sala = d["objetos_en_sala"]
        self.enemigo_en_sala = d["enemigo_en_sala"]
        self.mapa.descubiertas = set(d.get("descubiertas", []))
        for s in d.get("pila_movimientos", []):
            self.historial.pila_movimientos.apilar(s)
        self._recien_cargado = True
        ui.escribir("  Partida cargada. Seguimos donde ibas.", "verde")

    def _pedir_salir(self):
        k = ui.elegir("¿Seguro que dejás la partida?",
                      [("s", "Sí, me voy"), ("n", "No, sigo jugando")], permitir_esc=True)
        if k == "s":
            ui.escribir("  Tirás la toalla. Ni modo.", "gris")
            self.terminado = True

    # ==================================================================
    #  COMBATE
    # ==================================================================
    def _combate(self, enemigo_id):
        enemigo = Enemigo.desde_id(enemigo_id)
        ui.escribir("\n  ⚔  ¡PLEITO!  ⚔", "negrita", "rojo_claro")
        combate = Combate(self.pampa, [enemigo], self.inv, self.catalogo_por_id, self.estado)
        resultado = combate.ejecutar()
        self._avanzar_mundo(combate.turno_global)
        if resultado == "victoria":
            self.enemigo_en_sala[self.sala_actual] = None
            self._tras_victoria(enemigo_id, enemigo)
        elif resultado == "huida":
            ui.escribir("  Salís pitado por donde viniste, sin ver pa' atrás.", "amarillo")
            if self.historial.puede_retroceder():
                self._entrar_sala(self.historial.retroceder(), por_retroceso=True)
        else:  # derrota -> final malo
            self._terminar(ko=True)

    def _tras_victoria(self, enemigo_id, enemigo):
        ui.escribir("  ¡Ganaste el pleito, maje!", "verde_claro")
        ui.escribir("  Te lo chineaste a pija al rival: quedó sin saber ni por dónde le llegó.", "verde")
        recup = self.pampa.curar(int(self.pampa.vida_max * 0.40))
        if recup:
            ui.escribir(f"  Agarrás aire y te sobás (+{recup} de vida).", "verde")
        self.pampa.efectos.clear()
        if enemigo_id == "guardaespaldas":
            self.estado.activar("guardaespaldas_derrotado")
            ui.escribir("  El camino a la planta de arriba queda libre.", "cian")
        elif enemigo_id == "tigre":
            self.estado.activar("tigre_derrotado")
        elif enemigo_id == "juan_magan":
            self.estado.activar("juan_derrotado")
            self.estado.establecer("juan_via", "pelea")
            ui.escribir("  " + datos.ENEMIGOS["juan_magan"]["frases"]["morir"], "verde_claro")
            ui.escribir("  Ahora podés 'Quedarte' con el cantón [K], o largarte abriendo un\n"
                        "  portal con la pistola en el recibidor. Vos decidís, cerote.", "cian")
        for oid in getattr(enemigo, "botin", []):
            ok, _ = self.inv.agregar(oid)
            if not ok:
                self.objetos_en_sala.setdefault(self.sala_actual, []).append(oid)
            ui.escribir(f"  Botín: {self.catalogo_por_id[oid]['nombre']} -> "
                        f"{'tu mochila' if ok else 'el suelo'}.", "amarillo_claro")

    # ==================================================================
    #  MUNDO / FINAL
    # ==================================================================
    def _avanzar_mundo(self, pasos=1):
        antes = self.turno_mundo
        self.turno_mundo += max(1, pasos)
        if antes // 12 != self.turno_mundo // 12 and not self.estado.esta_activa("juan_derrotado"):
            ui.escribir("  » Allá arriba el bajo sube un puntito más. El Juan sigue en lo suyo.", "magenta")

    def _terminar(self, **contexto):
        """Clasifica el final con el ÁRBOL DE DECISIÓN de finales.py y acaba."""
        self.contexto_final = contexto
        traza = []
        self.final_id = finales.clasificar(contexto, traza)
        self._traza_final = traza
        self.terminado = True

    def _final(self):
        ui.ENTRADA = None
        if self.final_id is None:
            ui.escribir("\n  Dejás el cantón del Juan a medio camino. Ni salís ni te quedás. Puro limbo.", "gris")
            return
        f = finales.FINALES[self.final_id]
        nuevo = self.final_id not in set(self.progreso.get("finales", []))
        self._guardar_progreso()
        try:
            os.remove(self._ruta_guardado())     # la partida terminó
        except OSError:
            pass

        segundos = time.perf_counter() - self.inicio_tiempo
        ui.regla("═")
        color = {"bueno": "verde_claro", "malo": "rojo"}.get(f["tipo"], "blanco")
        ui.escribir("  " + f["titulo"], "negrita", color)
        ui.regla("─")
        for linea in f["texto"]:
            ui.escribir("  " + linea, "blanco")
        ui.regla("═")
        if getattr(self, "_traza_final", None):
            ui.escribir("  (árbol de decisión de finales: " + " → ".join(self._traza_final) + ")", "gris")
        if nuevo:
            ui.escribir("  ¡DESTRABASTE UN FINAL NUEVO, MAJE!", "amarillo_claro")

        ui.escribir("\n  RESUMEN DE LA PARTIDA", "negrita", "cian_claro")
        ui.escribir(f"   Tiempo jugado        {segundos:.0f} s")
        ui.escribir(f"   Turnos de mundo      {self.turno_mundo}")
        ui.escribir(f"   Nivel de Pampa       {self.pampa.nivel}")
        ui.escribir(f"   Tragos               {self.pampa.tragos}  ({alcohol.resaca(self.pampa)})")
        ui.escribir(f"   Enemigos derrotados  {len(self.pampa.enemigos_vencidos)}")
        ui.escribir(f"   Salas visitadas      {len(set(self.estado.obtener('bitacora', [])))}/{len(datos.SALAS)}")
        ui.escribir(f"   Accesos al dict      {self.estado.lecturas} lecturas / {self.estado.escrituras} escrituras")

        vistos = self.progreso.get("finales", [])
        ui.escribir(f"\n   FINALES DESCUBIERTOS: {len(vistos)}/{finales.contar_finales()}", "amarillo_claro")
        for k, ff in finales.FINALES.items():
            ui.escribir(f"     [{'✓' if k in vistos else ' '}] {ff['titulo'] if k in vistos else '???'}")
        if len(vistos) < finales.contar_finales():
            ui.escribir("\n   Volvé a jugar y probá otro camino, otra salida u otra maña.", "gris")
        else:
            ui.escribir("\n   ¡Los sacaste TODOS, cerote! De a peluche.", "verde_claro")

    # ==================================================================
    #  TOUR TÉCNICO (modo --demo)
    # ==================================================================
    def tour_tecnico(self):
        ui.habilitar_ansi_windows()
        ui.titulo("TOUR TÉCNICO — ESTRUCTURAS DE DATOS Y ALGORITMOS DEL JUEGO")
        ui.escribir("Demostración automática de cada tema del curso sobre los datos reales del juego.\n", "gris")

        ui.escribir("\n" + "═" * 70)
        ui.escribir("1) GRAFO DEL MAPA — lista y matriz de adyacencia", "negrita", "cian_claro")
        self.mapa.revelar_todo()
        self.inv._objetos.append("mapa_mansion")
        self.mapa.mostrar(self.sala_actual, self.inv)
        self.inv._objetos.remove("mapa_mansion")

        ui.escribir("\n" + "═" * 70)
        ui.escribir("2) BFS y DFS desde la celda", "negrita", "cian_claro")
        g = self.mapa.grafo
        ui.escribir("   BFS (cola):        " + " → ".join(g.bfs("celda")))
        ui.escribir("   DFS (pila):        " + " → ".join(g.dfs_iterativo("celda")))
        ui.escribir("   DFS (recursivo):   " + " → ".join(g.dfs_recursivo("celda")))
        ui.escribir("   BFS camino corto celda→cuarto_juan: " +
                    " → ".join(g.camino_mas_corto("celda", "cuarto_juan")))
        ui.escribir(f"   nº de caminos simples celda→salon: {len(g.todos_los_caminos('celda', 'salon'))}")

        ui.escribir("\n" + "═" * 70)
        ui.escribir("3) PILA — historial de movimientos y backtracking", "negrita", "cian_claro")
        for s in ["celda", "pasillo_sotano", "escalera", "salon"]:
            self.historial.registrar_movimiento(s)
        ui.escribir("   pila (cima→fondo): " + str(self.historial.pila_movimientos.a_lista()))
        ui.escribir("   retroceder() -> " + self.historial.retroceder())
        ui.escribir("   retroceder() -> " + self.historial.retroceder())
        ui.escribir("   pila ahora:        " + str(self.historial.pila_movimientos.a_lista()))
        self.historial.limpiar()

        ui.escribir("\n" + "═" * 70)
        ui.escribir("4) COLA de turnos + COLA de eventos — combate automático de ejemplo", "negrita", "cian_claro")
        self._demo_combate()

        ui.escribir("\n" + "═" * 70)
        ui.escribir("5) LISTA (inventario) + BÚSQUEDA lineal vs binaria", "negrita", "cian_claro")
        for oid in ["energetica", "palo_selfie", "pistola_portal", "bandeja", "bocina_aire"]:
            self.inv.agregar(oid)
        oid, comps = self.inv.buscar_por_nombre("bandeja")
        ui.escribir(f"   inventario: {self.inv.ids()}")
        ui.escribir(f"   búsqueda LINEAL 'bandeja' -> {oid} en {comps} comparaciones")
        ficha, cb = buscar_en_catalogo(self.catalogo_ordenado, "bandeja")
        ui.escribir(f"   búsqueda BINARIA 'bandeja' en catálogo ({len(self.catalogo_ordenado)}) -> "
                    f"{ficha['nombre']} en {cb} comparaciones")

        ui.escribir("\n" + "═" * 70)
        ui.escribir("6) ORDENAMIENTO — inventario por valor + comparación de algoritmos", "negrita", "cian_claro")
        ordenado, m = self.inv.ordenar_por("valor")
        ui.escribir("   por valor (quicksort): " +
                    ", ".join(f"{self.catalogo_por_id[o]['nombre']}({self.catalogo_por_id[o]['valor']})"
                              for o in ordenado))
        filas = ordenamiento.comparar([self.catalogo_por_id[o]["valor"] for o in self.inv.ids()])
        ui.tabla(["algoritmo", "comparaciones", "intercambios", "correcto"], [list(f) for f in filas])

        ui.escribir("\n" + "═" * 70)
        ui.escribir("7) RECURSIÓN y DIVIDE Y VENCERÁS", "negrita", "cian_claro")
        ui.escribir(f"   fibonacci(15)          = {recursion.fibonacci(15)}   (O(2^n))")
        ui.escribir(f"   fibonacci_memo(50)     = {recursion.fibonacci_memo(50)}   (O(n))")
        ui.escribir(f"   factorial(6)           = {recursion.factorial(6)}")
        ui.escribir(f"   potencia(2, 10) rápida = {recursion.potencia(2, 10)}   (O(log n))")
        ui.escribir(f"   Torres de Hanói n=3    = {recursion.hanoi(3)}")
        objetos_por_sala = {s: list(d.get('objetos', [])) for s, d in datos.SALAS.items()}
        ui.escribir(f"   objetos alcanzables desde 'celda' (DFS recursivo) = "
                    f"{recursion.contar_objetos_alcanzables(self.mapa.grafo, 'celda', objetos_por_sala)}")

        ui.escribir("\n" + "═" * 70)
        ui.escribir("8) ÁRBOL de misiones (con algunas ya completadas)", "negrita", "cian_claro")
        self.estado.activar("tigre_derrotado")
        self.estado.activar("visito_cuarto_juan")
        self.estado.activar("mision_vista_juan_derrotado")
        for linea in self.misiones.render(self.estado):
            ui.escribir("   " + linea)

        ui.escribir("\n" + "═" * 70)
        ui.escribir("9) ÁRBOL DE DECISIÓN de la IA enemiga", "negrita", "cian_claro")
        from . import ia
        jefe = Enemigo.desde_id("juan_magan")
        jefe.vida = 10
        traza = []
        accion = ia.decidir_accion(jefe, self.pampa, turno=2, hay_invocados=False, traza=traza)
        ui.escribir("   Juan Magán al 14% de vida, turno 2:")
        ui.escribir("   camino en el árbol: " + " | ".join(traza))
        ui.escribir("   -> acción elegida: " + accion)

        ui.escribir("\n" + "═" * 70)
        ui.escribir(f"9b) ÁRBOL DE DECISIÓN DE LOS {finales.contar_finales()} FINALES (finales.py)",
                    "negrita", "cian_claro")
        for linea in finales.render_arbol():
            ui.escribir("   " + linea, "gris")
        ui.escribir("\n   cómo juegas -> qué final te toca:", "cian_claro")
        for desc, ctx in finales.CONTEXTOS_EJEMPLO:
            ui.escribir(f"     {desc:44} -> {finales.FINALES[finales.clasificar(ctx)]['titulo']}")
        from .alcohol import tabla_probabilidades
        ui.escribir("\n   la mecánica del alcohol (alcohol.py): probabilidad y valor esperado", "cian_claro")
        ui.tabla(["trago k", "magnitud", "P(positivo)", "E[efecto]", "P(desmayo)"],
                 [list(f) for f in tabla_probabilidades(9)])

        ui.escribir("\n" + "═" * 70)
        ui.escribir("10) DICCIONARIO de estados del mundo (tabla hash)", "negrita", "cian_claro")
        for k, v in self.estado.resumen():
            if k != "bitacora":
                ui.escribir(f"    {k:32} = {v}")
        ui.escribir(f"    {self.estado}")

        ui.escribir("\n" + "═" * 70)
        complejidad.imprimir_todo()
        ui.escribir("\n" + "═" * 70)
        ui.escribir("Fin del tour. 'python main.py' para jugar; '--benchmark' para el informe empírico.\n", "verde")

    def _demo_combate(self):
        guion = iter(["2", "1"] + ["1"] * 20)
        ui.ENTRADA = lambda _p: next(guion)
        self.inv.agregar("bocina_aire")
        self.estado.establecer("bocina_usos", 3)
        try:
            combate = Combate(self.pampa, [Enemigo.desde_id("guardaespaldas")],
                              self.inv, self.catalogo_por_id, self.estado)
            ui.escribir(f"   resultado del combate de ejemplo: {combate.ejecutar()}", "amarillo_claro")
        except ui.SalirDelJuego:
            ui.escribir("   (combate de ejemplo interrumpido)", "gris")
        finally:
            ui.ENTRADA = None
            self.inv._objetos.clear()
            self.pampa.vida = self.pampa.vida_max
            self.pampa.efectos.clear()
