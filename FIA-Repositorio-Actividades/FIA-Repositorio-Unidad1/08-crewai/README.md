[↩ Volver a la Unidad 1](../README.md)

# Práctica CrewAI

Sistema multiagente hecho con [CrewAI](https://crewai.com). Dos agentes trabajan en secuencia:

1. **Investigador**: reúne datos, estadísticas, fuentes y posturas sobre un tema, sin redactar.
2. **Redactor**: convierte esa investigación en una noticia para redes sociales.

El tema configurado es «La muerte del formato físico y la propiedad digital».

| Ruta | Contenido |
|---|---|
| [src/taller_crewai/](src/taller_crewai/) | Código del crew: agentes y tareas en `config/`, lógica en `crew.py` y entrada en `main.py`. |
| [report.md](report.md) | Noticia generada en la ejecución principal. |
| [noticias/](noticias/) | Noticias generadas en ejecuciones programadas, agrupadas por fecha. |
| [scripts/run_scheduled.ps1](scripts/run_scheduled.ps1) | Script de PowerShell para ejecutar el crew de forma programada. |
| [knowledge/](knowledge/) | Contexto adicional que pueden consultar los agentes. |
| [tests/](tests/) | Pruebas del proyecto. |

## Ejecutar

Requiere Python 3.10–3.13, [uv](https://docs.astral.sh/uv/) y una clave de API del modelo en el archivo `.env`.

```bash
pip install uv
crewai install
crewai run
```

Para cambiar el tema, edita `inputs` en `src/taller_crewai/main.py`.
