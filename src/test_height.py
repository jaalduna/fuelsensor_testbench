import firmware
import unittest

class TestFirmware(unittest.TestCase):

    def test_pulse(self):
        """
        Test that the height is within acceptable values
        """
        result = firmware.pulse_script()
        self.assertTrue(0.155 <= result <= 0.162)
        # height is on meters and the test column has a height of 15.7cm

if __name__ == '__main__':
    unittest.main(exit=False)