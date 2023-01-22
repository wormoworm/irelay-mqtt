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
import time
from paho.mqtt.client import Client
from model.mqtt_config import MqttConfig
from model.http_config import HttpConfig
from model.ispindel import IspindelReport
from model.irelay import IrelayReport, IrelayReportGrainfather, IrelayReportBrewfather, TemperatureUnit
import requests
import http.client as http_client
from model.destination import Destination
from constants import MAX_ISPINDEL_CHANNELS


MAIN_LOOP_INTERVAL_S = 5

DEBUG = os.getenv("DEBUG", "True").lower() == "true"

# Get MQTT config from environment variables
MQTT_ENDPOINT = os.getenv("MQTT_ENDPOINT")
MQTT_PORT = int(os.getenv("MQTT_PORT"))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", default = "irelay_publisher")
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
TOPIC_FORMAT_ISPINDEL_REPORT = os.getenv("TOPIC_FORMAT_ISPINDEL_REPORT")
TOPIC_IRELAY_REPORT= os.getenv("TOPIC_IRELAY_REPORT")

# Get HTTP config from environment variables
HTTP_ENDPOINT = os.getenv("HTTP_ENDPOINT")
HTTP_PATH_ISPINDEL_CHANNEL_1 = os.getenv("HTTP_PATH_ISPINDEL_CHANNEL_1")
HTTP_PATH_ISPINDEL_CHANNEL_2 = os.getenv("HTTP_PATH_ISPINDEL_CHANNEL_2")
HTTP_PATH_IRELAY = os.getenv("HTTP_PATH_IRELAY")
HTTP_MIN_PUBLICATION_INTERVAL = os.getenv("HTTP_MIN_PUBLICATION_INTERVAL", default = 15 * 60)
HTTP_DESTINATION_SERVICE = Destination.from_string(os.getenv("HTTP_DESTINATION_SERVICE"))

class IrelayPublisher:

    publication_timestamps = dict()
    
    def _os_signal_handler(self, signum, frame):
        """Handle OS signal"""

        logging.info(f"Received signal from OS ({signum}), shutting down gracefully...")
        self.stop()
        sys.exit()

    def __init__(self, mqtt_config: MqttConfig, http_config: HttpConfig):

        self.mqtt_config = mqtt_config
        self.http_config = http_config

        if HTTP_DESTINATION_SERVICE:
            logging.debug(f"Using destination service: {HTTP_DESTINATION_SERVICE.name}")

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
        self.mqtt_client.subscribe(topic = TOPIC_IRELAY_REPORT, qos = 1)
        
    
    def on_message_received(self, client, userdata, message):
        print(f"Message received on topic: {message.topic}")
        for channel in range(1, MAX_ISPINDEL_CHANNELS + 1):
            topic = TOPIC_FORMAT_ISPINDEL_REPORT.format(channel)
            if message.topic == topic:
                logging.debug(f"Processing iSpindel report for channel {channel}")
                # Create the report from the message payload.
                report = IspindelReport.parse_raw(str(message.payload, encoding = "utf-8"))

                # Do any per-service post-processing that is required.
                report = self.process_ispindel_report_for_service(report, HTTP_DESTINATION_SERVICE)

                # Publish the report to the web service.
                self.publish_ispindel_report(channel, report)
                return
        if message.topic == TOPIC_IRELAY_REPORT:
            logging.debug("Processing Irelay report")
            report = IrelayReport.parse_raw(str(message.payload, encoding = "utf-8"))
            logging.debug(f"Raw report JSON: {json.dumps(report.dict())}")
            # Transform the report into the model required by the selected service.
            service_report = self.process_irelay_report_for_service(report, HTTP_DESTINATION_SERVICE)
            if service_report:
                self.publish_irelay_report(service_report)
    

    def process_ispindel_report_for_service(self, report: IspindelReport, service: Destination) -> IspindelReport:
        if service:
            if service == Destination.GRAINFATHER:
                report.name = report.name + ",SG"
            elif service == Destination.BREWFATHER:
                report.name = report.name + "[SG]"
        return report


    def process_irelay_report_for_service(self, report: IrelayReport, service: Destination) -> BaseModel:
        if service:
            if service == Destination.GRAINFATHER:
                return IrelayReportGrainfather(report)
            elif service == Destination.BREWFATHER:
                return IrelayReportBrewfather(report)
        return report

    
    def publish_ispindel_report(self, channel: int, report: IspindelReport):
        ispindel_url = self.http_config.get_ispindel_url(channel)
        logging.debug(f"iSpindel URL for channel {channel} is {ispindel_url}")
        
        if ispindel_url:
            if self.should_publish(ispindel_url, int(time.time())):
                logging.debug(f"Will publish to {ispindel_url}")
                response = requests.post(url = ispindel_url, data = json.dumps(report.dict()), headers={"Content-Type":"application/json"})
                logging.debug(f"Response code from server: {response.status_code}")
                self.set_publication_timestamp(ispindel_url, int(time.time()))
            else:
                logging.debug(f"Skipped publication for URL {ispindel_url}.")
        else:
            logging.error(f"Could not get URL for iSpindel with channel {channel}")
    

    def publish_irelay_report(self, report: BaseModel):
        irelay_url = self.http_config.get_irelay_url()
        if irelay_url:
            if self.should_publish(irelay_url, int(time.time())):
                logging.debug(f"Will publish to {irelay_url}")
                response = requests.post(url = irelay_url, data = json.dumps(report.dict()), headers={"Content-Type":"application/json"})
                logging.debug(f"Response code from server: {response.status_code}")
                self.set_publication_timestamp(irelay_url, int(time.time()))
            else:
                logging.debug(f"Skipped publication for URL {irelay_url}.")
        else:
            logging.error(f"Could not get URL for Irelay")
    

    def set_publication_timestamp(self, key: str, timestamp: int):
        self.publication_timestamps[key] = timestamp
        print(self.publication_timestamps)


    def get_publication_timestamp(self, key: str) -> int:
        timestamp = self.publication_timestamps.get(key)
        if timestamp:
            return timestamp
        else:
            return 0
    

    def should_publish(self, key: str, timestamp_to_check: int) -> bool:
        time_since_last_publication_s = timestamp_to_check - self.get_publication_timestamp(key)
        logging.debug(f"Time since last publication: {time_since_last_publication_s}, min interval: {self.http_config.min_publication_interval_s}")
        return time_since_last_publication_s >= self.http_config.min_publication_interval_s


"""Entrypoint"""
if __name__ == "__main__":
    # Housekeeping
    logging.basicConfig(
        level="DEBUG" if DEBUG else "INFO",
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(omit_repeated_times=False)],
    )

    # Exit if destination not supported
    if not HTTP_DESTINATION_SERVICE:
        logging.error("HTTP_DESTINATION_SERVICE must be set, exiting...")
        sys.exit()

    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.propagate = True
    http_client.HTTPConnection.debuglevel = 2

    mqtt_config = MqttConfig(MQTT_ENDPOINT, MQTT_PORT, MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)

    ispindel_http_paths = {
        "1": HTTP_PATH_ISPINDEL_CHANNEL_1,
        "2": HTTP_PATH_ISPINDEL_CHANNEL_2
    }
    http_config = HttpConfig(HTTP_ENDPOINT, ispindel_http_paths, HTTP_PATH_IRELAY, HTTP_MIN_PUBLICATION_INTERVAL)

    linakMqtt = IrelayPublisher(mqtt_config, http_config)