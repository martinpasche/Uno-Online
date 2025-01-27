import interfaz
import sys
import interfaz
import lector_parametros
from PyQt5.QtWidgets import QApplication
from conexion_servidor import Cliente

parametros = lector_parametros.obtener_parametros()


def hook(type, value, traceback):
    print(type)
    print(traceback)
    sys.__excepthook__ = hook 

app = QApplication([])


#instanciar clases
cliente = Cliente(parametros)
ventana_inicio = interfaz.WidgetVentanaInicio()
ventana_partida = interfaz.VentanaPartida()
ventana_espera = interfaz.WidgetVentanaEspera(ventana_partida)


#señales
cliente.senal_ventana_inicio.connect(ventana_inicio.iniciar_ventana)
cliente.senal_error_conexion.connect(ventana_inicio.error_conexion)
cliente.senal_error_conexion.connect(ventana_espera.error_conexion)
cliente.senal_error_conexion.connect(ventana_partida.error_conexion)
cliente.senal_error_nombre.connect(ventana_inicio.error_nombre)
cliente.senal_entrar_espera.connect(ventana_inicio.entrar_espera)
cliente.senal_entrar_espera.connect(ventana_espera.entrar_espera)
cliente.senal_mostrar_chat.connect(ventana_espera.mostrar_chat)
cliente.senal_mostrar_chat.connect(ventana_partida.mostrar_chat)
cliente.senal_enviar_cartas.connect(ventana_partida.mostrar_cartas)
cliente.senal_enviar_nombres.connect(ventana_partida.sentar_jugadores)
cliente.senal_enviar_nombres.connect(ventana_espera.cerrar_ventana)
cliente.senal_turno_color_sacar.connect(ventana_partida.mostrar_turno_color_sacar)
cliente.senal_pozo.connect(ventana_partida.pozo)
cliente.senal_escoger_color.connect(ventana_partida.escoger_color)
cliente.senal_avisar_cambio_color.connect(ventana_partida.color_cambiado)
cliente.senal_act_perdedores.connect(ventana_partida.act_perdedores)
cliente.senal_fin_partida.connect(ventana_partida.fin_partida)

ventana_inicio.senal_nombre_usuario.connect(cliente.confirmar_nombre_usuario)

ventana_espera.senal_eviar_chat.connect(cliente.enviar_chat)

ventana_partida.senal_enviar_chat.connect(cliente.enviar_chat)
ventana_partida.senal_botar_carta.connect(cliente.enviar_botar_carta)
ventana_partida.senal_robar_carta.connect(cliente.enviar_robar_carta)
ventana_partida.senal_color_escogido.connect(cliente.enviar_color)
ventana_partida.senal_gritar_dccuatro.connect(cliente.enviar_dccuatro)


cliente.start()
sys.exit(app.exec_())

