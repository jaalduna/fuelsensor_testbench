Estructura de paquetes
===================

La comunicación entre la api y el dispositivo fuelsensor ocurre mediante intercambio de paquetes de bytes. La api genera solicitudes para el dispositivo fuelSensor mediante un `paquete query`. El dispositivo fuelsensor procesa el paquete y responde con el `paquete response`. 


Paquete Query
-------------

El formato del `paquete query` es:


+---------+---------+---------+
| cmd     | params  | crc     |
+=========+=========+=========+
| 2 bytes | 8 bytes | 2 bytes |
+---------+---------+---------+

* `cmd` representa una instrucción de comando a ejecutar para el dispositivo fuelsensor
* `params` es una lista de parámetros que depende del tipo de query que se esta realizando
* `crc` es un chequeo de redundancia ciclica de 16 bits en formato `xmodem`
  
Paquete response
----------------
El formato del `paquete response` es:

+---------+-----------+-----------+---------+
| cmd     | num_bytes | payload   | crc     |
+=========+===========+===========+=========+
| 2 bytes | 2 bytes   | num_bytes | 2 bytes |
+---------+-----------+-----------+---------+

* `cmd`  es el comando al que está respondiendo
* `num_bytes` es el número de bytes en el campo payload
* `payload` son los bytes de respuesta
* `crc` es un chequeo de redundancia ciclica de 16 bits en formato `xmodem`


Lista de commandos (cmd)
----------------

+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| cmd_id | cmd name                        | params                           | DESCRIPCIÓN                                                                                                                                          |
+========+=================================+==================================+======================================================================================================================================================+
| 1      | BK_TIMESERIES                   | ---                              | se guarda un spanshot de la series de tiempo obtenedias en la última medición                                                                        |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 2      | GET_NORM_ECHO                   | offset (uint16), length (uint16) | retorna la secuencia de tiempo del eco almacenada en el snapshot a partir de la muestra `offset` y de largo `length` números de muestras             |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 3      | GET_SDFT_ECHO                   | offset (uint16), length (uint16) | retorna la secuencia SDFT almacenada en el snapshot  a partir de la muestra `offset` y de largo `length` números de muestras                         |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 4      | RESET                           | ---                              | resetea la aplicación. El bootloader queda a la espera de una señal por 30 segundos. Si no se recibe nada, entonces se vuelve a cargar la aplicacion |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 5      | GET_HEIGHT                      | ---                              | solicita la altura cálculada en metros (float32)                                                                                                     |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 6      | GET_POS                         | ---                              | solitica la posición del eco  (float32)                                                                                                              |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 7      | GET_PARAM                       | PARAM_ID                         | solicita el valor del parámetro identificado por `PARAM ID`                                                                                          |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 8      | SET_PARAM                       | PARAM_ID, PARAM_VALUE            | actualiza el valor del parámetro identificado por `PARAM ID` con el valor `PARAM_VALUE`                                                              |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 9      | RESTORE_DEFAULT_PARAMS_TO_FLASH | ---                              | resetea parámetros por defecto en la flash. Utilizar esta función para tener parámetros conocidos en la flash como un punto de partida.              |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+
| 10     | BACKUP_PARAMS_TO_FLASH          | ---                              | guarda los parámetros actuales en la memoria flash. Utiliza esta función una vez se esté conforme con los parámetros escogidos.                      |
+--------+---------------------------------+----------------------------------+------------------------------------------------------------------------------------------------------------------------------------------------------+

La información en el campo de parámetros se ajusta a la izquierda. Por ejemplo, para los comandos GET_NORM_ECHO y GET_SDFT_ECHO se utilizan únicamente los primeros 4 bytes del campo de parámetros.

Comando BK_TIMESERIES
"""""""""""""""""""""
Gatilla un respaldo de la series de tiempo obtenedias por el dispositivo en su última medición.

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x0001 | 0x00000000 | crc |
+--------+------------+-----+

Una vez que el dispositivo ha realizado el respaldo de las series de tiempo, retorna un mensaje de respuesta `ack`:

+--------+-----------+---------+---------+
| cmd    | num_bytes | payload | crc     |
+========+===========+=========+=========+
| 0x0001 | 0x0000    | ---     | 2 bytes |
+--------+-----------+---------+---------+


Comando GET_NORM_ECHO
""""""""
Solicita la serie de tiempo del eco normalizado. Recibe como parámetros un `offset` en número de muestras respecto del inicio de la secuencia y largo `length` para indicar cuantas muestras está solicitando.
El parámetro `length` típicamente no puede ser muy largo (<1000 muestras) debido a limitaciones en la interfaz de comunicaciones 485, interfaz asincrona. Entonces, para obtener una serie de tiempo completa es necesario
solicitarla por tramos.


+--------+----------------------+-----+
| cmd_id | params               | crc |
+========+======================+=====+
| 0x0002 | offset length 0x0000 | crc |
+--------+----------------------+-----+

 La respuesta de retorno sigue el siguiente formato:

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0002 | length    | payload | crc |
+--------+-----------+---------+-----+

Comando GET_SDFT_ECHO
"""""""""""""""""""""
Comando identico al comando GET_NORM_ECHO, tan solo que rescata la serie de tiempo de la SDFT. La solicitud es:

+--------+----------------------+-----+
| cmd_id | params               | crc |
+========+======================+=====+
| 0x0003 | offset length 0x0000 | crc |
+--------+----------------------+-----+

La respuesta es:

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0003 | length    | payload | crc |
+--------+-----------+---------+-----+


Comando RESET
""""""""""""""
Resetea al dispositivo. Este comando se utiliza para reinicar al equipo, típicamente para entrar a modo bootloader y reprogramar el firmware.

Formato de solicitud:

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x0004 | 0x00000000 | crc |
+--------+------------+-----+

Debido a que el dispositivo se resetea una vez recibido el comando, no hay respuesta a este comando.

Comando GET_HEIGHT
""""""""
Solicita el valor estimado de la altura actual del estanque. 

Formato de solicitud:

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x0005 | 0x00000000 | crc |
+--------+------------+-----+


Formato de respuesta:

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0005 | 0x0004    | heigth  | crc |
+--------+-----------+---------+-----+

Comando GET_POS
"""""""""""""""
retorna el valor de posición, en número de muestras, del eco.

formato de solicitud:

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x0006 | 0x00000000 | crc |
+--------+------------+-----+

formato de respuesta:

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0006 | 0x0004    | pos     | crc |
+--------+-----------+---------+-----+

Comando GET_PARAM
"""""""""""""""""
Solicita el valor de un parámetro. Existen 3 tipos de parámetros: bytes, unsigned short y float32. El formato de respuesta es siempre el mismo, la tarea de decodificar los strings de bytes se realiza en el lado del equipo host.

formato de solicitud:

+--------+--------------------+-----+
| cmd_id | params             | crc |
+========+====================+=====+
| 0x0007 | PARAM_ID 0x0000000 | crc |
+--------+--------------------+-----+

PARAM_ID es un byte que indica el parámetro se quiere solicitar. Una lista detallada de parámetros se encuentra en `Lista de parámetros`_.

formato de respuesta:

Independiente del tipo de parámetro solicitado, la respusta siempre consiste en 4 bytes en el campo de payload. En el caso de solicitarse un parámetro de tipo byte, se utiliza el byte de más a la izquierda. En el caso de solicitarse parámetro de tipo unsigned short, se utilizan los dos primeros bytes de izquierda a derecha. Y si se solicita un parámetro de tipo float32, se utilizan todos los bytes.

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0007 | 0x0004    | pos     | crc |
+--------+-----------+---------+-----+

Comando SET_PARAM
"""""""""""""""""
Actualiza el valor de un parámetro. La respuesta retorna el valor del parámetro actualizado.

Formato de solicitud:

+--------+----------------------+-----+
| cmd_id | params               | crc |
+========+======================+=====+
| 0x0008 | PARAM_ID 0x000 value | crc |
+--------+----------------------+-----+

formato de respuesta:

+--------+-----------+---------+-----+
| cmd    | num_bytes | payload | crc |
+========+===========+=========+=====+
| 0x0008 | 0x0004    | value   | crc |
+--------+-----------+---------+-----+

Comando RESTORE_DEFAULT_PARAMS_TO_FLASH
"""""""""""""""""""""""""""""""""""""""
Solicita restaurar los valores por defecto de los parámetros. Este comando se llama típicamente al inicio de una instalación, con el fin de partir desde un punto de configuración conocido.

formato de solicitud:

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x0009 | 0x00000000 | crc |
+--------+------------+-----+

formato de respuesta:

+--------+-----------+---------+---------+
| cmd    | num_bytes | payload | crc     |
+========+===========+=========+=========+
| 0x0009 | 0x0000    | ---     | 2 bytes |
+--------+-----------+---------+---------+

Comando BACKUP_PARAMS_TO_FLASH
""""""""""""""""""""""""""""""
Solicita respaldar los actuales parámetros en memoria no volatil. Esta función se llama cada vez que se actualicen los parámetros y se considere que los cambios realizados deben mantenerse. Cada vez que el dispositivo se reinicia, carga los parámetros desde la memoria no volatil.

formato de solicitud:

+--------+------------+-----+
| cmd_id | params     | crc |
+========+============+=====+
| 0x000a | 0x00000000 | crc |
+--------+------------+-----+

formato de respuesta:

+--------+-----------+---------+---------+
| cmd    | num_bytes | payload | crc     |
+========+===========+=========+=========+
| 0x000a | 0x0000    | ---     | 2 bytes |
+--------+-----------+---------+---------+


Lista de parámetros
"""""""""""""""""""
PARAM_BASE_ADDRESS = 0x9D021000

+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| PARAM_ADDR | PARAM_ID | type           | nombre                   | descripción                                                                 |
+============+==========+================+==========================+=============================================================================+
| 0x9D021000 | 00       | unsigned short | data_vector_type         | descripción pendiente                                                       |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021004 | 04       | unsigned short | data_vector_offset       | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021008 | 08       | byte           | pga_gain                 | ganancia del pga. Toma valores de 0 a 7                                     |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021009 | 09       | byte           | num_pulses               | número de pulsos del eco enviado.                                           |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D02100A | 0A       | byte           | pulse_period             | período de los pulsos. Cada unidad equivale a 10ns.                         |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D02100B | 0B       | byte           | pulse_width              | ancho del pulso. Cada unidad equivale a 10ns.                               |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D02100C | 0C       | byte           | res_hv                   | valor de resistencia de ajuste de fuente de alto voltaje. Valor Fijo de 40. |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D02100D | 0D       | float32        | sdft_min_peak_value_th   | threshold minimo para que el peak de sdft sea considerado valido            |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021011 | 11       | unsigned short | sdft_k                   | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021013 | 13       | unsigned short | sdft_n                   | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021015 | 15       | unsigned short | sdft_i_min               | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021017 | 17       | byte           | sdft_min_eco_limit       | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021018 | 18       | byte           | sdft_max_eco_limit       | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021019 | 19       | float32        | sdft_var_norm            | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D02101D | 1D       | float32        | sdft_peak                | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021021 | 21       | unsigned short | sdft_sound_speed         | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021023 | 23       | unsigned short | sdft_sample_rate         | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021025 | 25       | unsigned short | sdft_n_smaples_one_valid | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+
| 0x9D021027 | 27       | unsigned short | skip_param               | pendiente                                                                   |
+------------+----------+----------------+--------------------------+-----------------------------------------------------------------------------+



