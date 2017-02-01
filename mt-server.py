from flask import Flask

import logging
from logging.handlers import RotatingFileHandler
import json

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
        app.logger.error(e)
    return res


@app.route("/co2")
def co2():
    res = None
    if co2meter:
        res = co2meter.read()
    return json.dumps({"CO2": res})


@app.route("/temperature")
def temp():
    res = None
    if bme280:
        res = bme280.read_temperature()
    return json.dumps({"temperature": res})


@app.route("/pressure")
def pressure():
    res = None
    if bme280:
        res = bme280.read_pressure()
    return json.dumps({"presssure": res})


@app.route("/humidity")
def humidity():
    res = None
    if bme280:
        res = bme280.read_humidity()
    return json.dumps({"humidity": res})


@app.route("/weight")
def weight():
    res = None
    if openscale:
        res = openscale.read()
    return json.dumps({"weight": res})


def config_logger():
    formatter = logging.Formatter(
        "%(asctime)s %(pathname)s:%(lineno)d %(levelname)s - %(message)s")
    handler = RotatingFileHandler('/tmp/mt-server.log', maxBytes=10000, backupCount=5)
    handler.setLevel(logging.INFO)
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)

if __name__ == "__main__":
    config_logger()
    co2meter = initobj(CO2Meter, "/dev/ttyS0")
    openscale = initobj(OpenScale, "/dev/ttyS1")
    bme280 = initobj(BME280)
    opc = initobj(OPCClient, "192.168.1.7:7890", long_connection=False)
    try:
        app.run()
    except Exception as e:
        app.logger.error(e)
    finally:
        co2meter.close() if co2meter else None
        openscale.close() if openscale else None
