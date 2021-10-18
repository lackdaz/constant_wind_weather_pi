#!/bin/bash

docker run -d --name weatherpi \
    --device=/dev/ttyAMA1 \
    --restart=on-failure:20 \
    --privileged \
    -e PYTHONUNBUFFERED=1 \
    weatherpi \
    60
