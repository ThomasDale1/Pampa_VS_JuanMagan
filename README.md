# Pampa y la Mazmorra de Juan Magán

Juego de terminal en Python puro (solo biblioteca estándar). Proyecto final de
**Programación / Estructura de Datos y Algoritmos**.

**Un solo modo**: un RPG por turnos donde exploras la mansión de Juan Magán
**pulsando una sola tecla** (no se escribe nada). Peleas (o no), recoges y usas
objetos, desbloqueas puertas, bebes... y **el final que te toca (hay 8) depende
de todo eso**: por dónde salgas, a quién te enfrentes, qué lleves y cuánto bebas.

> Anoche Pampa estaba en el **Superb** (la disco), tranquilo con sus cheros y
> sus Pilseners. De la nada, apagón: despierta encerrado en el sótano de su
> peor enemigo, **Juan Magán**, que lo sacó cargado de la disco para cobrarse
> un pleito viejo. Para salir tendrá que vérselas con el **Tigre de Juan
> Magán**, con **Juan Magán** y, sobre todo, con la barra libre.
>
> Toda la narración va con toque salvadoreño y, cuando se puede, rimando.

Cada mecánica está construida sobre una estructura de datos o un algoritmo del
temario, y el código lo documenta en el punto donde se usa.

---

## Cómo ejecutar

```bash
cd juegoPED
py main.py                 # jugar
py main.py --demo          # TOUR TÉCNICO de todas las estructuras y
                               # algoritmos (incluye el ÁRBOL DE DECISIÓN de los
                               # finales y la tabla de probabilidad del alcohol)
py main.py --benchmark     # informe empírico de rendimiento
py main.py --complejidad   # imprime solo las tablas Big-O
py main.py --sin-color     # sin colores ANSI
py main.py --historia-lenta  # narración con efecto "máquina de escribir"
py main.py --semilla=42    # fija la aleatoriedad (partidas reproducibles)

py autojugar.py            # el juego jugado solo hasta "Fuga limpia"
py autojugar.py ventana    # ... hasta otro final (ventana / alarma / duelo / nuevo_juan)
```

Requiere **Python 3.9 o superior**. No hay dependencias externas.
`progreso.json` recuerda qué finales has descubierto entre partidas.

---

## Cómo se juega

**El juego se juega con UNA sola tecla — no se escribe nada en la terminal.**
En cada sala aparece un menú; pulsás una tecla:

| Tecla | Qué hace |
|---|---|
| **1 – 9** | ir a la salida con ese número (**Grafo** + **Pila** de historial) |
| **A – H** | agarrar el objeto con esa letra (**Lista** + búsqueda lineal); lo mejor se equipa solo |
| **I** | mochila (**8 objetos "pesados"**; llaves y notas no cuentan) → `[U]` usar · `[B]` beber · `[E]` equipar · `[S]` soltar · `[1]` ordenar (quicksort) · `[2]` lineal vs binaria · `[3]` deshacer (**Pila**) |
| **M** | **plano 2D del piso** donde estás; `[1/2/3]` ver otro piso; `[A]` lista/matriz de adyacencia; `[C]` ruta más corta (**BFS**); `[X]` recorrer todo (**DFS**) |
| **L** | volver a mirar la sala |
| **T** | objetivos (**Árbol** de misiones) + estado del mundo (**diccionario / tabla hash**) |
| **P** | ficha de Pampa + ranking de enemigos (**Ordenamientos**) |
| **R** | volver a la sala anterior (**Pila**) |
| **V** / **X** / **J** / **Z** | beber un trago / acertijo (**Recursividad**, Fibonacci) / beer pong / alarma |
| **G** / **Q** / **?** | guardar · salir · abrir el **manual** |

Al arrancar, el juego **pregunta si querés ver el manual** completo de teclas.
Dentro del juego, cada pantalla y cada menú **te recuerda qué tecla hace qué**
(p. ej. en combate: "pulsá 3 y elegí una poción para curarte").

**Con un enemigo delante** el menú cambia: `1` pelear, y según a quién tengás
`2/3` la salida sin bronca (sobornar/cantar/retar · colarse/bailar), `4` alarma
(solo con Juan), `9` alejarte. **En combate:** `1` atacar · `2` habilidad ·
`3` usar objeto (¡curarte!) · `4` defender · `5` huir.

Podés hacer una partida **pacifista** (sobornar al guardaespaldas, cantarle al
tigre, ganarle a Juan bailando) sin ganar una sola pelea.

---

## Los 8 finales

El final lo decide un **árbol de decisión** (`finales.py`) a partir del estado
del mundo al terminar:

| Final | Tipo | Cómo se llega |
|---|---|---|
| **Fuga limpia** | bueno | conseguir la pistola de portal y salir abriendo un portal a la calle |
| **Salida técnica (por la ventana)** | bueno | escaparte por la ventana del baño (ruta corta, sin jefes) |
| **Se acabó la fiesta** | bueno | tirar de la alarma de incendios (`Z`) y salir en la estampida |
| **El nuevo Juan Magán** | bueno | vencer a Juan y quedarte con la mansión (`K`) |
| **Colega de fiesta** | bueno | ganarle una **batalla de perreo** |
| **El que aguanta, gana** | bueno | ganarle un **duelo de chupitos** |
| **Otra ronda** | malo | desmayarte por beber de más → vuelves a la celda |
| **K.O. técnico** | malo | perder una pelea → vuelves a la celda |

---

## El alcohol (`beber`): decisión con riesgo y probabilidad creciente

Beber es una **apuesta** que empeora cuanto más bebes. En el trago número *k*:

* **magnitud** `= 1 + (k-1)//2` → ±1 (tragos 1-2), ±2 (3-4), ±3 (5-6)...
* **P(efecto positivo)** `= limitar(0.85 − 0.075·k, entre 0.40 y 0.85)` → ≈ 78 % el
  1er trago, ≈ 48 % el 5º y un **piso del 40 %** del trago 6 en adelante
* el efecto (±magnitud) cae **al azar** en tu ataque o tu defensa, y es **acumulativo**
* a partir del **trago 5** hay probabilidad de **desmayo** (`0.13·(k−4)`) → final "Otra ronda"

El **valor esperado** del trago es positivo hasta el 4º y se vuelve negativo hacia
el 5º; el **piso del 40 %** lo mantiene *acotado* (nunca peor de −1 por trago), así
que seguir bebiendo es una apuesta viable —cara, pero viable— y no un suicidio
seguro (lo verifica `alcohol.tabla_probabilidades`, comando `--demo`).
Un par de tragos, además, dan "valor líquido": hacen falta para `colarse`
ante el guardaespaldas y para la batalla de perreo.

**El trago es de uso limitado.** Cada sala con barra tiene una reserva contada
(`datos.BARRA_SALAS`: bodega 5, comedor 3, salón 2, cuarto de Juan 4) y, cuando
se agota, hay que cargar botellas en la mochila: **Lata de Regia** (1 trago),
**Botella de tequila a medio morir** (2), **Botella de 1800 sellada** (3). El
duelo de chupitos contra Juan va aparte (lo sirve él).

---

## Arquitectura (varios archivos)

```
juegoPED/
├── main.py                 punto de entrada y flags de línea de comandos
├── autojugar.py            el juego jugado solo (defensa técnica)
├── README.md               este documento
└── juego/
    ├── __init__.py         índice del paquete
    ├── datos.py            DATOS del mundo: salas, aristas, objetos, enemigos, narrativa
    ├── ui.py               presentación en terminal (cajas, colores, barras)
    │
    ├── finales.py          los 8 FINALES + ÁRBOL DE DECISIÓN que los clasifica  [sem. 14]
    ├── alcohol.py          decisión con PROBABILIDAD y valor esperado (beber)   [sem. 4]
    │
    ├── pila.py             PILA (LIFO)                         [semana 5]
    ├── cola.py             COLA (FIFO) y COLA DE PRIORIDAD      [semana 6]
    ├── historial.py        pila aplicada: historial + backtracking + deshacer
    ├── turnos.py           cola aplicada: turnos + cola de eventos pendientes
    │
    ├── grafo.py            GRAFO: lista/matriz de adyacencia, BFS, DFS  [sem. 12-13]
    ├── mapa.py             el mapa de la mansión como grafo + puertas
    │
    ├── busqueda.py         búsqueda LINEAL y BINARIA + justificación    [semana 11]
    ├── ordenamiento.py     burbuja, selección, inserción, quicksort, mergesort [sem. 10]
    ├── recursion.py        recursividad y divide y vencerás             [semana 7]
    │
    ├── estado_mundo.py     DICCIONARIO / tabla hash de estados          [sem. 12,15]
    ├── misiones.py         ÁRBOL de misiones y dependencias             [semana 14]
    ├── ia.py               ÁRBOL DE DECISIÓN de la IA enemiga           [semana 14]
    │
    ├── inventario.py       LISTA / estructura lineal                    [semana 2]
    ├── entidades.py        modelado de datos: Pampa, Enemigo, alcohol   [semana 3]
    ├── combate.py          combate por turnos (integra cola + árbol + lista)
    │
    ├── complejidad.py      tablas de complejidad temporal y espacial    [semana 4]
    ├── benchmark.py        análisis empírico de rendimiento             [semana 16]
    │
    └── motor.py            bucle principal, menús por tecla y tour técnico
```

---

## Dónde está cada tema del temario

| Semana | Contenido | Producto pedido | Dónde está en el código |
|---|---|---|---|
| 2 | Arreglos, listas, estructuras lineales | Inventario funcional y listas de entidades | [`inventario.py`](juego/inventario.py) (`Inventario` sobre `list`), [`datos.py`](juego/datos.py) (`CATALOGO_OBJETOS`, `ENEMIGOS`) |
| 3 | Abstracción y modelado de datos | Diagramas/pseudocódigo de mecánicas | [`entidades.py`](juego/entidades.py) (`Entidad`→`Pampa`/`Enemigo`), [`datos.py`](juego/datos.py) (mundo como datos), sección *Pseudocódigo* |
| 4 | Análisis de algoritmos, conteo de operaciones, complejidad, **probabilidad** | **Tabla inicial de análisis de complejidad** | [`complejidad.py`](juego/complejidad.py) (comando `complejidad`); [`alcohol.py`](juego/alcohol.py) (probabilidad y **valor esperado** de cada trago); todas las búsquedas/ordenamientos cuentan operaciones |
| 5 | Pilas. Historial de acciones. Backtracking | **Módulo de pila para historial o retroceso** | [`pila.py`](juego/pila.py) (`Pila`), [`historial.py`](juego/historial.py) (`pila_movimientos` → `retroceder`, `pila_acciones` → `deshacer`) |
| 6 | Colas. Turnos. Eventos pendientes | **Sistema de turnos o eventos usando colas** | [`cola.py`](juego/cola.py) (`Cola`, `ColaPrioridad`), [`turnos.py`](juego/turnos.py) (`SistemaTurnos`, `ColaEventos` para veneno/sangrado/buffs) |
| 7 | Recursividad y divide y vencerás | **Algoritmo recursivo aplicado al juego** | [`recursion.py`](juego/recursion.py): `fibonacci` (acertijo de la biblioteca), `fibonacci_memo`, `potencia` rápida, mergesort/quicksort, `busqueda_binaria_recursiva`, DFS recursivo |
| 10 | Ordenamiento: burbuja, selección, inserción, quicksort, mergesort | **Ranking ordenado y comparación de algoritmos** | [`ordenamiento.py`](juego/ordenamiento.py) (5 algoritmos + `comparar`), comando `ranking`, orden de iniciativa en [`turnos.py`](juego/turnos.py) |
| 11 | Búsqueda lineal, binaria, criterios de eficiencia | **Módulo de búsqueda y justificación técnica** | [`busqueda.py`](juego/busqueda.py) (`JUSTIFICACION`), comandos `buscar` y `examinar` |
| 12 | Grafos: nodos, aristas, matriz/lista de adyacencia | **Mapa del juego representado como grafo** | [`grafo.py`](juego/grafo.py) (`Grafo`, `matriz_adyacencia`); [`mapa.py`](juego/mapa.py) construye la mansión desde `datos.ARISTAS`; comando `mapa` |
| 12 | Tablas hash / diccionarios | **Acceso eficiente a estados del juego** | [`estado_mundo.py`](juego/estado_mundo.py) (`EstadoMundo` sobre `dict`); las banderas que abren puertas y deciden el final; comando `estado` |
| 13 | BFS y DFS. Recorridos sobre grafos | **Algoritmo BFS/DFS integrado al juego** | [`grafo.py`](juego/grafo.py) (`bfs`, `camino_mas_corto`, `dfs_iterativo`, `dfs_recursivo`); comandos `camino` (BFS) y `explorar` (DFS) |
| 14 | Árboles, árboles de decisión y dependencias | **Árbol de misiones o desbloqueos** | [`misiones.py`](juego/misiones.py) (`NodoMision`, post-orden recursivo); [`ia.py`](juego/ia.py) (`NodoDecision` de la IA enemiga); [`finales.py`](juego/finales.py) (**árbol de decisión que elige cuál de los 8 finales**) |
| 15 | Diccionario de estados del mundo | — | [`estado_mundo.py`](juego/estado_mundo.py); `guardar`/`cargar` serializan ese diccionario a JSON |
| 16 | Análisis empírico, medición de tiempo, comparación de estructuras | **Informe de experimentación y métricas** | [`benchmark.py`](juego/benchmark.py) — comando `benchmark` / `py main.py --benchmark` |
| 17 | Integración, depuración, optimización, defensa | **Juego funcional, código, métricas y defensa** | Todo el proyecto + `--demo` |

---

## Tabla de análisis de complejidad (resumen)

`n` = tamaño de la entrada · `V` = salas · `E` = puertas · `h` = altura del árbol

### Estructuras de datos

| Estructura | Operación | Mejor | Promedio | Peor | Espacio |
|---|---|---|---|---|---|
| Lista (inventario) | acceso por índice | O(1) | O(1) | O(1) | O(n) |
| Lista (inventario) | buscar por nombre (lineal) | O(1) | O(n) | O(n) | O(1) |
| Lista (inventario) | insertar al final | O(1) | O(1) | O(1) | O(1) |
| Lista (inventario) | eliminar por valor | O(n) | O(n) | O(n) | O(1) |
| Pila (historial) | apilar / desapilar / cima | O(1) | O(1) | O(1) | O(n) |
| Cola (turnos) | encolar / desencolar | O(1) | O(1) | O(1) | O(n) |
| Cola de prioridad (heap) | encolar / desencolar | O(1) | O(log n) | O(log n) | O(n) |
| Diccionario (estado del mundo) | obtener / establecer / `in` | O(1) | O(1) | O(n) | O(n) |
| Grafo — lista de adyacencia | vecinos de un nodo | O(1) | O(1) | O(1) | O(V+E) |
| Grafo — matriz de adyacencia | ¿hay arista a–b? | O(1) | O(1) | O(1) | O(V²) |
| Árbol de misiones | recorrer / evaluar | O(n) | O(n) | O(n) | O(h) |

### Algoritmos

| Algoritmo | Mejor | Promedio | Peor | Espacio | Uso en el juego |
|---|---|---|---|---|---|
| Búsqueda lineal | O(1) | O(n) | O(n) | O(1) | inventario |
| Búsqueda binaria (iter. y rec.) | O(1) | O(log n) | O(log n) | O(1) / O(log n) | catálogo de objetos |
| BFS | O(V+E) | O(V+E) | O(V+E) | O(V) | camino más corto a la salida |
| DFS | O(V+E) | O(V+E) | O(V+E) | O(V) | explorar toda la mansión |
| Ordenamiento burbuja | O(n) | O(n²) | O(n²) | O(1) | comparativa |
| Ordenamiento selección | O(n²) | O(n²) | O(n²) | O(1) | comparativa |
| Ordenamiento inserción | O(n) | O(n²) | O(n²) | O(1) | orden de iniciativa (lista casi ordenada) |
| Quicksort | O(n log n) | O(n log n) | O(n²) | O(log n) | inventario, ranking |
| Mergesort | O(n log n) | O(n log n) | O(n log n) | O(n) | ranking estable, catálogo |
| Fibonacci recursivo | O(2ⁿ) | O(2ⁿ) | O(2ⁿ) | O(n) | acertijo de la biblioteca |
| Fibonacci con memoización | O(n) | O(n) | O(n) | O(n) | versión optimizada (defensa) |
| Exponenciación rápida | O(log n) | O(log n) | O(log n) | O(log n) | ejemplo divide y vencerás |
| Torres de Hanói | O(2ⁿ) | O(2ⁿ) | O(2ⁿ) | O(n) | ejemplo recursivo |

El comando `benchmark` **mide empíricamente** varias de estas filas y muestra
que la curva real coincide con el Big-O (p. ej. `dict` vs lista de pares,
lineal vs binaria, `deque` vs `list.pop(0)`).

---

## Pseudocódigo de las mecánicas principales

### Bucle principal

```
describir sala inicial
mientras el juego NO haya terminado:
    si hay un enemigo -> mostrar el menú de enemigo (1 pelear, 2/3 esquivar, 9 irse)
    si no             -> mostrar el menú de sala (objetos A..H, salidas 1..9, I/M/T/P...)
    leer UNA tecla y ejecutar la acción:
        salida N   -> validar puerta en el GRAFO ; apilar sala en la PILA
                      si el destino es una SALIDA de la casa -> disparar un FINAL
        pelear     -> COMBATE por turnos ; si Pampa pierde -> final "K.O. técnico"
        agarrar    -> BÚSQUEDA LINEAL en la LISTA de objetos de la sala
        beber (V)  -> ver abajo ; si Pampa se desmaya -> final "Otra ronda"
        retar/bailar/alarma/quedarse -> disparar un FINAL
        mapa (M)   -> plano 2D del piso ; con el plano: BFS y DFS
        ...
al terminar:
    contexto <- {salida, juan, se_queda, ko, desmayo}      # DICCIONARIO
    final <- recorrer el ÁRBOL DE DECISIÓN de finales.py con ese contexto
    mostrar el FINAL + cuántos de los 8 llevas descubiertos
```

### Alcohol (`beber`): decisión con probabilidad creciente

```
función beber(pampa):
    pampa.tragos <- pampa.tragos + 1
    k <- pampa.tragos
    magnitud   <- 1 + (k - 1) // 2                    # ±1, ±2, ±3, ...
    p_positivo <- limitar(0.85 - 0.075*k, entre 0.40 y 0.85)   # piso 40%
    estadística <- elegir_al_azar("ataque", "defensa")
    signo <- (+1 con probabilidad p_positivo, si no -1)
    aplicar  signo * magnitud  a esa estadística de pampa (acumulativo)
    si k >= 5 y azar() < 0.13*(k-4):
        return DESMAYO            # -> final malo "Otra ronda"
```

### Clasificar el final (árbol de decisión, `finales.py`)

```
función clasificar(contexto):
    si contexto.ko:                 -> "K.O. técnico"
    si contexto.desmayo:            -> "Otra ronda"
    si contexto.salida == alarma:   -> "Se acabó la fiesta"
    si contexto.salida == ventana:  -> "Salida técnica (por la ventana)"
    si contexto.juan == duelo:      -> "El que aguanta, gana"
    si contexto.juan == baile:      -> "Colega de fiesta"
    si contexto.se_queda:           -> "El nuevo Juan Magán"
    si no:                          -> "Fuga limpia"
```

### Movimiento con backtracking (Pila)

```
función ir(destino):
    si arista(sala_actual, destino) está cerrada:
        avisar del requisito ; return
    PILA_movimientos.apilar(sala_actual)
    sala_actual <- destino
    describir(sala_actual)

función retroceder():
    si PILA_movimientos está vacía: return
    sala_actual <- PILA_movimientos.desapilar()
    describir(sala_actual)
```

### Combate por turnos (Cola + Cola de eventos + Árbol de decisión)

```
función combate(pampa, enemigos):
    ronda <- 1
    COLA_turnos <- ordenar_por_iniciativa(pampa + enemigos)   # ORDENAMIENTO
    mientras pampa.vivo y algún enemigo.vivo:
        si COLA_turnos está vacía:                            # fin de ronda
            para cada evento en COLA_eventos:                 # veneno, sangrado, buffs
                evento.turnos -= 1
                si evento.turnos == 0: ejecutar(evento)
            COLA_turnos <- ordenar_por_iniciativa(vivos)
            ronda += 1
        actor <- COLA_turnos.desencolar()
        si actor está aturdido: continuar
        si actor es pampa: pedir acción al jugador
        si no: acción <- recorrer ÁRBOL_DE_DECISIÓN(actor, pampa, ronda)
        aplicar acción
        COLA_turnos.encolar(actor)   # vuelve al final si sigue vivo
    devolver "victoria" si pampa.vivo si no "derrota"
```

### Camino más corto a la salida (BFS)

```
función camino_mas_corto(inicio, fin):
    COLA <- [inicio] ; previo[inicio] <- nulo
    mientras COLA no vacía:
        actual <- COLA.desencolar()
        para cada vecino de actual (que no sea puerta cerrada):
            si vecino no visitado:
                previo[vecino] <- actual
                si vecino == fin: return reconstruir(previo, fin)
                COLA.encolar(vecino)
    return "no hay camino"
```

### Árbol de misiones (evaluación recursiva post-orden)

```
función completada(nodo, estado):
    si nodo tiene hijos:
        devolver Y_lógico( completada(h, estado) para cada hijo h )   # post-orden
    si no:
        devolver nodo.condicion(estado)
```

---

## Créditos

Personajes: **Pampa** (protagonista) y **Juan Magán** (antagonista, su enemigo)
con su tigre. Ambientado en El Salvador; la disco se llama **Superb**.
Proyecto académico, sin ánimo de lucro.
