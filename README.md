## Weather station client

Authored by: Seth Loh

## Installation

`docker build . -t weatherpi`

Run docker:  
`./run.sh`  
or

```
docker run --name weatherpi \
    --device=/dev/ttyAMA1 \
    --restart=unless-stopped \
    --privileged \
    -e PYTHONUNBUFFERED=1 \
    weatherpi \
    <poll-interval-secs>
```
