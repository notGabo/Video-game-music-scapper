import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import os

def textoColor(texto, color):
    colores = {
        -1: "\033[91m", # rojo
        0: "\033[95m", # magenta
        1: "\033[94m", # azul
        2: "\033[92m", # verde
        3: "\033[93m", # amarillo
        4: "\033[96m", # cyan
        5: "\033[90m", # gris
        6: "\033[91m", # rojo claro
        7: "\033[97m", # blanco
        8: "\033[38;5;208m", # naranja
        9: "\033[38;5;201m", # rosa

    }
    if color not in colores:
        print(texto)
        return
    reinicio = "\033[0m"
    colorSeleccionado = colores.get(color, "\033[0m")
    print(f"{colorSeleccionado}{texto}{reinicio}")

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
    tablaCanciones = tablaCanciones.find_all('tr')[1:-1]

    print(f"Cantidad de canciones en el album {nombreAlbum}: {len(tablaCanciones)}")
    for fila in tablaCanciones:
        try:
            celdasCancion = fila.find_all('td', class_='clickable-row')
            link = celdasCancion[0].find('a')['href']
            objetoAlbum["linksCanciones"].append(f"https://downloads.khinsider.com/{link}")
        except Exception as e:
            print(f"Error al obtener el link de la cancion, saltando descarga... Error: {e}")
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

def decodearNombreCancion(nombre:str):
    """
    Este metodo se encargara de decodificar el nombre de la cancion, ya que algunos caracteres pueden estar codificados.
    Ej: %20 es un espacio, %5B es [, %5D es ], etc.
    """
    return unquote(nombre, encoding='utf-8', errors='replace').lstrip()

def hiloDescarga(WAITTIME: int, headers: dict, linksAlbumes: list, indiceAlbumes: list, nombreHilo: str = "", color: str = ""):
    caracteresProhibidos = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
    # Comienza ciclo de descarga
    for indiceAlbume in indiceAlbumes:
        # Obtener el html del album seleccionado, en caso de que sea none, se saltara la descarga de ese album
        htmlAlbum = obtenerHTML(linksAlbumes[indiceAlbume], headers)
        if htmlAlbum is None:
            textoColor(f"Error al obtener el album {linksAlbumes[indiceAlbume]}, saltando descarga...",11)
            continue
        objetoAlbum = GenerarObjetoAlbum(htmlAlbum)
        textoColor(f"[{nombreHilo}] [{indiceAlbume + 1}/{len(indiceAlbumes)}] nombre album: {objetoAlbum['nombreAlbum']}",color)
        textoColor(f"[{nombreHilo}] cantidad de canciones: {len(objetoAlbum['linksCanciones'])}",color)
        
        # Crear carpeta del album, si ya existe se saltara este paso
        if any(character in objetoAlbum['nombreCarpeta'] for character in caracteresProhibidos):
            for character in caracteresProhibidos:
                objetoAlbum['nombreCarpeta'] = objetoAlbum['nombreCarpeta'].replace(character, " ")
        if not os.path.exists(objetoAlbum['nombreCarpeta']):
            os.makedirs(objetoAlbum['nombreCarpeta'])
        
        # Descargar contenido del album
        rutaCaratula = os.path.join(objetoAlbum['nombreCarpeta'], f"{objetoAlbum['nombreAlbum']}.png")
        descargarRecurso(objetoAlbum['linkCaratula'], rutaCaratula, headers)
    
        # Descargar canciones del album
        for linkCancion in objetoAlbum['linksCanciones']:
            textoColor(f"[{nombreHilo}] [{objetoAlbum['linksCanciones'].index(linkCancion) + 1}/{len(objetoAlbum['linksCanciones'])}] Obteniendo link de descarga para la cancion {linkCancion}...", color)
            
            # Obtener el html de la pagina de la cancion, en caso de que sea none, se saltara la descarga de esa cancion
            cargarPaginaCancion = obtenerHTML(linkCancion, headers)
            if cargarPaginaCancion is None:
                textoColor(f"[{nombreHilo}] Error al cargar la pagina de la cancion {linkCancion}, saltando descarga...",-1)
                continue

            # En caso de que el link de descarga sea none, se saltara la descarga de esa cancion
            linkCancion = linkDirecto(cargarPaginaCancion)[0]
            if linkCancion is None:
                textoColor(f"[{nombreHilo}] No se encontro link de descarga para la cancion {linkCancion}, saltando descarga...",-1)
                continue
            nombreArchivo = linkCancion.split("/")[-1]
            nombreArchivo = decodearNombreCancion(nombreArchivo)

            # Ruta a guardar la cancion, se guardara dentro de la carpeta del album
            rutaGuardar = os.path.join(objetoAlbum['nombreCarpeta'], nombreArchivo)
            exito = descargarRecurso(linkCancion, rutaGuardar, headers)
            if exito:
                textoColor(f"[{nombreHilo}] {nombreArchivo} descargado correctamente.",color)
            else:
                textoColor(f"[{nombreHilo}] Error al descargar {nombreArchivo}.",-1)
            textoColor(f"[{nombreHilo}] Esperando {WAITTIME} segundos para la siguiente descarga y no saturar el servidor...",color)
    textoColor(f"[{nombreHilo}] Descarga del album {objetoAlbum['nombreAlbum']} completada.",color)