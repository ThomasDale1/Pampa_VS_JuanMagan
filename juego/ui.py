"""
ui.py — Utilidades de presentación para la terminal.

No implementa estructuras de datos: solo dibuja texto, cajas, barras de vida
y un efecto "máquina de escribir" para la narrativa. Se mantiene aparte para
que el resto de módulos no mezcle lógica con presentación.
"""

import os
import sys
import time
import unicodedata


def normalizar(texto):
    """minúsculas y sin acentos, para comparar lo que teclea el jugador."""
    desc = unicodedata.normalize("NFKD", str(texto).lower())
    return "".join(ch for ch in desc if not unicodedata.combining(ch)).strip()

# ---------------------------------------------------------------------------
# Configuración global de estilo (se ajusta desde main.py con los flags)
# ---------------------------------------------------------------------------
COLOR = True          # usar códigos ANSI de color
VELOCIDAD_TEXTO = 0.0  # segundos por carácter en la narración (0 = instantáneo)
ENTRADA = None         # si es un callable(prompt)->str, se usa en vez de input()
EN_COMBATE = False      # lo activa combate.py; útil para guiones de prueba


class SalirDelJuego(Exception):
    """Se lanza cuando se agota la entrada (EOF / fin del guion de demo)."""

_ANSI = {
    "reset": "\033[0m", "negrita": "\033[1m", "tenue": "\033[2m",
    "rojo": "\033[31m", "verde": "\033[32m", "amarillo": "\033[33m",
    "azul": "\033[34m", "magenta": "\033[35m", "cian": "\033[36m",
    "gris": "\033[90m", "rojo_claro": "\033[91m", "verde_claro": "\033[92m",
    "amarillo_claro": "\033[93m", "cian_claro": "\033[96m", "blanco": "\033[97m",
}


def habilitar_ansi_windows():
    """En Windows hay que 'despertar' el soporte ANSI de la consola."""
    if os.name == "nt":
        os.system("")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def c(texto, *estilos):
    """Devuelve 'texto' envuelto en códigos de color (o sin ellos si COLOR=False)."""
    if not COLOR or not estilos:
        return str(texto)
    prefijo = "".join(_ANSI.get(e, "") for e in estilos)
    return f"{prefijo}{texto}{_ANSI['reset']}"


def escribir(texto="", *estilos, salto=True):
    """Imprime con efecto máquina de escribir si VELOCIDAD_TEXTO > 0."""
    texto = c(texto, *estilos) if estilos else str(texto)
    if VELOCIDAD_TEXTO <= 0:
        print(texto, end="\n" if salto else "")
        return
    for caracter in texto:
        sys.stdout.write(caracter)
        sys.stdout.flush()
        time.sleep(VELOCIDAD_TEXTO)
    if salto:
        sys.stdout.write("\n")


def titulo(texto):
    """Encabezado grande centrado en una caja doble."""
    ancho = max(len(linea) for linea in texto.splitlines()) + 4
    print(c("╔" + "═" * ancho + "╗", "cian"))
    for linea in texto.splitlines():
        print(c("║ " + linea.center(ancho - 2) + " ║", "cian", "negrita"))
    print(c("╚" + "═" * ancho + "╝", "cian"))


def caja(texto, titulo_caja=None, estilo="gris"):
    """Dibuja un párrafo dentro de una caja simple."""
    lineas = texto.splitlines() or [""]
    ancho = max([len(l) for l in lineas] + [len(titulo_caja or "")]) + 2
    tope = "┌" + "─" * ancho + "┐"
    if titulo_caja:
        etiqueta = f" {titulo_caja} "
        tope = "┌─" + etiqueta + "─" * (ancho - len(etiqueta) - 1) + "┐"
    print(c(tope, estilo))
    for l in lineas:
        print(c("│ " + l.ljust(ancho - 1) + "│", estilo))
    print(c("└" + "─" * ancho + "┘", estilo))


def barra_vida(actual, maximo, largo=20):
    """Barra de vida ASCII: [#########-----------] 14/30"""
    actual = max(0, actual)
    llenos = 0 if maximo <= 0 else int(round(largo * actual / maximo))
    llenos = min(largo, llenos)
    color = "verde" if actual > maximo * 0.5 else "amarillo" if actual > maximo * 0.25 else "rojo"
    barra = "█" * llenos + "░" * (largo - llenos)
    return c(f"[{barra}] {actual}/{maximo}", color)


def regla(caracter="─", ancho=60, estilo="gris"):
    print(c(caracter * ancho, estilo))


# ===========================================================================
#  ENTRADA POR UNA SOLA TECLA  (el juego no se escribe: se pulsa)
# ===========================================================================
CONTEXTO_MENU = ""   # título del último menú/pantalla (para guiones de prueba)

_ESPECIALES = {
    "": "ENTER", "enter": "ENTER", "esc": "ESC", "escape": "ESC",
    "arriba": "ARRIBA", "abajo": "ABAJO", "izq": "IZQUIERDA", "der": "DERECHA",
    "space": " ", "espacio": " ",
}


def _getch_crudo():
    """Un keypress crudo -> 'a'..'z', '0'..'9', o 'ENTER'/'ESC'/'ARRIBA'/..."""
    if os.name == "nt":
        import msvcrt
        ch = msvcrt.getwch()
        if ch in ("\x00", "\xe0"):                 # tecla extendida (flechas, F...)
            ch2 = msvcrt.getwch()
            return {"H": "ARRIBA", "P": "ABAJO", "K": "IZQUIERDA", "M": "DERECHA"}.get(ch2, "")
        if ch == "\r":
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch.lower()
    # POSIX
    import termios
    import tty
    import select
    fd = sys.stdin.fileno()
    viejo = termios.tcgetattr(fd)
    try:
        tty.setcbreak(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            if select.select([sys.stdin], [], [], 0.001)[0]:
                seq = sys.stdin.read(2)
                return {"[A": "ARRIBA", "[B": "ABAJO", "[C": "DERECHA",
                        "[D": "IZQUIERDA"}.get(seq, "ESC")
            return "ESC"
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, viejo)
    if ch in ("\r", "\n"):
        return "ENTER"
    if ch == "\x03":
        raise KeyboardInterrupt
    return ch.lower()


def leer_tecla(eco=True):
    """Devuelve UNA tecla. Si hay guion (ui.ENTRADA), la toma de ahí."""
    if ENTRADA is not None:
        try:
            tok = str(ENTRADA("tecla")).strip()
        except (StopIteration, EOFError):
            raise SalirDelJuego()
        k = _ESPECIALES.get(tok.lower(), tok.lower()[:1] if tok else "ENTER")
        if eco:
            print(c(f"  ▸ [{tok or 'Enter'}]", "gris"))
        return k
    try:
        return _getch_crudo()
    except EOFError:
        raise SalirDelJuego()


def preguntar(prompt, opciones=None):
    """Compatibilidad: lee UNA tecla (ya no se escribe en la terminal)."""
    escribir(prompt, "amarillo_claro")
    return leer_tecla()


def menu(titulo_menu, opciones, alias=None):
    """
    Menú numerado de UNA tecla. Devuelve el índice (0-based) elegido.
    'alias' es un dict opcional {tecla: indice}.
    """
    global CONTEXTO_MENU
    CONTEXTO_MENU = titulo_menu
    alias = alias or {}
    escribir()
    escribir("  " + titulo_menu, "negrita", "cian_claro")
    for i, texto in enumerate(opciones, start=1):
        escribir(f"    [{i}] {texto}")
    escribir("  (pulsá el número)", "gris")
    while True:
        k = leer_tecla()
        if k.isdigit() and 1 <= int(k) <= len(opciones):
            return int(k) - 1
        if k in alias:
            return alias[k]
        escribir(f"  Pulsá un número del 1 al {len(opciones)}.", "rojo")


def elegir(titulo_menu, entradas, permitir_esc=True,
           prompt="  Pulsá la tecla de tu opción:"):
    """
    Pantalla de opciones por letra/número. 'entradas' es una lista de
    (tecla, etiqueta) o (tecla, etiqueta, color).  Devuelve la tecla (str)
    en minúscula, o 'ESC'.
    """
    global CONTEXTO_MENU
    CONTEXTO_MENU = titulo_menu
    validas = set()
    if titulo_menu:
        escribir()
        escribir("  " + titulo_menu, "negrita", "cian_claro")
    for e in entradas:
        tecla, etiqueta = e[0], e[1]
        color = e[2] if len(e) > 2 else None
        validas.add(str(tecla).lower())
        linea = f"    [{str(tecla).upper()}] {etiqueta}"
        escribir(linea, color) if color else escribir(linea)
    if permitir_esc:
        escribir("    [Esc] volver", "gris")
    escribir(prompt, "amarillo_claro")
    while True:
        k = leer_tecla()
        if k in validas:
            return k
        if k in ("ESC", "ENTER") and permitir_esc:
            return "ESC"
        escribir("  Esa tecla no hace nada acá.", "rojo")


def pausa(mensaje="  — pulsá una tecla para seguir —"):
    if ENTRADA is not None:          # guion de prueba / autojugar: no esperamos
        return
    escribir(mensaje, "gris")
    try:
        leer_tecla(eco=False)
    except (SalirDelJuego, KeyboardInterrupt):
        pass


def tabla(encabezados, filas, estilo_encabezado="cian_claro"):
    """Imprime una tabla de texto alineada por columnas."""
    columnas = list(zip(*([encabezados] + filas))) if filas else [[h] for h in encabezados]
    anchos = [max(len(str(celda)) for celda in col) for col in columnas]
    sep = "─┼─".join("─" * a for a in anchos)

    def fila_texto(celdas):
        return " │ ".join(str(celda).ljust(anchos[i]) for i, celda in enumerate(celdas))

    print(c(fila_texto(encabezados), estilo_encabezado, "negrita"))
    print(c(sep, "gris"))
    for fila in filas:
        print(fila_texto(fila))
