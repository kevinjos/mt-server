import serial


class OpenScale(serial.Serial):
    def __init__(self, *args, **kwargs):
        super(OpenScale, self).__init__(*args, **kwargs)
