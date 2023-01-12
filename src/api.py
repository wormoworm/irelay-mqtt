from typing import Any, Dict, List, Union
from fastapi import FastAPI
from pydantic import BaseModel
import json
import logging
from rich.logging import RichHandler
import os
from paho.mqtt.client import Client

# TODO: Allow passing of topics via env vars.
TOPIC_FORMAT_ISPINDEL_REPORT= "devices/ispindel/channel/{}/data"
TOPIC_NAUTILIS_REPORT= "devices/nautilis/data"

class IspindelReport(BaseModel):
    ID: int
    name: str
    RSSI: int
    battery: float
    interval: int
    angle: float
    gravity: float
    temperature: float
    temp_units: str

    def get_channel_number(self) -> int:
        if self.name[0] == '1':
            return 1
        elif self.name[0] == '2':
            return 2
        else:
            return None


class NautilisReport(BaseModel):
    temperature: float
    unit: str


class MqttConfig:
    """Contains config data used to connect to MQTT."""

    def __init__(self, endpoint: str, port: int, client_id: str, username: str, password: str) -> None:
        self.endpoint = endpoint
        self.port = port
        self.client_id = client_id
        self.username = username
        self.password = password


DEBUG = os.getenv("DEBUG", "True").lower() == "true"
MQTT_ENDPOINT = os.getenv("MQTT_ENDPOINT")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", default = "irelay_mqtt")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

app = FastAPI()
logging.basicConfig(
    level="DEBUG" if DEBUG else "INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(omit_repeated_times=False)],
)
mqtt_config = MqttConfig(MQTT_ENDPOINT, MQTT_PORT, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)
mqtt_client = Client(mqtt_config.client_id)
mqtt_client.username_pw_set(mqtt_config.username, mqtt_config.password)


def connect_to_mqtt() -> bool:
    return mqtt_client.connect(host = mqtt_config.endpoint, port = mqtt_config.port) == 0


def disconnect_from_mqtt() -> bool:
    return mqtt_client.disconnect() == 0

@app.post("/api/ispindel")
def data_ispindel(report: IspindelReport):
    ispindel_channel_number = report.get_channel_number()
    if ispindel_channel_number:
        logging.debug(f"iSpindel channel is {ispindel_channel_number}")
    else:
        logging.debug(f"Could not determine iSpindel channel, will assume channel 1.")
        ispindel_channel_number = 1
    logging.debug(f"iSpindel report: {json.dumps(report.dict(), indent=4)}")
    if connect_to_mqtt():
        mqtt_client.publish(topic = TOPIC_FORMAT_ISPINDEL_REPORT.format(ispindel_channel_number), payload = json.dumps(report.dict()), qos = 1)
        disconnect_from_mqtt()
    # TODO Return error code if MQTT connection failed.
    return '{"message": "ok"}'


@app.post("/api/nautilis")
def nautilis(report: NautilisReport):
    logging.debug(f"Nautilis report: {json.dumps(report.dict(), indent=4)}")
    if connect_to_mqtt():
        mqtt_client.publish(topic = TOPIC_NAUTILIS_REPORT, payload = json.dumps(report.dict()), qos = 1)
        disconnect_from_mqtt()
    # TODO Return error code if MQTT connection failed.
    return '{"message": "ok"}'