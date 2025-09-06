import requests
from time import sleep
from bs4 import BeautifulSoup
import os
from funciones import clearConsole, buscadorVideoGameMusic, obtenerLinksDeAlbumes, obtenerHTML, GenerarObjetoAlbum, descargarRecurso, linkDirecto

def main():
    # Constantes
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    remplazoPalabras = {
        "%20": " ",
        "%2520": " ",
        "%255B": "[",
        "%255D": "]",
        "%5B": "[",
        "%5D": "]",
        "%27": "'",
        "%28": "(",
        "%29": ")",
        "%233": "#",
        "%2527": "'",
    }
    WAITTIME = 10  # segundos
    query = input("Ingrese el nombre del videojuego o banda sonora que desea buscar: ")
    htmlBusqueda = buscadorVideoGameMusic(query, headers)
    sleep(WAITTIME)
    if htmlBusqueda is None:
        print("Error al realizar la busqueda.")
        return
    linksAlbumes = obtenerLinksDeAlbumes(htmlBusqueda)
    for linkAlbum in linksAlbumes:
        indice = linksAlbumes.index(linkAlbum) + 1
        print(f"{indice}. {linkAlbum}")
    while True:
        try:
            eleccion = input("Ingrese el numero del album que desea descargar, si se desea descargar multiples albums se deben separar por coma. Ej: 1,2,3 (0 para salir): ")
            if eleccion == "0":
                print("Saliendo del programa.")
                break
            indices = [int(i) - 1 for i in eleccion.split(",")]
            clearConsole()
            for indice in indices:
                print(f"Descargando album {linksAlbumes[indice]}")
                htmlAlbum = obtenerHTML(linksAlbumes[indice], headers)
                if htmlAlbum is None:
                    print(f"Error al obtener el album {linksAlbumes[indice]}")
                    continue
                objetoAlbum = GenerarObjetoAlbum(htmlAlbum)
                print(f"nombre album: {objetoAlbum['nombreAlbum']}")
                print(f"año: {objetoAlbum['anio']}")
                print(f"link caratula: {objetoAlbum['linkCaratula']}")
                print(f"nombre carpeta: {objetoAlbum['nombreCarpeta']}")
                print(f"cantidad de canciones: {len(objetoAlbum['linksCanciones'])}")
                print("-------------------")
                # generar carpeta
                print(f"Creando carpeta {objetoAlbum['nombreCarpeta']}")
                if not os.path.exists(objetoAlbum['nombreCarpeta']):
                    os.makedirs(objetoAlbum['nombreCarpeta'])
                print("Descargando caratula...")
                rutaCaratula = os.path.join(objetoAlbum['nombreCarpeta'], f"{objetoAlbum['nombreAlbum']}.jpg")
                descargarRecurso(objetoAlbum['linkCaratula'], rutaCaratula, headers)
                print("Esperando 5 segundos para iniciar las descargas de las canciones...")
                sleep(WAITTIME)
                print("Iniciando descargas, se preferiran archivos flac por sobre otros...")
                for linkCancion in objetoAlbum['linksCanciones']:
                    cargaPaginaCancion = obtenerHTML(linkCancion, headers)
                    if cargaPaginaCancion is None:
                        print(f"Error al cargar la pagina de la cancion {linkCancion}, saltando descarga...")
                        continue
                    linkCancion = linkDirecto(cargaPaginaCancion)[0]
                    if linkCancion is None:
                        print(f"No se encontro link de descarga para la cancion {linkCancion}, saltando descarga...")
                        continue
                    nombreArchivo = linkCancion.split("/")[-1]
                    for clave, valor in remplazoPalabras.items():
                        nombreArchivo = nombreArchivo.replace(clave, valor)
                    rutaGuardar = os.path.join(objetoAlbum['nombreCarpeta'], nombreArchivo)
                    print(f"Descargando {nombreArchivo}...")
                    exito = descargarRecurso(linkCancion, rutaGuardar, headers)
                    if exito:
                        print(f"{nombreArchivo} descargado correctamente.")
                    else:
                        print(f"Error al descargar {nombreArchivo}.")
                    print("Esperando 5 segundos para la siguiente descarga y no saturar el servidor...")
                    sleep(WAITTIME)
            print("Descarga completada. en 5 segundos se limpiara la consola.")
            sleep(WAITTIME)
            clearConsole()
            for linkAlbum in linksAlbumes:
                indice = linksAlbumes.index(linkAlbum) + 1
                print(f"{indice}. {linkAlbum}")
        except ValueError:
            print("Entrada invalida, intente de nuevo.")
            continue

if __name__ == "__main__":
    main()