from machine import I2C
import time

MAX30100_ADDRESS = 0x57

REG_INTR_STATUS = 0x00
REG_INTR_ENABLE = 0x01
REG_FIFO_WR_PTR = 0x02
REG_OVF_COUNTER = 0x03
REG_FIFO_RD_PTR = 0x04
REG_FIFO_DATA = 0x05
REG_MODE_CONFIG = 0x06
REG_SPO2_CONFIG = 0x07
REG_LED_CONFIG = 0x09

class MAX30100:
    def init(self, i2c):
        self.i2c = i2c
        self.addr = MAX30100_ADDRESS


        self.i2c.writeto_mem(self.addr, REG_MODE_CONFIG, b'\x40')
        time.sleep(0.1)


        self.i2c.writeto_mem(self.addr, REG_MODE_CONFIG, b'\x03')


        self.i2c.writeto_mem(self.addr, REG_LED_CONFIG, b'\xFF')

        self.i2c.writeto_mem(self.addr, REG_SPO2_CONFIG, b'\x27')

    def read_raw(self):
        data = self.i2c.readfrom_mem(self.addr, REG_FIFO_DATA, 4)
        ir = (data[0] << 8) | data[1]
        red = (data[2] << 8) | data[3]
        return ir, red