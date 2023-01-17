#!/bin/bash

export MQTT_ENDPOINT=10.0.1.2
export MQTT_PORT=8884
export MQTT_CLIENT_ID=irelay_publisher_2
export DEBUG=True

export HTTP_ENDPOINT=bleh
export HTTP_PATH_ISPINDEL_CHANNEL_1=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_2=ADD
export HTTP_PATH_NAUTILIS=ADD
export HTTP_DESTINATION_SERVICE=grainfather
export GRAVITY_OFFSET_ISPINDEL_CHANNEL_1=-0.123

poetry run python -u ../src/publisher.py