# Aritmética protegida, programación genética y curvas

**Versión 3:** la interfaz incorpora ahora un generador libre con biblioteca explícita de once operaciones, altura máxima y semillas, además del muestreo por tamaño de paso. La explicación de esos controles y su API está en [GENERADOR.md](GENERADOR.md). Los módulos de esta guía siguen disponibles.

## Primero entendamos las tres mejoras

Una expresión aleatoria puede contener `1/0`, `sqrt(-9)` o `ln(0)`. Un algoritmo que compara cientos de expresiones necesita una regla consistente para esos casos. A esto se le llama **aritmética protegida**. No hay una convención universal: cada sistema elige y documenta sus reglas.

La programación genética representa cada candidato como un árbol. El algoritmo genético selecciona candidatos, cruza partes de sus árboles y los muta. El núcleo ahora puede trabajar con esos árboles sin Flask ni navegador.

La gráfica requiere otro proceso: evaluar la misma expresión muchas veces, cambiando una variable dentro de un dominio y manteniendo fijas las demás.

## 1. Reglas numéricas

La interfaz comienza en modo **protegido**. Puedes cambiar a **estricto** en la barra de evaluación.

| Operación | Modo protegido |
| --- | --- |
| `a / b`, `a % b` | Si `abs(b) < epsilon`, usa `copysign(epsilon, b)`; conserva el signo, incluso el de −0.0 |
| `sqrt(x)` | Usa `sqrt(abs(x))` |
| `root(x,n)` | Conserva las raíces impares negativas; en otros casos negativos usa abs(x). El índice cercano a cero usa epsilon y el exponente recíproco se limita a ±1000 |
| `ln`, `log`, `log10` | Argumento `max(abs(x), epsilon)`; la base también debe ser positiva y, si queda cerca de 1, pasa a `1+epsilon` |
| Potencias | Base negativa con exponente fraccionario: abs(base). Base cero con exponente negativo: epsilon. Exponente entre −1000 y 1000 |
| `asin`, `acos` | Argumento limitado a [−1,1] |
| `exp`, `sinh`, `cosh` | Argumentos limitados según el máximo configurado para evitar desbordamientos |
| Factorial | Redondea abs(x) a entero y lo limita a 170; luego limita el resultado |
| Todos los nodos | El valor se satura al intervalo [−max_value, max_value], incluyendo números y variables usados como hojas |

Valores por defecto: `epsilon=1e-9` y `max_value=1e12`. Epsilon admite [1e-15, 0.01]; el máximo admite [1, 1e100]. Las variables de entrada deben ser finitas y estar en ±1e100.

Ejemplos:

```text
1 / 0       → 1 / 0.000000001 ≈ 1 000 000 000
sqrt(-9)    → sqrt(abs(-9))   = 3
root(-27,3) → -3               (no necesita corrección)
ln(0)       → ln(0.000000001) ≈ -20.72326584
exp(10000)  → resultado limitado, aproximadamente 1e12
```

Estas son **convenciones computacionales**, no igualdades de la aritmética real: matemáticamente, `1/0` sigue sin estar definido y `sqrt(-9)` no es un número real. No se están calculando números complejos. `sqrt(abs(x))` se elige porque permite mantener resultados reales para candidatos genéticos.

Cada nodo guarda `warnings`. La respuesta general agrupa los nodos modificados en `corrections`. La interfaz muestra ese registro y el inspector explica la modificación local. Las variables faltantes y los errores sintácticos conservan sus errores; no se inventan datos de entrada.

El modo estricto conserva los errores y límites anteriores. La API de Python y las peticiones HTTP sin `policy` siguen siendo estrictas por compatibilidad.

## 2. La clase ExpressionTree

Archivos independientes de la web: `arithmetic.py`, `interpreter.py`, `expression_tree.py` y `sampling.py`. Solo necesitan la biblioteca estándar de Python. El árbol se analiza una vez y se reutiliza para cada evaluación.

```python
from arithmetic import EvaluationPolicy
from expression_tree import ExpressionTree

policy = EvaluationPolicy(mode="protected", epsilon=1e-9, max_value=1e12)
tree = ExpressionTree("sqrt(x) + 1/y", policy=policy)

print(tree.evaluate({"x": -9, "y": 0}))  # Aproximadamente 1e9 + 3
print(tree.report({"x": -9, "y": 0})["corrections"])

rows = [{"x": -4, "y": 2}, {"x": 0, "y": 2}, {"x": 9, "y": 2}]
print(tree.predict(rows))  # [2.5, 0.5, 3.5]
```

`EvaluationPolicy` es un objeto que reúne las reglas. `ExpressionTree` representa un individuo. `evaluate` calcula una fila de variables; `predict` calcula muchas. `report` devuelve árbol, valores, correcciones y estadísticas.

`evaluate` lanza `ExpressionError` si no puede obtener un resultado. `predict` devuelve `None` para una fila inválida, de modo que puedas penalizarla en lugar de interrumpir toda la población.

### Fitness: medir qué candidato es mejor

Una función de **fitness** mide la calidad de una solución. Aquí usamos el **error cuadrático medio**, MSE: promedio de `(predicción − objetivo)^2`. Un error menor significa un candidato mejor; cero indica coincidencia exacta sobre esos datos.

```python
candidate = ExpressionTree("x^2 + x + 1", policy)
rows = [{"x": 0}, {"x": 1}, {"x": 2}]
targets = [1, 3, 7]

print(candidate.fitness(rows, targets))  # 0.0
```

Si cualquier fila falla, `fitness` devuelve una penalización configurable: `1e100` por defecto. Los errores mayores se limitan a esa penalización. Las correcciones protegidas se consideran cálculos válidos; si deseas penalizarlas también, utiliza `report()["corrections"]` en una función de fitness propia.

### Generación, cruce y mutación

```python
import random

rng = random.Random(7)  # Semilla: permite reproducir el experimento.
parent_a = ExpressionTree("x^2 + 1", policy)
parent_b = ExpressionTree("sin(x)", policy)

child_a, child_b = parent_a.crossover(parent_b, rng=rng, max_depth=8)
mutated = child_a.mutate(rng=rng, max_depth=8)
random_tree = ExpressionTree.random(
    variables=("x",), max_depth=4, rng=rng, policy=policy,
    primitives=("+", "-", "*", "/", "sqrt"),
)

print(mutated.to_expression())
```

Un **cruce** intercambia subárboles entre dos padres. Una **mutación** reemplaza un subárbol por uno nuevo. Ambos métodos devuelven copias y conservan los padres. Los hijos mantienen la política del padre que los recibe.

La **aridad** es la cantidad de argumentos de una operación. Se valida para que una suma tenga dos hijos y una raíz cuadrada uno. Los identificadores de los nodos se renumeran para evitar duplicados.

Los operadores genéticos aceptan hasta 12 niveles y 160 nodos como límites de trabajo, además del límite de 512 caracteres. El cruce usa 12 niveles por defecto; la mutación, 8; la generación, 4. Si un intento excede los límites, se reintenta hasta 30 veces; cruce y mutación pueden devolver clones como alternativa. No se garantiza que toda mutación cambie la expresión ni que mejore su fitness.

`paths()` devuelve rutas de índices desde la raíz: `()` es la raíz, `(0,)` el primer hijo y `(1,0)` el primer hijo del segundo hijo. `replace_subtree` permite reemplazar una ruta concreta.

### Guardar y recuperar candidatos

```python
import json

serialized = json.dumps(mutated.to_dict())
restored = ExpressionTree.from_dict(json.loads(serialized))
print(restored.to_expression())
```

Se conservan estructura y política. Al cargar se validan tipos de nodo, nombres, argumentos y límites. Los valores anteriores no se reutilizan: se recalculan con los nuevos datos. Cada árbol conserva el último cálculo; usa `clone()` si varios trabajadores necesitan evaluar simultáneamente un mismo candidato.

### Ejemplo evolutivo completo

```powershell
python -m examples.genetic_demo --seed 7 --generations 12 --population 40
```

El ejemplo intenta aproximar `x²+x+1` en 21 puntos de [−1,1]. Incluye población inicial, evaluación, selección por torneo, elitismo, cruce y mutación. Imprime el mejor error de cada generación y la expresión ganadora; puedes pegarla en Arboria para explorar árbol y curva. Es un experimento estocástico, no garantiza recuperar la fórmula exacta.

Pseudocódigo:

```text
crear una población de árboles
repetir por cada generación:
    evaluar el error de cada árbol sobre los datos
    conservar los mejores
    seleccionar padres mediante torneos
    cruzar subárboles y mutar algunos hijos
    formar la siguiente población
devolver el árbol con menor error
```

## 3. Graficar resultados en un dominio

Debajo del árbol hay una sección para elegir variable, inicio, final y número de muestras. Por ejemplo, para graficar `sqrt(x)` en [−4,4], selecciona x, inicio −4, final 4 y 201 muestras.

- En modo protegido aparece `sqrt(abs(x))`; las muestras modificadas se marcan en naranja.
- En modo estricto, la parte negativa queda sin resultados reales y no se dibuja.
- Para `x+y`, si eliges x, el valor de y se conserva desde el panel de variables.
- El botón de comparación acepta tres expresiones adicionales, una por línea. Las variables adicionales deben tener valores disponibles en el panel; si faltan, se indica cuáles.
- Los controles de dominio y comparación se aplican al pulsar **Graficar resultados**. Las modificaciones de la expresión o de sus variables actualizan la gráfica después de generar/evaluar.
- Puedes elegir escala lineal o logarítmica simétrica. Esta última transforma la posición vertical mediante `sign(y)*log10(1+abs(y))`; las etiquetas y el inspector de muestras muestran los valores originales.
- Puedes inspeccionar puntos con el puntero o con las flechas del teclado al enfocar la gráfica. Home y End seleccionan los extremos.
- La tabla muestra las primeras 20 muestras; el CSV contiene todas, con errores, correcciones, cortes, modo, epsilon, máximo y variables fijas.

Se incluyen ambos extremos del dominio. Hay entre 2 y 100,001 muestras por curva. El sistema no une puntos sin resultado y detecta cruces de denominadores por cero, polos comunes de tangente y bases por cero en potencias negativas. **No es un detector universal de discontinuidades**: un muestreo finito puede omitir polos entre puntos. No hay suavizado que invente valores adicionales. Consulta COMPARACION.md para comparar objetivos, importar CSV y simplificar constantes.

Si un valor protegido muy grande aplasta visualmente el resto, prueba la escala logarítmica simétrica o ajusta el dominio y el límite protegido.

### Muestreo desde Python

```python
from sampling import sample_expressions

curves = sample_expressions(
    ["sqrt(x)", "x^2", "sin(x)"],
    variable="x", start=-4, end=4, points=201,
    policy={"mode": "protected", "epsilon": 1e-9},
)
print(curves["x"][:3])
print(curves["series"][0]["y"][:3])
```

La API HTTP equivalente es `POST /api/sample`. Recibe `expressions`, `variable`, `start`, `end`, `points`, `variables` y `policy`. `POST /api/parse` también acepta `policy`. Se reutiliza el mismo evaluador en navegador, curvas y programación genética.

## Prueba de escritorio

Para `sqrt(x)+1/y`, x = −9, y = 0, epsilon = 1e-9:

1. Leer x y aplicar el valor absoluto al argumento de sqrt: −9 pasa a 9.
2. Calcular sqrt(9) = 3 y registrar la corrección en el nodo sqrt.
3. Leer y = 0 y sustituir el divisor por 1e-9.
4. Calcular 1/1e-9 ≈ 1e9 y registrar la corrección en el nodo división.
5. Sumar los resultados: aproximadamente 1 000 000 003.
6. En modo estricto, ambos nodos permanecen sin resultado real y la suma hereda el error.

## Qué aprendiste y qué practicar

**Resumen:** separar la estructura de una fórmula de sus reglas de evaluación permite reutilizarla como candidato genético y como función para graficar.

**Conceptos clave:** epsilon, saturación, aridad, individuo, subárbol, fitness, MSE, población, selección, cruce, mutación, dominio y muestreo.

**Práctica:** cambia el objetivo del ejemplo a `x²−2x+3`; predice la forma de su curva, ejecuta la evolución con dos semillas distintas y compara los errores. Después añade una penalización por tamaño para favorecer árboles pequeños.

**Prompt mejorado:** «Añade aritmética protegida con epsilon configurable y registro de ajustes; crea una clase independiente para evaluar, serializar, cruzar y mutar árboles con límites de tamaño; y permite graficar varias expresiones sobre un dominio configurable usando exactamente las mismas reglas numéricas».

## Referencias

- [Funciones protegidas de gplearn](https://gplearn.readthedocs.io/en/latest/intro.html): explica por qué se definen versiones protegidas. Sus convenciones de división y logaritmo no son idénticas a las de Arboria.
- [Programación genética en DEAP](https://deap.readthedocs.io/en/stable/tutorials/advanced/gp.html): primitivas, terminales y representación mediante árboles. Arboria tiene una implementación propia y no requiere instalar DEAP.
