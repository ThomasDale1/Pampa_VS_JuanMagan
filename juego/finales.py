"""
finales.py — LOS FINALES DEL JUEGO y el ÁRBOL DE DECISIÓN que los clasifica.

Semana 14: "Árboles y árboles de decisión."

El juego tiene UN solo modo (RPG por turnos) pero NO un solo final. El
desenlace depende del ESTADO DEL MUNDO (el diccionario de banderas de
`estado_mundo.py`) en el momento en que Pampa sale de la casa:

    - por dónde sale        (portal en el recibidor / ventana del baño / alarma)
    - si venció a Juan Magán y CÓMO   (a golpes / duelo de chupitos / baile)
    - si decide quedarse con la mansión
    - si se desmaya por beber, o si cae en un combate

`ARBOL_FINALES` es un ÁRBOL DE DECISIÓN: cada nodo interno es una pregunta
sobre el contexto y cada hoja es el id de un final. `clasificar(contexto)` lo
recorre de la raíz a una hoja -> O(altura). Es el mismo mecanismo que la IA
enemiga (`ia.NodoDecision`), reutilizado aquí.
"""

from .ia import NodoDecision

# ===========================================================================
# TEXTOS DE LOS 8 FINALES
# ===========================================================================
FINALES = {
    "fuga_limpia": {
        "titulo": "FINAL: FUGA LIMPIA",
        "tipo": "bueno",
        "texto": [
            "Sacás la pistola de portal, la apuntás al muro del zaguán y apretás sin temblar:",
            "un aro verde se abre chisporroteando y del otro lado se oye la calle despertar.",
            "Pampa cruza el portal de un solo brinco y cae en la acera, con goma pero cabal;",
            "atrás quedan el bajo, el tigre y el cantón. Chao, Juan Magán. Que te vaya mal.",
        ],
    },
    "por_la_ventana": {
        "titulo": "FINAL: SALIDA TÉCNICA (por la ventana del baño)",
        "tipo": "bueno",
        "texto": [
            "Ni llave, ni jefe, ni tigre: te escurrís por la ventana como gato asustado",
            "y caés sobre unos tambos de basura que te dejan medio embarrado.",
            "Cojeás calle abajo mientras adentro la fiesta ni cuenta se ha dado.",
            "Rápido, sucio y efectivo. Como una búsqueda binaria: bien optimizado.",
        ],
    },
    "se_acabo_fiesta": {
        "titulo": "FINAL: SE ACABÓ LA FIESTA",
        "tipo": "bueno",
        "texto": [
            "Jalás la palanca roja y todo se prende: se corta la música, se acabó el vacil.",
            "Doscientas personas caen en la cuenta de que llevan seis horas ahí, sin sentir.",
            "En la corredera hacia la puerta nadie se fija en un maje con gorro de feliz",
            "cumpleaños, saliendo tranquilito, silbando, como quien no rompió ni un candil.",
        ],
    },
    "nuevo_juan": {
        "titulo": "FINAL: EL NUEVO JUAN MAGÁN",
        "tipo": "bueno",
        "texto": [
            "Juan, tirado en la alfombra, te pasa las llaves, el control de las luces y la correa:",
            "—Cuidámelo, cerote. Come dos veces al día y odia que le canten mala idea.",
            "Nunca llegás a salir del cantón: ahora el cantón es tuyo, con tigre y con jaleo.",
            "Te coronan con el gorrito de fiesta. Felicidades, supongo. Qué feo.",
        ],
    },
    "colega_fiesta": {
        "titulo": "FINAL: COLEGA DE FIESTA",
        "tipo": "bueno",
        "texto": [
            "Le ganás la batalla de perreo y Juan te alza la mano como a campeón de feria:",
            "—¡ESTE SÍ SABE, VA! —Y te acompaña él mismo a la puerta, sin más miseria.",
            "Te pide un taxi, te da el número y te palmea la espalda con cariño:",
            "—La próxima nos vemos en el Superb, sin secuestro. Cuidate, Pampiño.",
        ],
    },
    "aguanta_gana": {
        "titulo": "FINAL: EL QUE AGUANTA, GANA",
        "tipo": "bueno",
        "texto": [
            "Juan mira el chupito número nueve, dice 'este me lo guardo pa' después'",
            "y se resbala despacito hasta el piso, roncando antes de tocar con los pies.",
            "Le sacás el llavero entero del bolsillo sin que se dé ni cuenta, va,",
            "y salís por la puerta grande caminando muy recto. Concentradísimo. Sin titubear.",
        ],
    },
    "otra_ronda": {
        "titulo": "FINAL MALO: OTRA RONDA",
        "tipo": "malo",
        "texto": [
            "El techo se te viene encima y todo se pone color chupito, maje.",
            "Despertás otra vez en la celda, con una goma peor y el mismo paisaje.",
            "Juan te dejó un vaso de agua y, pegado con babas, un papel que te desarma:",
            "'Descansá, cerote. Mañana seguimos'. Puchica. Volvé a empezar, y con calma.",
        ],
    },
    "ko_tecnico": {
        "titulo": "FINAL MALO: K.O. TÉCNICO",
        "tipo": "malo",
        "texto": [
            "Ves el suelo acercarse en cámara lenta mientras la cumbia sigue sonando.",
            "Despertás otra vez en la celda del sótano, todo entumido y cabeceando.",
            "Alguien te puso una bolsa de hielo en la frente, hay que reconocerlo:",
            "hasta el enemigo tiene sus detalles. Sobate y volvé a intentarlo.",
        ],
    },
}


def contar_finales():
    return len(FINALES)


# ===========================================================================
# EL ÁRBOL DE DECISIÓN
#
#   ¿cayó en combate?  -> KO TÉCNICO
#   └ no: ¿se desmayó por beber? -> OTRA RONDA
#        └ no: ¿salió por la alarma? -> SE ACABÓ LA FIESTA
#             └ no: ¿salió por la ventana? -> POR LA VENTANA
#                  └ no: ¿venció a Juan en un duelo de chupitos? -> EL QUE AGUANTA GANA
#                       └ no: ¿lo venció en una batalla de perreo? -> COLEGA DE FIESTA
#                            └ no: ¿se quedó con la mansión? -> EL NUEVO JUAN MAGÁN
#                                 └ no: -> FUGA LIMPIA
# ===========================================================================
def _construir_arbol():
    n_queda = NodoDecision(
        lambda c: c.get("se_queda", False),
        "nuevo_juan", "fuga_limpia", etiqueta="¿se queda con la mansión?")
    n_baile = NodoDecision(
        lambda c: c.get("juan") == "baile",
        "colega_fiesta", n_queda, etiqueta="¿venció a Juan bailando?")
    n_duelo = NodoDecision(
        lambda c: c.get("juan") == "duelo",
        "aguanta_gana", n_baile, etiqueta="¿venció a Juan a chupitos?")
    n_ventana = NodoDecision(
        lambda c: c.get("salida") == "ventana",
        "por_la_ventana", n_duelo, etiqueta="¿salió por la ventana?")
    n_alarma = NodoDecision(
        lambda c: c.get("salida") == "alarma",
        "se_acabo_fiesta", n_ventana, etiqueta="¿tiró de la alarma?")
    n_desmayo = NodoDecision(
        lambda c: c.get("desmayo", False),
        "otra_ronda", n_alarma, etiqueta="¿se desmayó por beber?")
    n_ko = NodoDecision(
        lambda c: c.get("ko", False),
        "ko_tecnico", n_desmayo, etiqueta="¿cayó en combate?")
    return n_ko


ARBOL_FINALES = _construir_arbol()


def clasificar(contexto, traza=None):
    """Recorre el árbol de decisión y devuelve el id del final. O(altura)."""
    return ARBOL_FINALES.decidir(contexto, traza)


def render_arbol(nodo=None, nivel=0, lineas=None):
    lineas = [] if lineas is None else lineas
    nodo = ARBOL_FINALES if nodo is None else nodo
    if isinstance(nodo, NodoDecision):
        lineas.append("   " * nivel + nodo.etiqueta)
        lineas.append("   " * (nivel + 1) + "sí ->")
        render_arbol(nodo.rama_si, nivel + 2, lineas)
        lineas.append("   " * (nivel + 1) + "no ->")
        render_arbol(nodo.rama_no, nivel + 2, lineas)
    else:
        lineas.append("   " * nivel + f"[{FINALES[nodo]['titulo']}]")
    return lineas


# contextos de ejemplo -> qué final da cada "forma de jugar"
CONTEXTOS_EJEMPLO = [
    ("Pierdes una pelea", {"ko": True}),
    ("Bebes de más y te desmayas", {"desmayo": True}),
    ("Tiras de la alarma de incendios", {"salida": "alarma"}),
    ("Escapas por la ventana del baño", {"salida": "ventana"}),
    ("Ganas a Juan un duelo de chupitos", {"juan": "duelo"}),
    ("Ganas a Juan una batalla de perreo", {"juan": "baile"}),
    ("Vences a Juan a golpes y te quedas la casa", {"juan": "pelea", "se_queda": True}),
    ("Vences a Juan a golpes y sales por la puerta", {"juan": "pelea", "salida": "puerta"}),
]
