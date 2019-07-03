from pyBusPirateLite import *
import time

def rtc_script():
    i2c = I2C()
    i2c.enter()
    #enable RTC
    i2c.write_then_read(3,0,[0xde, 0x00, 0x80])
    time.sleep(1.25)
    i2c.write_then_read(2,0,[0xde, 0x00])
    return (i2c.write_then_read(1,1,[0xdf]))

def ds2482_script():
    i2c = I2C()
    i2c.enter()
    #reset device
    i2c.write_then_read(2,0,[0x30, 0xf0])
    i2c.write_then_read(1,1,[0x31])
    #set config reg
    i2c.write_then_read(3,0,[0x30, 0xd2, 0xe1])
    return i2c.write_then_read(1,1,[0x31])

def temp_sensor_script():
    ONEWWB = 0xa5
    ONEWRB = 0x96
    SRP = 0xe1
    DATAREG = 0xe1
    idle_time = 0.1

    #reset i2c to 1-wire converter
    ds2482_script()
    i2c = I2C()
    i2c.enter()
    #1wr reset
    i2c.write_then_read(2,0,[0x30, 0xb4])
    time.sleep(idle_time)
    i2c.write_then_read(1,1,[0x31])
    #1wr write 0x33 (ask for address)
    i2c.write_then_read(3,0,[0x30, ONEWWB, 0x33])
    time.sleep(idle_time)

    #read one byte
    i2c.write_then_read(2,0,[0x30, ONEWRB])
    time.sleep(idle_time)
    i2c.write_then_read(3,0,[0x30, SRP, DATAREG])
    return i2c.write_then_read(1,1,[0x31])


def imu_script():
    i2c = I2C()
    i2c.enter()
    #read who_am_i register (0x0f)
    i2c.write_then_read(2,0,[0xd6, 0x0f])
    return i2c.write_then_read(1,1,[0xd7])


def ad5272_script():
    i2c = I2C()
    i2c.enter()
    #enable writing
    i2c.write_then_read(3,0,[0x5e, 0x1c, 0x03])
    #write some value on the rdac
    i2c.write_then_read(3,0,[0x5e, 0x05, 0x80])
    #backup data to memory
    i2c.write_then_read(3,0,[0x5e, 0x0c, 0x00])
    #read current value
    time.sleep(0.2)
    i2c.write_then_read(3,0,[0x5e, 0x08, 0x00])
    return i2c.write_then_read(1,2,[0x5f])