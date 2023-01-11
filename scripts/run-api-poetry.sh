#!/bin/bash

cd ../src
poetry run uvicorn api:app --host 0.0.0.0 --proxy-headers --reload