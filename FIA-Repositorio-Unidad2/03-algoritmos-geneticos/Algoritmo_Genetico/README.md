[↩ Volver a los algoritmos genéticos](../README.md)

# Algoritmo genético binario y real

Algoritmos genéticos basados en el libro *Algoritmos Evolutivos: un enfoque práctico* (Araujo y Cervigón). Cada generación se puede ver en una ventana interactiva hecha con PySide6 y Matplotlib.

| Ruta | Contenido |
|---|---|
| [algoritmo_genetico.py](algoritmo_genetico.py) | AG binario básico: cromosoma calculado a partir de la precisión, selección por torneo, cruza y mutación. |
| [funcion_mate.py](funcion_mate.py) | Gráfica de la función que se optimiza. |
| [visor_ag.py](visor_ag.py) | Ventana común para ver el AG generación por generación. |
| [proyecto1/](proyecto1/) | AG binario en tres versiones: maximizar, minimizar y varias variables. Incluye animaciones GIF. |
| [proyecto2/](proyecto2/) | AG con codificación real sobre funciones como Rastrigin, Schaffer y Schwefel, comparando cruces aritmética y SBX. Incluye animaciones y gráficas. |

## Ejecutar

```bash
pip install numpy matplotlib PySide6
cd proyecto1 && python app_proyecto1.py
cd proyecto2 && python app_proyecto2.py
```
