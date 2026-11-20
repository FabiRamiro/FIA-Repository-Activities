"""
Crawler de Anime para la materia de Fundamentos de IA con el proposito de aprender
"""

#Para la habilidad de leer y escribir en CSV
import csv
#Es para poder buscar patrones dentro de textos o mejor dicho expresiones regulares
import re
#Es para poder trabajar con tiempos y pausas
import time
#Collections es un módulo que contiene estructuras de datos especializadas. deque permite agregar y retirar elementos eficientemente
from collections import deque
#Sirve para manejar URLs. Con urljoin construye una URL completa, urlparse separa una URL en sus componentes y urldefrag elimina fragmentos de una URL
from urllib.parse import urljoin, urlparse, urldefrag
#Sirve esta clase para permitir interpretar las reglas publicadas en el archivo robots.txt de una página web
from urllib.robotparser import RobotFileParser

#Es una biblioteca que permite realizar solicitudes HTTP a servidores web
import requests
#Es una clase o herramienta que permite interpretar HTML y buscar etiquetas, atributos y textos
from bs4 import BeautifulSoup, Tag

URL_INICIAL = "https://tomatoanime.online/anime/sword-art-online"
DOMINIO = "tomatoanime.online"
URL_CATALOGO = f"https://{DOMINIO}/anime"
META = 300
MAX_CONSULTAS = 900
PAUSA_SEGUNDOS = 3
ARCHIVO = "animes_html.csv"
AGENTE = "ProyectoUniversitarioCrawler/1.0 (uso educativo)"

sesion = requests.Session()
sesion.headers.update({"User-Agent": AGENTE, "Accept": "text/html"})

def normalizar_url(enlace, base):
    """Convierte enlaces relativos a absolutos y descarta otros dominios."""
    url, _ = urldefrag(urljoin(base, enlace))
    partes = urlparse(url)
    if partes.scheme not in ("http", "https"):
        return None
    if partes.hostname not in (DOMINIO, "www." + DOMINIO):
        return None
    if not re.fullmatch(r"/anime/[a-zA-Z0-9_-]+/?", partes.path):
        return None
    return f"https://{DOMINIO}{partes.path.rstrip('/')}"


def normalizar_url_catalogo(enlace, base):
    """Convierte una URL de página del catálogo y conserva su paginación."""
    url, _ = urldefrag(urljoin(base, enlace))
    partes = urlparse(url)
    if partes.scheme not in ("http", "https"):
        return None
    if partes.hostname not in (DOMINIO, "www." + DOMINIO):
        return None
    if partes.path.rstrip("/") != "/anime":
        return None
    return f"https://{DOMINIO}/anime{('?' + partes.query) if partes.query else ''}"


def extraer_enlaces_catalogo(html, base):
    """Extrae animes y la siguiente página desde una página del catálogo."""
    soup = BeautifulSoup(html, "html.parser")
    enlaces = []
    for etiqueta in soup.select("a[href]"):
        href = etiqueta.get("href")
        if not isinstance(href, str):
            continue
        anime = normalizar_url(href, base)
        if anime:
            enlaces.append(anime)

    siguiente = soup.select_one('link[rel="next"], a[rel="next"]')
    if isinstance(siguiente, Tag):
        href = siguiente.get("href")
        if isinstance(href, str):
            pagina = normalizar_url_catalogo(href, base)
            if pagina:
                enlaces.append(pagina)
    return enlaces


def configurar_robots():
    """Consulta robots.txt; si no es legible, no inicia el rastreo."""
    robots = RobotFileParser()
    robots_url = f"https://{DOMINIO}/robots.txt"
    robots.set_url(robots_url)
    try:
        respuesta = sesion.get(robots_url, timeout=15)
        respuesta.raise_for_status()
        robots.parse(respuesta.text.splitlines())
        return robots
    except requests.RequestException as error:
        print(f"No se pudo verificar robots.txt: {error}")
        print("Por prudencia, se cancela el rastreo.")
        return None


def limpiar(texto):
    return " ".join(texto.split())


def extraer_anime(html):
    """Lee elementos HTML con BeautifulSoup; no consume ninguna API."""
    soup = BeautifulSoup(html, "html.parser")
    zona = soup.select_one("main") or soup
    titulo_tag = zona.find("h1")
    if not titulo_tag:
        return None, []
    titulo = limpiar(titulo_tag.get_text(" ", strip=True))

    # La sinopsis suele estar en un párrafo cercano a la cabecera.
    # Se detiene antes de la sección «Title details» para evitar texto extra.
    sinopsis = ""
    for elemento in titulo_tag.next_elements:
        if getattr(elemento, "name", None) in ("h2", "h3"):
            encabezado = limpiar(elemento.get_text(" ", strip=True)).lower()
            if encabezado in ("title details", "official trailers", "seasons"):
                break
        if getattr(elemento, "name", None) == "p":
            texto = limpiar(elemento.get_text(" ", strip=True))
            if len(texto) >= 60 and not texto.lower().startswith(titulo.lower() + " is a"):
                sinopsis = texto
                break

    # Géneros: localizar rótulo «Genres» y su valor (dt/dd, tabla u otro bloque).
    generos = []
    for tag in zona.find_all(["dt", "th", "strong", "h3", "span", "div"]):
        if limpiar(tag.get_text(" ", strip=True)).lower() == "genres":
            siguiente = tag.find_next_sibling(["dd", "td", "div", "span", "p"])
            if siguiente:
                generos = [limpiar(x) for x in siguiente.get_text(" ", strip=True).split(",") if x.strip()]
                if generos:
                    break
    # Respaldo: enlaces de género cerca del título, antes de la sección de detalles.
    if not generos:
        for etiqueta in titulo_tag.find_all_next("a", href=True):
            seccion = etiqueta.find_previous(["h2", "h3"])
            if seccion and limpiar(seccion.get_text(" ", strip=True)).lower() == "title details":
                break
            if not isinstance(etiqueta, Tag):
                continue
            href = etiqueta.get("href")
            if not isinstance(href, str):
                continue
            if "/genre" in href:
                nombre = limpiar(etiqueta.get_text(" ", strip=True))
                if nombre and nombre not in generos:
                    generos.append(nombre)

    # Enlaces exclusivamente dentro de las secciones «Recommended anime» y «Similar anime».
    relacionados = []
    for encabezado in zona.find_all(["h2", "h3"]):
        nombre = limpiar(encabezado.get_text(" ", strip=True)).lower()
        if nombre not in ("recommended anime", "similar anime"):
            continue
        for elemento in encabezado.next_elements:
            if elemento is encabezado:
                continue
            if getattr(elemento, "name", None) in ("h2", "h3"):
                break
            if not isinstance(elemento, Tag) or elemento.name != "a":
                continue
            href = elemento.get("href")
            if isinstance(href, str) and href:
                relacionados.append(href)

    if not (titulo and sinopsis and generos):
        return None, relacionados
    return {"titulo": titulo, "resena": sinopsis, "generos": ", ".join(generos)}, relacionados


def rastrear():
    if not 1 <= META <= 1000:
        raise ValueError("META debe estar entre 1 y 1000")
    robots = configurar_robots()
    if robots is None:
        return

    pendientes = deque([URL_INICIAL, URL_CATALOGO])
    descubiertas = {URL_INICIAL, URL_CATALOGO}
    visitadas = set()
    consultas = 0
    guardados = 0

    with open(ARCHIVO, "w", encoding="utf-8-sig", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=["titulo", "resena", "generos"])
        escritor.writeheader()

        while pendientes and guardados < META and consultas < MAX_CONSULTAS:
            url = pendientes.popleft()
            if url in visitadas:
                continue
            visitadas.add(url)
            if not robots.can_fetch(AGENTE, url):
                print(f"Omitida por robots.txt: {url}")
                continue

            if consultas:
                time.sleep(PAUSA_SEGUNDOS)
            consultas += 1
            try:
                respuesta = sesion.get(url, timeout=20)
                if respuesta.status_code in (403, 429):
                    print(f"Bloqueo o límite ({respuesta.status_code}). Se detiene el programa.")
                    break
                respuesta.raise_for_status()
                if "text/html" not in respuesta.headers.get("Content-Type", ""):
                    print("Respuesta no HTML; se omite.")
                    continue
            except requests.RequestException as error:
                print(f"Error en {url}: {error}")
                continue

            if urlparse(url).path.rstrip("/") == "/anime":
                enlaces = extraer_enlaces_catalogo(respuesta.text, url)
                anime = None
            else:
                anime, enlaces = extraer_anime(respuesta.text)
            if anime:
                escritor.writerow(anime)
                archivo.flush()
                guardados += 1
                print(f"[{guardados}/{META}] {anime['titulo']} ({consultas} consultas)")
            else:
                print(f"Sin campos completos: {url}")

            for enlace in enlaces:
                nuevo = normalizar_url(enlace, url)
                if nuevo is None:
                    nuevo = normalizar_url_catalogo(enlace, url)
                if nuevo and nuevo not in descubiertas:
                    descubiertas.add(nuevo)
                    pendientes.append(nuevo)

    print(f"Finalizado: {guardados} filas; {consultas} consultas. Archivo: {ARCHIVO}")


if __name__ == "__main__":
    rastrear()
