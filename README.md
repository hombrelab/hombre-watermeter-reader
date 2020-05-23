# hombre-watermeter-reader
![Docker Pulls](https://img.shields.io/docker/pulls/hombrelab/hombre-watermeter-reader) ![Docker Image Version (latest by date)](https://img.shields.io/docker/v/hombrelab/hombre-watermeter-reader) ![GitHub commit activity](https://img.shields.io/github/last-commit/hombrelab/hombre-watermeter-reader)  

The [hombre-watermeter-reader](https://hub.docker.com/repository/docker/hombrelab/hombre-watermeter-reader) image is based on the [hombre-gpio](https://hub.docker.com/repository/docker/hombrelab/hombre-gpio) image and the watermeter-reader.py script.  
It is a Docker image for and by [@Hombrelab](me@hombrelab.com) to read the watermeter and publish it to mqtt.

More information about the hardware can be found [here](https://www.rutg3r.com/watermeter-reading-with-inductive-proximity-sensor/).

Will run on *arm* and *arm64* only.

Deployment examples:

Command line
```shell script
docker run \
    --name watermeter-reader \
    --detach \
    --restart unless-stopped \
    --volume /home/data/watermeter-reader/logs:/app/log \
    --volume /sys:/sys \
    --device /dev/gpiomem \
    --env CONSUMED=0 \
    --env BROKER_URL=broker.url \
    --env BROKER_PORT=1883 \
    --env TOPIC=home-assistant/watermeter-reader \
    --env LOG_LEVEL=logging.INFO \
    --cap-add SYS_RAWIO \
    hombrelab/hombre-watermeter-reader
```
Docker Compose
```yaml
    watermeter-reader:
        container_name: watermeter-reader
        restart: unless-stopped
        image: hombrelab/hombre-watermeter-reader
        volumes:
            - /home/data/watermeter-reader/logs:/app/log
            - /sys:/sys
            - /etc/localtime:/etc/localtime:ro
        devices:
            - /dev/gpiomem
        environment:
            - CONSUMED=0
            - BROKER_URL=broker.url
            - BROKER_PORT=1883
            - TOPIC=home-assistant/watermeter-reader
            - LOG_LEVEL=logging.INFO
        cap_add:
            - SYS_RAWIO
```