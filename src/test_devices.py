import devices
import unittest

class TestDevices(unittest.TestCase):
    """
    Test devices scripts
    """

    def test_rtc(self):
        """
        test rtc device
        """
        print("testint rtc")
        result = devices.rtc_script()
        self.assertEqual(result,b'\x81')
        

    def test_ds2482(self):
        """
        test ds2482 i2c to 1-wire
        """
        print("testint ds2482")
        result = devices.ds2482_script()
        self.assertEqual(result,b'\x01')
    def test_imu(self):
        """
        test imu i2c connectivity
        """
        print("testint imu")
        result =  devices.imu_script()
        self.assertEqual(result,b'\x68')

    def test_temp_sensor(self):
        """
        test ds18b20 temp sensor trough ds2482 converter
        """
        print("testint temperature sensor")
        result = devices.temp_sensor_script()
        self.assertEqual(result,b'\x28')
    def test_ad5272(self):
        """
        teset ds5272 variable resistor for HV control
        """
        print("testing ad5272")
        result = devices.ad5272_script()
        self.assertEqual(result,b'\x01\x80')

if __name__ == '__main__':
    unittest.main(exit=False)