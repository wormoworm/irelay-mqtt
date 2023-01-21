#!/bin/bash

export MQTT_ENDPOINT=10.0.1.2
export MQTT_PORT=8884
export MQTT_CLIENT_ID=irelay_api
export TOPIC_FORMAT_ISPINDEL_REPORT=test/devices/ispindel/channel/{}/data
export TOPIC_NAUTILIS_REPORT=test/devices/nautilis/data
export DEBUG=True

cd ../src
poetry run uvicorn api:app --proxy-headers --reload