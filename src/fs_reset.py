import sys
from Fuelsensor_interface import Fuelsensor_interface
import time

if len(sys.argv) == 3:
    fs = Fuelsensor_interface(str(sys.argv[1]), int(sys.argv[2]))
else:
    fs = Fuelsensor_interface()
fs.connect()
fs.reset()
time.sleep(0.2)
fs.send_raw_byte(1)
#fs.backup_timeseries() # ver porque se pega la respuesta aqui, ver que hay en la interfaz serial o bien debugear el codigo, programando con el pickit 2.
#fs.get_pos()
fs.close_socket()
