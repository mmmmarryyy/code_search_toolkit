FROM --platform=linux/amd64 ubuntu:20.04 AS build_amd64

WORKDIR /app

RUN apt-get update && apt-get install -y git python-is-python3

# Installing dependencies
RUN apt-get install -y python3-pip
RUN python -m pip install pandarallel==1.6.5

RUN git clone https://github.com/CCStokener/CCStokener.git

WORKDIR /app/CCStokener/ccstokener

RUN chmod +x ./clone-detect/clonedetector
RUN chmod +x ./clone-detect/cloneverify

# TODO: change this environment parameters
ENV DATASET_PATH="./bcb_reduced/" 
ENV LANGUAGE="java"

CMD python runner.py -i $DATASET_PATH -m bcb -l $LANGUAGE
