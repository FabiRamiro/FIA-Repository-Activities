import numpy as np
import matplotlib.pyplot as plt

# PARAMTROS DEL ALGORITMO GENETICO
PREC = 0.001
LIMITE_INF = 0.0
LIMITE_SUP = 1.0
POBLACION_TAM = 50
GENERACIONES = 100
PROB_CRUZA = 0.85
PROB_MUTACION = 0.01
TORNEO_TAM = 3

# CALCULO DEL LARGO DEL CROMOSOMA
# Formula usada: 2^L >= (Limite_Superior - Limite_Inferior) / Precision
rango_valores = (LIMITE_SUP - LIMITE_INF) / PREC
L = int(np.ceil(np.log2(rango_valores))) # Para 0.001 y rango de 1, L = 10 bits

# FUNCIONES BASE
def f_1(x):
    # La misma funcion matematica que se definio
    return (np.sin(5 * np.pi * x) ** 6) * np.exp(-2 * np.log(2) * ((x - 0.1) / 0.8))

def decodificar(cromosoma):
    # Convierte el arreglo binario a un valor decimal siendo el fenotipo
    # en el rango [0, 1]
    entero = int("".join(str(bit) for bit in cromosoma), 2)
    return LIMITE_INF + entero * (LIMITE_SUP - LIMITE_INF) / ((2**L) - 1)

def inicializador_poblacion():
    # Matriz aleatoria de 0s y 1s de tamaño (Poblacion * Largo del Cromosoma)
    return np.random.randint(2, size=(POBLACION_TAM, L))

def seleccion_torneo(poblacion, aptitudes):
    # Seleccion por Torneo: Escoge k individuos al azar y se queda con el mejor
    seleccionados = np.zeros_like(poblacion)
    for i in range(POBLACION_TAM):
        participantes_idx = np.random.choice(POBLACION_TAM, TORNEO_TAM, replace=False)
        mejor_idx = participantes_idx[np.argmax(aptitudes[participantes_idx])]
        seleccionados[i] = poblacion[mejor_idx]

def cruza(padres):
    # Cruza de un solo punto
    hijos = np.zeros_like(padres)
    for i in range(0, POBLACION_TAM, 2):
        padre1, padre2 = padres[i], padres[i + 1]
        if np.random.rand() < PROB_CRUZA:
            punto = np.random.randint(1, L) # PUNTO DE CORTE
            hijos[i] = np.concatenate([padre1[:punto], padre2[punto:]])
            hijos[i + 1] = np.concatenate([padre2[:punto], padre1[punto:]])
        else:
            hijos[i], hijos[i + 1] = padre1, padre2
    return hijos

def mutacion(poblacion):
    # Invierte bits (0 a 1, o 1 a 0) segun la probabilidad de mutacion
    mascara = np.random.rand(POBLACION_TAM, L) < PROB_MUTACION
    poblacion[mascara] = 1 - poblacion[mascara]
    return poblacion

# CICLO PRINCIPAL DEL ALGORITMO (PSEUDOCODIGO A PYTHON)
poblacion = inicializador_poblacion()
historial_mejores = []
mejor_x_historico = None
max_aptitud = -np.inf

for gen in range(GENERACIONES):
    # A. Evaluacion (Fitness)
    fenotipos = np.array([decodificar(ind) for ind in poblacion])
    aptitudes = f_1(fenotipos)

    # Guardar el individuo mas apto de la generacion
    mejor_idx = np.argmax(aptitudes)
    if aptitudes[mejor_idx] > max_aptitud:
        max_aptitud = aptitudes[mejor_idx]
        mejor_x_historico = fenotipos[mejor_idx]

    historial_mejores.append(max_aptitud)

    # B. Seleccion
    padres = seleccion_torneo(poblacion, aptitudes)

    # C. Cruza
    hijos = cruza(padres)

    # D. Mutacion
    poblacion = mutacion(hijos)

# RESULTADOS Y GRAFICACION
print("-" * 40)
print(f"Generaciones ejecutadas: {GENERACIONES}")
print(f"Largo del cromosoma (L): {L} bits")
print(f"Mejor valor de x encontrado: {mejor_x_historico:.5f}")
print(f"Máximo valor de f_1(x): {max_aptitud:.5f}")
print("-" * 40)

# Graficar la convergencia del algoritmo
plt.plot(historial_mejores, color='green', linewidth=2)
plt.title('Convergencia del Algoritmo Genético', fontsize=14)
plt.xlabel('Generación', fontsize=12)
plt.ylabel('Mejor Aptitud $f_1(x)$', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.7)
plt.show()