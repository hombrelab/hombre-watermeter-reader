# Dockerfile: hombre-watermeter-reader

FROM hombrelab/hombre-gpio

ARG version

LABEL version="${version}"
LABEL description="Customized Watermeter Reader Docker image"
LABEL maintainer="Hombrelab <me@hombrelab.com>"
LABEL inspiration="getting things done my way"

RUN mkdir -p /app/log

COPY ./app/watermeter-reader.py /app/watermeter-reader.py
COPY ./app/LICENSE /app/LICENSE

CMD python /app/watermeter-reader.py