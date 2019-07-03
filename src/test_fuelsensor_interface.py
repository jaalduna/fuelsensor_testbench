import unittest
from mock import patch
from Fuelsensor_interface import Fuelsensor_interface
import struct
from Fuelsensor_interface import Params
import crcmod
from Bootloader import Bootloader
import time



crc16 = crcmod.predefined.mkPredefinedCrcFun("xmodem")

class TestFuelsensor_interface(unittest.TestCase):

    def setUp(self):
        #print 'setUp'
        self.int_1 = Fuelsensor_interface()
        self.params = Params(self.int_1)
        self.bld = Bootloader()

    def tearDown(self):
        self.int_1.close_socket()
        pass

    def test_send_cmd(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.receive_retry') as mocked_receive_retry, \
             patch('Fuelsensor_interface.socket.socket.send') as mocked_send:
            rtrn = bytearray()
            data = struct.pack('>B',10)
            crc = struct.pack('>H', crc16(str(data)))
            rtrn.append(data)
            rtrn +=crc

            mocked_receive_retry.return_value = rtrn

            params_field = bytearray()
            params_field = struct.pack('>HH', 0,self.params.PARAM_PGA_GAIN)

            #result =  self.int_1.send_cmd(self.int_1.GET_PARAM,params_field, self.params.pga_gain.num_bytes)
            #mocked_receive_retry.assert_called_with()
            #self.assertEqual(result, data)

    def test_get_param(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.send_cmd') as mocked_send_cmd, \
             patch('Fuelsensor_interface.socket.socket.send') as mocked_send:

             data = struct.pack('>B', 10)
             mocked_send_cmd.return_value = data

             result = self.int_1.get_param(self.params.pga_gain.param_id, self.params.pga_gain.num_bytes)
             self.assertEqual(result, data)
             #mocked_send_cmd.assert_called_with('')

             #send_cmd(GET_PARAM, param_field, num_bytes_response) 

    def test_get_param_byte(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.get_param') as mocked_get_param, \
             patch('Fuelsensor_interface.socket.socket.send') as mocked_send:     

             data = 10
             mocked_get_param.return_value =  str(bytearray([0,7,0,4,data,0,0,0,0,0]))

             result = self.int_1.get_param_byte(self.params.pga_gain.param_id)
             mocked_get_param.assert_called_with(self.params.pga_gain.param_id,4)
             self.assertEqual(result, data)
    def test_get_param_unsigned_short(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.get_param') as mocked_get_param:   

             source_data = 1000;
             data = struct.pack('<H', source_data)
             mocked_get_param.return_value =  str(bytearray([0,7,0,4,0,0]) + data + bytearray([0,0]))

             result = self.int_1.get_param_unsigned_short(self.params.sdft_sound_speed.param_id)
             mocked_get_param.assert_called_with(self.params.sdft_sound_speed.param_id,4)
             self.assertEqual(result, source_data)

    def test_get_param_float_32(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.get_param') as mocked_get_param:   

             source_data = 3.14161;
             data = struct.pack('<f', source_data)
             mocked_get_param.return_value =  str(bytearray([0,7,0,4]) + data + bytearray([0,0]))

             result = self.int_1.get_param_float_32(self.params.sdft_min_peak_value_th.param_id)
             mocked_get_param.assert_called_with(self.params.sdft_min_peak_value_th.param_id,4)
             self.assertAlmostEqual(result, source_data,places=5)

    def test_set_param(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.send_cmd') as mocked_send_cmd:
             #print('test set_param')
             data = struct.pack('>B', 1)
             mocked_send_cmd.return_value = data
             value = struct.pack('>B',10)
             result = self.int_1.set_param(self.params.pga_gain.param_id, self.params.pga_gain.num_bytes, value)
             self.assertEqual(result, data)

    def test_set_param_byte(self):
        with patch('Fuelsensor_interface.Fuelsensor_interface.set_param') as mocked_set_param:    
             data = 10
             data_field = struct.pack('>BBBB',data,0,0,0)
             mocked_set_param.return_value =  str(bytearray([0,7,0,4]) + data_field + bytearray([0,0]))

             result = self.int_1.set_param_byte(self.params.pga_gain.param_id,data)
             mocked_set_param.assert_called_with(self.params.pga_gain.param_id,4,data_field)
             self.assertEqual(result, mocked_set_param.return_value)  

    def test_set_param_unsigned_short(self):    
        with patch('Fuelsensor_interface.Fuelsensor_interface.set_param') as mocked_set_param:    
             data = 1000
             data_field = struct.pack('<H', data)
             mocked_set_param.return_value =  str(bytearray([0,7,0,4,]) + data_field + bytearray([0,0]))

             result = self.int_1.set_param_unsigned_short(self.params.sdft_sound_speed.param_id,data)
             mocked_set_param.assert_called_with(self.params.sdft_sound_speed.param_id,4,   str(bytearray([0,0]))+str(data_field))
             self.assertEqual(result,mocked_set_param.return_value)  
    def test_set_param_float_32(self):    
        with patch('Fuelsensor_interface.Fuelsensor_interface.set_param') as mocked_set_param:    
             data = 3.1416
             data_field = struct.pack('<f',data)
             mocked_set_param.return_value =  str(bytearray([0,7,0,4]) + data_field + bytearray([0,0]))

             result = self.int_1.set_param_float_32(self.params.sdft_sound_speed.param_id,data)
             mocked_set_param.assert_called_with(self.params.sdft_sound_speed.param_id,4,data_field)
             self.assertEqual(result,mocked_set_param.return_value)  

    def test_get_height(self):
            print "testing get_height"
            self.int_1.connect()
            result = self.int_1.get_height();
            self.int_1.close_socket()

            self.assertEqual(result, 0)
    def test_bk_timeseries(self):
            print "testing test_bk_timeseries"
            self.int_1.connect()
            result = self.int_1.bk_timeseries()
            self.int_1.close_socket()
            self.assertEqual(result,bytearray([0,1,0,0,0,0]))
    def test_get_norm_echo(self):
            print "testing get_norm_echo"
            self.int_1.connect()
            offset = 0
            length = 10
            result = self.int_1.get_norm_echo(offset,length)
            self.int_1.print_modbus(str(result))
            self.int_1.close_socket()

    def test_get_sdft_echo(self):
            print "testing get_norm_echo"
            self.int_1.connect()
            offset = 0
            length = 10
            result = self.int_1.get_sdft_echo(offset,length)
            self.int_1.print_modbus(str(result))
            self.int_1.close_socket()
    def test_get_pos(self):
            print "testing get_pos"
            self.int_1.connect()
            result = self.int_1.get_pos();
            self.int_1.close_socket()

            self.assertEqual(result, 0)
    def test_reset(self):
        print "testing reset"
        print "reseting"
        self.int_1.connect()
        self.int_1.reset()
        self.int_1.close_socket()

        print "entering bootloader"
        self.bld.connect()
        self.bld.enter_bootloader()
        self.bld.close_socket()
        print "read bld version"
        time.sleep(0.5)
        self.bld.read_version()
        self.bld.connect()

        print "jumping back to app"
        self.bld.jump_to_app()
        self.bld.close_socket()

    def test_get_param(self):
        print "testing get param"
        print "get param_data_vector_type"
        
        
        print "get data_vector_offset"    

        self.params.data_vector_offset.get_value()
        self.params.data_vector_offset.get_value()
        self.assertEqual(self.params.data_vector_offset.value, 0)

        print "get pga_gain"    
        self.params.pga_gain.get_value()
        self.assertEqual(self.params.pga_gain.value, 2)

        print "get num_pulses"   
        self.params.num_pulses.get_value()
        self.assertEqual(self.params.num_pulses.value, 4)

        print "get pulse_period"   
        self.params.pulse_period.get_value()
        self.assertEqual(self.params.pulse_period.value, 87)

        print "get pulse_width"   
        self.params.pulse_width.get_value()
        self.assertEqual(self.params.pulse_width.value, 30)

        print "get res_hv"   
        self.params.res_hv.get_value()
        self.assertEqual(self.params.res_hv.value, 40)

        print "get sdft_min_peak_value_th"   
        self.params.sdft_min_peak_value_th.get_value()
        self.assertEqual(self.params.sdft_min_peak_value_th.value, 0.5)

        print "get sdft_k"   
        self.params.sdft_k.get_value()
        self.params.sdft_k.get_value()
        self.assertEqual(self.params.sdft_k.value, 39)

        print "get sdft_n"   
        self.params.sdft_n.get_value()
        self.assertEqual(self.params.sdft_n.value, 107)

        print "get sdft_i_min"   
        self.params.sdft_i_min.get_value()
        self.assertEqual(self.params.sdft_i_min.value, 450)

        print "get sdft_min_eco_limit"   
        self.params.sdft_min_eco_limit.get_value()
        self.assertEqual(self.params.sdft_min_eco_limit.value, 30)

        print "get sdft_max_eco_limit"   
        self.params.sdft_max_eco_limit.get_value()
        self.assertEqual(self.params.sdft_max_eco_limit.value, 80)

        print "get sdft_var_norm"   
        self.params.sdft_var_norm.get_value()
        self.assertEqual(self.params.sdft_var_norm.value, 50000)

        print "get sdft_peak"   
        self.params.sdft_peak.get_value()
        self.assertEqual(self.params.sdft_peak.value, 10)

        print "get sdft_sound_speed"   
        self.params.sdft_sound_speed.get_value()
        self.assertEqual(self.params.sdft_sound_speed.value, 1495)

        print "get sdft_sample_rate"   
        self.params.sdft_sample_rate.get_value()
        self.assertEqual(self.params.sdft_sample_rate.value, 2981)

        print "get sdft_n_samples_one_valid"   
        self.params.sdft_n_samples_one_valid.get_value()
        self.assertEqual(self.params.sdft_n_samples_one_valid.value, 20)

        print "get skip_param"   
        self.params.skip_param.get_value()
        self.assertEqual(self.params.skip_param.value, 20000)

    def test_set_param(self):
        print "test set param: unsigned short type"
        value = 32
        self.int_1.connect()
        self.params.sdft_n.set_value(value)
        self.assertEqual(self.params.sdft_n.value,value)

        value = 107
        self.params.sdft_n.set_value(value)
        self.assertEqual(self.params.sdft_n.value,value)

        print "test set param: byte type"
        value = 32
        self.int_1.connect()
        self.params.pulse_period.set_value(value)
        self.assertEqual(self.params.pulse_period.value,value)

        value = 87
        self.params.pulse_period.set_value(value)
        self.assertEqual(self.params.pulse_period.value,value)

        print "test set param: float32 type"
        value = 32
        self.int_1.connect()
        self.params.sdft_var_norm.set_value(value)
        self.assertAlmostEqual(self.params.sdft_var_norm.value,value,places=5)
        value = 50000
        self.params.sdft_var_norm.set_value(value)
        self.assertAlmostEqual(self.params.sdft_var_norm.value,value,places=5)
        



if __name__ == '__main__':
    unittest.main()