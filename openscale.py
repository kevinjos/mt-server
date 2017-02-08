import serial
import time


class OpenScale(serial.Serial):
    MENUCHR = "\x78"
    TARECHR = "\x31"
    READCHR = "\x30"

    def __init__(self, *args, **kwargs):
        super(OpenScale, self).__init__(*args, **kwargs)
        self.write(self.READCHR)
        time.sleep(0.1)
        self.readall()
        self.flush()

    def tare(self):
        self.write(self.MENUCHR)
        time.sleep(0.1)
        self.write(self.TARECHR)
        time.sleep(0.1)
        self.write(self.MENUCHR)
        time.sleep(0.1)
        self.readall()
        self.flush

    def readone(self):
        self.write(self.READCHR)
        time.sleep(0.1)
        r = self.readall()
	return r
