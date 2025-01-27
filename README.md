# Task 03: DDCuatro

## General Considerations

* Reviewer, I deeply apologize for not uploading the `README` earlier. I focused on my other exams and completely forgot about it. I hope you can review it even though it's SUPER late (to make your correction process easier).
* The task can run and be played completely, although some bugs may occur when closing windows or after the game ends.
* On the client side, it only receives information from the server and displays it on the interface. Then, whatever the user sends is forwarded to the server for processing.
* The server handles all the information processing, and the game logic is located in the back-end module.
* Important note: I renamed the `color.png` card to `color_.png` to make the code implementation easier.
* The two major issues in my code are poor parameter usage (I implemented the required parameters from the instructions but didn't add others to the JSON file) and exceeding the line limit in some files.

### Implemented and Unimplemented Features

* Networking:
  * Socket management: Done
  * Connection: Done
  * Client management: This was the last part of the program I implemented, and I'm not 100% sure the code can handle users disconnecting during a game (I didn't implement any control for when a player leaves while choosing a color).

* Client-Server Architecture:
  * Roles: Done
  * Consistency: Done
  * Logs: Done

* Byte Handling:
  * Card Encoding: Done
  * Card Decoding: Done
  * Integration: Done

* Graphical Interface:
  * Modeling: Done
  * General: Done
  * Start Window: Done
  * Waiting Room: Done
  * Game Room: Mostly done. There may be an error when closing the window (I believe the waiting room opens, and spectator mode works as far as I know).
  * Game End: Restarting the game was not implemented.

* DCCuatro Rules:
  * Dealing Cards: Done
  * Playing a Card: Done
  * Drawing a Card: Done
  * Shouting "DCCuatro!": Done
  * Game End: Done

* General:
  * Parameters: I didn't save any parameters other than those required by the instructions (I need to improve this).
  * Deck Generator: Done

* Bonus:
  * Chat: Fully implemented.

## Execution

In the `server` folder, the `main.py` file runs the server for the program. The following files are needed for it to function:

1. `sprites` in `server`. Inside this folder, in the `simples` subfolder, the card `color.png` was renamed to `color_.png`.
2. `generador_de_mazos.py` in `server`
3. `servidor.py` in `server`
4. `back_end.py` in `server`
5. `funciones_ext.py` in `server`
6. `parametros.json` in `server`

In the `client` folder, the `main.py` file runs the program's client. It includes:

1. All files from Designer with the `.ui` extension, which are used to load game widgets. These are: `dialog_avisar_color.ui`, `dialog_cambio_color.ui`, `dialog_conexion_perdida.ui`, `ventana_espera.ui`, `ventana_inicio.ui`, and `ventana_partida.ui` in `client`.
2. `conexion_servidor.py` in `client`
3. `lector_parametros.py` in `client`
4. `interfaz.py` in `client`
5. `parametros.json` in `client`
6. `sprites` in `client` with images for logos, the card back, and a blue card with the number 0. These are needed to start the program, as the `.ui` files look for these images in this folder (the rest of the game cards are sent by the server).

## Libraries

### External Libraries Used
The external libraries I used are:

1. `sys`: `__excepthook__`, `exit()`
2. `socket`: `gethostname()`, `socket()`, `AF_INET`, `SOCK_STREAM`
3. `os`: `path`
4. `json`: `loads()`, `dumps()`, `load()`
5. `threading`: `Lock()`, `Event()`, `Thread`
6. `time`: `sleep()`
7. `random`: `shuffle()`
8. `collections`: `namedtuple`
9. `PyQt5`: `uic`,  
               : `QtWidgets`: `QLayoutItem`, `QLabel`, `QApplication`,   
               : `QtGui`: `QPixmap`, `QTextCursor`, `QImage`, `QTransform`,  
               : `QtCore`: `pyqtSignal`, `Qt`, `QRect`, `QObject` 

### Custom Libraries
The custom modules created are:

1. `generador_de_mazos.py`: A file provided for the task.
2. `servidor.py`: Contains the `Servidor` class, which manages client connections.
3. `back_end.py`: Contains the `DCCuatro` class.
4. `funciones_ext.py`: Contains complementary functions for the classes.
5. `parametros.json`: Contains the parameters required by the instructions.
6. All files from Designer with the `.ui` extension, which are used to load game widgets. These are: `dialog_avisar_color.ui`, `dialog_cambio_color.ui`, `dialog_conexion_perdida.ui`, `ventana_espera.ui`, `ventana_inicio.ui`, and `ventana_partida.ui`.
7. `conexion_servidor.py`: Contains the `Cliente` class, which handles communication with the server and interface.
8. `lector_parametros.py`: A module with useful functions for the classes.
9. `interfaz.py`: Contains the classes for the game's windows.

## Assumptions and Additional Considerations

There is code I copied from Stack Overflow and made small changes to. It is located in the `interfaz` module in the `client` folder and comes from the following link:

https://stackoverflow.com/a/10067548

This code is used to delete labels from a layout (e.g., when updating the user's deck).
