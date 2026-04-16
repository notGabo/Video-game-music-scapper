from time import sleep
from funciones import clearConsole, buscadorVideoGameMusic, obtenerLinksDeAlbumes, obtenerHTML, GenerarObjetoAlbum, descargarRecurso, linkDirecto, decodearNombreCancion, textoColor, hiloDescarga
import threading
from os import getenv
from dotenv import load_dotenv

load_dotenv("config.ini")

WAITTIME = int(getenv("WAITTIME", 2))
headers = eval(getenv("headers", "{}"))

def main():
    clearConsole()
    query = input("Ingrese el nombre del videojuego o banda sonora que desea buscar: ")
    htmlBusqueda = buscadorVideoGameMusic(query, headers)

    threads = []
    
    # En caso de que el html a retornar sea none, significa que hubo un error y retornara para que se cierre el programa 
    if htmlBusqueda is None:
        print("Error al realizar la busqueda.")
        return
    
    # Obtener los links de los albumes y mostrarlos para hacer la seleccion
    linksAlbumes = obtenerLinksDeAlbumes(htmlBusqueda)
    for linkAlbum in linksAlbumes:
        indice = linksAlbumes.index(linkAlbum) + 1
        print(f"{indice}. {linkAlbum}")
    
    # Control de errores para la seleccion de los albumes a descargar
    while True:
        threads = []
        eleccion = input("Ingrese el numero del album que desea descargar, si se desea descargar multiples albums se deben separar por coma. Ej: 1,2,3 (0 para salir): ")
        try:
            if eleccion == "0":
                print("Saliendo del programa.")
                break
            indiceAlbumes = [int(i) - 1 for i in eleccion.split(",")]
            for indice in indiceAlbumes:
                nombreHilo = f"Hilo-{indice + 1}"
                # Numero del 0 al 9 para elegir el color del hilo, se asignara un color diferente a cada hilo para diferenciar las descargas. Se utiliza el indice, si el indice es mayor a 9, se operara con el modulo para asignar un color dentro del rango de 0 a 9.
                color = indice % 10 if indice % 10 in range(0, 10) else 10
                thread = threading.Thread(target=hiloDescarga, args=(WAITTIME, headers, linksAlbumes, [indice], nombreHilo, color))
                threads.append(thread)
                
            
            for t in threads:
                t.start()
                sleep(WAITTIME)

            for t in threads:
                t.join()

            
        except ValueError:
            textoColor(f"Entrada invalida, intente de nuevo.","rojo")

        

if __name__ == "__main__":
    main()