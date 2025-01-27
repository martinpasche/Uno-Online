import json


def obtener_parametros ():
    """
    Nos servirá para leer el archivo json
    y entregarnos un diccionario con los parametros
    """
    #el unico parametro pre definido es el path de la carpeta
    path_parametros = "parametros.json"

    with open(path_parametros, "rb") as file:
        dic_parametros = json.load(file)

    return dic_parametros


def logs(obj1, obj2, obj3 = "-"):
    obj1 = str(obj1)
    obj2 = str(obj2)
    obj3 = str(obj3)
    texto = "{:^35}|{:^35}|{:^35}"
    print(texto.format(obj1, obj2, obj3))

def connection_error_script(servidor, nombre, error):
    servidor.avisar_partida_usuario_desconectado(nombre)
    logs(f"{nombre}", "Perdida de conexion", str(error))
    servidor.socket_clientes[nombre].close()
    with servidor.locket_socket_clientes:
        if servidor.socket_clientes.get(nombre):
            del servidor.socket_clientes[nombre]
    with servidor.locket_usuarios_conectados:
        servidor.usuarios_conectados -= 1
    if servidor._partida_activa:
        jugadores, perdedores = servidor.partida.actualizar_interfaces()
        if jugadores:
            servidor.enviar_todos_cartas(jugadores)
            servidor.enviar_todos({"perdedores" : perdedores})
            turno, color, pozo, sacar = servidor.partida.turno_color_pozo()
            servidor.enviar_todos({"turno" : turno, "color" : color, "cantidad sacar" : sacar})
            servidor.enviar_todos_pozo(pozo)
            servidor.enviar_todos({
                "chat" : f"{nombre} se ha desconectado", "cliente" : "Servidor"})



if __name__ == "__main__":

    dic = obtener_parametros()

    print("Host:\t", dic["host"], "\tPort:\t", dic["port"])


