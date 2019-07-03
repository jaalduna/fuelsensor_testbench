import struct
import crcmod
import socket
import time

#AN1388 Microchip bootloader implementation

#constants declaration

##Control character description
SOH  = 0x01 #Marks the beginning of a frame
EOT = 0x04 #Marks the end of a frame
DLE = 0x10 #Data link escape

##Command description
READ_BOOTLOADER_VERSION = 0x01
ERASE_FLASH = 0x02
PROGRAM_FLASH = 0x03
READ_CRC = 0x04
JUMP_TO_APP = 0x05

crc16 = crcmod.predefined.mkPredefinedCrcFun("xmodem")

class Bootloader(object):
    """Bootloader class"""
    def __init__(self,tcp_ip='192.168.0.10', tcp_port=5000, timeout=2):
        super(Bootloader, self).__init__()
        """ Constructor. No parameters are expected"""
        self.TCP_IP = tcp_ip
        self.TCP_PORT = tcp_port 
        self.BUFFER_SIZE  = 1024
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.timeout = timeout
        self.socket.settimeout(self.timeout)

    def __del__(self):
        self.socket.close()


    def read_version(self):
        """ Return bootloader firmware version from FuelSensor device.
        Function calls internally connect() and close_socket(), so there is no need to call them manually."""
        response = self.tx_rx_cmd(READ_BOOTLOADER_VERSION,7)
        try:
            #get version
            mayor_version = response[1]
            minor_version = response[2]
            print "Bootloader version: "+ str(mayor_version) + "." + str(minor_version)
        except:
            print "error"
            time.sleep(1)
    def tx_rx_cmd(self,cmd_name, response_len, payload = None, connect = True):
        packet = bytearray()
        packet.append(SOH)
        packet.append(cmd_name)
        #crc calculation
        if(payload != None):
            packet += payload
        packet += struct.pack("<H", crc16(str(packet[1:len(packet)]))) # calculate CRC discarding SOH
        packet.append(EOT)
        packet = self.encode(packet)
        response = self.receive_retry(packet,response_len,False, connect)
        response = self.decode(response)

        self.print_modbus(str(response))
        if(self.check_crc(response)):
            pass
            #print "crc ok"
        else:
            print "crc error"
            return
        if(response[0] == cmd_name):
            pass
            #print "READ_BOOTLOADER_VERSION response"
        else:
            print "invalid cmd answer"
            return 0

        return response

    def erase_flash(self,connect = True):
        """ Erase program memory flash from FuelSensor device.
        This function only clear the app. Bootloader persist on memory.
        
        'connect' parameter controls if tcp connection is stablished before executing the the erase flash operation.
        Always keep it as True, or wich is the same, call the function with the default values as erase_flash()"""
        response = self.tx_rx_cmd(ERASE_FLASH, 5,None,connect)
        try:
            print "flash erased"
        except:
            print "error"
            time.sleep(1)
#02 00 00 04 00 00 fa
    def program_flash(self, record, verbose = False, connect = True):
        record_in_bytes = bytearray.fromhex(record)
        response = self.tx_rx_cmd(PROGRAM_FLASH,5,record_in_bytes, connect)
        #self.print_modbus(str(response))
        if (len(response) == 3):
            print "program ok"

    def read_crc(self,addr, num_bytes):
        payload = bytearray()
        payload += addr[len(num_bytes):None:-1]
        payload +=num_bytes[len(num_bytes):None:-1]
        self.print_modbus(str(payload))
        response = self.tx_rx_cmd(READ_CRC,7,payload)
        if(len(response) == 5):
            print "crc received: ",
            self.print_modbus(str(response[1:3]))

    def jump_to_app(self):
        """Jump to application from bootloader."""
        print "jumping to app"
        packet = bytearray()
        packet.append(SOH)
        packet.append(JUMP_TO_APP)
        packet += struct.pack("<H", crc16(str(packet[1:len(packet)]))) # calculate CRC discarding SOH
        packet.append(EOT)
        packet = self.encode(packet)
        self.socket.send(packet)
        # response = self.receive_retry(packet,0,False)

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
    def encode(self, packet):
        #for each data byte
        result = bytearray()
        result.append(packet[0])

        for x in packet[1:len(packet) - 1]:
            if(x == DLE or x == SOH or x == EOT):
                result.append(DLE)
                result.append(x)
            else:
                result.append(x)

        result.append(packet[len(packet) - 1])
        return result
    def decode(self, packet):
        prev_is_dle = False
        #for each data byte
        result = bytearray()
        #find first SOH byte

        if(packet[0] != b'\x01'):
            print "First byte is not SOH!"
            return 0
        if(packet[len(packet) - 1 ] != b'\x04'):
            print "Last byte is not EOT"
            return 0

        for x in packet[1:len(packet) -1]:
            if(prev_is_dle):
                prev_is_dle = False
                result.append(x)
            elif(x == b'\x10'):
                prev_is_dle = True
            else:
                prev_is_dle = False
                result.append(x)
        return result

    def connect(self):
        """Try to stablish a tcp/ip socket with FuelSensor device. """
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
        print connect
        if(connect):
            self.connect()
        while True:
            try:
                if(verbose):
                    print "sending: ",
                    self.print_modbus(str(packet))
                start_time = (time.time()*1000)
                #self.print_modbus(str(packet))

                self.socket.send(packet)
                time.sleep(0.6) 
                counter = 5 
                data = ""
                if(length > 0):
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
                                self.print_modbus(data)
                            return data
                else:
                    return 0
                
            except:
                
                print "no answer...",
                
                if(True):
                    self.close_socket()
                    self.connect()

    def close_socket(self):
        """ Try to close socket connection."""
        #lets close socket
        self.socket.close()
        time.sleep(0.1)
        #lets reasign socket so it can be opened again
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.timeout)
        time.sleep(0.1)

    def print_modbus(self,res):
        print(":".join("{:02x}".format(ord(c)) for c in res))

    def calculate_record_crc(self, record):
        #record structure :BBaaAATTDDCC
        #transform record into bytearray

        result = list()
        record = bytearray.fromhex(record)

        #get number of num_bytes
        i = 0
        num_bytes = record[i]
        i += 1
        #address
        addr_h = record[i]
        i += 1
        addr_l = record[i]
        i += 1
        #get type
        _type = record[i]
        if(_type == 0): #if data record
            i +=1
            #lets calculate data crc
            calculated_crc = struct.pack("<H", crc16(str(record[i:i+num_bytes])))
            result.append(num_bytes)
            result.append(addr_h)
            result.append(addr_l)
            result.append(_type)
            result.append(calculated_crc)
            return result
        else:
            return []
    #this function is not implemented yet
    def program_flash_and_validate(self, record):
        #TODO: keep track of high bytes address on each write record so CRC
        result = self.calculate_record_crc(record)
        if(len(result) > 0):
            calculated_crc = result[2]
            self.program_flash(record)
        else:
            self.program_flash(record)


    def file_len(self, file_name):
        with open(file_name) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

    def program_file(self, file_name, connect = True):
        """ Program file specified in parameter 'file_name' ."""
        self.erase_flash(connect)

        numLinesTotal = self.file_len(file_name)
        numLines = 0

        f = open(file_name, 'r')
        mtu = 900 

        while(True):
            print "\rprogramming: {:0.1f}%".format(numLines*1.0/numLinesTotal*100),
            record = ''
            num_bytes = 0
            inc = 0
            while len(record) < mtu:
                line = f.readline()
                if(len(line) == 0):
                    break
                record += line[1:-1]
                inc += 1

            print "record len: " + str(len(record))

            if(len(record) == 0):
                print ""
                print "program transfer complete ;)"
                break
            self.program_flash(record,False, connect)
            numLines +=inc
    def validate_file(self, file_name):
        numLinesTotal = self.file_len(file_name)
        numLines = 0
        f = open(file_name, 'r')
        while(True):
            print "\validating: {:0.1f}%".format(numLines*1.0/numLinesTotal*100),
            record = ''
            num_bytes = 0
            inc = 1
            record = f.readline()
            record = record[1:-1]
            if(len(record) == 0):
                print ""
                print "program transfer complete ;)"
                break
    def enter_bootloader(self):
        response = self.socket.send(bytearray(1))
# b = Bootloader()
# b.read_version()
# b.connect()
# b.program_file("aiko1_diciembre.hex", False)
# b.close_socket()

# b.connect()
# b.jump_to_app();
# b.close_socket()

#b.read_version()

# while(True):
#     b.jump_to_app()
#     b.connect()
#     data = ""
#     time.sleep(2)
#     data += b.socket.recv(250)
#     b.close_socket()
#     print data

#b = Bootloader()
#count = 1
#while(count>0):
#    count -= 1
#    print"reading version"
#    b.read_version()
#    print ""
#    #print "eraseing flash"
#    #b.erase_flash()
#    #print ""
#    #print "programming flash"
#    #b.program_flash("020000040000fa")
#    #b.program_flash("020000041d00dd")
#    #data_record = "100010000600400f0000000000601a40c0045a7f34100020000500401300000000019d1a3c881f5a275c"
#    #b.program_flash(data_record)
#    #b.close_socket()
#    b.connect()
#    b.program_file('test_hola.hex', False)
#    b.close_socket()
#    #result = b.calculate_record_crc(data_record)
#    #b.print_modbus(str(result[2]))
#    print ""
#    print "reading crc"
#    #b.read_crc(bytearray.fromhex("9d000010"),bytearray.fromhex("00000010"))
#    #b.erase_flash()
#    b.jump_to_app()
#    
#    b.connect()
#    time.sleep(1) 
#    data = b.socket.recv(22)
#    b.close_socket()
#    print data
