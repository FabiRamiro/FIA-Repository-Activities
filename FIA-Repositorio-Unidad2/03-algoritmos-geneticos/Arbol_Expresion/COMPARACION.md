# Comparar funciones y entender el tamaño de los árboles

## Primero entendamos el problema

Una función objetivo es la respuesta que queremos aproximar. Una candidata es otra
expresión que intentamos acercar a ella. La gráfica permite ver diferencias y las
métricas permiten medirlas. Generar fórmulas al azar todavía no equivale a buscar
automáticamente la mejor: esta pantalla evalúa las candidatas que le proporciones.

Entradas: función objetivo o CSV, candidatas, variable, intervalo y paso.
Proceso: construir cada árbol una vez, evaluar todas las muestras, comparar pares
con el mismo x. Salidas: curvas, métricas, CSV de datos y CSV de métricas.

## Ejecutar el ejercicio

1. Ejecuta `python app.py` y abre http://127.0.0.1:5000/.
2. Pulsa **Cargar ejercicio del coseno** en el panel de curvas.
3. Se usa `6.87 + 11 * cos(7.23 * x^3)` como objetivo, intervalo -10 a 10,
   paso 0.001. Son 20,001 puntos, incluidos ambos extremos. El coseno usa radianes.
4. La candidata inicial cambia 11 por 10 para mostrar una comparación real.
   Puedes editarla, agregar otras dos o borrar todas para graficar solo el objetivo.
5. Cambia Desde, Hasta y Paso y pulsa **Graficar resultados** para aplicarlos.
6. Descarga los datos y las métricas con sus botones respectivos.

El límite es 100,001 puntos por curva y cuatro curvas contando el objetivo. Un
paso que no divide exactamente el intervalo conserva sus incrementos y añade el
extremo final como último tramo más corto. Los límites evitan solicitudes enormes.

## Cómo usar un CSV

Selecciona **Valores de un archivo CSV** como objetivo y elige un archivo UTF-8.
Se admite coma o punto y coma como separador; los decimales usan punto.

```csv
x,y
0,1
0.3,1.6
1,3
```

Genera `2*x+1` en el editor y pulsa **Graficar resultados**. Obtendrás MSE=0,
RMSE=0, NMSE=0 y R²=1. En este modo la expresión del árbol es una candidata,
el CSV es f1 y puedes añadir otras dos candidatas.

Se utilizan exactamente los x del archivo, sin interpolarlos ni remuestrearlos;
los controles de intervalo y paso se desactivan. Deben estar ordenados, no
repetidos, con al menos dos filas. No se aceptan celdas vacías, NaN ni infinitos.
El tamaño máximo de solicitud es 16 MB, incluyendo el formulario.

La columna objetivo se busca como `y_objetivo`, `y`, `target` o la primera columna
`f1:` del CSV exportado por Arboria. La columna independiente se busca como la
variable seleccionada o `x`. También puedes escribir los encabezados exactos en
los campos de columnas.

## Lógica y pseudocódigo

```text
obtener los x del intervalo o del CSV
construir cada árbol una sola vez
para cada x:
    evaluar objetivo y candidatas
para cada candidata:
    si hay valores sin definir: informar, sin omitir filas
    si todos son válidos: calcular métricas
dibujar una representación adaptada al ancho de la pantalla
exportar todas las muestras originales
```

La gráfica reduce únicamente los puntos dibujados, conservando extremos locales
y bordes de los cortes detectados. La inspección, los cálculos y los CSV mantienen
todas las muestras. En funciones de oscilación rápida, una pantalla tiene menos
píxeles que datos: consulta un intervalo más pequeño para apreciar cada oscilación.
El muestreo finito no garantiza detectar todas las discontinuidades.

## Qué significan las métricas

Para n pares, y objetivo, p predicción y media(y):

- MSE = suma((y-p)²) / n. Penaliza más las diferencias grandes.
- RMSE = raíz(MSE). Se interpreta en las unidades del objetivo.
- NMSE = MSE / varianza poblacional(y), con divisor n en la varianza.
- R² = 1 - NMSE, bajo esa definición concreta de normalización.

Las tres primeras tienen ideal 0; R² tiene ideal 1 y puede ser negativo. NMSE
tiene otras convenciones: verifica cuál usa tu profesor. Con objetivo constante,
NMSE y R² no están definidos porque su denominador es cero. Se muestran vacíos,
con una explicación, y se mantienen MSE/RMSE. Si cualquier par no está definido,
no se calcula ninguna métrica de esa candidata: omitirlo podría favorecerla.

El modo protegido puede modificar operaciones inválidas o saturar resultados.
Sus valores sí participan en las métricas y se conservan los conteos de protección
en el CSV. Para comparar modelos usa la misma política y revisa esos conteos.

Prueba de escritorio: objetivo [1,3], candidata [2,2]. Las diferencias son [-1,1],
los cuadrados [1,1], MSE=1, RMSE=1. La media del objetivo es 2, su varianza es 1:
NMSE=1 y R²=0. Comparar el objetivo consigo mismo da error cero, pero no demuestra
que otra candidata se acerque a él.

## Reutilización desde Python

```python
from sampling import sample_expressions
from metrics import regression_metrics
from expression_tree import ExpressionTree

curvas = sample_expressions(
    ["6.87 + 11*cos(7.23*x^3)", "6.87 + 10*cos(7.23*x^3)"],
    start=-10, end=10, step=0.001,
)
print(curvas["points"])   # 20001
print(curvas["metrics"])
print(regression_metrics([1, 3], [2, 2]))

original = ExpressionTree("(2+3)*x")
reducido = original.simplify()
print(original.size, reducido.size)  # 5, 3
print(reducido.evaluate({"x": 4}))   # 20
```

`sample_expressions` prepara el dominio y reutiliza los árboles sin crear informes
visuales por muestra. `regression_metrics` recibe dos listas de igual longitud y
devuelve un diccionario; puede usarse en un algoritmo genético sin Flask ni Three.js.
`simplify()` devuelve un árbol nuevo: no modifica al individuo padre.

## Técnicas para que el árbol no crezca demasiado

No sabemos cuál nombró tu profesor. Son técnicas distintas:

- **Simplificación de constantes:** `(2+3)*x` pasa a `5*x`. Es la implementada
  por el botón **Simplificar constantes del árbol**. Se calculan subárboles sin
  variables, únicamente si no producen errores ni protecciones numéricas.
- **Límites de altura y tamaño:** el generador ya limita niveles (1 a 12) y nodos
  (hasta 160); cruce y mutación también admiten límites. Esto controla el crecimiento.
- **Poda:** reemplaza ramas por partes más pequeñas. Puede alterar la función;
  en programación genética se vuelve a medir su error antes de aceptarla.
- **Presión de parsimonia:** penaliza la complejidad, por ejemplo
  `puntuacion = MSE + coeficiente * numero_de_nodos`. No está activada en esta
  interfaz. El coeficiente depende de la escala del error.
- **Subexpresiones compartidas (DAG):** permite almacenar una parte repetida una
  vez y reutilizarla. Cambia la representación; este sistema conserva árboles.

No aplicamos identidades indiscriminadas: `0*(1/0)` no se debe convertir a 0 en
modo estricto, porque escondería un error. Tampoco se reagrupan operaciones, pues
en aritmética protegida la saturación intermedia puede cambiar el resultado.
La simplificación de constantes preserva el cálculo flotante y las protecciones
bajo la política actual; si cambias esa política, vuelve a usar la fórmula original.

## Pruebas y práctica

Ejecuta `python -m unittest discover -s tests -v` y `node tests/test_plot.mjs`. Se comprueban el ejercicio de
20,001 puntos, resultados conocidos de métricas, CSV y conservación de errores al
simplificar.

Conceptos clave: muestreo, objetivo/predicción, error cuadrático, varianza,
árbol reutilizable y simplificación conservadora.

Practica con objetivo `x^2` y candidata `x^2+1`: MSE y RMSE deben valer 1 en
cualquier dominio válido. Después compara `(2+3)*x` antes y después de simplificar.

Prompt mejorado: «Adapta Arboria para definir intervalo y paso, evaluar 20,001
puntos, comparar candidatas con una función o CSV mediante MSE/RMSE/NMSE/R² y
simplificar subárboles constantes conservando la evaluación protegida».
