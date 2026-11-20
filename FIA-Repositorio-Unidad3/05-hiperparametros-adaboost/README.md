[↩ Volver a la Unidad 3](../README.md)

# Práctica de optimización de hiperparámetros

Ajuste de tres hiperparámetros de `AdaBoostClassifier` (`n_estimators`, `learning_rate` y `algorithm`) sobre el dataset Wine, con validación cruzada de 5 particiones. Se comparan los valores por defecto, la búsqueda en malla y la búsqueda con algoritmos genéticos.

| Enfoque | Hiperparámetros encontrados | Accuracy |
|---|---|---|
| Por defecto | `n_estimators=50`, `learning_rate=1.0` | 64.57 % |
| Búsqueda en malla (`GridSearchCV`) | `n_estimators=70`, `learning_rate=0.359` | 93.26 % |
| Búsqueda genética (`GASearchCV`) | `n_estimators=70`, `learning_rate=0.359` | 93.26 % |
| Genético directo (DEAP) | `n_estimators=69`, `learning_rate=0.628` | 94.92 % |

| Archivo | Contenido |
|---|---|
| [hyperparameter.ipynb](hyperparameter.ipynb) | Notebook con el código y los resultados. |

```bash
pip install numpy pandas matplotlib seaborn scikit-learn deap sklearn-genetic-opt
jupyter notebook hyperparameter.ipynb
```
