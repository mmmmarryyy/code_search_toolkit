FROM --platform=linux/amd64 ubuntu:20.04 AS build_amd64

RUN uname -a

WORKDIR /app

RUN apt-get update && apt-get install -y wget git python-is-python3

# Installing dependencies
RUN apt-get install -y python3-pip gettext-base

# Install FreeTXL
RUN wget https://github.com/CordyJ/OpenTxl/releases/download/v11.3.5/opentxl-11.3.5-linux-x64.tar.gz
RUN tar -xf opentxl-11.3.5-linux-x64.tar.gz
WORKDIR /app/opentxl-11.3.5-linux-x64

RUN ./InstallTxl.sh

WORKDIR /app

# Install NiCad
RUN wget https://github.com/CordyJ/Open-NiCad/releases/download/v7.0.1/nicad-7.0.1-linux-x86_64.tar.gz
RUN tar -xf nicad-7.0.1-linux-x86_64.tar.gz
WORKDIR /app/nicad-7.0.1-linux-x86_64

COPY myconfig.cfg.template /app/nicad-7.0.1-linux-x86_64/lib/nicad/config/


ENV DATASET_PATH="/data/dataset"
ENV LANGUAGE="java"
ENV THRESHOLD=0.3
ENV MIN_SIZE=10
ENV MAX_SIZE=10000

WORKDIR /app/nicad-7.0.1-linux-x86_64
ENTRYPOINT ["/bin/bash", "-c", "envsubst < lib/nicad/config/myconfig.cfg.template > lib/nicad/config/myconfig.cfg && ./bin/nicad functions $LANGUAGE $DATASET_PATH myconfig"]
