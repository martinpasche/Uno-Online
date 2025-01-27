from PyQt5.QtCore import QObject, pyqtSignal
from collections import namedtuple
import socket
import threading
import json
import sys
import time

Carta = namedtuple("Carta_type", ["color", "tipo", "imagen"])


class Cliente (QObject):

    senal_error_conexion = pyqtSignal(str)
    senal_ventana_inicio = pyqtSignal()
    senal_error_nombre = pyqtSignal()
    senal_entrar_espera = pyqtSignal(list, int)
    senal_sala_llena = pyqtSignal()
    senal_mostrar_chat = pyqtSignal(str, str)
    senal_enviar_cartas = pyqtSignal(list)
    senal_enviar_nombres = pyqtSignal(dict)
    senal_turno_color_sacar = pyqtSignal(str, str, str)
    senal_pozo = pyqtSignal(tuple)
    senal_escoger_color = pyqtSignal()
    senal_avisar_cambio_color = pyqtSignal(str, str)
    senal_act_perdedores = pyqtSignal(list)
    senal_fin_partida = pyqtSignal(str)

    def __init__(self, parametros):
        super().__init__()
        self.parametros = parametros
        self.host = parametros["host"]
        self.port = parametros["port"]
        self.nombre = ""
        self.socket_cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    def start(self):
        self.senal_ventana_inicio.emit()
        try:
            self.socket_cliente.connect((self.host, self.port))

            self.thread_escuchar = threading.Thread(
                target=self.escuchar_servidor,
                daemon=True,
            )
            self.thread_escuchar.start()
        
        except ConnectionError as error:
            print(error)
            print(f"Error no se pudo conectar al servidor {self.host}")
            self.socket_cliente.close()
            self.senal_error_conexion.emit(str(error))

        #entrar a la ventana de espera

    def confirmar_nombre_usuario(self, name):
        self.nombre = name.strip().upper()
        self.enviar({
            "nombre" : self.nombre,
        })

    def enviar_chat(self, chat):
        self.enviar({
            "chat" : chat.strip(),
        })

    def enviar_botar_carta(self, tupla_carta):
        #si es de color, se pide al usuario que envie el color
        self.enviar({
            "accion" : True, "botar" : tupla_carta,
        })

    def enviar_robar_carta(self):
        self.enviar({
            "accion" : True, "robar" : True,
        })

    def enviar_color(self, color):
        self.enviar({
            "color" : color,
        })

    def enviar_dccuatro(self):
        self.enviar({
            "accion" : True, "dccuatro" : True,
        })

    def iniciar_nueva_partida(self):
        #no la haremos self.start()
        pass


    def enviar(self, mensaje):
        #mensaje es un diccionario
        mensaje_json = json.dumps(mensaje)
        mensaje_json_bytes = mensaje_json.encode("utf-8")
        mensaje_json_size_bytes = len(mensaje_json_bytes).to_bytes(4, byteorder="big")
        self.socket_cliente.sendall(mensaje_json_size_bytes + mensaje_json_bytes)




    def escuchar_servidor(self):
        try:
            while True:
                dic_size_bytes = self.socket_cliente.recv(4)
                dic_size = int.from_bytes(dic_size_bytes, byteorder="big")
                dic_bytes = bytearray()
                while len(dic_bytes) < dic_size:
                    read_size = min(128, dic_size - len(dic_bytes))
                    dic_bytes.extend(self.socket_cliente.recv(read_size))

                dic = dic_bytes.decode(encoding="utf-8")

                if dic != "":
                    dic_real = json.loads(dic)
                    
                    if dic_real.get("entrar"):
                        jugadores = dic_real["jugadores"]
                        cantidad_jugadores = dic_real["cantidad jugadores"]
                        self.senal_entrar_espera.emit(jugadores, cantidad_jugadores)

                    elif dic_real.get("chat"):
                        chat = dic_real["chat"]
                        cliente_enviador = dic_real["cliente"]
                        self.senal_mostrar_chat.emit(chat, cliente_enviador)
                    
                    elif dic_real.get("error"):
                        if dic_real["error"] == "nombre":
                            self.senal_error_nombre.emit()
                        elif dic_real["error"] == "sala llena":
                            self.senal_error_conexion.emit("Sala llena")

                    elif dic_real.get("pedir color"):
                        self.senal_escoger_color.emit()

                    elif dic_real.get("color cambiado"):
                        self.senal_avisar_cambio_color.emit(
                            dic_real["usuario"], dic_real["color cambiado"])
                        

                    elif dic_real.get("nombres"):
                        #contiene una lista con los nombres de los participantes
                        #esta en orden
                        self.senal_enviar_nombres.emit({
                            "nombres" : dic_real["nombres"], "usuario" : self.nombre,
                        })

                    elif dic_real.get("perdedores"):
                        self.senal_act_perdedores.emit(dic_real["perdedores"])

                    elif dic_real.get("turno"):
                        #recibe el nombre del usuario que le toca en el turno y el color jugando
                        self.senal_turno_color_sacar.emit(
                            dic_real["turno"], dic_real["color"], dic_real["cantidad sacar"])

                    elif dic_real.get("pozo"):
                        id_bytes = self.socket_cliente.recv(4)
                        identificador = int.from_bytes(id_bytes, byteorder="big")
                        #recibir cartas
                        while identificador != 0:
                            #tamaño
                            info_size_bytes = self.socket_cliente.recv(4)
                            info_size = int.from_bytes(info_size_bytes, byteorder="little")
                            info_bytes = bytearray()
                            while len(info_bytes) < info_size:
                                read_size = min(128, info_size - len(info_bytes))
                                info_bytes.extend(self.socket_cliente.recv(read_size))
                              
                            if identificador == 1:
                                info = info_bytes.decode("utf-8")
                                color = info

                            elif identificador == 2:
                                info = info_bytes.decode("utf-8")
                                tipo = info

                            elif identificador == 3:
                                #se envia como un tuple
                                self.senal_pozo.emit((Carta(color, tipo, info_bytes)))
                          
                            id_bytes = self.socket_cliente.recv(4)
                            identificador = int.from_bytes(id_bytes, byteorder="big")


                    elif dic_real.get("nombre"):
                        #jugador es una lista, [nombre, [cartas]]
                        jugador = list()
                        jugador.append(dic_real["nombre"])
                        mazo = list()

                        #nos dirá si vienen cartas o no
                        id_bytes = self.socket_cliente.recv(4)
                        identificador = int.from_bytes(id_bytes, byteorder="big")
                        
                        #recibir cartas
                        while identificador != 0:
                            #tamaño
                            info_size_bytes = self.socket_cliente.recv(4)
                            info_size = int.from_bytes(info_size_bytes, byteorder="little")
                            info_bytes = bytearray()
                            while len(info_bytes) < info_size:
                                read_size = min(128, info_size - len(info_bytes))
                                info_bytes.extend(self.socket_cliente.recv(read_size))
                              
                            if identificador == 1:
                                info = info_bytes.decode("utf-8")
                                color = info

                            elif identificador == 2:
                                info = info_bytes.decode("utf-8")
                                tipo = info

                            elif identificador == 3:
                                mazo.append(Carta(color, tipo, info_bytes))

                                
                            id_bytes = self.socket_cliente.recv(4)
                            identificador = int.from_bytes(id_bytes, byteorder="big")
                            
                        jugador.append(mazo)
                        self.senal_enviar_cartas.emit(jugador)


                    elif dic_real.get("ganador"):
                        self.senal_fin_partida.emit(dic_real["ganador"])
                        break
                            

        except ConnectionError as error:
            print(error)
            print(f"Error de conexion {self.host}")
            self.socket_cliente.close()
            self.senal_error_conexion.emit(str(error))

        else:
            time.sleep(5)
            self.socket_cliente.close()





        