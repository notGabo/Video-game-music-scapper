import requests
from time import sleep
from bs4 import BeautifulSoup
import os
# import dotenv
# from dotenv import load_dotenv


# dotenv.load_dotenv()

def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')


def buscadorVideoGameMusic(query: str, headers: dict = None):
    query.replace(" ", "+")
    urlArmada = f"https://downloads.khinsider.com/search?search={query}"
    solicitud = requests.get(url=urlArmada, headers=headers)
    if solicitud.status_code == 200:
        return solicitud.content
    else:
        return None

def obtenerLinksDeAlbumes(html: str):
    links = []
    soup = BeautifulSoup(html, 'html.parser')
    tablaAlbums = soup.find('table', class_='albumList')
    if len(tablaAlbums) == 0:
        return None
    tablaAlbums = tablaAlbums.find_all('tr')[1:]
    for fila in tablaAlbums:
        link = fila.find('a')
        links.append(f"https://downloads.khinsider.com{link['href']}")
    return links


def obtenerHTML(link: str, headers: dict):
    solicitud = requests.get(url=link, headers=headers)
    if solicitud.status_code == 200:
        return solicitud.content
    else:
        return None

def linkDirecto(html: str):
    """
    Este metodo extraera el link directo de descarga desde la pagina de la cancion.
    """
    soup = BeautifulSoup(html, 'html.parser')
    pageContent = soup.find('div', id='pageContent')
    # buscar todos los anchor que tengan href y que terminen en .mp3 o flac
    linksDescargas = pageContent.find_all('a', href=True)
    linksDescargas = [link['href'] for link in linksDescargas if link['href'].endswith('.mp3') or link['href'].endswith('.flac')]
    # retornar el primer link que termine en .flac, si no hay ninguno retornar el primer link que termine en .mp3
    linksDescargas = sorted(linksDescargas, key=lambda x: (not x.endswith('.flac'), x))
    if len(linksDescargas) == 0:
        return None
    return linksDescargas

def GenerarObjetoAlbum(html: str):
    """
    Este metodo sera un poco mas complejo, ya que retornara un dict con la siguiente información
    {
        "nombreAlbum": str,
        "anio": str,
        "linkCaratula": str,
        "nombreCarpeta": str,
        "linksCanciones": [str]
    }
    El nombre de la carpeta sera una mezcla del año, artista y nombre del album.
    Ej: f"[anio] artista - nombreAlbum"
    El link de la caratula sera el link absoluto, no el relativo.
    linkCanciones sera una lista de links.
    """
    objetoAlbum = {
        "nombreAlbum": "",
        "anio": "",
        "linkCaratula": "",
        "nombreCarpeta": "",
        "linksCanciones": []
    }
    contadorErrores = 0
    soup = BeautifulSoup(html, 'html.parser')

    # Conseguir nombre album
    nombreAlbum = soup.find('h2').text
    # Conseguir año
    anio = soup.find('p', align='left').find('b').text

    # Conseguir link caratula
    albumImage = soup.find('div', class_='albumImage').find('a')['href']

    # Conseguir links canciones
    tablaCanciones = soup.find('table', id='songlist')
    tablaCanciones = tablaCanciones.find_all('tr')[1:]

    print(f"Cantidad de canciones en el album {nombreAlbum}: {len(tablaCanciones)}")
    for fila in tablaCanciones:
        try:
            celdasCancion = fila.find_all('td', class_='clickable-row')
            link = celdasCancion[0].find('a')['href']
            objetoAlbum["linksCanciones"].append(f"https://downloads.khinsider.com/{link}")
        except Exception as e:
            contadorErrores += 1
            continue
        objetoAlbum["anio"] = anio
    print(f"Se encontraron {contadorErrores} errores")

    objetoAlbum["nombreAlbum"] = nombreAlbum
    objetoAlbum["linkCaratula"] = albumImage
    objetoAlbum["anio"] = anio
    objetoAlbum["nombreCarpeta"] = f"[{anio}] {nombreAlbum}"

    return objetoAlbum

def descargarRecurso(link: str, rutaGuardar: str, headers: dict):
    """
    Este metodo descargara un recurso desde un link y lo guardara en la ruta especificada.
    """
    solicitud = requests.get(url=link, headers=headers)
    if solicitud.status_code == 200:
        with open(rutaGuardar, 'wb') as archivo:
            archivo.write(solicitud.content)
        return True
    else:
        return False

# print(linkDirecto(obtenerHTML("https://downloads.khinsider.com/game-soundtracks/album/cold-snap-2014/01.%2520Freedom.mp3", {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
#     })))

# print(GenerarObjetoAlbum(obtenerHTML("https://downloads.khinsider.com/game-soundtracks/album/cold-snap-2014", {
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
# #     })))
#     })))