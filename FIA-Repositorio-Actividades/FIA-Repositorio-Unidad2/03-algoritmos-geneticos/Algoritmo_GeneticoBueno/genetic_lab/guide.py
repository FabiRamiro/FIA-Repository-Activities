"""Guía accesible desde la propia aplicación."""
GUIDE = """
<h1>De puntos a fórmulas</h1>
<p>Una introducción práctica a la programación genética, sin DEAP.</p>
<p><b>Motor nativo:</b> árboles, errores, evolución, CSV y exportación usan Python
estándar: listas, tuplas, ciclos, math, random, csv y json. PySide6 y Matplotlib
dibujan la interfaz; NumPy se limita a preparar datos para las gráficas.</p>
<h2>01 · Primero entendamos el problema</h2>
<p>Conocemos pares (x, y), pero buscamos una expresión f(x) que produzca valores
parecidos a y. Esto se llama <b>regresión simbólica</b>. Aquí evolucionamos la
estructura de una fórmula, no solamente sus coeficientes.</p>
<p><b>Entrada:</b> CSV x,y y configuración. <b>Proceso:</b> evolución de árboles.
<b>Salida:</b> fórmula, predicciones y métricas por generación.</p>
<h2>02 · Datos y árboles</h2>
<p>En (x * x) + 1, la raíz es +; sus hijos son * y 1. La multiplicación tiene
dos hojas x. Una hoja es un dato (x o constante); un nodo interno es una operación.
La profundidad cuenta niveles, incluyendo la raíz como nivel 1.</p>
<h2>03 · Algoritmo</h2>
<pre>crear población aleatoria (generación 0)
evaluar cada árbol con todos los puntos del CSV
repetir N veces:
    conservar al campeón y las élites
    reservar un porcentaje para árboles aleatorios nuevos
    mientras falten individuos:
        seleccionar padres por torneo
        posiblemente cruzar ramas
        posiblemente mutar una rama o constante
        reparar estructura y limitar profundidad
        opcionalmente podar expresiones redundantes
    evaluar la nueva población
    guardar y mostrar la generación</pre>
<h2>04 · Selección, cruza y mutación</h2>
<p><b>Torneo:</b> se sortean k individuos y gana el de menor aptitud penalizada.
<b>Cruza:</b> se injerta una rama del padre B en el padre A para producir un hijo.
<b>Mutación:</b> se cambia una rama aleatoria o se perturba una constante.
Las probabilidades de cruza y mutación son independientes: un hijo puede recibir ambas.</p>
<p><b>Elitismo:</b> se conserva al mejor del criterio elegido y luego a los mejores
por aptitud. MSE, NMSE y RMSE se minimizan; R² se maximiza usando la pérdida 1−R².</p>
<p><b>Aptitud:</b> pérdida / pérdida de predecir el promedio + penalización × nodos.
Si la pérdida de referencia es cero, se usa 1 como escala. La penalización inicia
en cero para priorizar el ajuste. Una métrica indefinida bloquea el inicio con
una explicación; puedes seleccionar MSE o RMSE.</p>
<p><b>Exploración:</b> por defecto entra un 10% de árboles aleatorios nuevos.
Las constantes iniciales mezclan enteros y decimales entre −12 y 12; las mutaciones
pueden dar pasos grandes o pequeños. Tras 8 generaciones sin mejora, la opción
de mutación adaptativa incrementa la probabilidad en 0.2, hasta 1.0.</p>
<p><b>Ajuste opcional de constantes:</b> se conserva una forma g(x) encontrada por
el algoritmo y se estiman a y b en a + b·g(x). La escala b cambia la amplitud y
el desplazamiento a sube o baja la curva. Esto evita descartar una forma útil
solo porque sus constantes iniciales sean malas.</p>
<p>El ajuste está escrito con sumas y ciclos: b = Σ((g−ḡ)(y−ȳ)) / Σ(g−ḡ)²,
a = ȳ − b·ḡ. Solo se acepta si disminuye el error real y respeta la profundidad.
Se intenta en el 25% de los hijos y en los inmigrantes; cada cambio se registra
en Operadores. Es una técnica adicional de mínimos cuadrados: desactiva
«Afinar escala y desplazamiento» para estudiar únicamente los operadores genéticos.</p>
<h2>05 · Poda, reconstrucción y reparación</h2>
<p><b>Poda:</b> x + 0 → x, x × 1 → x; las operaciones entre constantes se calculan.
<b>Reconstrucción:</b> al sustituir una rama se reconstruye el camino hasta la raíz;
los padres y el historial permanecen intactos.
<b>Reparación:</b> verifica operadores, número de hijos y constantes; sustituye por
hojas las ramas que exceden la profundidad máxima. Una población válida puede
no necesitar reparaciones en algunas generaciones.</p>
<p>En Operadores se muestran ejemplos reales de la transición hacia la generación
seleccionada. No necesariamente son los ancestros del campeón. Los contadores
incluyen todas las operaciones; cada ejemplo muestra una ocurrencia.</p>
<p>Reconstrucción muestra cómo se rehace un árbol después de sustituir una rama.
Es parte de la cruza y la mutación, no un proceso aleatorio adicional. Su contador
registra una reconstrucción por cada una de esas sustituciones.</p>
<h2>06 · Cómo medir el error</h2>
<p>ŷ es la predicción, ȳ es el promedio observado y n es el número de puntos.</p>
<table cellspacing="10">
<tr><th>Métrica</th><th>Fórmula</th><th>Interpretación</th></tr>
<tr><td>MSE</td><td>Σ(y − ŷ)² / n</td><td>0 es perfecto; menor es mejor.</td></tr>
<tr><td>NMSE</td><td>Σ(y − ŷ)² / Σy²</td><td>Normalización por la energía de y; 0 es perfecto.</td></tr>
<tr><td>R²</td><td>1 − Σ(y − ŷ)² / Σ(y − ȳ)²</td><td>1 es perfecto; puede ser negativo.</td></tr>
<tr><td>RMSE</td><td>√MSE</td><td>Error en las mismas unidades que y; 0 es perfecto.</td></tr>
</table>
<p><b>Fórmulas de clase:</b> se implementan las cuatro métricas de tu fotografía.
La última se llama RMSE. Con esta definición de NMSE, R² no se obtiene como 1 − NMSE.</p>
<p>Si todos los valores y son iguales, R² es N/D. Si todos son cero, NMSE también
es N/D. MSE y RMSE siguen siendo válidos. Las métricas se calculan sobre el CSV
completo: son errores de ajuste, no una evaluación independiente de generalización.</p>
<h2>¿Por qué aparece una línea central?</h2>
<p>El promedio minimiza el error entre <b>las predicciones constantes</b>, pero una
fórmula que siga correctamente las oscilaciones puede tener un error mucho menor.
Para y = [−1, 1, −1, 1], predecir 0 siempre da MSE = 1 y R² = 0;
predecir los cuatro valores correctos da MSE = 0 y R² = 1.</p>
<p>Para un mismo CSV, MSE, NMSE y RMSE son transformaciones crecientes de la misma
suma de errores cuadrados; R² disminuye cuando esa suma aumenta. Por tanto,
cambiar entre estas métricas no cambia el orden matemático de los candidatos.
Una línea central suele indicar estancamiento o una búsqueda insuficiente.
El selector cambia el criterio y su escala, pero no garantiza una forma oscilatoria.</p>
<h2>07 · Operaciones protegidas</h2>
<p>Para poder evaluar fórmulas aleatorias sin detener el programa:
div(a,b) usa divisor 1 cuando |b| &lt; 10⁻⁹; sqrt(a) = √|a|;
log(a) = ln(1 + |a|). Los resultados de operaciones se limitan a ±1 000 000.
La fórmula debe interpretarse con estas reglas, especialmente fuera del intervalo del CSV.
No se usa eval(): los árboles se recorren explícitamente.</p>
<h2>08 · Prueba de escritorio</h2>
<p>Si x = [0,1,2], y = [1,2,5] y el candidato es x², sus predicciones son [0,1,4].
Los residuos son [1,1,1]; por tanto MSE = 1. El promedio de y es 8/3,
la suma de y² es 30 y NMSE = 3/30 = 0.1.
La varianza es 26/9: R² = 17/26 ≈ 0.65385; RMSE = 1.
El candidato x² + 1 obtiene MSE = 0.</p>
<h2>09 · Controles y lectura visual</h2>
<p>Iniciar comienza una ejecución nueva. Pausa detiene las solicitudes de nuevas
generaciones (una generación en cálculo puede terminar). Paso avanza una sola generación.
La barra de historial permite regresar. Reproducir recorre las generaciones guardadas y,
al llegar al presente, continúa el cálculo. Detener conserva el historial.</p>
<p><b>Comparación:</b> la gráfica grande muestra en azul los puntos del CSV unidos
en orden de x y en verde al élite de la generación. Puedes activar los círculos
de predicción. La rueda amplía alrededor del cursor; arrastrar en la vista general
elige un tramo; los campos de x fijan límites exactos; Ver todo restaura el intervalo.</p>
<p>El objetivo de coseno cúbico empieza con un detalle de [−1.5, 1.5] para distinguir
las oscilaciones. Los datos siguen en [−10,10]. El zoom se conserva entre generaciones
y <b>nunca cambia los puntos usados para calcular las métricas</b>.</p>
<p><b>Errores:</b> muestra las cuatro métricas, un historial seleccionable, residuos
y la referencia de predecir siempre el promedio. R² usa escala lineal; los errores
usan symlog para incluir el cero. Configuración, Datos, Árbol y Operadores tienen
sus propias pestañas para mantener despejada la gráfica principal.</p>
<h2>10 · Errores comunes y práctica</h2>
<p>CSV sin encabezados, coma decimal, filas incompletas, profundidad excesiva,
poca diversidad y confundir un buen ajuste con una fórmula verdadera.</p>
<p>El algoritmo es aleatorio: no garantiza encontrar la expresión exacta.
La semilla hace reproducible una ejecución con los mismos datos y parámetros.</p>
<p><b>Practica:</b> compara una recta y una parábola; cambia solo la mutación;
añade ruido; desactiva la poda; compara tamaño del árbol y MSE.
Después explica por qué un R² negativo es posible.</p>
<p><b>Conceptos clave:</b> recursión, árboles, inmutabilidad, funciones, selección,
azar reproducible, error, complejidad y señales de una interfaz.</p>
"""
