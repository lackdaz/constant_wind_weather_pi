#!/bin/bash

docker run --name weatherpi \
    --device=/dev/ttyAMA1 \
    --restart=unless-stopped \
    --privileged \
    -e PYTHONUNBUFFERED=1 \
    weatherpi \
    10
