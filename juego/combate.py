"""
combate.py — COMBATE POR TURNOS.

Integra varias estructuras del curso:
    - COLA de turnos (turnos.SistemaTurnos) ordenada por INICIATIVA,
    - COLA DE EVENTOS (turnos.ColaEventos) para veneno, sangrado y buffs,
    - ÁRBOL DE DECISIÓN (ia.py) para la IA enemiga,
    - LISTA (inventario.py) para usar objetos en combate,
    - PILA (historial) indirectamente: huir equivale a un retroceso.

Bucle:  mientras haya un bando vivo:
          si la cola de turnos está vacía -> nueva RONDA: se procesa la cola
          de eventos y se recalcula la iniciativa.
          se desencola al combatiente en turno y actúa (jugador: menú;
          enemigo: árbol de decisión). Vuelve al final de la cola.
"""

import random

from . import ui
from . import ia
from .entidades import Enemigo
from .turnos import SistemaTurnos, ColaEventos


class Combate:
    def __init__(self, pampa, enemigos, inventario, catalogo_por_id, estado_mundo):
        self.pampa = pampa
        self.enemigos = list(enemigos)
        self.inv = inventario
        self.catalogo = catalogo_por_id
        self.estado = estado_mundo
        self.eventos = ColaEventos()
        self.ronda = 0
        self.turno_global = 0
        self._invocados = []

    # ------------------------------------------------------------------
    def _combatientes_vivos(self):
        return [self.pampa] + [e for e in self.enemigos + self._invocados if e.vivo]

    def _enemigos_vivos(self):
        return [e for e in self.enemigos + self._invocados if e.vivo]

    def ejecutar(self):
        ui.EN_COMBATE = True
        try:
            return self._bucle()
        finally:
            ui.EN_COMBATE = False

    def _bucle(self):
        for e in self.enemigos:
            frase = e.frases.get("aparecer")
            if frase:
                ui.escribir("  " + frase, "rojo_claro")
        ui.regla()

        turnos = SistemaTurnos(self._combatientes_vivos())
        self.ronda = 1
        self._anunciar_orden(turnos)

        while self.pampa.vivo and self._enemigos_vivos():
            if not turnos.hay_turnos():
                # ---- fin de ronda: procesar COLA DE EVENTOS ----
                for msg in self.eventos.procesar_ronda():
                    ui.escribir("  » " + msg, "magenta")
                if not self.pampa.vivo or not self._enemigos_vivos():
                    break
                self.ronda += 1
                turnos = SistemaTurnos(self._combatientes_vivos())
                ui.regla("·")
                ui.escribir(f"  --- Ronda {self.ronda} ---", "gris")

            actor = turnos.siguiente()
            if not actor.vivo:
                continue
            self.turno_global += 1

            # ---- aturdimiento ----
            if actor.tiene_efecto("aturdir"):
                actor.efectos = [e for e in actor.efectos if e["tipo"] != "aturdir"]
                ui.escribir(f"  {actor.nombre} está ATURDIDO y pierde el turno.", "amarillo")
                turnos.devolver_al_final(actor)
                continue

            actor.defendiendo = False    # 'defender' solo dura hasta tu próximo turno

            if actor is self.pampa:
                resultado = self._turno_jugador()
                if resultado == "huida":
                    return "huida"
            else:
                self._turno_enemigo(actor, turnos)

            turnos.devolver_al_final(actor)

        return "victoria" if self.pampa.vivo else "derrota"

    # ------------------------------------------------------------------
    def _anunciar_orden(self, turnos):
        orden = " → ".join(f"{n}({i})" for n, i in turnos.orden_inicial)
        ui.escribir(f"  Iniciativa (velocidad+dado): {orden}", "gris")
        ui.escribir(f"  --- Ronda {self.ronda} ---", "gris")

    def _estado_combate(self):
        ui.regla()
        ui.escribir(f"  {self.pampa.nombre:22} {ui.barra_vida(self.pampa.vida, self.pampa.vida_max)}"
                    f"   ({self.pampa.descripcion_efectos()})")
        for e in self._enemigos_vivos():
            ui.escribir(f"  {e.nombre:22} {ui.barra_vida(e.vida, e.vida_max)}"
                        f"   ({e.descripcion_efectos()})", "rojo")
        ui.regla()

    # ---- TURNO DEL JUGADOR ------------------------------------------
    def _turno_jugador(self):
        self._estado_combate()
        opciones = ["Atacar", "Habilidad / hechizo (bocina de aire, etc.)",
                    "Usar objeto  ← acá te curás con las pociones", "Defender", "Huir"]
        alias = {"a": 0, "h": 1, "o": 2, "d": 3, "f": 4}
        if self.pampa.vida < self.pampa.vida_max * 0.35:
            ui.escribir("  Vas mal de vida: pulsá 3 y elegí una poción / kit para curarte.", "amarillo")
        eleccion = ui.menu("Tu turno, Pampa:", opciones, alias=alias)

        if eleccion == 0:
            self._jugador_ataca()
        elif eleccion == 1:
            if not self._jugador_habilidad():
                return self._turno_jugador()      # acción inválida -> repetir menú
        elif eleccion == 2:
            if not self._jugador_usa_objeto():
                return self._turno_jugador()
        elif eleccion == 3:
            self.pampa.defendiendo = True
            ui.escribir("  Pampa se hace bolita y aguanta. La defensa sube este turno.", "cian")
        elif eleccion == 4:
            return self._jugador_huye()
        return "sigue"

    def _elegir_enemigo(self):
        vivos = self._enemigos_vivos()
        if len(vivos) == 1:
            return vivos[0]
        idx = ui.menu("¿A quién le entrás?", [f"{e.nombre} ({e.vida}/{e.vida_max})" for e in vivos])
        return vivos[idx]

    def _jugador_ataca(self):
        objetivo = self._elegir_enemigo()
        arma = self.catalogo.get(self.pampa.arma, {})
        variacion = random.randint(-1, 2)
        base = self.pampa.ataque + variacion
        critico = ia.tirada(0.15)
        if critico:
            base = int(base * 1.6)
        dano = objetivo.recibir_dano(base)
        texto = f"  Pampa le mete un pijazo a {objetivo.nombre}: {dano} de daño."
        ui.escribir(texto + ("  ¡DE CACHIMBAZO!" if critico else ""), "verde" if not critico else "verde_claro")

        # efecto de arma: la bandeja de chupitos puede aturdir
        if arma.get("efecto", {}).get("aturdir") and ia.tirada(arma["efecto"]["aturdir"]):
            objetivo.aplicar_efecto("aturdir", 1)
            ui.escribir(f"  ¡El bandejazo deja a {objetivo.nombre} viendo estrellitas!", "amarillo")
        self._comprobar_muerte(objetivo)

    def _jugador_habilidad(self):
        acciones = []
        if self.inv.contiene("bocina_aire"):
            usos = self.estado.obtener("bocina_usos", self.catalogo["bocina_aire"]["efecto"]["usos"])
            acciones.append(("bocina", f"Bocina de aire ({usos} usos) — 16 daño, ignora defensa"))
        if self.pampa.nivel >= 2:
            acciones.append(("golpe_giro", "Golpe giratorio — daña a TODOS los enemigos"))
        acciones.append(("concentrar", "Concentrarse — +3 ataque durante 3 turnos"))
        if not acciones:
            ui.escribir("  No tienes habilidades disponibles.", "rojo")
            return False

        idx = ui.menu("Habilidades:", [d for _, d in acciones] + ["« volver"])
        if idx == len(acciones):
            return False
        clave = acciones[idx][0]

        if clave == "bocina":
            usos = self.estado.obtener("bocina_usos", self.catalogo["bocina_aire"]["efecto"]["usos"])
            objetivo = self._elegir_enemigo()
            dano = objetivo.recibir_dano(self.catalogo["bocina_aire"]["efecto"]["dano_fijo"],
                                         ignora_defensa=True)
            ui.escribir(f"  Pampa suelta un bocinazo en la cara de {objetivo.nombre}: {dano} "
                        f"(ignora defensa).", "magenta")
            usos -= 1
            self.estado.establecer("bocina_usos", usos)
            if usos <= 0:
                self.inv.quitar("bocina_aire")
                ui.escribir("  La bocina se queda sin gas.", "gris")
            self._comprobar_muerte(objetivo)
        elif clave == "golpe_giro":
            for e in self._enemigos_vivos():
                d = e.recibir_dano(max(1, self.pampa.ataque - 2))
                ui.escribir(f"  Golpe giratorio: {e.nombre} recibe {d}.", "verde")
            for e in list(self._enemigos_vivos()):
                self._comprobar_muerte(e)
        elif clave == "concentrar":
            self.eventos.programar_buff_temporal(self.pampa, "ataque", 3, 3, "concentración")
            ui.escribir("  Pampa respira hondo. +3 de ataque durante 3 turnos.", "cian")
        return True

    def _jugador_usa_objeto(self):
        usables = [i for i in self.inv.ids()
                   if self.catalogo.get(i, {}).get("tipo") in ("consumible", "arrojadizo")]
        if not usables:
            ui.escribir("  No llevas objetos usables en combate.", "rojo")
            return False
        etiquetas = [f"{self.catalogo[i]['nombre']} — {self.catalogo[i]['descripcion']}" for i in usables]
        idx = ui.menu("¿Qué objeto usas?", etiquetas + ["« volver"])
        if idx == len(usables):
            return False
        id_obj = usables[idx]
        ficha = self.catalogo[id_obj]
        efecto = ficha.get("efecto", {})

        if ficha["tipo"] == "arrojadizo":
            objetivo = self._elegir_enemigo()
            d = objetivo.recibir_dano(efecto.get("dano", 5))
            ui.escribir(f"  Pampa lanza {ficha['nombre']}: {d} de daño a {objetivo.nombre}.", "verde")
            if efecto.get("sangrado"):
                self.eventos.programar_sangrado(objetivo, efecto["sangrado"], 2)
                ui.escribir(f"  {objetivo.nombre} está SANGRANDO.", "rojo")
            if efecto.get("aturdir") and ia.tirada(efecto["aturdir"]):
                objetivo.aplicar_efecto("aturdir", 1)
                ui.escribir(f"  ¡Cae en un vaso! {objetivo.nombre} tiene que beber y pierde el turno.",
                            "amarillo")
            if efecto.get("ralentizar"):
                self.eventos.programar_buff_temporal(
                    objetivo, "velocidad", -efecto["ralentizar"], efecto.get("turnos", 3), ficha["nombre"])
                ui.escribir(f"  {objetivo.nombre} resbala con la gomina: -{efecto['ralentizar']} de velocidad.",
                            "cian")
            self._comprobar_muerte(objetivo)
        else:
            if "curar" in efecto:
                curado = self.pampa.curar(efecto["curar"])
                ui.escribir(f"  Pampa usa {ficha['nombre']} y recupera {curado} de vida.", "verde_claro")
            if efecto.get("cura_estado"):
                self.pampa.quitar_efectos_negativos()
                ui.escribir("  Se limpia el veneno y el sangrado.", "verde_claro")
            if "velocidad" in efecto:
                self.eventos.programar_buff_temporal(
                    self.pampa, "velocidad", efecto["velocidad"], efecto.get("turnos", 3), ficha["nombre"])
                ui.escribir(f"  +{efecto['velocidad']} de velocidad durante {efecto.get('turnos', 3)} turnos.", "cian")
        self.inv.quitar(id_obj)
        return True

    def _jugador_huye(self):
        enemigo = max(self._enemigos_vivos(), key=lambda e: e.velocidad)
        prob = 0.5 + (self.pampa.velocidad - enemigo.velocidad) * 0.08
        if enemigo.tipo in ("miniboss", "jefe"):
            prob -= 0.25
        if ia.tirada(max(0.1, min(0.9, prob))):
            ui.escribir("  Pampa se escurre por la puerta como jabón mojado.", "amarillo")
            return "huida"
        ui.escribir("  ¡No hallás por dónde salir! Perdés el turno, maje.", "rojo")
        return "sigue"

    # ---- TURNO ENEMIGO (ÁRBOL DE DECISIÓN) -------------------------
    def _turno_enemigo(self, enemigo, turnos):
        enemigo.turno_contador += 1
        traza = []
        hay_invocados = any(i.vivo for i in self._invocados)
        accion = ia.decidir_accion(enemigo, self.pampa, enemigo.turno_contador,
                                   hay_invocados=hay_invocados, traza=traza)
        ui.escribir(f"  [IA {enemigo.nombre}] árbol de decisión: "
                    + " | ".join(traza) + f"  ⇒ {accion}", "gris")

        # activación de furia de los jefes al bajar del 45% de vida
        if (enemigo.habilidad_furia and not enemigo.enfurecido
                and enemigo.vida < enemigo.vida_max * 0.45):
            enemigo.enfurecido = True
            enemigo.ataque_base += 3
            ui.escribir("  " + enemigo.frases.get("furia", f"{enemigo.nombre} se enfurece."), "rojo_claro")

        if accion == "atacar":
            self._enemigo_ataca(enemigo)
        elif accion == "defender":
            enemigo.defendiendo = True
            ui.escribir(f"  {enemigo.nombre} se cuadra y se cubre.", "gris")
        elif accion == "invocar":
            self._enemigo_invoca(enemigo, turnos)
        elif accion == "habilidad":
            self._enemigo_habilidad(enemigo)

    def _enemigo_ataca(self, enemigo):
        base = enemigo.ataque + random.randint(-1, 2)
        dano = self.pampa.recibir_dano(base)
        ui.escribir(f"  {enemigo.nombre} le zampa a Pampa: {dano} de daño.", "rojo")

    def _enemigo_habilidad(self, enemigo):
        hab = enemigo.habilidad_furia if (enemigo.enfurecido and enemigo.habilidad_furia) else enemigo.habilidad
        if not hab:
            return self._enemigo_ataca(enemigo)
        efecto = hab.get("efecto", {})
        ui.escribir(f"  {enemigo.nombre} usa {hab['nombre']}!", "rojo_claro")

        objetivos = [self.pampa] if not efecto.get("area") else [self.pampa]
        for obj in objetivos:
            dano = obj.recibir_dano(hab.get("dano", enemigo.ataque + 3))
            ui.escribir(f"    {obj.nombre} recibe {dano} de daño.", "rojo")
        if efecto.get("veneno"):
            self.eventos.programar_veneno(self.pampa, efecto["veneno"], 2)
            ui.escribir("    ¡Pampa queda ENVENENADO! (o fue la comida de la disco)", "magenta")
        if efecto.get("sangrado"):
            self.eventos.programar_sangrado(self.pampa, efecto["sangrado"], 3)
            ui.escribir("    ¡Pampa va SANGRANDO!", "magenta")
        if efecto.get("aturdir_prob") and ia.tirada(efecto["aturdir_prob"]):
            self.pampa.aplicar_efecto("aturdir", 1)
            ui.escribir("    ¡Pampa queda viendo pajaritos!", "amarillo")

    def _enemigo_invoca(self, enemigo, turnos):
        ui.escribir("  " + enemigo.frases.get("invocar", f"{enemigo.nombre} pide refuerzos."), "rojo_claro")
        eco = Enemigo.desde_id("eco_musical")
        self._invocados.append(eco)
        turnos.agregar_combatiente(eco)
        ui.escribir(f"  Se aparece un {eco.nombre}.", "rojo")

    # ---- muerte de enemigos --------------------------------------
    def _comprobar_muerte(self, enemigo):
        if enemigo.vivo:
            return
        frase = enemigo.frases.get("morir")
        ui.escribir("  " + (frase or f"{enemigo.nombre} cae derrotado."), "verde_claro")
        if enemigo.xp:
            subio = self.pampa.ganar_xp(enemigo.xp, enemigo.nombre)
            ui.escribir(f"  +{enemigo.xp} de experiencia.", "cian")
            if subio:
                self.pampa.aplicar_equipo(self.catalogo)
                ui.escribir(f"  ¡Pampa sube a nivel {self.pampa.nivel}! Más vida y más pegue.",
                            "amarillo_claro")
