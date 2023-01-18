from typing import Any, Dict, List, Union
from fastapi import FastAPI
from pydantic import BaseModel
import json
import logging
from rich.logging import RichHandler
import os
from paho.mqtt.client import Client
from model.mqtt_config import MqttConfig
from model.ispindel import IspindelReport, ExtendedIspindelReport
from model.nautilis import NautilisReport
from constants import MAX_ISPINDEL_CHANNELS

# TODO: Allow passing of topics via env vars.
TOPIC_FORMAT_ISPINDEL_REPORT= "devices/ispindel/channel/{}/data"
TOPIC_NAUTILIS_REPORT= "devices/nautilis/data"


DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ROUND_VALUES = os.getenv("ROUND_VALUES", "True").lower() == "true"

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

ispindel_gravity_offsets = dict()
for channel in range(1, MAX_ISPINDEL_CHANNELS + 1):
    offset = os.getenv(f"GRAVITY_OFFSET_ISPINDEL_CHANNEL_{channel}")
    if offset:
        logging.debug(f"Will use offset of {offset} for iSpindel channel {channel}")
        ispindel_gravity_offsets[channel] = float(offset)


def connect_to_mqtt() -> bool:
    return mqtt_client.connect(host = mqtt_config.endpoint, port = mqtt_config.port) == 0


def disconnect_from_mqtt() -> bool:
    return mqtt_client.disconnect() == 0


@app.post("/api/ispindel")
def data_ispindel(report: IspindelReport):
    channel = report.get_channel_number()
    # Adjust the gravity offset if required.
    gravity_offset = ispindel_gravity_offsets.get(channel)
    if gravity_offset:
        logging.debug(f"Will adjust gravity for iSpindel channel {channel} by {gravity_offset}")
        report.gravity += gravity_offset
    
    # The extended report allows us to calculate extra values from the original iSpindel data.
    extended_report = ExtendedIspindelReport(report)
    if ROUND_VALUES:
        logging.debug("Rounding values")
        extended_report.battery = round(extended_report.battery, 3)
        extended_report.angle = round(extended_report.angle, 1)
        extended_report.gravity = round(extended_report.gravity, 3)
        extended_report.temperature = round(extended_report.temperature, 1)
        extended_report.battery_percentage = round(extended_report.battery_percentage, 1)
        
    if channel:
        logging.debug(f"iSpindel channel is {channel}")
    else:
        logging.debug(f"Could not determine iSpindel channel, will assume channel 1.")
        channel = 1
    logging.debug(f"iSpindel report: {json.dumps(extended_report.dict(), indent=4)}")
    if connect_to_mqtt():
        # report_dict = calculate_extra_fields(report_dict)
        mqtt_client.publish(topic = TOPIC_FORMAT_ISPINDEL_REPORT.format(channel), payload = json.dumps(extended_report.dict()), qos = 1)
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


@app.post("/test")
def dummy(request_dict: Union[List,Dict,Any] = None):
    logging.warn(f"/test: {request_dict}")
    return {"a": "b"}


# def calculate_extra_fields(report_dict: dict) -> dict:
#     report_dict["battery_percentage"] = 