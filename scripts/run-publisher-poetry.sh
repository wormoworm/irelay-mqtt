#!/bin/bash

export MQTT_ENDPOINT=ADD
export MQTT_PORT=42
export MQTT_CLIENT_ID=irelay_publisher
export DEBUG=True

export HTTP_ENDPOINT=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_1=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_2=ADD
export HTTP_PATH_NAUTILIS=ADD
export HTTP_DESTINATION_SERVICE=grainfather
export GRAVITY_OFFSET_ISPINDEL_CHANNEL_1=-0.123

poetry run python -u ../src/publisher.py