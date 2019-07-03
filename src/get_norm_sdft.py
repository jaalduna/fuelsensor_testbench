import sys
from Fuelsensor_interface import Fuelsensor_interface
import time
import matplotlib.pyplot as plt
import struct
import pickle

if len(sys.argv) == 5:
    fs = Fuelsensor_interface(str(sys.argv[1]), int(sys.argv[2]))
else:
    fs = Fuelsensor_interface()
print "conectando"
fs.connect()
print "backup_timeseries"
fs.bk_timeseries()
time.sleep(1)
print "get norm echo"
offset = 0
length = int(sys.argv[3])
packet_size = int(sys.argv[4])
#data = fs.get_norm_echo(offset, length)
data = fs.get_complete_sdft_echo(length,packet_size)
fs.print_modbus(str(data))



#fs.backup_timeseries() # ver porque se pega la respuesta aqui, ver que hay en la interfaz serial o bien debugear el codigo, programando con el pickit 2.
#fs.get_pos()
fs.close_socket()


data_norm = []
for i in range(0,length/4):
    new_data = struct.unpack('<f', data[i*4:(i+1)*4])
    # if (new_data[0] > 1 or new_data[0] < -1):
    #     print "new_data:" + str(new_data)
    #     pass
    #     new_data = (0.5,1)
    data_norm.append(new_data[0])
print len(data_norm)

for i in range(1,len(data_norm)):
    print data_norm[i]

plt.plot(data_norm)
plt.grid(True)
plt.title('Echo vs time')
plt.ylabel('norm echo')
plt.show()


with open('noise_raw_data', 'w') as f:  # Python 3: open(..., 'wb')
    pickle.dump([data_norm], f) 