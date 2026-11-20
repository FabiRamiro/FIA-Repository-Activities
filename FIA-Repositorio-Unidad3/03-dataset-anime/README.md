[↩ Volver a la Unidad 3](../README.md)

# Dataset de anime

Crawler que recorre un catálogo de anime en la web y construye un dataset con el título, la reseña y los géneros de cada título. Respeta `robots.txt`, hace pausas entre peticiones y se detiene tras 900 consultas como máximo.

| Archivo | Contenido |
|---|---|
| [crawler_anime.py](crawler_anime.py) | Crawler comentado línea por línea. |
| [animes_html.csv](animes_html.csv) | Dataset obtenido (`titulo`, `resena`, `generos`). |

```bash
pip install requests beautifulsoup4
python crawler_anime.py
```
