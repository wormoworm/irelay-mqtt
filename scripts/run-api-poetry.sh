#!/bin/bash

cd ../src
poetry run uvicorn api:app --proxy-headers --reload