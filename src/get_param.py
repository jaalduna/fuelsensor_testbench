import sys
from Fuelsensor_interface import Fuelsensor_interface
from Fuelsensor_interface import Params

if len(sys.argv) == 3:
    fs = Fuelsensor_interface(str(sys.argv[1]), int(sys.argv[2]))
else:
    fs = Fuelsensor_interface('192.168.1.101', 5000)

params = Params(fs)

params.sdft_i_min.interface.connect()
params.pulse_period.get_value()
print "pulse_period: ", params.pulse_period.value

params.sdft_i_min.interface.close_socket()


 