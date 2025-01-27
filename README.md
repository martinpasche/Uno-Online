# Tarea 03: DDCuatro

## Consideraciones generales

* Corrector, lamento mucho no haber subido el ```README``` antes. Me centré en mis otros exámenes y se me fue completamente de la cabeza. Espero que lo pueda ver aunque lo haya entregado SUPER tarde (para que le facilite la correción).
* La tarea se puede correr y jugar competamente, con alguno que otro bug que pueda aparecer por cerrar ventanas o que haya terminado la partida.
* En el cliente, este solo recibe la informacion del servidor y la muestra en la interfaz. Luego, lo que le manda el usuario, se lo manda al servidor para que procese la informacion.
* El servidor es el encargado de procesar toda la informacion y la lógica del juego se encuentra en el modulo back-end.
* Dato importante: modifique el nombre de la carta ```color.png``` -> ```color_.png```, ya que facilita mucho la implementación del codigo.
* Los dos grandes errores en mi código, es el mal uso de los parametros (implementé los que se pedian en el enunciado, pero los demás no los agregue en el archivo json) y que en algunos archivos me pase en lineas.
  

### Cosas implementadas y no implementadas

* Networking:
    * Manejo de sockets: Hecho
    * Conexion: Hecho
    * Manejo de clientes: Fue lo ultimo que implete en el programa y no estoy 100% seguro si el codigo puede resistir a que se desconecten usuarios en partida (no realice ningun control cuando un jugador se sale cuando tiene que escoger color)
* Arquitectura Cliente-Servidor:
    * Roles: Hecho
    * Consistencia: Hecho
    * Logs: Hecho
* Manejo de Bytes:
    * Codificación Cartas: Hecho
    * Decodificación Cartas: Hecho
    * Integración: Hecho
* Interfaz Gráfica:
    * Modelación: Hecho
    * General: Hecho
    * Ventana de inicio: Hecho
    * Sala de espera: Hecho
    * Sala de juego: Hecho en su mayoria. Puede que haya un error al cerrar la ventana (creo que se abre la sala de espera y el modo espectador según yo funciona)
    * Fin de la partida: Faltó hacer el reinicio de la partida.
* Reglas del DCCuatro:
    * Repartir cartas: Hecho
    * Jugar una carta: Hecho
    * Robar una carta: Hecho
    * Gritar ¡DCCuatro!: Hecho
    * Termino del juego: Hecho
* General:
    * Parámetros: No guarde ningun otro parametro aparte de los pedidos en el enunciado (tengo que mejorar esto)
    * Generador de Mazos: Hecho
* Bonus:
    * Chat: Implementado completamente

## Ejecución

En la carpeta ```servidor```, el archivo ```main.py``` corre el servidor del programa, el cual debe tener los siguientes archivos para funcionar:

1. ```sprites``` en ```servidor```. Dentro de esta carpeta, en la subcarpeta ```simples``` modifique el nombre de la carta color de ```color.png``` a ```color_.png```.
2. ```generador_de_mazos.py``` en ```servidor```
3. ```servidor.py``` en ```servidor```
4. ```back_end.py``` en ```servidor```
5. ```funciones_ext.py``` en ```servidor```
6. ```parametros.json``` en ```servidor```

En la carpeta ```Cliente```, el archivo ```main.py``` corre el cliente del programa, el cual contiene:

1. Todos los archivos provenientes de Designer con extension ```.ui``` que son utilizados para cargar los widgets del juego. Estos son: ```dialog_avisar_color.ui```, ```dialog_cambio_color.ui```, ```dialog_conexion_perdida.ui```, ```ventana_espera.ui```, ```ventana_inicio.ui``` y ```ventana_partida.ui```, en ```Cliente```
2. ```conexion_servidor.py``` en ```Cliente```
3. ```lector_parametros.py``` en ```Cliente```
4. ```interfaz.py``` en ```Cliente```
5. ```parametros.json``` en ```Cliente```
6. ```sprites``` en ```Cliente``` con las imagenes de los logos, la carta reverso y una carta azul del numero 0, para poder partir el programa, ya que los archivos ```.ui``` buscaran estas imagenes en esta carpeta (el resto de las cartas de la partida se las envia el servidor).



## Librerías
### Librerías externas utilizadas
La lista de librerías externas que utilicé fue la siguiente:

1. ```sys```: ```__excepthook__``` ```exit()```
2. ```socket```: ```gethostname()``` ```socket()``` ```AF_INET``` ```SOCK_STREAM```
3. ```os``` : ```path```
4. ```json```: ```loads()``` ```dumps()``` ```load()```
5. ```threading```: ```Lock()``` ```Event()``` ```Thread```
6. ```time```: ```sleep()```
7. ```random```: ```shuffle()```
8. ```collections```: ```namedtuple```
9. ```PyQt5``` : ```uic```,  
               : ```QtWidgets``` : ```QLayoutItem``` ```QLabel``` ```QApplication```,   
               : ```QtGui``` : ```QPixmap``` ```QTextCursor``` ```QImage``` ```QTransform```,  
               :```QtCore``` : ```pyqtSignal``` ```Qt``` ```QRect``` ```QObject``` 

### Librerías propias 
Por otro lado, los módulos que fueron creados fueron los siguientes:

1. ```generador_de_mazos.py``` que es un archivo entregado para la tarea
2. ```servidor.py``` que contiene la clase ```Servidor``` que se dedica a conectarse con los clientes
3. ```back_end.py``` que contiene la clase ```DCCuatro```
4. ```funciones_ext.py``` que contiene algunas funciones complementarias a las clases
5. ```parametros.json``` es el archivo que contiene los parametros requeridos en el enunciado
6. Todos los archivos provenientes de Designer con extension ```.ui``` que son utilizados para cargar los widgets del juego. Estos son: ```dialog_avisar_color.ui```, ```dialog_cambio_color.ui```, ```dialog_conexion_perdida.ui```, ```ventana_espera.ui```, ```ventana_inicio.ui``` y ```ventana_partida.ui```
7. ```conexion_servidor.py``` que contiene la clase ```Cliente``` que es la que se dedica a la comunicacion con el servidor y la interfaz.
8. ```lector_parametros.py``` es modulo con funciones utiles para las clases
9. ```interfaz.py``` que tiene las clases de las ventanas del juego.

## Supuestos y consideraciones adicionales

Hay un codigo que copie de stackoverflow y le hice pequeñas variaciones, se encuentra en el modulo ```interfaz``` de la carpeta ```Cliente``` que proviene del siguiente link:

https://stackoverflow.com/a/10067548

Que sirve para eliminar los labels de un layout. (e.j. cuando se quiere actualizar el mazo del usuario)

## Muchas Gracias por Corregir mi Tarea, espero que te haya servido el ```README``` y suerte en tus examenes!!