from generador_de_mazos import sacar_cartas
from funciones_ext import logs
import random
import threading

class DCCuatro:

    lock_partida = threading.Lock()
    def __init__(self, parametros, flag_info_partida, flag_info_server):
        self.parametros = parametros
        self.cantidad_jugadores = parametros["cantidad_jugadores"]
        self.cantidad_cartas_iniciales = parametros["cartas_iniciales"]
        self.cartas_max = parametros["cartas_maximo"]
        self.dccuatro = parametros["dccuatro"]
        self.jugadores = list()
        self.partida_activa = True
        self.flag_info_partida = flag_info_partida
        self.flag_info_server = flag_info_server

        self.ganador = list()

        self.perdedores = list()

        #accion
        self.accion = dict()

        #color escogido por el usuario
        self.color_escogido = str()

        #representa la carta del pozo
        self.__pozo = tuple()

        #entregarle al usuario el color
        self.color = str()

        #acumulacion de +2, 0 para cuando no hay acumulacion
        self.sacar_multiple = 0

        #el sentido puede ser -1 o +1
        self.__sentido = 1 

        #representa el indice del jugador
        self.__jugador = 0

    @property
    def sentido(self):
        return self.__sentido 

    def cambiar_sentido(self):
        self.__sentido *= -1

    @property
    def jugador(self):
        return self.__jugador

    @jugador.setter
    def jugador(self, numero):
        if numero > len(self.jugadores) - 1:
            self.__jugador = 0
        elif numero < 0:
            self.__jugador = len(self.jugadores) - 1
        else:
            self.__jugador = numero

        #posible error cuadno los jugadores se salen d ela partida.

    @property
    def pozo(self):
        return self.__pozo

    @pozo.setter
    def pozo(self, carta):
        self.color = carta[1]
        self.__pozo = carta


    def jugador_desconectado(self, nombre):
        with self.lock_partida:
            self.perdedores.append(nombre)
            self.eliminar_jugador(nombre)

    def pasar_turno (self):
        self.jugador += self.sentido

    def eliminar_jugador(self, nombre):
        jugador_eliminar = list()
        for jugador in self.jugadores:
            if jugador[0] == nombre:
                jugador_eliminar = list(jugador)

        logs("Partida", "jugador eliminar", jugador_eliminar)

        if self.jugadores[self.jugador][0] == nombre:
            self.jugadores.remove(jugador_eliminar)
            self.jugador += -1 * self.sentido
            self.pasar_turno()

        elif jugador_eliminar: #jugador eliminar no esta en turno
            jugador_turno = list(self.jugadores[self.jugador])
            self.jugadores.remove(jugador_eliminar)

            indice_turno = int()
            for i, jugador in enumerate(self.jugadores):
                if jugador == jugador_turno:
                    indice_turno = i
                    break
            self.jugador = indice_turno
            

        else:
            logs("Partida", "Error", "se ejecuto 2 veces eliminar_jugador")

    def resetear_sacar_multiples(self):
        self.sacar_multiple = 0

    def botar_carta(self, carta):
        tupla_carta = (*carta,)
        self.pozo = tupla_carta

        logs(self.jugadores[self.jugador][0], "Carta botada - cartas jugador",
            str(tupla_carta) + " - " + str(self.jugadores[self.jugador][2]))

        self.jugadores[self.jugador][2].remove(tupla_carta)

    def iniciar_partida(self, dic_sockets):
        #definir usuarios, cartas y thread principal.
        nombres = list(dic_sockets.keys())
        random.shuffle(nombres)
        
        """
        La lista self.jugadores consistira en una lista de jugadores tales q su
        primer elementos es el nombre, el segundo el socket y el tercero una 
        lista de las cartas del jugador
        [ [ "MARTIN", dccuatro (True or false), [ ("1", "rojo), ("0", "verde") ], ["JUAN", ....  ] ]
        """
        for i in range(self.cantidad_jugadores):
            jugador = list()
            try:
                jugador.append(nombres[i])
                jugador.append(False)
                jugador.append(sacar_cartas(self.cantidad_cartas_iniciales))
                self.jugadores.append(jugador)

            except IndexError as error:
                logs("Partida", "Error en creacion partida", error)
        #obtenemos la carta del pozo, entrega una lista
        carta = sacar_cartas(1)
        logs("Partida", "Primera carta pozo", carta)
        self.pozo = carta[0]

        #comenzar partida
        thread_partida = threading.Thread(target=self.partida, daemon=True)
        thread_partida.start()

    def actualizar_interfaces(self):
        with self.lock_partida:
            return list(self.jugadores), list(self.perdedores)

    def situacion_partida(self):
        #returna true si sigue la partida y false si termino
        return self.partida_activa

    def turno_color_pozo(self):
        self.lock_partida.acquire()
        turno = self.jugadores[self.jugador][0]
        color = self.color
        pozo = self.pozo
        sacar = self.sacar_multiple if self.sacar_multiple >= 2 else 1
        self.lock_partida.release()
        logs("Partida", "Turno, Color, Pozo y Sacar", 
            str(turno) + "-" + str(color) + "-" + str(pozo) + "-" + str(sacar))
        return turno, color, pozo, str(sacar)
        
    def confirmar_botar_carta(self, nombre, dic):
        if self.jugadores[self.jugador][0] == nombre:
            self.accion = dic
            logs("Partida", "Botar carta " + self.jugadores[self.jugador][0], dic)
            return True
        else:
            logs("Partida", "Error Botar carta " + str(nombre), dic)
            return False

    def confirmar_robar_carta(self, nombre, dic):
        if self.jugadores[self.jugador][0] == nombre:
            self.accion = dic
            logs("Partida", "Robar carta " + self.jugadores[self.jugador][0], dic)
            return True
        else:
            logs("Partida", "Error Botar carta " + self.jugadores[self.jugador][0], dic)
            return False

    def partida_color_escogido(self, str_color):
        self.color_escogido = str_color
        if str_color in ["rojo", "verde", "amarillo", "azul"]:
            return True
        else:
            return False

    def confirmar_dccuatro(self, nombre):
        with self.lock_partida:
            indice_usuario = int()
            for i, jugador in enumerate(self.jugadores):
                if jugador[0] == nombre:
                    indice_usuario = i
                    if len(jugador[2]) == 1:
                        jugador[1] = True
                        return "Ha gritado DCCuatro y se a protegido"
                else:
                    if len(jugador[2]) == 1 and not jugador[1]:
                        jugador[2].extend(sacar_cartas(self.dccuatro))
                        return f"Gritó DCCuatro antes que {jugador[0]}, por lo que suman 4 cartas"
            #si llego aca es porque nadie tenia una carta o le ganaron en gritar DCCuartro
            self.jugadores[indice_usuario][2].extend(sacar_cartas(self.dccuatro))
            return "Ha gritado DCCuatro de manera invalida, se le suman 4 cartas"

    def enviar_ganador(self):
        return self.ganador

    def partida (self):
        #primer momento con el pozo---------------------------------------------------
        self.lock_partida.acquire()

        if self.pozo[0] == "+2":
            self.sacar_multiple += 2

        elif self.pozo[0] == "sentido":
            self.cambiar_sentido()

        elif self.pozo[0] == "color":
             #escoger color -----------------------------------------------
            self.lock_partida.release()
            self.flag_info_partida.set()
            self.flag_info_server.wait()
            self.flag_info_server.clear()
            self.lock_partida.acquire()
            self.color = self.color_escogido
    
        else: #carta ordinaria
            #no pasa nada fuera de lo ordinario
            pass
        #--------------------------------Fin primer momento--------------------------

        while self.partida_activa:
            #el ciclo del while es un turno y esta determinado por jugador q es un int
            #representando quien va a jugar en el turno
            self.lock_partida.release()
            self.flag_info_partida.set()

            jugador_turno = list(self.jugadores[self.jugador])
            while not self.flag_info_server.is_set():
                with self.lock_partida:
                    for i in range(len(self.jugadores)):
                        players = list(self.jugadores)
                        if len(players[i][2]) > self.cartas_max:
                            logs(players[i][0], "Perdio", "superó el maximo de cartas")
                            perdedor = players[i]
                            self.perdedores.append(perdedor[0])
                            self.eliminar_jugador(perdedor[0])
                            break
                        elif len(self.jugadores[i][2]) == 0: #gano partida
                            self.partida_activa = False
                            self.ganador = self.jugadores[self.jugador]
                            break
                    #confirmacion
                    if len(self.jugadores) == 1:
                        self.ganador = self.jugadores[0]
                        self.partida_activa = False
                        break
                    elif len(self.jugadores) == 0:
                        logs("Partida", "Error", "No hay jugadores jugando")
                        self.partida_activa = False
                        break

                    elif not jugador_turno in self.jugadores:
                        jugador_turno = self.jugadores[self.jugador]
            #ocurre cuando rompemos el while anterior porq termino partida
            if not self.flag_info_server.is_set():
                break
                            
            self.flag_info_server.clear()

            self.lock_partida.acquire()
            
            if self.sacar_multiple > 0: #revisar si se tiraron +2
                if self.accion.get("carta"):
                    #revisamos si la carta q tiro es un +2
                    if self.accion["carta"][0] == "+2":
                        self.botar_carta(self.accion["carta"])
                        self.sacar_multiple += 2
                    else:
                        #volver a pedir q entregue una carta
                        logs(str(self.jugadores[self.jugador][0]), 
                                "Carta incorrecta", self.accion["carta"]) 
                        continue
                
                elif self.accion.get("sacar"):
                    cartas_nuevas = sacar_cartas(self.sacar_multiple)
                    self.resetear_sacar_multiples()
                    self.jugadores[self.jugador][2].extend(cartas_nuevas)
                    #se resetea el grito dccuatro
                    self.jugadores[self.jugador][1] = False

                else:
                    logs(self.jugadores[self.jugador][0], "Error sacar multiples", self.accion)
                    continue
   
            #revisar el caso normal
            else:#eleccion
                if self.accion.get("carta"):#cambio sentido
                    if self.accion["carta"][0] == "sentido":
                        if self.accion["carta"][1] == self.color or self.pozo[0] == "sentido":
                            self.cambiar_sentido()
                            #quitar la carta al jugador
                            self.botar_carta(self.accion["carta"])
                        else:
                            #que tire otra carta
                            logs(self.jugadores[self.jugador][0], 
                                "Carta incorrecta", self.accion["carta"])
                            continue
                    elif self.accion["carta"][0] == "color":#cambio de color
                        #escoger color -----------------------------------------------
                        self.lock_partida.release()
                        self.flag_info_server.wait()
                        self.flag_info_server.clear()
                        self.lock_partida.acquire()
                        if self.color_escogido == "deshacer":
                            logs(self.jugadores[self.jugador][0], 
                                "Jugada Deshecha", self.accion["carta"])
                            continue
                        else:
                            self.botar_carta(self.accion["carta"])
                            self.color = self.color_escogido
                         
                    elif self.accion["carta"][0] == "+2":  #+2
                        if (self.accion["carta"][1] == self.color or 
                            self.accion["carta"][0] == self.pozo[0]):
                            #la carta es del color
                            self.botar_carta(self.accion["carta"])
                            self.sacar_multiple += 2
                        else:
                            #que tire otra carta
                            logs(self.jugadores[self.jugador][0], 
                                "Carta incorrecta", self.accion["carta"])
                            continue
                    
                    else: #carta normal
                        if (self.accion["carta"][1] == self.color or 
                            self.accion["carta"][0] == self.pozo[0]):
                            #la carta es del color o el numero
                            self.botar_carta(self.accion["carta"])
                        else:
                            #que tire otra carta
                            logs(self.jugadores[self.jugador][0], 
                                "Carta incorrecta", self.accion["carta"])
                            continue

                elif self.accion.get("sacar"):
                    self.jugadores[self.jugador][2].extend(sacar_cartas(1))
                    #se resetea el grito dccuatro
                    self.jugadores[self.jugador][1] = False
                    
                else:
                    logs("Partida", "Error opcion usuario", str(self.accion))
     
            #revisar si termino la partida--------------------------------------------

            #si supera el maximo de cartas
            if len(self.jugadores[self.jugador][2]) > self.cartas_max:
                logs(self.jugadores[self.jugador][0], "Perdio", "superó el maximo de cartas")
                perdedor = self.jugadores[self.jugador]
                #nombre
                self.perdedores.append(perdedor[0])
                self.eliminar_jugador(perdedor[0]) #funcion peligrosa

            elif len(self.jugadores[self.jugador][2]) == 0:
                #gano la partida
                self.partida_activa = False
                self.ganador = self.jugadores[self.jugador]

            #confirmacion
            if len(self.jugadores) == 1:
                self.ganador = self.jugadores[0]
                self.partida_activa = False
            elif len(self.jugadores) == 0:
                logs("Partida", "Error", "No hay jugadores jugando")
                self.partida_activa = False
            else:
                #se sigue la partida en este caso
                self.pasar_turno()
        #--------------------------Fin---------------------------------
        if self.ganador:
    
            logs(self.ganador[0], "Gano la partida!!", "-----")
            #avisar que gano
            if self.lock_partida.locked():
                self.lock_partida.release()
            self.flag_info_partida.set()
        else:
            #avisar de un error en el sistema
            print("error")