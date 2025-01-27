from funciones_ext import logs, connection_error_script
import os
import json
import socket
import back_end
import threading
import time

class Servidor:

    locket_socket_clientes = threading.Lock()
    locket_usuarios_conectados = threading.Lock()
    locket_partida_activa = threading.Lock()
    pedir_info_partida = threading.Event()
    pedir_info_servidor = threading.Event()

    def __init__(self, host, port, parametros):
        self.parametros = parametros
        self.socket_clientes = dict()
        self.__cantidad_jugadores = parametros["cantidad_jugadores"]
        self.usuarios_conectados = 0
        self._partida_activa = False
        self.partida = back_end.DCCuatro(
            parametros, self.pedir_info_partida, self.pedir_info_servidor)
        self.perdedores = list()
        self.path_cartas = os.path.join(*parametros["path_cartas"].split(","))
        with open(os.path.join(*parametros["path_reverso_carta"].split(",")), "rb") as archivo:
            imagen_reverso = archivo.read()
        imagen_reverso_largo = len(imagen_reverso).to_bytes(4, byteorder="little")
        self.imagen_reverso_bytes_completa = imagen_reverso_largo + imagen_reverso
        self.reiniciar_partida = False

        print("Iniciando servidor...")

        self.host = host
        self.port = port

        #IPv4 y tcp
        self.socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        #ligar socket a la direccion y puerto
        self.socket_server.bind((host, port))

        #empezar a escuchar por clientes
        self.socket_server.listen()
        print(f"Servidor escuchando host: {self.host} y puerta: {self.port}")

        
        thread = threading.Thread(target=self.conectar_varios_clientes, daemon=True)
        thread.start()

        #thread para saber cuando comenzar la partida
        thread_partida_activa = threading.Thread(
            target=self.confirmar_inicio_partida, daemon= True)
        thread_partida_activa.start()

    @property
    def cantidad_jugadores(self):
        return self.__cantidad_jugadores

    def confirmar_inicio_partida(self):
        self.locket_partida_activa.acquire()
        while not self._partida_activa:
            self.locket_partida_activa.release()
            time.sleep(1)
            with self.locket_usuarios_conectados:
                #esto nos dira cuando todos los usuarios se conectaron
                #es la unica forma de cambiar self._partida_activa
                if self.usuarios_conectados >= self.cantidad_jugadores:
                    with self.locket_partida_activa:
                        self._partida_activa = True
            self.locket_partida_activa.acquire()

        self.locket_partida_activa.release()
        #avisar que partida comenzo
        with self.locket_socket_clientes:
            sockets = dict(self.socket_clientes)
        self.partida.iniciar_partida(sockets)

        thread_escuchar_partida = threading.Thread(
            target=self.escuchar_partida, daemon=True
        )
        thread_escuchar_partida.start()     

    def conectar_varios_clientes(self):
        numero = 1

        while True:
            socket_cliente, _ = self.socket_server.accept()
            logs(F"Cliente {numero}", "Conexion Aceptada", "-")
            thread_escuchar_ventana_cliente = threading.Thread(
                target=self.escuchar_ventana_inicio,
                args=(socket_cliente, numero, ),
                daemon=True,
            )
            thread_escuchar_ventana_cliente.start()
            numero += 1

    def escuchar_ventana_inicio(self, socket_cliente, numero):

        try:
            #este ciclo escuchara por el nombre de usuario
            while True:      
                name_size_bytes = socket_cliente.recv(4)
                name_size = int.from_bytes(name_size_bytes, byteorder="big")
                name_bytes = bytearray()
                while len(name_bytes) < name_size:
                    read_size = min(128, name_size - len(name_bytes))
                    name_bytes.extend(socket_cliente.recv(read_size))
                name = name_bytes.decode(encoding="utf-8")

                #se envio un string
                if name != "":
                    dic = json.loads(name)
                    nombre = dic["nombre"]

                    #si no es alfanumerico, se envia un error
                    if not nombre.isalnum():
                        logs(f"Cliente {numero}", "Nombre erroneo", str(nombre))
                        mensaje = {"error" : "nombre"}
                        self.enviar(socket_cliente, mensaje, numero)
                    #es alfanumerico
                    else:

                        self.locket_socket_clientes.acquire()
                        self.locket_usuarios_conectados.acquire()
                        with self.locket_partida_activa:
                            if self.socket_clientes.get(nombre):
                                self.locket_socket_clientes.release()
                                self.locket_usuarios_conectados.release()
                                #nombre repetido
                                logs(f"Cliente {numero}", "Nombre Repetido", str(nombre))
                                mensaje = {"error" : "nombre"}
                                self.enviar(socket_cliente, mensaje, numero)

                            elif (self.usuarios_conectados >= self.cantidad_jugadores 
                                    or self._partida_activa):
                                self.locket_usuarios_conectados.release()
                                self.locket_socket_clientes.release()
                                #levantamos excepcion para cerrar thread y socket
                                raise ValueError("Sala llena")
                            
                            else:
                                self.socket_clientes[nombre] = socket_cliente
                                logs(f"Cliente {numero}", "Nuevo nombre", str(nombre))
                                nombres = list(self.socket_clientes.keys())
                                self.usuarios_conectados += 1
                                self.locket_socket_clientes.release()
                                self.locket_usuarios_conectados.release()
                                self.enviar_todos({
                                    "entrar" : True, "jugadores" : nombres, "nombre" : nombre,
                                    "cantidad jugadores" : self.cantidad_jugadores,
                                })
                                break
                        
        
        except ConnectionError as error:
            logs(f"Cliente {numero}", "Error conexion", str(error))
            mensaje = {"cerrar" : True}
            socket_cliente.close()

        except ValueError as error:
            logs(f"Cliente {numero}", "Error conexion", str(error))
            mensaje = {"error" : "sala llena"}
            self.enviar(socket_cliente, mensaje, numero)
            socket_cliente.close()

        else:
            thread_escuchar_ventanas = threading.Thread(
                target=self.escuchar_ventanas,
                args=(socket_cliente, nombre, ),
                daemon=True,
            )
            thread_escuchar_ventanas.start()
    
    def escuchar_ventanas(self, socket_cliente, nombre):
        try:
            while True:
                respuesta_largo_bytes = socket_cliente.recv(4)
                respuesta_largo = int.from_bytes(respuesta_largo_bytes, byteorder="big")
                respuesta = bytearray()
                while len(respuesta) < respuesta_largo:
                    leer_largo = min(128, respuesta_largo - len(respuesta))
                    respuesta.extend(socket_cliente.recv(leer_largo))

                mensaje_json = respuesta.decode(encoding="utf-8")
                if mensaje_json != "":
                    mensaje = json.loads(mensaje_json)
                    if mensaje.get("chat"):
                        logs(nombre, "envia mensaje", mensaje["chat"])
                        self.enviar_todos({"chat" : mensaje["chat"], "cliente" : nombre})
                    
                    elif mensaje.get("accion"):
                        self.revisar_accion(nombre, mensaje, socket_cliente)

                    elif mensaje.get("color"):
                        self.color_escogido(nombre, mensaje)
                    
                     
        except ConnectionError as error:
            connection_error_script(self, nombre, error)
            with self.locket_socket_clientes:
                jugadores = list(self.socket_clientes.keys())
            self.enviar_todos({"entrar" : True, "jugadores" : jugadores, 
                "cantidad jugadores" : self.cantidad_jugadores})

    def escuchar_partida(self):
        logs("Servidor", "escuchando partida")
        self.pedir_info_partida.wait()
        self.pedir_info_partida.clear()

        turno, color, pozo, sacar = self.partida.turno_color_pozo()
        self.enviar_todos({"turno" : turno, "color" : color, "cantidad sacar" : sacar})
        self.enviar_todos_pozo(pozo)

        #la primera vez le entregamos a los clientes los usuarios conectado
        jugadores, self.perdedores= self.partida.actualizar_interfaces()
        nombres = [i[0] for i in jugadores]
        self.enviar_todos({"nombres" : nombres})

        self.enviar_todos_cartas(jugadores)
        self.enviar_todos({"perdedores" : self.perdedores})

        if pozo[0] == "color":
            #hay que pedir color al usuario
            logs(turno, "Preguntando color")
            self.enviar(self.socket_clientes[turno], {"pedir color" : True}, turno)

        self._partida_activa = self.partida.situacion_partida()

        while self._partida_activa:
            
            self.pedir_info_partida.wait()
            self.pedir_info_partida.clear()

            ganador = self.partida.enviar_ganador()
            if ganador:
                self.enviar_todos({"ganador" : ganador[0]})
            else:
                jugadores, self.perdedores = self.partida.actualizar_interfaces()

                self.enviar_todos_cartas(jugadores)
                self.enviar_todos({"perdedores" : self.perdedores})
                turno, color, pozo, sacar = self.partida.turno_color_pozo()
                self.enviar_todos({"turno" : turno, "color" : color, "cantidad sacar" : sacar})
                self.enviar_todos_pozo(pozo)
            self._partida_activa = self.partida.situacion_partida()
        ganador = self.partida.enviar_ganador()
        if ganador:
            self.enviar_todos({"ganador" : ganador[0]})

        time.sleep(5)
        self.reiniciar_partida = True
        



    def revisar_accion(self, nombre, dic_accion, socket_cliente):
        if nombre in self.perdedores:
            return
        if dic_accion.get("dccuatro"):
            respuesta = self.partida.confirmar_dccuatro(nombre)
            logs(nombre, "Grito dccuatro", respuesta)
            self.enviar_todos({"chat" : respuesta, "cliente" : nombre})
            jugadores, self.perdedores = self.partida.actualizar_interfaces()

            self.enviar_todos_cartas(jugadores)
            self.enviar_todos({"perdedores" : self.perdedores})

        elif not self.pedir_info_servidor.is_set():
            if dic_accion.get("botar"):
                if self.partida.confirmar_botar_carta(nombre, {"carta" : dic_accion["botar"]}):
                    if dic_accion["botar"][0] == "color" and not self.partida.sacar_multiple > 0:
                        #se le pide al usuario un cambio de color
                        logs(nombre, "Preguntando color")
                        self.enviar(socket_cliente, {"pedir color" : True}, nombre)
                    self.pedir_info_servidor.set()
                    
            elif dic_accion.get("robar"):
                if self.partida.confirmar_robar_carta(nombre, {"sacar" : True}):
                    self.pedir_info_servidor.set()
        else:
            logs(nombre, "Accion cuando partida procesa", "accion denegada")


    def color_escogido(self, nombre, dic_color):
        aprobacion = self.partida.partida_color_escogido(dic_color["color"])
        if aprobacion:
            self.enviar_todos({"color cambiado" : dic_color["color"], "usuario" : nombre})
        self.pedir_info_servidor.set()

    def avisar_partida_usuario_desconectado (self, nombre):
        if nombre in self.socket_clientes.keys():
            logs("Servidor", "Usuario desconectado", nombre)
            self.partida.jugador_desconectado(nombre)

    def enviar_todos_cartas(self, jugadores):
        """
        El protocolo de envio será el siguiente:
        Primero se enviara un mensaje diciendo que llegaran cartas,
        luego se envia el nombre del jugador y despues se envian las 
        las cartas. Despues esto se repite para los siguientes jugadores.
        """
        for lista_jugador in jugadores:
            
            self.enviar_todos({"nombre" : lista_jugador[0]})

            #el cliente sabra que no hay más cartas pq el id será 0
            for carta in lista_jugador[2]:

                #color
                id_color_bytes = int(1).to_bytes(4, byteorder="big")
                color_bytes = carta[1].encode("utf-8")
                color_bytes_largo = len(color_bytes).to_bytes(4, byteorder="little")
                
                #tipo
                id_tipo_bytes = int(2).to_bytes(4, byteorder="big")
                tipo_bytes = carta[0].encode("utf-8")
                tipo_bytes_largo = len(tipo_bytes).to_bytes(4, byteorder="little")

                #imagen
                id_imagen_bytes = int(3).to_bytes(4, byteorder="big")
                #carta normal
                path_carta = os.path.join(self.path_cartas, f"{carta[0]}_{carta[1]}.png")
                with open(path_carta, "rb") as imagen:
                    imagen_bytes = imagen.read()
                imagen_bytes_largo = len(imagen_bytes).to_bytes(4, byteorder="little")

                bytes_principal = id_color_bytes + color_bytes_largo + color_bytes
                bytes_principal += id_tipo_bytes + tipo_bytes_largo + tipo_bytes
                bytes_principal += id_imagen_bytes #+ imagen_bytes_largo + imagen_bytes
                
                with self.locket_socket_clientes:
                    nombres = list(self.socket_clientes.keys())
                    for nombre in nombres:
                        if nombre == lista_jugador[0]:
                            bytes_enviar = bytes_principal + imagen_bytes_largo + imagen_bytes
                        else:
                            bytes_enviar = bytes_principal + self.imagen_reverso_bytes_completa
                        try:
                            self.socket_clientes[nombre].sendall(bytes_enviar)
                        except ConnectionError as error:
                            connection_error_script(self, nombre, error)
                        except IndexError as error:
                            logs(f"{nombre}", "no existe socket", str(error))

                    
            #hay que enviar un 0 para indicar que no se enviaran mas cartas del jugador
            id_no_info = int(0).to_bytes(4, byteorder="big")
            self.enviar_todos_bytes(id_no_info) 

    def enviar_todos_pozo(self, carta):
        #color
        id_color_bytes = int(1).to_bytes(4, byteorder="big")
        color_bytes = carta[1].encode("utf-8")
        color_bytes_largo = len(color_bytes).to_bytes(4, byteorder="little")
                
        #tipo
        id_tipo_bytes = int(2).to_bytes(4, byteorder="big")
        tipo_bytes = carta[0].encode("utf-8")
        tipo_bytes_largo = len(tipo_bytes).to_bytes(4, byteorder="little")

        #imagen
        id_imagen_bytes = int(3).to_bytes(4, byteorder="big")
        #carta normal
        path_carta = os.path.join(self.path_cartas, f"{carta[0]}_{carta[1]}.png")
        with open(path_carta, "rb") as imagen:
            imagen_bytes = imagen.read()
        imagen_bytes_largo = len(imagen_bytes).to_bytes(4, byteorder="little")

        bytes_principal = id_color_bytes + color_bytes_largo + color_bytes
        bytes_principal += id_tipo_bytes + tipo_bytes_largo + tipo_bytes
        bytes_principal += id_imagen_bytes + imagen_bytes_largo + imagen_bytes

        self.enviar_todos({"pozo" : True})
        self.enviar_todos_bytes(bytes_principal)                    
        #hay que enviar un 0 para indicar que no se enviaran mas cartas del jugador
        id_no_info = int(0).to_bytes(4, byteorder="big")
        self.enviar_todos_bytes(id_no_info)


    def enviar_todos_bytes(self, mensaje_bytes):
        with self.locket_socket_clientes:
            nombres = list(self.socket_clientes.keys())
            for nombre in nombres:
                try:
                    self.socket_clientes[nombre].sendall(mensaje_bytes)
                except ConnectionError as error:
                    connection_error_script(self, nombre, error)
                except IndexError as error:
                    logs(f"{nombre}", "no existe socket", str(error))
        

    def enviar(self, socket_cliente, mensaje, identidad):
        #envia un diccionario
        try:
            mensaje_json = json.dumps(mensaje)
            mensaje_json_bytes = mensaje_json.encode("utf-8")
            mensaje_json_size_bytes = len(mensaje_json_bytes).to_bytes(4, byteorder="big")
            socket_cliente.sendall(mensaje_json_size_bytes + mensaje_json_bytes)
        except ConnectionError as error:
            if isinstance(identidad, str): #es un nombre
                logs(identidad, "Perdida de conexion enviar", str(error))
            else: #es un numero
                logs(f"Cliente {identidad}", "Perdida de conexion", str(error))
            socket_cliente.close()

    def enviar_todos(self, mensaje):
        #envia un diccionario en formato json
        mensaje_json = json.dumps(mensaje)
        mensaje_json_bytes = mensaje_json.encode("utf-8")
        mensaje_json_size_bytes = len(mensaje_json_bytes).to_bytes(4, byteorder="big")
        with self.locket_socket_clientes:
            nombres = list(self.socket_clientes.keys())
            for nombre in nombres:
                try:
                    self.socket_clientes[nombre].sendall(mensaje_json_size_bytes + mensaje_json_bytes)
                except ConnectionError as error:
                    connection_error_script(self, nombre, error)
                except IndexError as error:
                    logs(f"{nombre}", "no existe socket", str(error))

