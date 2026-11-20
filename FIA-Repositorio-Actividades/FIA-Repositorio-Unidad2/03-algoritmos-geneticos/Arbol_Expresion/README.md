[↩ Volver a los algoritmos genéticos](../README.md)

# Arboria · Expression Lab

Un laboratorio de árboles de expresión con **Python + Flask** y **Three.js**. Escribe una fórmula, explora su estructura en 2D o 3D y observa cómo se calcula cada nodo.

**Versión 2:** evaluación protegida configurable, clase `ExpressionTree` para programación genética y curvas de resultados en un dominio. Consulta [GENETICA.md](GENETICA.md) para las reglas, la API de Python y ejemplos completos.

**Versión 3:** generación libre de fórmulas desde una biblioteca de once operaciones con aridades fijas, selección de operaciones, altura máxima, semillas y muestreo por paso. Al abrir la aplicación se genera una primera fórmula automáticamente. Consulta [GENERADOR.md](GENERADOR.md) para entender el algoritmo y reutilizarlo desde Python.

**Versión 4:** hasta 100,001 muestras por curva, comparación con función objetivo o CSV, MSE/RMSE/NMSE/R² y simplificación conservadora de constantes. El botón «Cargar ejercicio del coseno» prepara el dominio [-10, 10], paso 0.001 y una candidata de ejemplo. Consulta [COMPARACION.md](COMPARACION.md) para aprender el flujo y sus límites.

## Ejecutar

Necesitas Python 3.10 o superior y Node.js con npm. En esta carpeta, desde PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm ci --ignore-scripts
npm run vendor
.\.venv\Scripts\python.exe app.py
```

Abre **http://127.0.0.1:5000**. Si el puerto está ocupado:

```powershell
.\.venv\Scripts\python.exe app.py --port 5001
```

No necesitas activar el entorno virtual: usamos su ejecutable directamente. Si ya tienes Flask instalado y `static/vendor` está preparado, basta con `python app.py`. Detén el servidor con `Ctrl+C`.

Three.js se sirve desde archivos locales después de `npm run vendor`. Las tipografías se solicitan a Google Fonts; si no tienes Internet se usan las fuentes del sistema y la aplicación sigue funcionando. No hay servicios externos de interpretación ni claves API.

## Qué puedes hacer

- Escribir expresiones y generarlas con el botón o `Ctrl+Enter`.
- Insertar raíces, potencias, funciones, π y paréntesis en la posición del cursor. Si seleccionas texto y pulsas raíz, se convierte en `sqrt(texto)`.
- Cambiar variables y recalcular los valores sin reconstruir la escena.
- Explorar los nodos con ratón o teclado y leer su descripción y valor.
- Desplazar y ampliar la vista 2D; girar en 3D y desplazar con el botón derecho.
- Animar preorden, inorden y postorden; pausar, reiniciar o avanzar de uno en uno.
- Descargar el árbol visible como PNG.
- Cargar ejemplos y consultar la guía integrada.
- Elegir evaluación protegida o estricta, ajustar epsilon y consultar las correcciones por nodo.
- Graficar la expresión sobre un dominio, comparar hasta cuatro fórmulas y exportar todos los resultados a CSV.
- Generar fórmulas sin escribirlas: elegir biblioteca, altura de 1 a 12 niveles, variable, constantes y semilla opcional. El mismo botón actualiza árbol y curva usando el dominio configurado.

La animación respeta la preferencia del sistema de reducir movimiento. La vista gráfica requiere un navegador con **WebGL 2**. Si no está disponible, se conservan la interpretación, la evaluación, el inspector y la secuencia accesible de recorridos.

## Gramática soportada

| Elemento | Ejemplos y reglas |
| --- | --- |
| Números | `3`, `1.5`, `.25`, `1.2e3`; usa punto decimal |
| Variables | `x`, `y`, `velocidad`, `x2`; distingue mayúsculas de minúsculas |
| Constantes | `pi`, `π`, `e`, `tau`, `τ` |
| Operadores binarios | `+`, `-`, `*`, `/`, `%`, `^`, `**` |
| Signos unarios | `-x`, `+x`, `--3` |
| Factorial | `5!`; argumento entero entre 0 y 170, sujeto al límite del resultado |
| Paréntesis | `(2+3)*4` |
| Multiplicación implícita | `2x`, `2(x+1)`, `(x+1)(x-1)`, `2sin(x)` |
| Funciones | `sqrt`, `root`, `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `ln`, `log`, `log10`, `exp`, `abs`, `floor`, `ceil`, `round`, `min`, `max`, `pow`, `hypot` |
| Alias | `√(x)`, `raiz(x)`, `raíz(x)`, `sen(x)`, `tg(x)` |

Convenciones que conviene conocer:

- Las funciones requieren paréntesis: `sqrt(9)`, no `sqrt 9`.
- `root(27, 3)` es la raíz cúbica de 27; `root(-27, 3)` produce −3.
- Los ángulos están en **radianes**: `sin(pi/2)` produce 1.
- `ln(x)` y `log(x)` usan base e. `log(x, b)` acepta otra base; `log10(x)` usa base 10.
- `2^3^2` equivale a `2^(3^2)` y produce 512. `-2^2` produce −4.
- `xy` es **una variable**, no el producto de x por y. Escribe `x*y` para ese producto.
- La multiplicación implícita tiene la misma prioridad que `*`: `6/2(1+2)` se interpreta como `(6/2)*(1+2)`. Usa paréntesis para expresar otra intención.
- `round(x)` usa el redondeo de Python: en un empate exacto elige el entero par.
- `%` usa el residuo de Python, con el signo del divisor.
- `min`, `max` e `hypot` reciben de 2 a 12 argumentos.
- Los nombres de funciones y constantes se reconocen sin distinguir mayúsculas. Esos nombres están reservados; las demás variables sí distinguen mayúsculas.

El alcance es un **intérprete de expresiones matemáticas reales**, no un intérprete completo de Python ni un sistema de álgebra simbólica: no resuelve ecuaciones, derivadas, integrales o matrices. Admite hasta 512 caracteres, 256 símbolos, 160 nodos y 48 niveles. En modo estricto, los valores deben ser finitos y no superar ±1e100; los exponentes se limitan a ±1000. En modo protegido, se aplican las convenciones documentadas en `GENETICA.md` y un límite por nodo configurable (±1e12 por defecto). Las entradas de variables deben ser números finitos dentro de ±1e100 en ambos modos. Los límites evitan cálculos o dibujos excesivos.

## Arquitectura

```text
Expresión escrita en el navegador
        ↓ POST /api/parse
Python: tokenizar → analizar → construir árbol → evaluar
        ↓ JSON con árbol, valores, recorridos y estadísticas
JavaScript: organizar nodos → crear escena Three.js → animar
```

| Archivo | Responsabilidad |
| --- | --- |
| `app.py` | Servidor Flask, archivos de la interfaz y API |
| `interpreter.py` | Tokenizador, analizador Pratt, nodos, evaluación y recorridos |
| `arithmetic.py` | Política y operaciones protegidas, sin dependencias web |
| `operations.py` | Biblioteca de once operaciones del generador y sus aridades |
| `generator.py` | Generación libre de un ExpressionTree y su curva |
| `expression_tree.py` | Individuos, evaluación por lotes, fitness, cruce, mutación y serialización |
| `sampling.py` | Muestreo de curvas con extremos incluidos y detección de polos comunes |
| `static/index.html` | Estructura y controles accesibles de la página |
| `static/styles.css` | Diseño visual y distribución adaptable |
| `static/app.js` | Eventos, solicitudes a Python y estado de la aplicación |
| `static/scene.js` | Distribución del árbol, cámara, objetos 3D y animaciones |
| `static/plot.js` | Gráfica SVG, inspección de muestras, tabla y exportación CSV |
| `static/analysis.css` | Estilos de políticas y curvas de resultados |
| `examples/genetic_demo.py` | Regresión simbólica con población, torneo, elitismo, cruce y mutación |
| `scripts/vendor.mjs` | Preparación de módulos locales de Three.js |
| `tests/test_interpreter.py` | Pruebas de reglas matemáticas y API |
| `tests/test_generator.py` | Pruebas de generación, altura, aridad, semillas y tamaño de paso |
| `APRENDE.md` | Explicación paso a paso y ejercicios |

La entrada se analiza con una gramática propia: **no se utiliza `eval` ni `exec`**. Las funciones disponibles están en una lista explícita. En modo estricto, un error de dominio como `sqrt(-1)` no elimina el árbol: cada nodo conserva su error y las ramas independientes conservan sus valores. En modo protegido, ese caso usa `sqrt(abs(-1))` y el nodo registra la corrección. La interfaz comienza en modo protegido; la API de Python y las peticiones sin política mantienen el modo estricto por compatibilidad.

## Agregar una función

En `interpreter.py`, registra una función y cuántos argumentos acepta. Por ejemplo, para añadir el doble:

```python
def doble(numero):
    return numero * 2

# Añade esta entrada dentro de FUNCTIONS:
"doble": (doble, 1, 1),
```

El primer `1` es el mínimo de argumentos; el segundo es el máximo. Reinicia Python y ya podrás escribir `doble(8)` y obtener un nodo de función con resultado 16. El catálogo de la guía se actualiza desde Python.

Para darle una explicación específica en el inspector, añade a `DETAILS`, en `static/app.js`:

```javascript
doble: ['Doble', 'Multiplica el valor de su hijo por dos.'],
```

Para añadir otro nombre equivalente, usa `ALIASES` en Python, por ejemplo `"doblar": "doble"`. No necesitas modificar el analizador.

## Pruebas

```powershell
python -m unittest discover -s tests -v
node --check static/app.js
node --check static/scene.js
```

Las pruebas cubren prioridades, potencias, signos, estructura, alias, funciones, multiplicación implícita, errores matemáticos, entradas inválidas, límites, operaciones protegidas, muestreo, serialización y operadores genéticos. Ejecuta la suite para consultar el total actualizado.

Prueba manual recomendada: carga `sqrt(x^2+y^2)`, cambia x a 6 e y a 8 y comprueba resultado 10; recorre en postorden; cambia a 3D; genera `sqrt(-1)` en modo protegido y verifica valor 1 y corrección; cambia a estricto y verifica el error; genera `sqrt(2+` y verifica la posición; grafica `1/x` en [-1,1] con 201 muestras y compara ambos modos; descarga PNG y CSV.

## Referencias

- [Instalación oficial de Three.js](https://threejs.org/manual/pages/installation.html): módulos ES e import maps.
- [OrbitControls](https://threejs.org/docs/pages/OrbitControls.html): controles de cámara.
- [Archivos estáticos de Flask](https://flask.palletsprojects.com/en/stable/tutorial/static/): entrega de los archivos del navegador.
