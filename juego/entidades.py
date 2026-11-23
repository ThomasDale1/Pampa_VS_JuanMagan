"""
entidades.py — MODELADO DE DATOS: personajes del juego.

Semana 3: "Abstracción, modelado de datos."
Semana 2: "listas de entidades del juego."

Se define una clase base `Entidad` y de ella heredan `Pampa` (protagonista) y
`Enemigo` (rata, guardaespaldas, tigre, Juan Magán...). Los efectos de estado
(veneno, sangrado, aturdido, buffs temporales) se guardan en una LISTA y los
procesa la COLA DE EVENTOS del sistema de turnos (ver turnos.py).
"""


class Entidad:
    def __init__(self, nombre, vida, ataque, defensa, velocidad):
        self.nombre = nombre
        self.vida_max = vida
        self.vida = vida
        self.ataque_base = ataque
        self.defensa_base = defensa
        self.velocidad_base = velocidad
        # Lista de efectos activos: [{"tipo": str, "turnos": int, "valor": int}, ...]
        self.efectos = []
        self.defendiendo = False

    # -- estadísticas efectivas (base + modificadores temporales) --------
    @property
    def ataque(self):
        return max(0, self.ataque_base + self._bono("ataque"))

    @property
    def defensa(self):
        extra = self._bono("defensa")
        if self.defendiendo:
            extra += self.defensa_base + 2      # defender duplica (aprox.) la defensa
        return max(0, self.defensa_base + extra)

    @property
    def velocidad(self):
        return max(1, self.velocidad_base + self._bono("velocidad"))

    def _bono(self, clave):
        return sum(e.get("valor", 0) for e in self.efectos if e["tipo"] == clave)

    # -- vida -----------------------------------------------------------
    @property
    def vivo(self):
        return self.vida > 0

    def recibir_dano(self, cantidad, ignora_defensa=False):
        if ignora_defensa:
            dano = max(0, int(cantidad))
        else:
            dano = max(1, int(cantidad) - self.defensa)   # siempre al menos 1
        self.vida = max(0, self.vida - dano)
        return dano

    def curar(self, cantidad):
        antes = self.vida
        self.vida = min(self.vida_max, self.vida + int(cantidad))
        return self.vida - antes

    # -- efectos de estado -------------------------------------------
    def aplicar_efecto(self, tipo, turnos, valor=0):
        """Agrega (o refresca) un efecto de estado."""
        for e in self.efectos:
            if e["tipo"] == tipo:
                e["turnos"] = max(e["turnos"], turnos)
                e["valor"] = valor or e["valor"]
                return
        self.efectos.append({"tipo": tipo, "turnos": turnos, "valor": valor})

    def tiene_efecto(self, tipo):
        return any(e["tipo"] == tipo for e in self.efectos)

    def quitar_efectos_negativos(self):
        self.efectos = [e for e in self.efectos if e["tipo"] not in ("veneno", "sangrado", "aturdir")]

    def limpiar_efectos_expirados(self):
        self.efectos = [e for e in self.efectos if e["turnos"] > 0]

    def descripcion_efectos(self):
        if not self.efectos:
            return "sin efectos"
        return ", ".join(f"{e['tipo']}({e['turnos']})" for e in self.efectos)

    def __repr__(self):
        return f"{self.nombre} [{self.vida}/{self.vida_max}]"


class Pampa(Entidad):
    """El protagonista. Añade inventario, equipo y experiencia."""

    def __init__(self):
        super().__init__("Pampa", vida=36, ataque=7, defensa=2, velocidad=6)
        self.arma = None            # id de objeto equipado como arma
        self.armadura = None        # id de objeto equipado como armadura
        self.xp = 0
        self.nivel = 1
        self.enemigos_vencidos = []  # lista de dicts -> usada por el 'ranking'
        # --- alcohol (ver alcohol.py) ---
        self.tragos = 0
        self.alcohol_atk = 0        # modificador acumulado de ataque por beber
        self.alcohol_def = 0        # modificador acumulado de defensa por beber

    # el equipo modifica las estadísticas efectivas
    def bono_equipo(self, catalogo_por_id):
        bono = {"ataque": 0, "defensa": 0, "velocidad": 0}
        for slot in (self.arma, self.armadura):
            if slot and slot in catalogo_por_id:
                for k, v in catalogo_por_id[slot].get("efecto", {}).items():
                    if k in bono:
                        bono[k] += v
        return bono

    def aplicar_equipo(self, catalogo_por_id):
        """Recalcula ataque/defensa/velocidad base a partir del equipo + alcohol."""
        b = self.bono_equipo(catalogo_por_id)
        self.ataque_base = 7 + b["ataque"] + (self.nivel - 1) * 2 + self.alcohol_atk
        self.defensa_base = 2 + b["defensa"] + (self.nivel - 1) + self.alcohol_def
        self.velocidad_base = 6 + b["velocidad"]

    def ganar_xp(self, cantidad, enemigo_nombre=None):
        self.xp += cantidad
        if enemigo_nombre and cantidad > 0:
            self.enemigos_vencidos.append({"nombre": enemigo_nombre, "xp": cantidad})
        subio = False
        while self.xp >= self.nivel * 30:
            self.xp -= self.nivel * 30
            self.nivel += 1
            self.vida_max += 8
            self.vida = self.vida_max
            subio = True
        return subio


class Enemigo(Entidad):
    def __init__(self, datos_enemigo):
        d = datos_enemigo
        super().__init__(d["nombre"], d["vida"], d["ataque"], d["defensa"], d["velocidad"])
        self.id = d["id"]
        self.xp = d.get("xp", 0)
        self.tipo = d.get("tipo", "normal")
        self.habilidad = d.get("habilidad")
        self.habilidad_furia = d.get("habilidad_furia")
        self.botin = list(d.get("botin", []))
        self.frases = d.get("frases", {})
        self.enfurecido = False
        self.turno_contador = 0

    @classmethod
    def desde_id(cls, id_enemigo, tabla=None):
        from .datos import ENEMIGOS
        tabla = tabla or ENEMIGOS
        return cls(tabla[id_enemigo])
