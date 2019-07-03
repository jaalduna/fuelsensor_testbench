import struct
import crcmod
import socket
import time
#import matplotlib.pyplot as plt
#AN1388 Microchip bootloader implementation

#constants declaration

##Command description
BK_TIMESERIES = 1
GET_NORM_ECHO = 2
GET_SDFT_ECHO = 3
RESET = 4
GET_HEIGHT = 5
GET_POS = 6
GET_PARAM = 7
SET_PARAM = 8
RESTORE_DEFAULT_PARAMS_TO_FLASH = 9
BACKUP_PARAMS_TO_FLASH = 10


#TODO: create a list of PARAMS constants using fields "PARAM_ID" and "nombre" from
# the table "lista de parametros" located at
#https://fuelsensor.readthedocs.io/en/latest/low_level_interface.html



crc16 = crcmod.predefined.mkPredefinedCrcFun("xmodem")

class Param(object):
    """ Param Class """
    def __init__(self,interface, param_id, num_bytes):
        super(Param, self).__init__()
        self.param_id = param_id 
        self.num_bytes = num_bytes
        self.value = 0
        self.interface = interface
    def get_value(self):
        if(self.num_bytes == 1):
            self.value = self.interface.get_param_byte(self.param_id)
        elif self.num_bytes == 2:
            self.value = self.interface.get_param_unsigned_short(self.param_id)
        elif self.num_bytes ==4:
            self.value = self.interface.get_param_float_32(self.param_id)
            
    def set_value(self,value):
        if(self.num_bytes ==1):
            self.interface.set_param_byte(self.param_id, value)
            self.value = self.interface.get_param_byte(self.param_id)
        elif (self.num_bytes == 2):
            self.interface.set_param_unsigned_short(self.param_id, value)
            self.value = self.interface.get_param_unsigned_short(self.param_id)
        elif (self.num_bytes == 4):
            self.interface.set_param_float_32(self.param_id, value)
            self.value = self.interface.get_param_float_32(self.param_id)



class Params(object):
    """ Params class """

    def __init__(self, interface):
        super(Params, self).__init__()
        self.PARAM_DATA_VECTOR_TYPE = 0x00
        self.PARAM_DATA_VECTOR_OFFSET = 0x02
        self.PARAM_PGA_GAIN = 0x04
        self.PARAM_NUM_PULSES = 0x05
        self.PARAM_PULSE_PERIOD = 0x06
        self.PARAM_PULSE_WIDTH = 0x07
        self.PARAM_RES_HV = 0x08
        self.PARAM_SDFT_MIN_PEAK_VALUE_TH = 0x09
        self.PARAM_SDFT_K = 0x0d
        self.PARAM_SDFT_N = 0x0f
        self.PARAM_SDFT_I_MIN = 0x11
        self.PARAM_SDFT_MIN_ECO_LIMIT = 0x13
        self.PARAM_SDFT_MAX_ECO_LIMIT = 0x14
        self.PARAM_SDFT_VAR_NORM = 0x15
        self.PARAM_SDFT_PEAK = 0x19
        self.PARAM_SDFT_SOUND_SPEED = 0x1d
        self.PARAM_SDFT_SAMPLE_RATE = 0x1f
        self.PARAM_SDFT_N_SAMPLES_ONE_VALID = 0x21
        self.PARAM_SKIP_PARAM = 0x23
        self.data_vector_type = Param(interface,self.PARAM_DATA_VECTOR_TYPE,2)
        self.data_vector_offset = Param(interface,self.PARAM_DATA_VECTOR_OFFSET,2)
        self.pga_gain = Param(interface, self.PARAM_PGA_GAIN,1)
        self.num_pulses = Param(interface, self.PARAM_NUM_PULSES,1)
        self.pulse_period = Param(interface, self.PARAM_PULSE_PERIOD,1)
        self.pulse_width = Param(interface, self.PARAM_PULSE_WIDTH,1)
        self.res_hv = Param(interface, self.PARAM_RES_HV,1)
        self.sdft_min_peak_value_th = Param(interface, self.PARAM_SDFT_MIN_PEAK_VALUE_TH,4)
        self.sdft_k = Param(interface, self.PARAM_SDFT_K,2)
        self.sdft_n = Param(interface, self.PARAM_SDFT_N,2)
        self.sdft_i_min = Param(interface,self.PARAM_SDFT_I_MIN,2)
        self.sdft_min_eco_limit = Param(interface, self.PARAM_SDFT_MIN_ECO_LIMIT,1)
        self.sdft_max_eco_limit = Param(interface, self.PARAM_SDFT_MAX_ECO_LIMIT,1)
        self.sdft_var_norm = Param(interface, self.PARAM_SDFT_VAR_NORM,4)
        self.sdft_peak = Param(interface, self.PARAM_SDFT_PEAK,4)
        self.sdft_sound_speed = Param(interface, self.PARAM_SDFT_SOUND_SPEED,2)
        self.sdft_sample_rate = Param(interface, self.PARAM_SDFT_SAMPLE_RATE,2)
        self.sdft_n_samples_one_valid = Param(interface, self.PARAM_SDFT_N_SAMPLES_ONE_VALID,2)
        self.skip_param = Param(interface, self.PARAM_SKIP_PARAM,2)

class Node(object):
    """ Node class """
    def __init__(self):
        super(Node,self).__init__()
        self.fs_interface = Fuelsensor_interface()
        self.params = Params(self.fs_interface)

class Fuelsensor_interface(object):
    """Fuelsensor_interface class """

    #command constants
    BK_TIMESERIES = 1
    GET_NORM_ECHO = 2
    GET_SDFT_ECHO = 3
    RESET = 4
    GET_HEIGHT = 5
    GET_POS = 6
    GET_PARAM = 7
    SET_PARAM = 8
    RESTORE_DEFAULT_PARAMS_TO_FLASH = 9
    BACKUP_PARAMS_TO_FLASH = 10

    def __init__(self,TCP_IP='192.168.0.10',TCP_PORT=5000):
        super(Fuelsensor_interface, self).__init__()
        self.TCP_IP = TCP_IP
        self.TCP_PORT = TCP_PORT 
        self.BUFFER_SIZE  = 2048
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout =1
        self.socket.settimeout(self.timeout)


    def __del__(self):
        self.socket.close()

    def send_cmd(self, cmd, params,rx_len,verbose=False):
        """ send a cmd to the device """
        packet = bytearray()
        packet += struct.pack(">H", cmd) # 2 bytes

        #fill with zeros so 4 bytes filled on the params field. 
        #for i in range(4 - len(params)):
        #        packet.append(0)

        #fill with params values #4 bytes
        for i in range(len(params)):
            packet.append(params[i])
#crc, not implemented yet
        packet.append(0)
        packet.append(0)
        #packet = bytearray()
        #for i in range(12):
        #    packet.append(i)
        if(verbose):
            self.print_modbus(str(packet))

        while(True):
            if(rx_len > 0):
                data = self.receive_retry(packet, rx_len + 2, verbose=False, connect=False)
                if(len(data) >= rx_len + 2):
                    data = data[0:rx_len + 2] #chunk garbage bytes
                    crc = str(data[len(data) - 2:])
                    calculated_crc = struct.pack('>H', crc16(str(data[4:len(data)- 2])))
                    if(verbose):
                        self.print_modbus(str(data))
                    if crc == calculated_crc:
                        break
                    else:
                        self.close_socket()
                        raise Exception("bad crc")
                else:
                    # print len(data)
                    #self.print_modbus(data)
                    raise Exception("not enougth rx bytes")
                    break
            else:
                #send packet in batches of 4 bytes

                self.send_batch(packet)
                return
        return data

    def bk_timeseries(self):
        """ backup timeseries on node. 

        data returns four bytes {0, cmd = 1, 0,0}
        """
        data = self.send_cmd_without_params(BK_TIMESERIES, 4)
        return data
    def get_norm_echo(self,offset, length):
        """ Return normalized echo"""
        params = bytearray()
        params += struct.pack('>H', offset)
        params += struct.pack('>H', length)
        for i in range(4):
            params.append(0)
        res = self.send_cmd(GET_NORM_ECHO, params, length +4) #+4 is for the  header 
        return res
    def get_sdft_echo(self,offset,length):
        """ returns sdft of echo"""
        params = bytearray()
        params += struct.pack('>H', offset)
        params += struct.pack('>H', length)
        for i in range(4):
            params.append(0)
        res = self.send_cmd(GET_SDFT_ECHO, params, length+4)
        return res        

    def get_complete_norm_echo(self, length,packet_size):
        """ get normalized echo timeseries of length 'length'"""
        truncated_len =  int(length / packet_size) + 1
        data = bytearray()
        for i in range (1,truncated_len):
            while(True):
                try:
                    partial_data = self.get_norm_echo((i-1)*packet_size,packet_size)
                except:
                    print "bad crc"
                    partial_data = bytearray(0)
                time.sleep(0.01)
                if len(partial_data) == (4+packet_size+2): 
                    break;
            data +=partial_data[4:len(partial_data) - 2 ]
            print len(data), "/", length  
        return data  

    def get_complete_sdft_echo(self, length,packet_size):
        """ get sdft echo timeseries of length 'length' """
        truncated_len =  int(length / packet_size) + 1
        data = bytearray()
        for i in range (1,truncated_len):
            while(True):
                try:
                        partial_data = self.get_sdft_echo((i-1)*packet_size,packet_size)
                except:
                        print "bad crc"
                        partial_data = bytearray(0)
                time.sleep(0.01)
                if len(partial_data) == (4+packet_size+2): 
                    break;
            data +=partial_data[4:len(partial_data) - 2 ]
            print len(data), "/", length 
        return data  

    def get_height(self):
        """ get hight of liquid in meters."""    
        data = self.send_cmd_without_params(GET_HEIGHT, 8)

        height = struct.unpack('<f', data[4:8])[0]
        print "height: " + str(height) + " [m]"
        return height

    def get_pos(self):
        """ get variable pos, an int value proportional to hight"""
        data = self.send_cmd_without_params(GET_POS, 8)
        pos = struct.unpack('<f', data[4:8])[0]
        print "pos: " + str(pos) + " [samples]" 
        return pos   
    def reset(self):
        """ reset fuelsensor and enter into Bootloader mode"""
        self.send_cmd_without_params(RESET, 0)

    def send_cmd_without_params(self, name, num_bytes):
        """ send command name, filling params with 4 zeros"""
        params_field = bytearray()
        params_field = struct.pack('>BBBBBBBB',0,0,0,0,0,0,0,0) 
        return self.send_cmd(name, params_field,num_bytes)
        

    def check_crc(self, msg):
        calculated_crc = bytearray()
        calculated_crc += struct.pack("<H", crc16(str(msg[0:len(msg)- 2])))
        #self.print_modbus(str(calculated_crc))
        if(calculated_crc == msg[len(msg) -2 : len(msg)]):
            return True
        else:
            return False

        # print "packet content: ",
        # print(":".join("{:02x}".format(ord(c)) for c in str(packet)))


    def connect(self):
        """ Try to stablish a tcp/ip connection with fuelSensor device"""
        while True:
            try:
                print "connecting...",
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.TCP_IP, self.TCP_PORT))
                #self.socket.settimeout(None)
                print "success!"
                return
            except:
                print "can't connect"
                self.close_socket()
                #return

    def receive_retry(self,packet,length,verbose = False,connect = True):
        start_time = 0
        stop_time = 0
        if(connect):
            self.connect() 
        while True:
            try:
                if(verbose):
                    print "sending: ",
                    #self.print_modbus(str(packet))
                start_time = (time.time()*1000)
                #self.print_modbus(str(packet))

                #self.socket.send(packet)
                self.send_batch(packet)
                
                counter = 5 
                data = ""

                while(counter >0):
                    counter -= 1
                    data += self.socket.recv(self.BUFFER_SIZE)
                    
                    # if(verbose):
                    #     print data
                    #self.print_modbus(data)
                     
                    if(len(data) >= length):
                        stop_time = (time.time()*1000)
                        if(connect):
                            self.close_socket()
                        if(verbose):
                            print "time elapsed: ",
                            print str(stop_time - start_time)
                            print "data received ok: ",
                            if(verbose):
                                self.print_modbus(data)


                        return data
                
            except:
                #self.print_modbus(data)
                print "no answer...",
                
                if(True):
                    self.close_socket()
                    self.connect()

    def close_socket(self):
        """ Try to close tcp/ip SOCKET with FuelSensor device"""
        #lets close socket
        self.socket.close()
        time.sleep(0.1)
        #lets reasign socket so it can be opened again
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        time.sleep(0.1)

    def print_modbus(self,res):
        print(":".join("{:02x}".format(ord(c)) for c in res))
    #def backup_timeseries(self):
    #    params = bytearray()
    #    self.send_cmd(BK_TIMESERIES,params,8)

    def get_param(self, param_id, num_bytes_response):
        #TODO: Implement get_param function. get_param should query, print and return the parameter given by param_id. 
        # using the command self.send_cmd. Return value should be converted from bytearray to type described at
        #table "Lista de parametros " located at https://fuelsensor.readthedocs.io/en/latest/low_level_interface.html. Use , using struct.unpack() function for that.
        #second argument from send_cmd should be 4 bytes. Add them at the end. 

        #lets transform param_id into a 4 bytes bytearra() with the last byte
        param_field = struct.pack('>BBBBBBBB', param_id,0,0,0,0,0,0,0)
        param_value_bytearray = self.send_cmd(GET_PARAM, param_field, num_bytes_response +4) #+4 is for header size 
        #check number of bytes returned, it seems that answer is always 4 bytes ??

        #complete for other param_id values, struct.unpack format should be
        # ''
        return param_value_bytearray

    def get_param_byte(self,param_id):
        param_value_bytearray = self.get_param(param_id,4)
        return struct.unpack('>B', param_value_bytearray[4])[0]

    def get_param_unsigned_short(self,param_id):
        param_value_bytearray = self.get_param(param_id,4)
        return struct.unpack('<H',param_value_bytearray[6:8])[0]

    def get_param_float_32(self, param_id):
        param_value_bytearray = self.get_param(param_id,4)
        return struct.unpack('<f', param_value_bytearray[4:8])[0]

    def set_param(self, param_id, num_bytes_response, value):
        param_field = struct.pack('>BBBB',param_id,0,0,0)
        param_field += value
        #update param on the remote node
        response = self.send_cmd(SET_PARAM, param_field, num_bytes_response +4) #+4 is for header size
        #update param on the local representation of the node
        return response

    def set_param_byte(self, param_id,value):
        value_field =  struct.pack('>BBBB',value,0,0,0)
        response =  self.set_param(param_id, 4, value_field)
        return response

    def set_param_unsigned_short(self, param_id,value):
        value_field =  struct.pack('<HH',0,value)
        response = self.set_param(param_id, 4, value_field)    
        return response
    def set_param_float_32(self, param_id,value):
        value_field =  struct.pack('<f',value)
        response = self.set_param(param_id, 4, value_field)  
        return response

    def backup_params_to_flash(self):
        response = self.send_cmd_without_params(BACKUP_PARAMS_TO_FLASH,4)

    def send_batch(self,packet):
        packet_size = 4 
        for i in range(len(packet)/packet_size):
            self.socket.send(packet[i*packet_size:i*packet_size+packet_size])
            time.sleep(0.05)  

    def get_reg(self):
        """ returns last unread log regsiter as raw_log. If there is no registers it returns 0.
        A raw_log correspond to a bytearray() object that has to be parsed. Log Class implement this parser """
        #call get_cmd with parameter GET_REG = 11 and length determined by number of bytes inside a log

    def get_reg_num(self):
        """ returns number of available log registers that have not being read yet"""
        #GET_REG_NUM = 12
    def increment_reg(self,id_reg):
        """ increment from id_reg register to the next one. 
        Cada registro debe contar con un ID, para determinar si la funcion increment_reg()

         """
    def send_raw_byte(self,byte):
        self.socket.send(bytearray(byte))


class Log(object):
    """Log class. It describes the sructure of data logs.

    Args:
        raw_log (bytearray) : bytearray with raw_log info.
     """
    def __init__(self, raw_log = 0):
        """ Log constructor. If no raw_log is given, log attributes are filled with default values"""
        super(Log, self).__init__()
        #if raw_log = 0, use default values
        #else parse raw_log and update attributes
        #attributes:
        # timestamp, hight
    def log_parser(self,raw_log):
        """ read raw_log, parse it, create and update object attributes"""        
        



# fs_interface = Fuelsensor_interface()
# fs_interface.connect()
# fs_interface.reset()
# fs_interface.close_socket()
# for i in range(1,10):
#     fs_interface.connect()
#     params = bytearray()
#     #fs_interface.reset()
#     fs_interface.get_height()
#     # fs_interface.reset()
#     # fs_interface.reset()
#     fs_interface.close_socket()
#     time.sleep(0.5)
#fs_interface.send_cmd(BK_TIMESERIES, params, 8)
# time.sleep(0.5)

# num_of_samples = 16000;
# data_bytes_norm = fs_interface.get_complete_norm_echo(num_of_samples)
# #data_bytes_sdft = fs_interface.get_complete_sdft_echo(num_of_samples)
# #fs_interface.send_cmd(RESET, params, 0)
# fs_interface.get_height()
# fs_interface.get_pos()
# fs_interface.close_socket()


# # data_bytes_sdft = fs_interface.get_complete_sdft_echo(num_of_samples)
# # fs_interface.close_socket()

# data_norm = []
# for i in range(0,num_of_samples/4):
#     new_data = struct.unpack('<f', data_bytes_norm[i*4:(i+1)*4])

#     # if (new_data[0] > 1 or new_data[0] < -1):
#     #     print "new_data:" + str(new_data)
#     #     pass
#     #     new_data = (0.5,1)
#     data_norm.append(new_data[0])
# print len(data_norm)

# plt.plot(data_norm)
# plt.grid(True)
# plt.title('Echo vs time')
# plt.ylabel('norm echo')
# plt.show()

# data_sdft = []
# for i in range(0,num_of_samples/4):
#     new_data = struct.unpack('<f', data_bytes_sdft[i*4:(i+1)*4])
#     data_sdft.append(new_data[0])
# print len(data_sdft)


# plt.plot(data_sdft)
# plt.ylabel('norm echo')
# plt.show()



