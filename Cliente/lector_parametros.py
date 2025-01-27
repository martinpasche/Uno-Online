import json
import socket
import sys

def obtener_parametros ():
    """
    Nos servirá para leer el archivo json
    y entregarnos un diccionario con los parametros
    """
    #el unico parametro pre definido es el path de la carpeta
    path_parametros = "parametros.json"

    with open(path_parametros, "rb") as file:
        dic_parametros = json.load(file)

    if dic_parametros.get("host"):
        try:
            host = dic_parametros["host"]
            host = host.strip()
            if host == "":
                host = socket.gethostname()
            
            dic_parametros["host"] = host
        
        except (TypeError, ValueError) as e:
            print(f"Error por archivo json en host:", e)
            sys.exit()
        
    else:
        dic_parametros["host"] = socket.gethostname()

    return dic_parametros




if __name__ == "__main__":

    dic = obtener_parametros()

    print("Host:\t", dic["host"], "\tPort:\t", dic["port"])


