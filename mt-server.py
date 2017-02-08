from flask import Flask, abort

import logging
from logging.handlers import RotatingFileHandler
import json
import time
import threading
import signal

from opc import OPCClient
from co2meter import CO2Meter
from openscale import OpenScale
from Adafruit_BME280 import BME280


app = Flask(__name__)


def initobj(obj, *args, **kwargs):
    res = None
    try:
        res = obj(*args, **kwargs)
    except Exception as e:
        app.logger.error("failed to initalize %s", obj.__name__, exc_info=e)
    return res


@app.route("/co2")
def co2():
    if not co2meter:
        app.logger.error("co2meter not found")
        abort(503) 
    res = co2meter.readone()
    return json.dumps({"CO2": res})


@app.route("/temperature")
def temperature():
    if not bme280:
        app.logger.error("bme280 not found")
        abort(503)
    res = bme280.read_temperature()
    return json.dumps({"temperature_bme": res})


@app.route("/pressure")
def pressure():
    if not bme280:
        app.logger.error("bme280 not found")
        abort(503)
    res = bme280.read_pressure()
    return json.dumps({"presssure": res})


@app.route("/humidity")
def humidity():
    if not bme280:
        app.logger.error("bme280 not found")
        abort(503)
    res = bme280.read_humidity()
    return json.dumps({"humidity": res})


@app.route("/weight")
def weight():
    if not openscale:
        app.logger.error("openscale not found")
        abort(503)
    res = openscale.readone()
    res = res.split(",")
    try:
        res = json.dumps({"weight":float(res[0]), "temperature_os": float(res[2])})
        return res
    except Exception as e:
        app.logger.error("openscale sensor result unexpected [%s]", res, exc_info=e)
        abort(503)


@app.route("/weight/tare")
def tare():
    if not openscale:
        app.logger.error("openscale not found")
        abort(503)
    openscale.tare()
    return "ok"


@app.route("/sensors")
def sensors():
    res = {}
    for f in [temperature, pressure, humidity, weight, co2]:
        try:
            res.update(json.loads(f()))
        except Exception as e:
            app.logger.error("failed to execute %s", f.__name__, exc_info=e)
    return json.dumps(res)


def dimlights(a, z):
    duration = 60.0 * 1 # in seconds
    maxbyi = (255, 61, 255)
    stepbyi = (1, 0.24, 1.2)
    def f(i, a, z):
        if a[i] < z[i]:
            a[i] = min(maxbyi[i], a[i] + stepbyi[i])
        elif a[i] > z[i]:
            a[i] = max(0, a[i] - stepbyi[i])
        return a[i]
    while a[0] != z[0] or a[1] != z[1] or a[2] != z[2]:
        for i in range(3):
            a[i] = f(i, a, z)
        app.logger.info(a)
        opc.put_pixels([a for x in range(480)], channel=0)
        time.sleep(duration/255)


@app.route("/lights/off")
def lightsoff():
    if not opc:
        app.logger.error("openpixel client not found")
        abort(503)
    thread = threading.Thread(target=dimlights, args=([255, 61, 255], [0, 0, 0]))
    thread.start()
    return "ok"


@app.route("/lights/on")
def lightson():
    if not opc:
        app.logger.error("openpixel client not found")
        abort(503)
    thread = threading.Thread(target=dimlights, args=([0, 0, 0], [255, 61, 255]))
    thread.start()
    return "ok"


def close():
    app.logger.info("stopping server")
    co2meter.close()
    openscale.close()
    app.logger.info("stopped server")


if __name__ == '__main__':
    app.logger_name = "mt-server"
    lfh = RotatingFileHandler("/tmp/mt-server.log", maxBytes=10E5, backupCount=3)
    formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
    lfh.setFormatter(formatter)
    app.logger.addHandler(lfh)
    app.logger.setLevel(logging.INFO)
    accesslog = logging.getLogger('werkzeug')
    accesslog.addHandler(lfh)

    app.logger.info("starting mt-server")
    bme280 = initobj(BME280)
    opc = initobj(OPCClient, "localhost:7890")
    co2meter = initobj(CO2Meter, "/dev/ttyO5", timeout=0.1)
    openscale = initobj(OpenScale, "/dev/ttyUSB0", timeout=1)
    app.logger.info("started mt-server")

    signal.signal(signal.SIGTERM, close)
    try:
        app.run()
    except Exception as e:
        app.logger.error("unknown exception", e)
    finally:
        close()

