[↩ Volver a los algoritmos genéticos](../README.md)

# Sakura Queens · Evolución genética 3D

N-Reinas con **algoritmos genéticos en Python** y una escena anime original
en Three.js. Cada generación se representa con reinas que se elevan,
cambian de columna y aterrizan. El proyecto funciona sin internet ni pip.

## Ejecutar y probar

Requiere Python 3.10 o posterior y un navegador moderno con WebGL:

```powershell
python app.py
```

Abre http://127.0.0.1:8000. Para otro puerto: `python app.py --port 8001`.
Detén el servidor con Ctrl+C. No abras el HTML directamente: necesita la API.

```powershell
python -m unittest discover -s tests -v
node --test tests/test_motion.mjs
```

Node solo es necesario para las pruebas de las trayectorias, no para usar la app.
Three.js, OrbitControls, las fuentes y la ilustración ya se incluyen localmente.

## Primero entendamos el problema

Hay que colocar N reinas en N × N casillas sin compartir filas, columnas ni
diagonales. El problema sigue siendo el mismo, pero la búsqueda ahora es genética.

| Entrada | Proceso | Salida |
| --- | --- | --- |
| N y parámetros genéticos | Crear, evaluar, seleccionar, cruzar y mutar poblaciones | Una solución o el mejor candidato y un historial de generaciones |

Una búsqueda genética no enumera todas las soluciones ni garantiza encontrar
una en el presupuesto elegido. Cero conflictos demuestra que un candidato es
válido. Agotar tiempo o generaciones **no demuestra imposibilidad**.
N = 1 es trivial; N = 2 y N = 3 son casos matemáticos imposibles conocidos.

## Qué significa «N sin máximo fijo»

El campo permite escribir un entero positivo, por ejemplo 16, 32, 100 o 1000.
No hay una comprobación como `n <= 12`. Sí existen límites físicos:

- Tiempo y generaciones: ajustables en «Configurar evolución».
- Memoria: se estima antes de reservar la población. El presupuesto por
  búsqueda es de 256 MB, configurable en `GeneticConfig.memory_budget_mb`.
  Una combinación excesiva de N y población devuelve un mensaje claro.
- La población es ajustable entre 4 y 1000; las generaciones entre 1 y
  100000; la búsqueda entre 1 y 120 segundos desde la interfaz.
- El navegador acepta enteros exactos dentro del rango seguro de JavaScript.
- A partir de 25 reinas el tablero usa una sola superficie con patrón;
  a partir de 49, las piezas comparten geometría mediante instancias de GPU.
- El historial conserva hasta 4000 muestras y un millón de valores de posición.
  Si los supera, reduce la frecuencia de muestreo e indica el resumen.
  Siempre conserva el inicio y el último candidato. En ejecuciones normales
  se guarda el campeón de **cada** generación.
- La vista 2D alternativa muestra una ventana de hasta 16 × 16; en Desafío
  permite colocar reinas de cualquier fila/columna mediante coordenadas.

No significa que un equipo pueda resolver o dibujar un N infinito.
El algoritmo tiene un costo por generación que crece con N y la población.

## Datos: el cromosoma

```python
genes = [1, 3, 0, 2]
```

El índice es la fila; el valor, la columna. Los índices empiezan en cero.
El tablero anterior es una solución válida de cuatro reinas.

Un **cromosoma** es una solución candidata codificada como datos. Usamos una
**permutación**: todos los valores de 0 a N − 1, sin repetir. Así ya hay una
reina por fila y columna; el algoritmo solo necesita reducir los conflictos
diagonales. Se admiten conflictos mientras evoluciona la población.

## Aptitud: cómo evaluamos un tablero

Dos reinas comparten diagonal si tienen el mismo `fila - columna` o el mismo
`fila + columna`. Contamos los **pares** que se atacan, no solo las reinas:

```text
aptitud = 1 / (1 + pares_en_conflicto)
```

Si hay 3 conflictos, la aptitud es 0.25. Si no hay ninguno, es 1.
Una diagonal con c reinas contiene `c * (c - 1) / 2` pares en conflicto.
La evaluación recorre las reinas en O(N), sin revisar las N² casillas.

## Lógica paso a paso del algoritmo genético

1. **Población:** crea varios cromosomas barajados al azar.
2. **Evaluación:** cuenta los conflictos de cada cromosoma.
3. **Selección por torneo:** elige tres candidatos aleatorios; el de menos
   conflictos gana la oportunidad de ser padre. Se repite para el otro padre.
4. **Cruce de orden:** copia un fragmento del primer padre y completa los
   espacios con las columnas del segundo que todavía no aparecen.
5. **Mutación:** con cierta probabilidad, intercambia dos columnas del hijo.
   La versión guiada elige una reina amenazada y compara hasta 14 posibles
   intercambios; también se permiten mutaciones puramente aleatorias.
6. **Elitismo:** los dos mejores individuos sobreviven. La mejor puntuación
   conocida nunca empeora, aunque cambie el campeón entre empates.
7. **Diversidad:** aumenta la mutación cuando hay estancamiento y, después de
   varias generaciones estancadas, introduce algunos cromosomas barajados.
8. Detente al hallar cero conflictos o alcanzar el presupuesto.

La mutación guiada es un operador dentro del algoritmo genético. No se usa
backtracking, enumeración exhaustiva, una fórmula de construcción ni un
solver externo que sustituya la evolución.

### Pseudocódigo

```text
población = crear permutaciones aleatorias
evaluar población
registrar campeón inicial (generación 0)
mientras campeón tenga conflictos y quede presupuesto:
    nueva = copias de los 2 mejores
    mientras nueva no esté completa y quede tiempo:
        padre_a = selección por torneo
        padre_b = selección por torneo
        hijo = cruce de orden(padre_a, padre_b)
        aplicar mutación por intercambio al hijo
        evaluar hijo y añadirlo a nueva
    población = ordenar nueva por conflictos
    registrar campeón de esta generación
devolver campeón y motivo de finalización
```

## Explicación de `solver.py`

- `GeneticConfig`: agrupa población, generaciones, mutación, tiempo, semilla
  y memoria. Un `dataclass` crea una estructura con campos con nombre.
- `validate`: comprueba entradas y presupuesto estimado antes de reservar memoria.
- `Random(seed)`: generador aleatorio propio. Una semilla fija permite repetir
  los cromosomas si no se interrumpe por tiempo.
- `diagonal_counts`: cuenta diagonales ocupadas y pares que se atacan.
- `ordered_crossover`: produce un hijo sin duplicar columnas ni modificar padres.
- `swap_delta`: calcula cómo cambiarían los conflictos al intercambiar dos
  reinas, examinando solo sus diagonales. Evita reevaluar N reinas por intento.
- `mutate`: cambia un hijo por intercambio, con la probabilidad configurada.
- `evolve_n_queens`: ejecuta la evolución y entrega eventos con `yield`.
  Una función con `yield` es un **generador**: produce datos poco a poco.
- `solve_n_queens`: recoge esos eventos para pruebas o clientes que prefieran
  una sola respuesta JSON. La interfaz utiliza la variante transmitida.

## Prueba de escritorio de aptitud y mutación

Considera el candidato `[0, 2, 1, 3]`:

```text
♛ · · ·
· · ♛ ·
· ♛ · ·
· · · ♛
```

Hay dos pares que comparten diagonal: las filas 0 y 3, y las filas 1 y 2.
Por tanto, `conflictos = 2`, `aptitud = 1 / 3`.
Si una mutación intercambia los valores de las filas 0 y 2, resulta
`[1, 2, 0, 3]`: tiene un conflicto, por lo que su aptitud sube a `1 / 2`.
Una mutación puede mejorar, mantener o empeorar un candidato; la selección
y el elitismo actúan sobre la población completa.

Para observar una ejecución real: selecciona N = 16 y semilla 42, deja los
parámetros predeterminados y reproduce el historial. Cada muestra indica su
generación, conflictos, aptitud y número de individuos evaluados.

## Animación: de un cromosoma a otro

La fila identifica la misma pieza entre generaciones. En vez de borrar las
reinas, conservamos su posición y calculamos una trayectoria:

1. Primer 22 %: se eleva sin cambiar de casilla.
2. Del 22 % al 78 %: cambia de columna a una altura constante.
3. Último 22 %: aterriza suavemente en la nueva casilla.

`sampleMotion` en `static/motion.js` devuelve la posición intermedia.
`smoothstep` suaviza la aceleración al inicio y al final.
`scene.js` actualiza la escena en cada fotograma. La reproducción espera a
que acaben las piezas antes de pasar a la siguiente generación. Al pausar,
la animación queda congelada; reanudar continúa desde ese punto.

Se anima el mejor individuo de cada generación, no todos los hijos de toda
la población. Dos campeones idénticos no necesitan movimiento.
Los cambios no representan jugadas legales de ajedrez.
Se respeta la preferencia del sistema de reducir movimiento.

## Interfaz y API

- **Explorar:** comienza en el último candidato; las flechas recorren generaciones.
- **Paso a paso:** comienza en la población inicial. Reproducir, pausar, avanzar,
  reiniciar y cambiar velocidad permiten estudiar la evolución.
- **Ver resultado:** salta al último candidato sin reproducir todo el historial.
- **Desafío:** coloca tus propias reinas. Flechas y Enter funcionan sobre el
  tablero enfocado; también se puede usar el ratón.
- **Detener búsqueda:** interrumpe la petición y conserva el último candidato recibido.

```text
GET /api/evolve?n=32&population=80&generations=2000&mutation=0.65&seconds=15&seed=42
```

Python transmite JSON delimitado por saltos de línea (**NDJSON**): un evento
por generación y un resultado final. JavaScript usa `fetch`, `ReadableStream`
y `TextDecoder` para recibirlo; `AbortController` permite cancelar la petición.
El servidor deja de calcular al detectar que la conexión se cerró.
`/api/solve` entrega una sola respuesta y `/api/validate` solo valida parámetros.
Cada búsqueda es nueva: no hay caché de resultados aleatorios.

La duración es el tiempo transcurrido en Python, incluida la emisión de eventos;
no cuenta la posterior reproducción visual. Los estados son `solved`,
`impossible`, `time_limit`, `generation_limit` y, en la interfaz, `cancelled`.

## Archivos y pruebas

| Archivo | Responsabilidad |
| --- | --- |
| `solver.py` | Algoritmo genético y aptitud |
| `app.py` | Servidor y API, sin dependencias externas |
| `static/app.js` | Historial, controles, transmisión y desafío |
| `static/scene.js` | Tablero, piezas, cámara y animación en Three.js |
| `static/motion.js` | Trayectoria en tres fases, independiente del dibujo |
| `tests/test_solver.py` | Permutaciones, cruces, mutación, aptitud, elitismo, semillas y presupuestos |
| `tests/test_server.py` | API, transmisión y validación de N grande |
| `tests/test_motion.mjs` | Elevación, desplazamiento, aterrizaje e interrupción |

Las pruebas verifican soluciones con semilla fija para N = 4, 8, 16, 32, 64
y 100. Esto comprueba esas ejecuciones; no garantiza todos los N y semillas.

## Errores comunes y práctica

- No confundas probabilidad de mutación con el porcentaje de genes alterados:
  aquí es la probabilidad de aplicar el operador a un hijo.
- Un cruce ingenuo puede duplicar columnas. El cruce de orden lo evita.
- Un mejor candidato con conflictos todavía no es una solución.
- Comparar dos búsquedas requiere fijar semilla y parámetros; un límite de
  tiempo puede interrumpirlas en generaciones distintas según el equipo.
- Un tablero grande tiene casillas pequeñas; acerca la cámara con la rueda.
- Si el puerto está ocupado, utiliza otro con `--port`.

Practica: compara mutación 20 % y 80 % con N = 32, semilla 42 y los mismos
límites. Anota generaciones y conflictos finales. Después cambia la población.

Conceptos clave: permutaciones, población, cromosoma, aptitud, selección,
cruce, mutación, elitismo, aleatoriedad reproducible y animación interpolada.

Prompt mejorado:

> Sustituye el solver por un algoritmo genético con selección, cruce, mutación
> y elitismo en Python. Permite escribir N sin un máximo fijo de 12 y controla
> los recursos mediante presupuestos explícitos. En Three.js, conserva cada
> pieza y anímala elevándose, desplazándose y aterrizando entre generaciones.
> Incluye reproducción, pausa, semilla, parámetros, historial real, pruebas y
> explicación para un estudiante. Distingue solución, mejor intento e imposibilidad.

## Créditos

Three.js y OrbitControls 0.170.0: MIT, licencia en `static/vendor/`.
DM Sans y Manrope: SIL Open Font License, licencias en `static/assets/`.
La ilustración original se conserva; su prompt está en `static/assets/ART.md`.
