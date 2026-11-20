[↩ Volver a la Unidad 2](../README.md)

# Problema de la hormiga

Una hormiga debe recoger entre 5 y 7 comidas dentro de un laberinto generado al azar y después encontrar la salida, usando búsqueda en anchura (BFS) y en profundidad (DFS).

La aplicación se generó con un equipo de seis agentes de CrewAI: arquitecto, especialista en grafos, desarrollador backend, desarrollador PyQt, integrador y tester. Cada uno dejó su entregable en `artifacts/`.

| Ruta | Contenido |
|---|---|
| [hormiga/](hormiga/README.md) | **Aplicación final** en Python y PyQt6, con instrucciones de uso. |
| [artifacts/](artifacts/) | Documentos de cada agente: arquitectura, algoritmos, backend, interfaz PyQt y reporte de pruebas. |
| [src/taller_crewai/](src/taller_crewai/) | Código del crew que generó la aplicación. |
| [tests/](tests/) | Pruebas del proyecto. |
| `report.md`, `noticias/`, `knowledge/`, `scripts/` | Archivos heredados de la plantilla de la [práctica CrewAI](../../FIA-Repositorio-Unidad1/08-crewai/README.md). |

## Ejecutar la aplicación

```bash
pip install PyQt6
python hormiga/main.py
```
