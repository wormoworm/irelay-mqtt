#!/bin/bash

export MQTT_ENDPOINT=TODO
export MQTT_PORT=TODO
export MQTT_CLIENT_ID=irelay_publisher
export DEBUG=True

export HTTP_ENDPOINT=TODO
export HTTP_PATH_ISPINDEL_CHANNEL_1=TODO
export HTTP_PATH_ISPINDEL_CHANNEL_2=TODO
export HTTP_PATH_NAUTILIS=TODO

poetry run python -u ../src/publisher.py