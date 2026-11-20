# Cómo pensar este proyecto

**Actualización:** esta guía explica la estructura original y las reglas matemáticas del modo estricto. La versión 2 agrega un modo protegido (activado inicialmente en la interfaz), programación genética y gráficas. Consulta [GENETICA.md](GENETICA.md) para entender esas convenciones y los nuevos módulos.

## Primero entendamos el problema

Una fórmula escrita es texto: `sqrt(x^2 + y^2)`. Para dibujarla y calcularla necesitamos descubrir su estructura. El signo `+` relaciona dos potencias; la raíz cuadrada recibe la suma completa. Un árbol representa esas relaciones.

No estamos dibujando la gráfica de una función sobre ejes x e y. Estamos dibujando **las partes de la expresión y cómo dependen unas de otras**.

## Datos, procesos y salidas

| Parte | En este proyecto |
| --- | --- |
| Entrada | Texto matemático y valores de variables |
| Proceso | Separar símbolos, aplicar prioridades, construir nodos y calcular |
| Salida | Árbol, valores por nodo, resultado, recorridos y estadísticas |

Python se encarga del significado matemático. JavaScript se ejecuta en el navegador y controla Three.js, que dibuja la escena. Flask permite que ambos se comuniquen mediante solicitudes HTTP.

## Las entidades que identificamos

Un **nodo** es una pieza del árbol. Tiene un identificador, una etiqueta, un tipo, sus hijos y un resultado. Por ejemplo, un nodo suma tiene etiqueta `+`, tipo `operator` y dos hijos.

Una **hoja** es un nodo sin hijos: `x`, `2` o `pi`. La **raíz del árbol** es el nodo superior que representa toda la expresión. No debes confundir raíz del árbol con raíz cuadrada: `2+3` tiene `+` como raíz del árbol, aunque no tenga ninguna raíz cuadrada.

Un **token** es una pieza de texto reconocida: `sqrt`, `(`, `x`, `^`, `2`, `+`, `y`, `^`, `2`, `)`. La **gramática** son las reglas que permiten combinar esas piezas.

## Lógica paso a paso

1. Leer el texto completo.
2. Separarlo en tokens. Una expresión regular reconoce patrones de números, nombres y operadores.
3. Crear hojas para números, constantes y variables.
4. Crear padres cuando aparecen operadores o funciones.
5. Respetar prioridades: multiplicar antes que sumar, agrupar paréntesis y asociar potencias desde la derecha.
6. Calcular los hijos antes de calcular su padre.
7. Convertir el árbol a JSON, un formato de datos que Python y JavaScript pueden compartir.
8. Asignar posiciones a las hojas y centrar cada padre sobre sus hijos.
9. Crear los objetos Three.js y actualizar su animación en cada cuadro.

## Pseudocódigo

```text
INTERPRETAR(expresión, variables):
    tokens = separar_en_símbolos(expresión)
    árbol = analizar_respetando_prioridades(tokens)
    evaluar(árbol, variables)
    devolver árbol, resultado, estadísticas y recorridos

EVALUAR(nodo, variables):
    si nodo es un número:
        devolver ese número
    si nodo es una constante:
        devolver su valor conocido
    si nodo es una variable:
        buscar su valor en variables
    en otro caso:
        resultados = evaluar cada hijo
        aplicar la operación del nodo a esos resultados
        guardar y devolver el resultado
```

## Cómo se expresa en código

Lee `interpreter.py` en este orden:

1. **`Node`**: la clase que describe los datos de cada nodo. `@dataclass` crea automáticamente un constructor a partir de sus campos. `children` es una lista de otros nodos. `field(default_factory=list)` crea una lista independiente para cada nodo.
2. **`FUNCTIONS`**: un diccionario. Sus claves son nombres como `sqrt`; cada valor contiene la función Python que se ejecutará y los límites de argumentos. Guardamos la función `math.sqrt`, sin llamarla todavía; se ejecuta después de evaluar sus hijos.
3. **`TOKEN` y `Parser.__init__`**: separan el texto en elementos y guardan sus posiciones para informar errores. `re.compile` prepara una expresión regular reutilizable.
4. **`Parser.expression`**: construye el árbol. Es un analizador Pratt: compara prioridades para decidir si una operación pertenece al hijo que está construyendo o al nivel superior.
5. **`evaluate`**: recorre el árbol y realiza los cálculos. Usa condicionales según el tipo del nodo.
6. **`traversal`**: cambia cuándo se visita el padre respecto de sus hijos.
7. **`interpret`**: coordina todos los pasos y prepara la respuesta.

Una **función recursiva** se llama a sí misma con un problema más pequeño. `evaluate` recibe un árbol y llama a `evaluate` con sus hijos. Se detiene cuando llega a una hoja. Esa condición de parada es el *caso base*.

El analizador también es recursivo: analizar lo que está dentro de unos paréntesis es una versión más pequeña del mismo problema.

### Un ejemplo de prioridades

Para `2 + 3 * 4`, el analizador encuentra una suma, pero antes de terminar su hijo derecho observa que `*` tiene más prioridad. Construye `*(3,4)` y después `+(2,resultado)`.

En `BINDING`, cada operador tiene dos prioridades. La diferencia entre ellas controla la asociación: la división agrupa desde la izquierda y la potencia desde la derecha. El signo negativo tiene prioridad 25 y la potencia 30; por eso `-2^2` se convierte en `neg(^(2,2))`.

### Del árbol al dibujo

En `static/scene.js`, `positionNode` asigna posiciones de izquierda a derecha a las hojas. Después coloca cada padre en el punto medio entre su primer y su último hijo. La profundidad determina su posición vertical.

Three.js necesita una **escena** (los objetos), una **cámara** (desde dónde los miramos) y un **renderer** (el motor que produce los píxeles). Los nodos son cilindros cortos; las ramas son tubos curvos. Las etiquetas son botones HTML proyectados sobre los objetos para poder seleccionarlos también con teclado.

`requestAnimationFrame` pide al navegador ejecutar la siguiente actualización antes de dibujar otro cuadro. En cada cuadro ajustamos escalas de entrada, anillos de selección y partículas que recorren las ramas. `OrbitControls` actualiza la cámara con los movimientos del usuario.

### Comunicación con Python

En `static/app.js`, `fetch('/api/parse', ...)` envía la expresión al servidor. `await` espera la respuesta sin congelar la interfaz. Flask llama a `interpret`, y `jsonify` transforma el resultado en una respuesta JSON.

Una respuesta de error sintáctico usa HTTP 400. Un árbol válido con un cálculo imposible, como `sqrt(-1)`, sigue siendo una interpretación correcta y usa HTTP 200 con un mensaje en `evaluation.error`.

## Prueba de escritorio

Para `sqrt(x^2 + y^2)`, con x = 3 e y = 4:

```text
         sqrt → 5
           |
           + → 25
        /     \
     ^ → 9   ^ → 16
     /  \     /  \
    x    2   y    2
    3        4
```

El postorden es `x, 2, ^, y, 2, ^, +, sqrt`.

| Paso | Acción | Resultado |
| --- | --- | --- |
| 1 | Leer x | 3 |
| 2 | Leer el exponente | 2 |
| 3 | Elevar x a 2 | 9 |
| 4 | Leer y | 4 |
| 5 | Leer el exponente | 2 |
| 6 | Elevar y a 2 | 16 |
| 7 | Sumar ambos resultados | 25 |
| 8 | Calcular la raíz cuadrada | 5 |

Observa que `sqrt` recibe un único argumento: la suma completa. Esa es la ventaja de trabajar con estructura en vez de buscar y reemplazar texto.

## Errores comunes

- **Confundir texto con estructura**: buscar `sqrt` y reemplazarlo por `√` cambia su apariencia, pero no permite evaluar argumentos anidados. Necesitas el árbol.
- **Calcular de izquierda a derecha sin prioridades**: `2+3*4` produciría 20 en lugar de 14.
- **Usar `eval` sobre la entrada**: ejecutaría código del usuario. Aquí solo interpretamos los elementos de nuestra gramática.
- **Olvidar el caso base de la recursión**: la llamada nunca terminaría. Las hojas cierran el proceso.
- **Confundir error de sintaxis con error matemático**: `sqrt(` está incompleto; `sqrt(-1)` está bien escrito, pero no tiene resultado real.
- **Olvidar reiniciar Python al cambiar su código**: el servidor usa `debug=False`; reinícialo después de modificar funciones. Para cambios en HTML/CSS/JS, recarga el navegador.

## Qué practicar después

1. Dibuja a mano el árbol de `(2+3)*4` y calcula su postorden antes de usar la aplicación.
2. Predice qué cambia entre `-2^2` y `(-2)^2`.
3. Agrega `doble(x)` siguiendo el README y comprueba que `doble(3+2)` produce 10.
4. Agrega una prueba para esa función en `tests/test_interpreter.py`.
5. Como siguiente reto, implementa un recorrido por niveles usando una cola: una estructura que procesa primero lo que entró primero.

**Lo aprendido:** convertir texto matemático en datos relacionados y separar interpretación, evaluación y visualización.

**Conceptos clave:** variables, funciones, diccionarios, listas, clases, árboles, recursión, prioridades, JSON, HTTP y animación por cuadros.

**Un prompt más preciso:** «Construye en esta carpeta una aplicación educativa con Python y Three.js para interpretar expresiones matemáticas reales y visualizar su árbol en 2D/3D. Debe admitir operadores, variables, funciones extensibles como sqrt, evaluación por nodo, recorridos animados y mensajes de error. Incluye un diseño propio, pruebas y una guía para comprender y extender el analizador».
