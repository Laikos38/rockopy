# Rockopy
Una rockola simple integrada con Spotify para encolar música elegida por los clientes.

## Dependencias
[Spotipy](https://github.com/plamere/spotipy) version >= 2.4.4

## Crear app en Spotify Dev

Ingresar a [Spotify Dev](https://developer.spotify.com/dashboard/). Crear una nueva aplicación, nombrarla como se desee y aceptar los términos. Una vez creada la aplicación ir a la opción de "Edit Settings", y en la sección "Redirect URLs" agregar `http://ROCKOPY/`. Guardar los cambios.

Copiar el CLIENT ID y el CLIENT SECRET de la aplicación. Pegar estos valores en las variables correspondientes en el archivo ```config.py```.

## Ejecución del servidor
Para ejecutar el servidor de rockopy:
+ Modifique la IP y puerto a utilizar en **`config.py`** si lo desea.
+ Ejecute el script python **`main.py`** ubicado en rockopy/server:
  `python main.py`
+ Debe iniciar sesión con spotify para que el servidor se ejecute.
+ Ingrese su nombre de usuario de spotify.
+ Se abrirá en su explorador web la página de autorización de la aplicación. Acepte.
+ Se redireccionará a un link con el token de autorización de rockopy.
+ Copie dicho link (`http://rockopy/?code= ... `)
+ Pegue el link en el script.

Una vez realizado los pasos anteriores el servidor se ejecutrá y esperará por clientes. Su usuario será recordado, no será necesario repetir los pasos.

## Ejecución del cliente
Para ejecutar el cliente de rockopy:
+ Ejecute el script python **`main.py`** ubicado en rockopy/client:
  `python main.py`
+ Si el servidor se encuentra en ejecución el cliente conectará automáticamente, caso contrario realizará 10 intentos antes de finalizar la ejecución.

## Funcionamiento y conceptos
#### Importante:
Una vez abierto Spotify y ejecutado el servidor, **NO** se deben utilizar los controles multimedia de Spotify, únicamente utilizar los del menú de playback de Rockopy.
#### Rockopy playlist:
Lista de canciones (tracks) que puede ser modificada tanto por el servidor como por el cliente. Tiene prioridad de reproducción ante la fill playlist.
#### Fill playlist:
Lista de canciones seleccionada por el server (perteneciente a la Spotify library del usuario). Si no hay canciones en la Rockopy playlist, y se seleccionana la opción "play", se reproducirá una canción aleatoria de la fill playlist.
#### Devices:
Dispositivos en los que se encuentra abierto Spotify. Es necesario abrir Spotify con el mismo usuario que Rockopy.
