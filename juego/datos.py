"""
datos.py — DATOS DEL MUNDO: salas, objetos, enemigos y narrativa.

Semana 3: "Abstracción, modelado de datos."
Semana 2: "Arreglos, vectores, listas y estructuras lineales."

Todo el contenido del juego está separado de la lógica: aquí solo hay
DICCIONARIOS y LISTAS con datos. Cambiar el mundo = editar este archivo.
"""

# ===========================================================================
# CATÁLOGO GLOBAL DE OBJETOS
# ---------------------------------------------------------------------------
# Es una lista FIJA durante la partida. El motor la ordena una vez por 'id'
# para poder aplicar BÚSQUEDA BINARIA en el comando 'examinar'.
#
# tipo: clave | consumible | arma | armadura | arrojadizo | hechizo | lore | alcohol
#
# Los objetos de tipo 'alcohol' (y la botella de tequila) llevan efecto
# {"alcohol": N}: son N TRAGOS y se acaban. El motor lleva la cuenta de las
# cargas restantes en el diccionario de estado (clave "alcohol_<id>").
# ===========================================================================
CATALOGO_OBJETOS = [
    # --- CLAVE: abren puertas / desbloquean mecánicas -------------------
    {
        "id": "carnet_falso", "nombre": "Carné falso", "tipo": "clave",
        "valor": 3, "peso": 0,
        "descripcion": "Un DUI trucho a nombre de 'Pampa Pámpano, 34 años'. Con este entrabas "
                       "al Superb; con el canto rígido forzás cualquier chapa barata.",
        "usar_en": "puerta_celda",
    },
    {
        "id": "llave_bici", "nombre": "Llave del candado de la bici", "tipo": "clave",
        "valor": 5, "peso": 0,
        "descripcion": "Pequeña y pegajosa de cubata. Abre algo más que un candado.",
        "abre": "estudio",
    },
    {
        "id": "pistola_portal", "nombre": "Pistola de portal", "tipo": "clave",
        "valor": 40, "peso": 1,
        "descripcion": "Un cacharro que zumba, con el cañón verde y una lucecita que "
                       "parpadea. Apuntás a cualquier pared, apretás el gatillo y se "
                       "abre un hoyo que da a la calle. Tu boleto de salida de la mansión.",
        "abre": "puerta_principal",
    },
    {
        "id": "mapa_mansion", "nombre": "Plano en una servilleta", "tipo": "clave",
        "valor": 20, "peso": 0,
        "descripcion": "El plano de la mansión dibujado a boli en una servilleta "
                       "manchada de salsa brava. Habilita 'camino' y 'explorar' y "
                       "revela las salas que aún no has visto.",
    },
    # --- CONSUMIBLES: curación y subidones -----------------------------
    {
        "id": "energetica", "nombre": "Lata de energética", "tipo": "consumible",
        "valor": 15, "peso": 1, "efecto": {"curar": 12},
        "descripcion": "Sabe a chicle de dentista y a mala decisión, pero levanta. Cura 12 de vida.",
    },
    {
        "id": "isotonica", "nombre": "Suero oral de bolsita", "tipo": "consumible",
        "valor": 30, "peso": 1, "efecto": {"curar": 26},
        "descripcion": "El remedio de toda abuela salvadoreña pa' la goma y la deshidratación. "
                       "Cura 26 de vida.",
    },
    {
        "id": "pizza_fria", "nombre": "Trozo de pizza fría", "tipo": "consumible",
        "valor": 4, "peso": 1, "efecto": {"curar": 6},
        "descripcion": "Sobró del reven. La grasa cura las penas del cuerpo y las del alma (6 de vida).",
    },
    {
        "id": "kit_goma", "nombre": "Kit anti-goma", "tipo": "consumible",
        "valor": 55, "peso": 2, "efecto": {"curar": 45, "cura_estado": True},
        "descripcion": "Ibuprofeno, un huevo crudo, sopa Maruchan y fe. Cura 45 de vida y "
                       "quita el veneno y el sangrado.",
    },
    {
        "id": "vape", "nombre": "Vape de sandía", "tipo": "consumible",
        "valor": 12, "peso": 0, "efecto": {"velocidad": 3, "turnos": 4},
        "descripcion": "Una jalada y se te despeja el coco. +3 de velocidad durante 4 turnos.",
    },
    {
        "id": "linterna_movil", "nombre": "Móvil con la linterna", "tipo": "consumible",
        "valor": 9, "peso": 1, "efecto": {"revelar": True},
        "descripcion": "3% de batería. Suficiente para alumbrar los rincones de una sala.",
    },
    # --- ARMAS (se equipan) -----------------------------------------
    {
        "id": "palo_selfie", "nombre": "Palo de selfie reforzado", "tipo": "arma",
        "valor": 18, "peso": 2, "efecto": {"ataque": 4},
        "descripcion": "De aluminio, telescópico. Aguantó 200 selfies en el Superb; "
                       "aguanta un pleito. +4 de ataque.",
    },
    {
        "id": "bandeja", "nombre": "Bandeja de chupitos", "tipo": "arma",
        "valor": 14, "peso": 2, "efecto": {"ataque": 2, "aturdir": 0.25},
        "descripcion": "Metálica, todavía con restos de tequila. Un bandejazo bien puesto "
                       "deja viendo estrellitas. +2 de ataque y 25% de aturdir.",
    },
    # --- HECHIZO / consumible de combate a distancia ------------------
    {
        "id": "bocina_aire", "nombre": "Bocina de aire", "tipo": "hechizo",
        "valor": 35, "peso": 1, "efecto": {"dano_fijo": 16, "usos": 3},
        "descripcion": "De las del estadio Cuscatlán. Un bocinazo en la oreja: 16 de daño "
                       "que ni la defensa aguanta. 3 usos antes de quedarse sin gas.",
    },
    # --- ARROJADIZOS -----------------------------------------------
    {
        "id": "botella_tequila", "nombre": "Botella de tequila (a medio morir)", "tipo": "arrojadizo",
        "valor": 10, "peso": 2, "efecto": {"dano": 9, "sangrado": 2, "alcohol": 2},
        "descripcion": "Ya va como por la mitad: le quedan dos tragos. O te los pegás, "
                       "o la aventás girando (9 de daño, y con los vidrios el rival queda sangrando).",
    },
    # --- ALCOHOL: se BEBE, son tragos contados y se acaba -------------
    {
        "id": "lata_regia", "nombre": "Lata de Regia", "tipo": "alcohol",
        "valor": 4, "peso": 1, "efecto": {"alcohol": 1},
        "descripcion": "Una Regia tibia que sobró en la hielera. Un solo trago y a la basura.",
    },
    {
        "id": "botella_1800", "nombre": "Botella de 1800 sellada", "tipo": "alcohol",
        "valor": 22, "peso": 2, "efecto": {"alcohol": 3},
        "descripcion": "Tequila 1800 reposado, todavía con el sello puesto. Da para tres "
                       "tragos buenos antes de quedar seca.",
    },
    {
        "id": "pelota_beerpong", "nombre": "Pelota de beer pong", "tipo": "arrojadizo",
        "valor": 6, "peso": 0, "efecto": {"dano": 3, "aturdir": 0.35},
        "descripcion": "Ligera. 3 de daño, pero un 35% de que caiga en un vaso y el "
                       "enemigo tenga que beber (pierde el turno).",
    },
    {
        "id": "gomina", "nombre": "Bote de gomina de Juan Magán", "tipo": "arrojadizo",
        "valor": 8, "peso": 1, "efecto": {"dano": 3, "ralentizar": 3, "turnos": 3},
        "descripcion": "Se lo tiras y todo se vuelve resbaladizo. 3 de daño y le baja "
                       "la velocidad al rival.",
    },
    # --- ARMADURAS (se equipan) ----------------------------------
    {
        "id": "chaleco", "nombre": "Chaleco de lentejuelas de Juan Magán", "tipo": "armadura",
        "valor": 25, "peso": 3, "efecto": {"defensa": 3},
        "descripcion": "Brilla como bola de disco y, aunque no lo creás, para pijazos. +3 de defensa.",
    },
    {
        "id": "rinonera", "nombre": "Riñonera cruzada", "tipo": "armadura",
        "valor": 12, "peso": 1, "efecto": {"defensa": 1, "ataque": 1},
        "descripcion": "Guarda el móvil, las llaves y algo de dignidad. +1 de defensa "
                       "y +1 de ataque.",
    },
    {
        "id": "gafas_sol", "nombre": "Gafas de sol (de noche)", "tipo": "armadura",
        "valor": 12, "peso": 0, "efecto": {"velocidad": 2},
        "descripcion": "No ves un pimiento, pero molas y nadie te lee la mirada. "
                       "+2 de velocidad.",
    },
    {
        "id": "sombrero_fiesta", "nombre": "Sombrero de fiesta cónico", "tipo": "armadura",
        "valor": 3, "peso": 0, "efecto": {"defensa": 1},
        "descripcion": "De cumpleaños, con una goma que aprieta la barbilla. Nadie pega en "
                       "serio a alguien con esto puesto. +1 de defensa.",
    },
    {
        "id": "cadena_tigre", "nombre": "Cadena de oro del tigre", "tipo": "armadura",
        "valor": 45, "peso": 1, "efecto": {"ataque": 3, "velocidad": 2},
        "descripcion": "El tigre la llevaba al cuello. Pesa, pero impone. +3 de ataque "
                       "y +2 de velocidad.",
    },
    # --- LORE (historia, sin efecto de combate) ------------------
    {
        "id": "diario_juan", "nombre": "Diario de Juan Magán", "tipo": "lore",
        "valor": 8, "peso": 1,
        "descripcion": "Tapas de escarcha y letra de niña. Cuenta por qué le agarró tanta rabia a Pampa.",
    },
    {
        "id": "postit", "nombre": "Papelito de la refri", "tipo": "lore",
        "valor": 1, "peso": 0,
        "descripcion": "\"El estante de la biblio pide un número: el décimo de la sucesión "
                       "0, 1, 1, 2, 3, 5... No seás yuca. —J.\"",
    },
    {
        "id": "ficha_poker", "nombre": "Ficha de póker de 1000", "tipo": "lore",
        "valor": 7, "peso": 0,
        "descripcion": "De la mesa de arriba. Con suerte cuela como pisto en la tiendita de la esquina.",
    },
]

# ===========================================================================
# SALAS DE LA MANSIÓN  (nodos del GRAFO)
# ===========================================================================
SALAS = {
    "celda": {
        "nombre": "Celda del sótano",
        "descripcion": "Un cuartito húmedo con catre de lata y una puerta de barrotes.\n"
                       "  Huele a encierro, a colonia barata y a tus propios alientotes.",
        "objetos": ["carnet_falso", "pizza_fria"],
        "enemigo": None,
        "primera_visita": "Abrís un ojo. Luego el otro, con calma y con dolor.\n"
                          "  Sos Pampa, y traés una goma que da miedo y da rubor.\n"
                          "  Anoche estabas en el Superb, contento y sin ninguna pena;\n"
                          "  hoy amanecés en un sótano ajeno, encerrado en esta celda con cadena.\n"
                          "  El cantón es de Juan Magán —ese rival tuyo, tan creído—;\n"
                          "  por el bajo que retumba arriba, la nochecita apenas ha corrido.",
    },
    "pasillo_sotano": {
        "nombre": "Pasillo del sótano",
        "descripcion": "Un corredor de piedra con un foco que titila sin razón.\n"
                       "  De algún piso allá arriba baja un bajo que te taladra el corazón.",
        "objetos": [],
        "enemigo": None,
    },
    "bodega": {
        "nombre": "Bodega",
        "descripcion": "Estantes con trago pa' un año y cajas de gaseosa amontonada.\n"
                       "  Huele dulzón, a licor derramado y a fiesta mal terminada.",
        "objetos": ["llave_bici", "energetica", "postit", "botella_tequila", "lata_regia"],
        "enemigo": "rata",
    },
    "escalera": {
        "nombre": "Escalera principal",
        "descripcion": "Una escalera de mármol sube hacia la planta de los ricos.\n"
                       "  La música pega más fuerte; ya se oyen hasta los silbidos.",
        "objetos": [],
        "enemigo": None,
    },
    "cocina": {
        "nombre": "Cocina",
        "descripcion": "Vasos de durapax hasta el techo, una refri que zumba de a montón,\n"
                       "  pizzas a medio comer... y algo que se movió tras un cartón.",
        "objetos": ["palo_selfie", "bandeja", "vape", "lata_regia"],
        "enemigo": "rata2",
    },
    "comedor": {
        "nombre": "Comedor",
        "descripcion": "Una mesota larga con las sobras del reven: vasos de chupito regados,\n"
                       "  confeti, un zapato solito y un beer pong con los cubos aún montados.",
        "objetos": ["botella_tequila", "pizza_fria", "ficha_poker",
                    "pelota_beerpong", "sombrero_fiesta"],
        "enemigo": None,
    },
    "salon": {
        "nombre": "Salón principal",
        "descripcion": "Luces de disco, un sofá en forma de bocota y dos torres de sonido a todo dar.\n"
                       "  Un guardaespaldas del tamaño de un ropero no te deja ni respirar.",
        "objetos": ["rinonera", "gafas_sol"],
        "enemigo": "guardaespaldas",
    },
    "biblioteca": {
        "nombre": "Biblioteca",
        "descripcion": "Mil libros que Juan nunca leyó y un estante giratorio con teclado.\n"
                       "  Pide un número pa' abrirse; el maje era bien complicado.",
        "objetos": [],            # el botín aparece al resolver el acertijo
        "enemigo": None,
        "acertijo": {
            "pregunta": "El estante pide el DÉCIMO número de Fibonacci (empezando F(0)=0, F(1)=1).",
            "respuesta": 34,       # F(9)=34 con esa numeración -> "el décimo número"
            "recompensa": ["mapa_mansion", "bocina_aire"],
            "exito": "El estante gira con un clunc y suelta un compartimiento escondido.",
        },
    },
    "recibidor": {
        "nombre": "Recibidor",
        "descripcion": "El zaguán de la entrada: un cerro de tenis regados por el piso\n"
                       "  y un portón de madera que da a la calle. Cerrado con llave, por si acaso.",
        "objetos": ["linterna_movil"],
        "enemigo": None,
    },
    "pasillo_alto": {
        "nombre": "Pasillo de la planta alta",
        "descripcion": "Retratos de Juan Magán en cien poses distintas, cada cual más presumida.\n"
                       "  Todos te siguen con la mirada. Puchica, qué falta de medida.",
        "objetos": [],
        "enemigo": None,
    },
    "bano": {
        "nombre": "Baño de mármol",
        "descripcion": "Un jacuzzi, espejos hasta el cielo raso, un bolo roncando en la bañera,\n"
                       "  un botiquín reventado... y una ventana que da justo pa' fuera.",
        "objetos": ["isotonica", "kit_goma"],
        "enemigo": None,
    },
    "estudio": {
        "nombre": "Estudio",
        "descripcion": "Discos de platino en la pared, un escritorio de vidrio bien pegajoso\n"
                       "  y una caja fuerte abierta de par en par, como quien no guarda nada valioso.",
        "objetos": ["pistola_portal", "chaleco", "diario_juan", "gomina", "botella_1800"],
        "enemigo": None,
    },
    "jardin": {
        "nombre": "Jardín interior",
        "descripcion": "Un patio techado con matas tropicales y una jaula vacía de par en par.\n"
                       "  Algo grande respira entre los helechos. Aguas, maje, con lo que hay ahí atrás.",
        "objetos": [],
        "enemigo": "tigre",
    },
    "cuarto_juan": {
        "nombre": "Cuarto de Juan Magán",
        "descripcion": "Cama redonda, otra bola de disco girando y, sentado como rey en su reino,\n"
                       "  el mismísimo Juan Magán con una copa en la mano y cara de veneno.",
        "objetos": [],
        "enemigo": "juan_magan",
    },
}

# ===========================================================================
# ARISTAS DEL GRAFO  (puertas y pasillos entre salas)
#   (sala_a, sala_b, cerradura)
#   cerradura = None                         -> abierta
#             = {"objeto": "id_objeto"}      -> necesita ese objeto en el inventario
#             = {"flag": "bandera"}          -> necesita esa bandera activa en EstadoMundo
#             = {"objeto": "...", "secreta": True} -> además, oculta hasta tener el plano
# ===========================================================================
ARISTAS = [
    ("celda", "pasillo_sotano", {"objeto": "carnet_falso", "consumir": False, "puerta": "puerta_celda"}),
    ("pasillo_sotano", "bodega", None),
    ("pasillo_sotano", "escalera", None),
    ("escalera", "cocina", None),
    ("escalera", "salon", None),
    ("cocina", "comedor", None),
    ("comedor", "salon", None),
    ("salon", "biblioteca", None),
    ("salon", "recibidor", None),
    ("salon", "escalera", None),
    ("salon", "pasillo_alto", {"flag": "guardaespaldas_derrotado"}),
    ("pasillo_alto", "bano", None),
    ("pasillo_alto", "estudio", {"objeto": "llave_bici", "consumir": False}),
    ("pasillo_alto", "jardin", None),
    ("biblioteca", "estudio", {"objeto": "mapa_mansion", "consumir": False, "secreta": True}),
    ("jardin", "cuarto_juan", {"flag": "tigre_derrotado"}),
    ("recibidor", "puerta_principal", {"objeto": "pistola_portal", "consumir": False, "puerta": "salida"}),
    ("bano", "ventana_calle", {"puerta": "ventana"}),   # ruta de fuga alternativa
]

SALA_INICIAL = "celda"
SALA_SALIDA = "puerta_principal"     # nodo virtual (fuga abriendo un portal con la pistola)
SALA_VENTANA = "ventana_calle"       # nodo virtual (fuga por la ventana del baño)
SALIDAS = {SALA_SALIDA, SALA_VENTANA}

# ===========================================================================
# BARRAS FIJAS DE CADA SALA  (tragos que se pueden servir ahí antes de agotarla)
# ---------------------------------------------------------------------------
# El alcohol es de USO LIMITADO en todos lados: cada sala con trago tiene una
# reserva contada. El motor descuenta de "barra_<sala>" en el diccionario de
# estado. Cuando se acaba, hay que buscar botellas (tipo 'alcohol') que se
# cargan en la mochila. El duelo de chupitos con Juan va aparte (él sirve).
# ===========================================================================
BARRA_SALAS = {
    "bodega": 5,        # es la bodega: estantes de trago pa' un año
    "comedor": 3,       # lo que quedó servido del reven
    "salon": 2,         # un par de botellas cerca de las torres de sonido
    "cuarto_juan": 4,   # la barra privada de Juan Magán
}

# ===========================================================================
# PLANTAS DE LA MANSIÓN  (para el plano 2D por pisos, mapa.plano_planta)
#   cada sala se coloca en una rejilla (columna, fila). Las salas que conectan
#   dos pisos (escalera, salón, biblioteca) aparecen en los dos.
#   'corto' = nombre corto para que quepa en la cajita del plano.
# ===========================================================================
CORTO = {
    "celda": "Celda", "pasillo_sotano": "Pasillo", "bodega": "Bodega",
    "escalera": "Escalera", "cocina": "Cocina", "comedor": "Comedor",
    "salon": "Salón", "biblioteca": "Biblio", "recibidor": "Recibidor",
    "puerta_principal": "» PORTAL", "pasillo_alto": "Pas.alto", "bano": "Baño",
    "estudio": "Estudio", "jardin": "Jardín", "cuarto_juan": "C.Juan",
    "ventana_calle": "» CALLE",
}

PLANTAS = [
    {"nombre": "SÓTANO", "salas": {
        "celda": (0, 0), "pasillo_sotano": (1, 0), "bodega": (2, 0),
        "escalera": (1, 1)}},
    {"nombre": "PLANTA NOBLE", "salas": {
        "escalera": (0, 0), "cocina": (0, 1), "comedor": (0, 2),
        "salon": (1, 1), "biblioteca": (2, 1),
        "recibidor": (1, 2), "puerta_principal": (1, 3)}},
    {"nombre": "PLANTA ALTA", "salas": {
        "salon": (1, 0),
        "estudio": (0, 1), "pasillo_alto": (1, 1), "bano": (2, 1), "ventana_calle": (3, 1),
        "jardin": (1, 2), "biblioteca": (2, 2),
        "cuarto_juan": (1, 3)}},
]


def piso_de(sala):
    """Devuelve el índice de planta 'principal' de una sala (0, 1 o 2)."""
    for i, planta in enumerate(PLANTAS):
        if sala in planta["salas"]:
            return i
    return 0

# ===========================================================================
# ENEMIGOS
#   habilidad: ataque especial que usa el árbol de decisión de ia.py
# ===========================================================================
ENEMIGOS = {
    "rata": {
        "id": "rata", "nombre": "Rata de bodega",
        "vida": 12, "ataque": 4, "defensa": 0, "velocidad": 8, "xp": 8,
        "tipo": "normal",
        "habilidad": {"nombre": "Mordisco infectado", "dano": 5, "efecto": {"veneno": 2}},
        "frases": {"aparecer": "Entre las cajas de cususa asoma una rata bien criada:\n"
                               "  del tamaño de un chucho chele y con cara de enojada.",
                   "morir": "La rata pega un chillido, se resbala en un charco de ron,\n"
                            "  y ahí queda, patas arriba, cerrando su triste función."},
    },
    "rata2": {
        "id": "rata2", "nombre": "Rata de cocina",
        "vida": 14, "ataque": 5, "defensa": 1, "velocidad": 8, "xp": 10,
        "tipo": "normal",
        "habilidad": {"nombre": "Salto sucio", "dano": 6, "efecto": {}},
        "frases": {"aparecer": "Salta otra rata, más gorda, de una torre de trastes sucios;\n"
                               "  se truena el cuello, te mira... y viene con más berrinches.",
                   "morir": "Cae en la olla de frijoles y se hunde sin decir 'adiós'.\n"
                            "  Descanse con su casamiento. Amén, y bendito Dios."},
    },
    "guardaespaldas": {
        "id": "guardaespaldas", "nombre": "Guardaespaldas de Juan",
        "vida": 22, "ataque": 5, "defensa": 2, "velocidad": 5, "xp": 24,
        "tipo": "elite",
        "habilidad": {"nombre": "Vergazo de ropero", "dano": 7, "efecto": {"aturdir_prob": 0.22}},
        "frases": {"aparecer": "—El jefe anda ocupado, bicho —dice el ropero con corbata—.\n"
                               "  Date la vuelta por las buenas, no me obligués a hacer piñata.",
                   "morir": "El guardaespaldas se derrumba sobre el sofá con forma de labios,\n"
                            "  roncando ya como un microbús. Que descanse de sus agravios."},
    },
    "eco_musical": {
        "id": "eco_musical", "nombre": "Eco de la bocina",
        "vida": 10, "ataque": 6, "defensa": 0, "velocidad": 7, "xp": 0,
        "tipo": "invocado",
        "habilidad": {"nombre": "Estribillo pegajoso", "dano": 4, "efecto": {}},
        "frases": {"aparecer": "De la torre de sonido sale una silueta hecha de puro bajo.",
                   "morir": "El eco se deshace en estática y se va como llegó: de relajo."},
    },
    "tigre": {
        "id": "tigre", "nombre": "El Tigre de Juan Magán",
        "vida": 42, "ataque": 10, "defensa": 3, "velocidad": 10, "xp": 55,
        "tipo": "miniboss",
        "habilidad": {"nombre": "Zarpazo doble", "dano": 15, "efecto": {"sangrado": 3}},
        "botin": ["cadena_tigre"],
        "frases": {"aparecer": "De los helechos sale el tigre, con su cadenota de oro;\n"
                               "  gruñe, saca los colmillos y te mira como a un toro.",
                   "morir": "El tigre bosteza, se hace rosca y te deja el paso franco.\n"
                            "  Le quitás la cadena de oro: hoy el chivo sos vos, no el blanco."},
    },
    "juan_magan": {
        "id": "juan_magan", "nombre": "Juan Magán",
        "vida": 72, "ataque": 12, "defensa": 4, "velocidad": 6, "xp": 120,
        "tipo": "jefe",
        "habilidad": {"nombre": "Perreo intenso", "dano": 10, "efecto": {"area": True}},
        "habilidad_furia": {"nombre": "Drop del bajo", "dano": 18, "efecto": {"aturdir_prob": 0.3}},
        "frases": {"aparecer": "—Pampa, Pampa... —Juan Magán suelta la copa despacito—.\n"
                               "  Te traje del Superb pa' esto: nadie humilla a Juan Magancito.",
                   "furia": "Juan se arranca el chaleco de lentejuelas y pega el grito:\n"
                            "  —¡AHORA VA EN SERIO, MAJE!— El bajo sube. Y tu goma, un martirio.",
                   "invocar": "Juan apunta a la bocina: —¡Coro, conmigo, no sean lentos!",
                   "morir": "Juan Magán cae de rodillas, la corona se le va de lado:\n"
                            "  —Ya, ya... ganaste, cerote. La puerta es tuya. Andate con cuidado."},
    },
}

# ===========================================================================
# NARRATIVA
# ===========================================================================
ARTE_TITULO = r"""
   ___  _   _  _  ___  _     __   __ ___   _  _   _   _  _
  | _ \/_\ | \| || _ \/_\   \ \ / // __| | || | /_\ | \| |
  |  _/ _ \| .` ||  _/ _ \   \ V / \__ \ | __ |/ _ \| .` |
  |_|/_/ \_\_|\_||_|/_/ \_\   \_/  |___/ |_||_/_/ \_\_|\_|
        M A G Á N   —   L A   M A Z M O R R A
"""

INTRO = [
    "Anoche te fuiste al Superb, a bailar y a desvelarte,",
    "con tus cheros, tus Pilseners y unas ganas de alegrarte.",
    "Sonó cumbia, sonó house, y la noche iba de a millón...",
    "hasta que todo se puso negro y despertaste en un rincón.",
    "",
    "Mala nota, Pampa: este cantón es de Juan Magán, tu enemigo declarado,",
    "que te sacó cargado de la disco pa' cobrarse un pleito atrasado.",
    "Buena nota: salidas hay varias —un portal, la ventana, una alarma que jalar—.",
    "Cómo salgás ya es cosa tuya, maje: a los pijazos, bailando o a puro chupitear.",
]

# (los textos de los 8 finales están en finales.py)

DIARIO_TEXTO = [
    "Día 1: agarré a Pampa en el Superb. Bien bolo iba el cerote, ni cuenta se dio.",
    "        Que se pudra en el sótano; conmigo nadie se pasa de listo, no.",
    "Día 12: el tigre ya no me pela. Solo obedece si le canto mi estribillo con cariño.",
    "Día 30: la pistola de portal quedó en la caja fuerte del estudio; la llave de la bici, en la bodega.",
    "Día 45: si Pampa lee esto: hay puerta, hay ventana, hay alarma. Escoja bien, que la noche se le apega.",
]
