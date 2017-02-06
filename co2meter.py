import serial
import time


class CO2Meter(serial.Serial):
    TAKE_ONE_CMD = "\xFE\x44\x00\x08\x02\x9F\x25"
    METER_MODEL = "K-30"

    def __init__(self, *args, **kwargs):
        super(CO2Meter, self).__init__(*args, **kwargs)
        self.flushInput()

    def readone(self):
        """
        Returns: `int` measured C02 level in ppm
        """
        self.write(CO2Meter.TAKE_ONE_CMD)
        time.sleep(.01)
        resp = self.read(7)
        try:
            high = ord(resp[3])
            low = ord(resp[4])
            co2 = (high * 256) + low
            return co2
        except IndexError:
            self.close()
            self.open()
            raise Exception("reset co2 meter")

if __name__ == '__main__':
    meter = CO2Meter("/dev/ttyO5", timeout=1)
    while True:
        print("CO2 ppm=[%s]" % meter.readone())
        time.sleep(1)
