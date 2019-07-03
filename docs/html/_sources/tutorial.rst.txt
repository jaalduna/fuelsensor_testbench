Tutorial
===================

Objetivos
---------

1. Aprender a usar la api Bootloader
2. Aprender a usar la api Fuelsensor_interface


Introducción
------------

El dispositivo FuelSensor, actualmente en su versión 1.8, permite medir la altura de liquidos en estanques de manera no invasiva. Haciendolo especialmente util en escenarios donde no hay acceso al interior de los estanques.

El firmware en el dispositivo FuelSensor se controla mediante dos api: bootloader y Fuelsensor_interface.
La interfaz Bootloader permite adminsitrar la aplicación que se ejecutará en operación normal del dispositvo. Mientras que la api FuelSensor_interface corresponde a la interfaz de la aplicación y permite obtener controlar los distintos sensores y actuadores del dispositivo, así como también obtener variables de interes tales como altura del estanque, series de tiempo, entre otras. 

Las interfaces están escritas en `Python 2.7 <https://www.python.org/downloads/release/python-2713/>`_ , luego para poder utilizarlas, es necesario tenerlo instalado tu computador.

Además deberas instalar los paquetes de dependencia crcmod y matplotlib mediante pip:

..	code-block:: sh

	pip install crcmod
	pip install matplotlib



Antes de comenzar las pruebas, procurar que el dispositivo FuelSensor esté alimentado y el cable ethernet esté conectado. 

El equipo FuelSensor posee en su interior el conversor ethernet serial Wiznet 108sr. El conversor opera como un servidor TCP por lo que será necesario configurar la interfaz ethernet en tu computador para que ambos equipos se encuentren en la misma red y así poder establer comunicación. La IP por defecto en los equipos Wiznet es 192.168.0.10 y el puerto de comunicación debería ser 5000. De todas formas, es posible validar estos parametros y si es necesario actualizarlos mediante la aplicación `configTool <https://www.wiznet.io/wp-content/uploads/wiznethome/S2E%20Module/WIZ107_108SR/Utility/WIZ107_108_config_tool.zip>`_ de Wiznet. Con los parámetros correctamente configurados, ya deberíamos poder utilizar la api de Bootloader.

Api Bootloader
--------------

El dispositivo FuelSensor trae desde fabrica un firmware que permite actualizar la aplicación que se ejecutará en operación normal. La interfaz de esta firmware corresponde a la api de Bootloader.

En la carpeta ``src`` ejecutarmos un terminal de python  y crearemos una instancia de la clase api Bootloader:

..	code-block:: python

	from Bootloader import Bootloader
	b = Bootloader()

Con la instancia creada podemos corroborar que todo este ok preguntando por la versión del Bootloader

.. code-block:: python

	b.read_version()

La api intentará conectarse con el dispositivo y encuestará la versión del bootloader. Si todo marcha bien, debería aparecer en pantalla como respuesta la versión actual del Firmware de bootloader.

Ahora cargaremos una nueva app al dispositivo. Para eso almacenaremos la aplicación compilada en la carpeta ``src``. Cargaremos la aplicación mediante la siguiente serie de comandos

..	code-block:: python

	b.connect()
	b.program_file(file_name)
	b.close_socket()

Reemplazando `file_name` por el nombre de la aplicación. El proceso de carga debería comenzar y el porcentaje de avanze debería desplegarse en pantalla. Una vez finalizado el proceso de carga debemos indicarla al Dispositivo que salga del modo Bootloader y entre al de Aplicación. Realizaremos esto mediante la siguiente serie de comandos:

..	code-block:: python
	
	b.connect()
	b.jump_to_app()
	b.close_socket()

El firmware de la App ya debería estar corriendo.

Api Fuelsensor_interface
------------------------

Con el dispositivo configurado en modo aplicación ya podemos comenzar a encuestarla. 
Al igual que en el caso de la api Bootloader, debemos crear una instancia de la interfaz Fuelsensor_interface. Realizaremos esto mediante la secuencia de comandos:

..	code-block:: python

	from FuelSensor_interface import FuelSensor_interface
	fs = FuelSensor_interface()

Con la interfaz creada, podemos obtener información de la altura del liquido en metros mediante el comando

..	code-block:: python

	fs.connect()
	fs.get_hight()
	fs.close_socket()


O bien el una variable entera proporcional al tiempo de vuelo de la señal:

..	code-block:: python

	fs.connect()
	fs.get_pos()
	fs.close_socket()

También podemos obtener series de tiempo del eco normalizado

..	code-block:: python

	fs.connect()
	norm_echo_ts = fs.get_complete_norm_echo(length)
	fs.close_socket()

Reemplazar ``length`` por el numero de muestras de tiempo a encuestar. Esta función diagnóstica es especialmente util a la hora de detectar problemas en la intalación del equipo u otros que influyan en la calidad del eco.

..	code-block:: python

	fs.connect()
	sdft_echo_ts = fs.get_complete_sdft_echo(length)
	fs.close_socket()

Reemplazar ``length`` por el número de muestras de tiempo a encuestar. Esta función diagnóstica permite determinar si la SDFT calculada posee un peak distintivo en el instante del eco.

Obtener la respuesta completa del eco no siempre es necesario y toma tiempo. Si ya conocemos de forma aproximada donde debería encontrarse el eco, podemos encuestar una porción de la respuesta completa mediante los comandos:

..	code-block:: python

	fs.connect()
	sliced_norm_echo_ts = fs.get_norm_echo(offset, length)
	sliced_sdft_echo_ts = fs.get_sdft_echo(offset, length)
	fs.close_socket()

``offset`` es el número de muestras a saltarse desde el principio y ``length`` el largo del intervalo a encuestar.

Finalmente, para volver al modo Bootloader es necesario reiniciar el dispositivo mediante el comando:

..	code-block:: python

	fs.connect()
	fs.reset()
	fs.close_socket()

Notar que si el dispositivo se reinicia debido a un corte de energía, entrará al modo Bootloader y por tanto para volver al modo aplicación será necesario reenviar el comando ``jump_to_app``.
