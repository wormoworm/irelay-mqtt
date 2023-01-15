#!/bin/bash

export MQTT_ENDPOINT=ADD
export MQTT_PORT=ADD
export MQTT_CLIENT_ID=irelay_publisher
export DEBUG=True

export HTTP_ENDPOINT=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_1=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_2=ADD
export HTTP_PATH_NAUTILIS=ADD

poetry run python -u ../src/publisher.py