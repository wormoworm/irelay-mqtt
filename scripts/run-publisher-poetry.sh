#!/bin/bash

export MQTT_ENDPOINT=10.0.1.2
export MQTT_PORT=8884
export MQTT_CLIENT_ID=irelay_publisher_2
export DEBUG=True

export HTTP_ENDPOINT=bleh
export HTTP_PATH_ISPINDEL_CHANNEL_1=ADD
export HTTP_PATH_ISPINDEL_CHANNEL_2=ADD
export HTTP_PATH_NAUTILIS=ADD
export HTTP_DESTINATION_SERVICE=brewfather
export GRAVITY_OFFSET_ISPINDEL_CHANNEL_1=-0.123
export TOPIC_FORMAT_ISPINDEL_REPORT=test/devices/ispindel/channel/{}/data
export TOPIC_NAUTILIS_REPORT=test/devices/nautilis/data
export IRELAY_NAME=iRelay_1

poetry run python -u ../src/publisher.py