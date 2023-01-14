from typing import Any, Dict, List, Union
from fastapi import FastAPI
from pydantic import BaseModel
import json
import asyncio
import logging
from rich.logging import RichHandler
import os
import sys
import signal
from paho.mqtt.client import Client
from model.mqtt_config import MqttConfig
from model.http_config import HttpConfig
from model.ispindel import IspindelReport
from model.nautilis import NautilisReport
import requests
import http.client as http_client

# TODO: Allow passing of topics via env vars.
TOPIC_FORMAT_ISPINDEL_REPORT_BASE = "devices/ispindel/channel/"
TOPIC_FORMAT_ISPINDEL_REPORT= TOPIC_FORMAT_ISPINDEL_REPORT_BASE + "{}/data"
TOPIC_NAUTILIS_REPORT= "devices/nautilis/data"

MAIN_LOOP_INTERVAL_S = 5
MAX_ISPINDEL_CHANNELS = 3

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Get MQTT config from environment variables
MQTT_ENDPOINT = os.getenv("MQTT_ENDPOINT")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", default = "irelay_publisher")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Get HTTP config from environment variables
HTTP_ENDPOINT = os.getenv("HTTP_ENDPOINT")
HTTP_PATH_ISPINDEL_CHANNEL_1 = os.getenv("HTTP_PATH_ISPINDEL_CHANNEL_1")
HTTP_PATH_ISPINDEL_CHANNEL_2 = os.getenv("HTTP_PATH_ISPINDEL_CHANNEL_2")
HTTP_PATH_NAUTILIS = os.getenv("HTTP_PATH_NAUTILIS")

class IrelayPublisher:
    
    def _os_signal_handler(self, signum, frame):
        """Handle OS signal"""

        logging.info(f"Received signal from OS ({signum}), shutting down gracefully...")
        self.stop()
        sys.exit()

    def __init__(self, mqtt_config: MqttConfig, http_config: HttpConfig):

        self.mqtt_config = mqtt_config
        self.http_config = http_config

        # Register a function to be invoked when we receive SIGTERM or SIGHUP.
        signal.signal(signal.SIGTERM, self._os_signal_handler)
        signal.signal(signal.SIGHUP, self._os_signal_handler)
        signal.signal(signal.SIGINT, self._os_signal_handler)

        # Connect to MQTT
        self.mqtt_client = Client(self.mqtt_config.client_id)
        self.mqtt_client.on_connect = self.on_mqtt_connected
        self.mqtt_client.on_message = self.on_message_received
        
        logging.debug(f"Setting MQTT username / password: {self.mqtt_config.username} / {self.mqtt_config.password}")
        self.mqtt_client.username_pw_set(self.mqtt_config.username, self.mqtt_config.password)
        
        logging.debug(f"About to connect to MQTT")
        self.mqtt_client.connect_async(host = self.mqtt_config.endpoint, port = self.mqtt_config.port)
        self.mqtt_client.loop_start()

        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self.main())
        self._loop.run_forever()
    
    def stop(self):
        """Stop application"""
        print("Stopping...")
        # Stop event loop
        self._loop.stop()

    async def main(self):
        try:
            while True:
                await asyncio.sleep(MAIN_LOOP_INTERVAL_S)
        except (KeyboardInterrupt, SystemExit):
            # Keyboard interrupt (SIGINT) or exception triggered by sys.exit()
            self.stop()

    def on_mqtt_connected(self, client, userdata, flags, rc):
        logging.debug("Connected to MQTT")
        self.subscribe_to_mqtt_topics()


    def subscribe_to_mqtt_topics(self):
        for channel in range(1, MAX_ISPINDEL_CHANNELS + 1):
            self.mqtt_client.subscribe(topic = TOPIC_FORMAT_ISPINDEL_REPORT.format(channel), qos = 1)
        self.mqtt_client.subscribe(topic = TOPIC_NAUTILIS_REPORT, qos = 1)
        
    
    def on_message_received(self, client, userdata, message):
        print(f"Message received on topic: {message.topic}")
        if message.topic.startswith(TOPIC_FORMAT_ISPINDEL_REPORT_BASE):
            channel = int(message.topic[len(TOPIC_FORMAT_ISPINDEL_REPORT_BASE)])
            logging.debug(f"Got channel {channel} from topic")
            report = IspindelReport.parse_raw(str(message.payload, encoding = "utf-8"))
            self.process_ispindel_report(channel, report)
        elif message.topic == TOPIC_NAUTILIS_REPORT:
            report = NautilisReport.parse_raw(str(message.payload, encoding = "utf-8"))
            self.process_nautilis_report(report)

    
    def process_ispindel_report(self, channel: int, report: IspindelReport):
        logging.debug(f"Processing iSpindel report for channel {channel}: {report}")
        if channel > MAX_ISPINDEL_CHANNELS:
            logging.warn(f"Channel {channel} is not supported, maximum number of iSpindel channels is {MAX_ISPINDEL_CHANNELS}")
            return
        ispindel_url = self.http_config.get_ispindel_url(channel)
        logging.debug(f"iSpindel URL for channel {channel} is {ispindel_url}")
        if ispindel_url:
            logging.debug(f"Will publish to {ispindel_url}")
            response = requests.post(url = ispindel_url, data = json.dumps(report.dict()), headers={"Content-Type":"application/json"})
            logging.debug(f"Response code from server: {response.status_code}")
        else:
            logging.error(f"Could not get URL for iSpindel with channel {channel}")
    

    def process_nautilis_report(self, report: NautilisReport):
        logging.debug("Processing Nautilis report")
        nautilis_url = self.http_config.get_nautilis_url()
        if nautilis_url:
            logging.debug(f"Will publish to {nautilis_url}")
            response = requests.post(url = nautilis_url, data = json.dumps(report.dict()), headers={"Content-Type":"application/json"})
            logging.debug(f"Response code from server: {response.status_code}")
        else:
            logging.error(f"Could not get URL for Nautilis")


"""Entrypoint"""
if __name__ == "__main__":
    # Housekeeping
    logging.basicConfig(
        level="DEBUG" if DEBUG else "INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(omit_repeated_times=False)],
    )
    http_client.HTTPConnection.debuglevel = 0
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.propagate = True

    mqtt_config = MqttConfig(MQTT_ENDPOINT, MQTT_PORT, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)

    ispindel_http_paths = {
        "1": HTTP_PATH_ISPINDEL_CHANNEL_1,
        "2": HTTP_PATH_ISPINDEL_CHANNEL_2
    }
    http_config = HttpConfig(HTTP_ENDPOINT, ispindel_http_paths, HTTP_PATH_NAUTILIS)

    linakMqtt = IrelayPublisher(mqtt_config, http_config)