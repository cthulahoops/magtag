import time
import ssl
import json

import socketpool
import board
from adafruit_seesaw.seesaw import Seesaw
import wifi
import adafruit_minimqtt.adafruit_minimqtt as MQTT

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


def main():
    soil_sensor = Seesaw(board.STEMMA_I2C(), addr=0x36)

    wifi.radio.connect(secrets["ssid"], secrets["password"])

    mqtt_client = MQTT.MQTT(
        broker=secrets["mqtt_broker"],
        port=secrets["mqtt_port"],
        username=secrets["mqtt_username"],
        password=secrets["mqtt_password"],
        socket_pool=socketpool.SocketPool(wifi.radio),
        ssl_context=ssl.create_default_context(),
    )

    mqtt_client.connect()

    send_discovery(mqtt_client)

    while True:
        data = {
            "temperature": soil_sensor.get_temp(),
            "moisture": soil_sensor.moisture_read(),
        }
        print(data)
        mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        time.sleep(120)


MQTT_TOPIC = "state/peace/soil-sensor"
DEVICE_ID = format_mac_address(wifi.radio.mac_address)
DEVICE = (
    {
        "name": "STEMMA Soil Sensor",
        "identifiers": [DEVICE_ID],
        "manufacturer": "Adafruit",
        "connections": [["mac", DEVICE_ID], ["ipv4", str(wifi.radio.ipv4_address)]],
    },
)


def send_discovery(mqtt_client):
    mqtt_client.publish(
        "homeassistant/sensor/peace-soil-sensor-moisture/config",
        json.dumps(
            {
                "name": "Peace Lily Moisture",
                "state_topic": MQTT_TOPIC,
                "device": DEVICE,
                "unit_of_measurement": "unknown",
                "value_template": "{{ value_json.moisture }}",
                "unique_id": DEVICE_ID + "-moisture",
            }
        ),
    )

    mqtt_client.publish(
        "homeassistant/sensor/peace-soil-sensor-temperature/config",
        json.dumps(
            {
                "name": "Peace Lily Temperature",
                "state_topic": MQTT_TOPIC,
                "device": DEVICE,
                "unit_of_measurement": "°C",
                "value_template": "{{ value_json.temperature }}",
                "unique_id": DEVICE_ID + ".temperature",
            }
        ),
    )


def format_mac_address(address_binary):
    return ":".join("{:02X}".format(x) for x in address_binary)


if __name__ == "__main__":
    main()
