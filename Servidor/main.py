from funciones_ext import logs, obtener_parametros
import servidor
import socket
import sys



if __name__ == "__main__":
    parametros = obtener_parametros()
    port = parametros["port"]
    host = socket.gethostname()

    try:
        print("CTRL + C para salir\n")
        server = servidor.Servidor(host, port, parametros)
        logs("Cliente", "Evento", "Detalles")
        logs("-" * 35, "-" * 35, "-" * 35)
        while True:
            if server.reiniciar_partida:
                server.socket_server.close()
                print("Reiniciar partida no fue implementado, byeeee")
                sys.exit(0)

    except KeyboardInterrupt:
        server.socket_server.close()
        print("Forzando cierra del server!")
        sys.exit(0)