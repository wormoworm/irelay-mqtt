#!/bin/bash

export MQTT_ENDPOINT=10.0.1.2
export MQTT_PORT=8884
export MQTT_CLIENT_ID=irelay_publisher
export DEBUG=True

export HTTP_ENDPOINT=community.grainfather.com
export HTTP_PATH_ISPINDEL_CHANNEL_1=/iot/feat-shit/ispindel
export HTTP_PATH_ISPINDEL_CHANNEL_2=TODO
export HTTP_PATH_NAUTILIS=/iot/rate-lame/custom

poetry run python -u ../src/publisher.py