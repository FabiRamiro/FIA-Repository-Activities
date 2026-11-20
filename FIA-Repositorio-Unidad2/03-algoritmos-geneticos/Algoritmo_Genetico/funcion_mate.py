import matplotlib.pyplot as plt
import numpy as np

# DEFINIR LOS LIMITES Y LA PRECISION
PREC = 0.001
#np.arange es para poder crear un arreglo desde 0.0 hasta 1.0 dando saltos de 0.001
x = np.arange(0.0, 1.0 + PREC, PREC)

# DEFINIR LA FUNCION f_1(x)
# np.sin() = seno
# np.pi = pi
# np.exp() = e^
# np.log() = logaritmo natural (ln)
y = (np.sin(5 * np.pi * x)**6) * np.exp(-2 * np.log(2) * ((x - 0.1) / 0.8))

# CONFIGURAR Y MOSTRAR LA GRAFICA
plt.figure(figsize=(10, 5))
plt.plot(x, y, label=r'$f_1(x)$', color='blue')

# DETALLES ESTETICOS DE LA GRAFICA
plt.title('Grafica de la funcion $f_1(x)$', fontsize=14)
plt.xlabel('x', fontsize=12)
plt.ylabel('$f_1(x)$', fontsize=12)
plt.xlim(0, 1)
plt.grid(True, linestyle='--', alpha=0.7)
plt.legend()

# MOSTRAR LA GRAFICA
plt.show()
