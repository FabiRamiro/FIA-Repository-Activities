# Generación libre desde una biblioteca de operaciones

## Primero entendamos el problema

Antes escribías una fórmula y el programa descubría su árbol. Ahora también hacemos el proceso inverso: **construimos un árbol aleatorio válido y, desde ese árbol, obtenemos la fórmula y su curva**.

Aquí una ecuación se presenta como `f(x) = expresión`. No se buscan soluciones de una igualdad entre dos miembros: se genera una función para evaluarla en un intervalo.

El generador no usa fórmulas predefinidas y no intenta aproximar un objetivo. La búsqueda guiada por fitness sigue estando en el ejemplo de programación genética; la generación libre produce individuos válidos para iniciar esos algoritmos.

## Entradas, procesos y salidas

| Parte | Datos |
| --- | --- |
| Entradas | Operaciones activadas, altura máxima, variable, uso de constantes, semilla opcional y dominio con paso o muestras |
| Proceso | Construir nodos respetando aridades, cerrar ramas, validar límites, obtener la fórmula y evaluarla |
| Salidas | `f(x)`, árbol, altura real, valores por nodo, curva y datos exportables |

En la interfaz, el dominio y el paso se configuran en la sección de curvas. Al pulsar **Generar fórmula libre**, se usan esos mismos controles y la política numérica actual. Al abrir la aplicación también se genera una primera fórmula automáticamente.

## Biblioteca de operaciones

Está definida en `operations.py`. Cada `Operation` contiene un identificador, nombre, símbolo visible, etiqueta que entiende el intérprete, tipo de nodo y **aridad**.

La aridad es el número exacto de argumentos o hijos que necesita una operación.

| Identificador | Operación | Representación | Aridad |
| --- | --- | --- | --- |
| `add` | Suma | `a+b` | 2 |
| `sub` | Resta | `a-b` | 2 |
| `mul` | Multiplicación | `a*b` | 2 |
| `div` | División | `a/b` | 2 |
| `mod` | Módulo | `a%b` | 2 |
| `sqrt` | Raíz cuadrada | `sqrt(a)` | 1 |
| `sin` | Seno | `sin(a)` | 1 |
| `cos` | Coseno | `cos(a)` | 1 |
| `tan` | Tangente | `tan(a)` | 1 |
| `pow` | Potencia o exponente | `a^b` | 2 |
| `log` | Logaritmo natural | `ln(a)` | 1 |

Por ejemplo, `Operation("add", "Suma", "+", "+", "operator", 2)` declara una suma con dos hijos. `Operation("sqrt", "Raíz cuadrada", "√", "sqrt", "function", 1)` declara una raíz con un hijo.

En esta biblioteca, **raíz** significa raíz cuadrada, **exponente** significa potencia de base y exponente, y **logaritmo** significa logaritmo natural. Esto evita que la cantidad de hijos cambie de una generación a otra. Las funciones adicionales del intérprete siguen disponibles para edición manual.

Las variables y constantes tienen aridad 0: son **terminales**, también llamados hojas. Las constantes del panel se eligen entre −5 y 5, con hasta tres decimales. En Python puedes configurar otro intervalo de constantes dentro de [−1000,1000]. Las constantes negativas siguen siendo hojas con signo, sin añadir una operación de negación al reconstruir la fórmula. Esto conserva la altura.

La etiqueta dirige al mismo evaluador estricto/protegido que ya utilizaba Arboria. La biblioteca no duplica la implementación matemática.

## Altura máxima

Contamos altura por **niveles**:

```text
x                 altura 1

sin               altura 2
 |
 x

    +             altura 3
   / \
 sin  2
  |
  x
```

En esta convención la raíz está en el nivel 1. Algunas bibliografías cuentan aristas y asignan altura 0 a una hoja; aquí la interfaz y la API especifican `height_convention="levels"`.

El máximo configurable está entre 1 y 12 niveles. Una altura máxima 5 permite árboles de altura 2, 3, 4 o 5; no obliga a llegar exactamente a 5. Con altura 1 se genera la variable sola. Si la altura es mayor, la raíz es una operación.

El generador puede terminar una rama antes del máximo. Además, aplica un presupuesto de 160 nodos y valida los límites del intérprete: 512 caracteres y 256 tokens. Nunca entrega una fórmula que, al reconstruirse, necesite una operación de aridad distinta o supere la altura solicitada.

## Lógica paso a paso

1. Cargar las operaciones permitidas y sus aridades.
2. Comenzar en el nivel 1 con un presupuesto de nodos.
3. Si se alcanzó el último nivel, crear una variable o constante.
4. En otros niveles, elegir entre cerrar la rama o crear una operación.
5. Si se eligió una operación, reservar un hijo por cada argumento requerido.
6. Construir cada hijo con el mismo procedimiento, un nivel más abajo.
7. Garantizar que aparezca la variable elegida al menos una vez.
8. Convertir el árbol a texto y reconstruirlo para verificar su estructura.
9. Evaluar esa misma expresión sobre el dominio y enviar árbol y curva juntos.

La variable puede cancelarse algebraicamente, por ejemplo `x-x`; esos árboles siguen siendo válidos y producen curvas constantes. No se simplifican ni se descartan por su forma matemática.

## Pseudocódigo

```text
CREAR_NODO(nivel, presupuesto):
    si nivel == altura_máxima o presupuesto == 1:
        devolver una hoja

    si no es la raíz y se decide cerrar esta rama:
        devolver una hoja

    operación = elegir una operación que quepa en el presupuesto
    hijos = lista vacía
    repetir operación.aridad veces:
        hijos.agregar(CREAR_NODO(nivel + 1, presupuesto_del_hijo))
    devolver nodo(operación, hijos)
```

La llamada a sí misma es **recursión**. Su caso base es crear una hoja: eso impide que el árbol siga creciendo indefinidamente. La aridad garantiza que una suma nunca quede con un solo hijo y que un seno nunca tenga dos.

## Código reutilizable en Python

```python
from generator import ExpressionGenerator

generator = ExpressionGenerator(
    operations=["sin", "mul"],
    seed=17,
    policy={"mode": "protected"},
)

tree = generator.generate(variable="x", max_height=4, constants=False)
print(tree.to_expression())      # sin(sin(x))
print(tree.depth)                # 3, menor o igual que 4
print(tree.evaluate({"x": 0.3}))
```

`ExpressionGenerator` devuelve un `ExpressionTree`, compatible con evaluación, fitness, cruce, mutación y serialización. El generador conserva su estado aleatorio: varias llamadas sobre una instancia producen una secuencia reproducible. Crear otra instancia con la misma semilla y configuración reproduce esa secuencia desde el principio.

Si dejas la semilla vacía, cada petición crea una secuencia nueva. Dos generaciones pueden coincidir, especialmente con una biblioteca pequeña o altura baja. Una semilla no es una garantía de fórmulas distintas: permite repetir el experimento.

Las operaciones activadas son **las permitidas**, no operaciones que deban aparecer obligatoriamente en cada fórmula. Para restringir también una mutación posterior a ese subconjunto, pasa las etiquetas del catálogo a `ExpressionTree.mutate(primitives=...)`; el valor por defecto usa la biblioteca completa de once operaciones.

### Obtener fórmula, árbol y curva juntos

```python
from generator import generate_expression

result = generate_expression(
    operations=["add", "sin", "pow"],
    variable="x",
    max_height=5,
    seed=7,
    start=0,
    end=1,
    step=0.1,
)

print(result["generation"]["formula"])
print(result["stats"]["depth"])
print(result["curve"]["x"])
print(result["curve"]["series"][0]["y"])
```

La evaluación protegida es el valor predeterminado de este generador. Si eliges modo estricto, una fórmula puede estar estructuralmente bien y tener valores no definidos en parte del dominio. La generación respeta la sintaxis y la aridad; no promete que cualquier operación estricta tenga resultado real para todos los valores.

## Muestreo por tamaño de paso

Puedes elegir entre **tamaño de paso** y **cantidad de muestras**. El modo paso avanza desde el inicio sin redistribuir las posiciones intermedias:

```text
inicio 0, final 1, paso 0.3 → [0, 0.3, 0.6, 0.9, 1]
```

El último intervalo mide 0.1 para incluir el final. La interfaz lo indica. Si el paso supera el tamaño del intervalo, se obtienen solo sus dos extremos. El máximo es 100,001 puntos; un paso que produzca más devuelve un error claro. Consulta COMPARACION.md para las métricas y el objetivo CSV.

Se usa `Decimal` para preparar el dominio sin acumular el error de sumar repetidamente números como 0.1. La evaluación matemática y la gráfica siguen usando números de punto flotante. Si el dominio es demasiado estrecho para distinguir las muestras con esa precisión, se rechaza.

Las posiciones de la curva dependen de los valores reales de x: el tramo de 0.9 a 1 ocupa un tercio del ancho de un tramo de longitud 0.3. La inspección con el puntero busca la muestra más cercana por su valor real. El CSV conserva el modo de muestreo y el paso solicitado.

## API y archivos

- `GET /api/operations`: biblioteca con aridades y convención de altura.
- `POST /api/generate`: genera fórmula, árbol, informe y curva en una respuesta.
- `POST /api/sample`: ahora acepta `step`; si se proporciona, determina las muestras y tiene prioridad sobre `points`.
- `operations.py`: definición de la biblioteca.
- `generator.py`: construcción aleatoria y validación.
- `tests/test_generator.py`: pruebas de catálogo, altura, aridad, semillas, reconstrucción y paso.

Ejemplo del cuerpo de `POST /api/generate`:

```json
{
  "operations": ["add", "sqrt", "sin", "pow", "log"],
  "variable": "x",
  "max_height": 5,
  "seed": 7,
  "constants": true,
  "policy": {"mode": "protected", "epsilon": 1e-9},
  "domain": {"start": 0, "end": 1, "step": 0.1}
}
```

## Prueba de escritorio y práctica

Con biblioteca seno y multiplicación, semilla 17, máximo 4 y constantes desactivadas, la fórmula generada es `sin(sin(x))`:

```text
sin         nivel 1
 |
sin         nivel 2
 |
 x          nivel 3
```

Para x = 0.3, se lee la hoja 0.3, se calcula sin(0.3) ≈ 0.295520 y luego sin(0.295520) ≈ 0.291238. Ambas funciones tienen aridad 1 y la altura 3 respeta el máximo 4.

**Errores comunes:** confundir altura máxima con altura exacta; creer que deben aparecer todas las operaciones seleccionadas; crear hijos sin consultar la aridad; contar una constante negativa como una operación nueva; y repartir uniformemente el último intervalo aunque sea más corto.

**Resumen:** un árbol válido se construye aplicando reglas locales: operación con su aridad, hojas como caso base y límite de niveles.

**Conceptos clave:** biblioteca de primitivas, terminales, aridad, recursión, altura, presupuesto de nodos, semilla y muestreo.

**Qué practicar:** activa solo suma y multiplicación, limita a tres niveles y dibuja a mano cinco árboles posibles. Después genera ejemplos y verifica sus aridades. Repite una semilla para comprobar que obtienes la misma fórmula.

**Prompt mejorado:** «Añade un generador aleatorio de f(x) basado en una biblioteca explícita de once operaciones y aridades fijas. Debe permitir seleccionar operaciones, limitar la altura por niveles y generar automáticamente fórmula, árbol y curva usando el dominio, paso y política numérica existentes. Incluye semillas reproducibles, pruebas y explicación del algoritmo».

La representación mediante primitivas con aridad y la generación recursiva son conceptos habituales de [programación genética documentados en DEAP](https://deap.readthedocs.io/en/stable/tutorials/advanced/gp.html). Arboria usa una implementación propia.
