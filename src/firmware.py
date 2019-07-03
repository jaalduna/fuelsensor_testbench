import time
from Fuelsensor_interface import Fuelsensor_interface
from Fuelsensor_interface import Params
from Bootloader import Bootloader

def pulse_script():
    fs = Fuelsensor_interface('192.168.1.101',5000)
    b = Bootloader('192.168.1.101',5000)

    #reset to go into bootloader
    fs.connect()
    fs.reset()
    time.sleep(0.2)
    fs.send_raw_byte(1)
    fs.close_socket()

    #jump to app
    b.read_version()
    b.connect()
    b.jump_to_app()
    b.close_socket()

    time.sleep(0.5)
    #set pga gain to 4
    print("configuring params")
    params = Params(fs)
    params.sdft_i_min.interface.connect()
    params.sdft_i_min.set_value(200)
    params.sdft_k.set_value(49)
    params.pga_gain.set_value(2)
    params.num_pulses.set_value(10)
    params.pulse_width.set_value(7)
    params.pulse_period.set_value(87)
    params.sdft_sample_rate.set_value(2500)
    params.sdft_i_min.interface.close_socket()

    print("sdft_i_min: ", params.sdft_i_min.value)
    print("sdft_k: ", params.sdft_k.value)
    print("pga_gain: ", params.pga_gain.value)
    print("num_pulses: ", params.num_pulses.value)
    print("pulse_width: ", params.pulse_width.value)
    print("pulse_period: ", params.pulse_period.value)
    print("sdft_sample_rate: ", params.sdft_sample_rate.value)

    #backup params to flash
    print("backup params to flash")
    fs.connect()
    fs.backup_params_to_flash()
    fs.close_socket()



    print("wait 10 sec to sdft get stabilized")
    time.sleep(10)
    #get high
    fs.connect()
    height = fs.get_height()
    fs.close_socket()

    return height