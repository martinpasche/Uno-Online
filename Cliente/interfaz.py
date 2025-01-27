from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QLayoutItem, QLabel
from PyQt5.QtGui import QPixmap, QTextCursor, QImage, QTransform
from PyQt5.QtCore import pyqtSignal, Qt, QRect
import os
import sys
import lector_parametros


parametros = lector_parametros.obtener_parametros()

widget_ventana_inicio, clase_ventana_inicio = uic.loadUiType(parametros["path_ventana_inicio"])
widget_ventana_espera, clase_ventana_espera = uic.loadUiType(parametros["path_ventana_espera"])
widget_dialog_conexion, clase_dialog_conexion = uic.loadUiType(
    parametros["path_dialog_conexion_perdida"])
widget_dialog_cambio_color, clase_dialog_cambio_color = uic.loadUiType(
    parametros["path_dialog_cambio_color"])
widget_dialog_avisar_color, clase_dialog_avisar_color = uic.loadUiType(
    parametros["path_dialog_avisar_color"])
widget_ventana_partida, clase_ventana_partida = uic.loadUiType(parametros["path_ventana_partida"])

class WidgetVentanaInicio (widget_ventana_inicio, clase_ventana_inicio):

    senal_nombre_usuario = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def iniciar_ventana(self):
        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            self.nombre_usuario()

    def nombre_usuario(self):
        name = self.le_nombre.text()
        self.senal_nombre_usuario.emit(name)

    def error_nombre(self):
        dialog = DialogConexionPerdida()
        dialog.l_texto.setText("Error con el nombre. Repetido o no alfanumerico")
        dialog.exec()
                
    def error_conexion (self, error):
        if self.isVisible():
            dialog = DialogConexionPerdida()
            dialog.l_texto.setText(str(error))
            dialog.exec()
            sys.exit()

    def entrar_espera(self, lista_jugadores):
        self.hide()


class WidgetVentanaEspera (widget_ventana_espera, clase_ventana_espera):

    senal_eviar_chat = pyqtSignal(str)

    def __init__(self, ventana_partida):
        super().__init__()
        self.setupUi(self)
        self.te_chat.setText("")
        self.ventana_partida = ventana_partida

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            chat = self.le_chat.text()
            self.le_chat.setText("")
            chat = chat.strip()
            if chat != "":
                self.senal_eviar_chat.emit(chat)

    def error_conexion (self, error):
        if self.isVisible():
            dialog = DialogConexionPerdida()
            dialog.l_texto.setText(str(error))
            dialog.exec()
            sys.exit()

    def mostrar_chat(self, mensaje, cliente_enviador):
        text_cursor = QTextCursor(self.te_chat.document())
        self.te_chat.moveCursor(text_cursor.End)
        self.te_chat.insertPlainText(cliente_enviador + ": " + mensaje + "\n")
        self.te_chat.moveCursor(text_cursor.End)

    def cerrar_ventana(self, lista_inutil):
        self.hide()

    def entrar_espera(self, lista_jugadores, cantidad_jugadores):
        if not self.ventana_partida.isVisible():
            jugadores_conectados = len(lista_jugadores)
            for i in range(cantidad_jugadores):
                if i == 0:
                    if jugadores_conectados > 0:
                        self.l_nombre_1.setText(lista_jugadores[i])
                    else:
                        self.l_nombre_1.setText("ESPERANDO")
                elif i == 1: 
                    if jugadores_conectados > 1:
                        self.l_nombre_2.setText(lista_jugadores[i])
                    else:
                        self.l_nombre_2.setText("ESPERANDO")
                elif i == 2:
                    if jugadores_conectados > 2:
                        self.l_nombre_3.setText(lista_jugadores[i])
                    else:
                        self.l_nombre_3.setText("ESPERANDO")
                elif i == 3:
                    if jugadores_conectados > 3:
                        self.l_nombre_4.setText(lista_jugadores[i])
                    else:
                        self.l_nombre_4.setText("ESPERANDO")

            for i in range(cantidad_jugadores, 4):
                if i == 0:
                    self.l_nombre_1.hide()
                elif i == 1:
                    self.l_nombre_2.hide()
                elif i == 2:
                    self.l_nombre_3.hide()
                else:
                    self.l_nombre_4.hide()
            self.update()
            self.show()
        

class DialogConexionPerdida (widget_dialog_conexion, clase_dialog_conexion):
    def __init__(self):
        super().__init__()
        self.setupUi(self)    

class DialogCambioColor (widget_dialog_cambio_color, clase_dialog_cambio_color):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def color_rojo(self):
        self.done(1)

    def color_verde(self):
        self.done(2)

    def color_amarillo(self):
        self.done(3)

    def color_azul(self):
        self.done(4)

class DialogAvisarColor (widget_dialog_avisar_color, clase_dialog_avisar_color):

    def __init__(self, nombre, color):
        super().__init__()
        self.setupUi(self)
        self.l_texto.setText(f"{nombre} cambio el color a:")
        if color == "azul":
            pintura = "rgb(0, 255, 255)"
        elif color == 'rojo':
            pintura =  "rgb(255, 0, 0)"
        elif color == 'amarillo':
            pintura = "rgb(255, 255, 0)"
        else:
            pintura = "rgb(0, 255, 0)"
        self.l_color.setStyleSheet(
            "QLabel#l_color{ color: " + pintura + "; font: 9 pt Comic Sans MS;}")
        self.l_color.setText(color.upper())

class VentanaPartida (widget_ventana_partida, clase_ventana_partida):

    senal_enviar_chat = pyqtSignal(str)
    senal_botar_carta = pyqtSignal(tuple)
    senal_robar_carta = pyqtSignal()
    senal_color_escogido = pyqtSignal(str)
    senal_gritar_dccuatro = pyqtSignal()
    senal_nueva_partida = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.te_chat.setText("")
        # self.mesa = [(nombre, (self.layout, self.label_nombre)), (nombre, ...)]
        self.mesa = list()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return:
            chat = self.le_chat.text()
            self.le_chat.setText("")
            chat = chat.strip()
            if chat != "":
                self.senal_enviar_chat.emit(chat)

    def pozo (self, carta):
        imagen = QImage()
        imagen.loadFromData(carta.imagen)
        pixeles = QPixmap()
        pixeles.convertFromImage(imagen)
        self.l_imagen_pozo.setPixmap(pixeles)

    def mousePressEvent(self, event):
        if self.l_imagen_robar_carta.geometry().contains(event.pos()):
            self.senal_robar_carta.emit()

    def dccuatro(self):
        self.senal_gritar_dccuatro.emit()

    def error_conexion (self, error):
        if self.isVisible():
            dialog = DialogConexionPerdida()
            dialog.l_texto.setText(str(error))
            dialog.exec()
            sys.exit()

    def escoger_color (self):
        nummero_color = 0
        while nummero_color == 0:
            dialog = DialogCambioColor()
            nummero_color = dialog.exec()
        if nummero_color == 1:
            #rojo
            self.senal_color_escogido.emit("rojo")
        elif nummero_color == 2:
            #verde
            self.senal_color_escogido.emit("verde")
        elif nummero_color == 3:
            #amarillo
            self.senal_color_escogido.emit("amarillo")
        elif nummero_color == 4:
            #azul
            self.senal_color_escogido.emit("azul")
        else:
            #cerrar ventana, hacer nada
            self.senal_color_escogido.emit("deshacer")

    def color_cambiado(self, nombre, color):
        dialog = DialogAvisarColor(nombre, color)
        dialog.exec()

    def mostrar_chat(self, mensaje, cliente_enviador):
        text_cursor = QTextCursor(self.te_chat.document())
        self.te_chat.moveCursor(text_cursor.End)
        self.te_chat.insertPlainText(cliente_enviador + ": " + mensaje + "\n")
        self.te_chat.moveCursor(text_cursor.End)

    def mostrar_turno_color_sacar(self, turno, color, cantidad_sacar):
        self.l_color.setText(color.upper())
        if color == "azul":
            pintura = "rgb(0, 255, 255)"
        elif color == 'rojo':
            pintura =  "rgb(255, 0, 0)"
        elif color == 'amarillo':
            pintura = "rgb(255, 255, 0)"
        else:
            pintura = "rgb(0, 255, 0)"
        self.l_color.setStyleSheet(
            "QLabel#l_color{ color: " + pintura + "; font: 9 pt Comic Sans MS;}")
        self.l_turno.setText(turno)
        self.l_texto_cantidad_sacar.setText(cantidad_sacar)
        self.update()

    def sentar_jugadores(self, dic_nombres):
        usuario = dic_nombres["usuario"]
        nombres_des = dic_nombres["nombres"]
        #lista donde usuario es el primero, nombres_ordenado
        indice_usuario = nombres_des.index(usuario)
        nombres = list(nombres_des[indice_usuario : ] + nombres_des[ : indice_usuario])

        cantidad_jugadores = len(nombres)
        for i in range(cantidad_jugadores):
            if i == 0:
                self.l_nombre_jugador_1.setText(nombres[i])
                self.mesa.append((nombres[i], (self.cartas_jugador_1, self.l_nombre_jugador_1)))
            elif i == 1:
                self.l_nombre_jugador_2.setText(nombres[i])
                self.mesa.append((nombres[i], (self.cartas_jugador_2, self.l_nombre_jugador_2)))
            elif i == 2:
                self.l_nombre_jugador_3.setText(nombres[i])
                self.mesa.append((nombres[i], (self.cartas_jugador_3, self.l_nombre_jugador_3)))
            elif i == 3:
                self.l_nombre_jugador_4.setText(nombres[i])
                self.mesa.append((nombres[i], (self.cartas_jugador_4, self.l_nombre_jugador_4)))

        for i in range(cantidad_jugadores, 4):
            if i == 0:
                self.l_nombre_jugador_1.hide()
            elif i == 1:
                self.l_nombre_jugador_2.hide()
            elif i == 2:
                self.l_nombre_jugador_3.hide()
            else:
                self.l_nombre_jugador_4.hide()
        self.update()
        self.show()
    
    def mostrar_cartas(self, jugador_lista):
        #borrar las anteriores
        indice = -1
        for i, jugador in enumerate(self.mesa):
            if jugador[0] == jugador_lista[0]:
                indice = i 
                break
        layout = self.mesa[indice][1][0]

        #codigo obtenido de la pagina 
        # https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt/
        # 13103617#:~:text=To%20remove%20a%20widget%20from,from%20the%20layout%20until%20QWidget.

        while layout.count() > 2: 
            child = layout.takeAt(1)
            if child.widget():
                child.widget().deleteLater()

        for carta in jugador_lista[1]:
            if 1 == indice or indice == 3:
                label = CartaHorizontal(carta, self)
            elif 2 == indice:
                label = Carta(carta, self)
            else:
                label = CartaJugador(carta, self.senal_botar_carta, self)
            layout.insertWidget(1, label)    
        self.update()

    def act_perdedores(self, perdedores):

        for perdedor in perdedores:
            #perdedores es una lista de nombres
            indice = -1
            for i, jugador in enumerate(self.mesa):
                if jugador[0] == perdedor:
                    indice = i 
                    break
            layout = self.mesa[indice][1][0]
            
            while layout.count() > 2: 
                child = layout.takeAt(1)
                if child.widget():
                    child.widget().deleteLater()

            label = QLabel("Eliminado",self)
            label.setObjectName("label_perdedor")
            label.setStyleSheet(
                """QLabel#label_perdedor{
                    background-color : transparent;
                    color : rgb(197,197,197);
                    font : 11 pt Comic Sans MS;}""")
            layout.insertWidget(1, label)
            
    def fin_partida(self, ganador):
        dialog = DialogConexionPerdida()
        texto = f"{ganador} ha ganado la partida!!! Presione Ok para entrar a una nueva"
        dialog.l_texto.setText(texto)
        respuesta = dialog.exec()
        sys.exit()
      
class Carta (QLabel):
    def __init__(self, carta, *args):
        super().__init__(*args)
        self.setFixedSize(40, 60)
        self.setScaledContents(True)
        self.tipo = carta.tipo
        self.color = carta.color
        imagen = QImage()
        imagen.loadFromData(carta.imagen)
        pixeles = QPixmap()
        pixeles.convertFromImage(imagen)
        self.setPixmap(pixeles)

class CartaHorizontal (Carta):

    def __init__(self, carta, *args):
        super().__init__(carta, *args)
        self.setFixedSize(60, 40)
        
        #rotacion de 90 grados
        transform = QTransform().rotate(90)
        pixeles = self.pixmap().transformed(transform, Qt.SmoothTransformation)
        self.setPixmap(pixeles)

class CartaJugador (Carta):

    def __init__(self, carta, senal, *args):
        super().__init__(carta, *args)
        self.setFixedSize(40, 60)
        self.hit_box = QRect(0, 0, 40, 60)
        self.senal_botar_carta = senal
        
    def mousePressEvent(self, event):
        tupla = (self.tipo, self.color)
        self.senal_botar_carta.emit(tupla)
        