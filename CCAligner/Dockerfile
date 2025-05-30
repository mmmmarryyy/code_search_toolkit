FROM --platform=linux/amd64 ubuntu:20.04 AS build_amd64

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y flex git python3-pip libboost-all-dev

RUN git clone https://github.com/PCWcn/CCAligner.git

WORKDIR /app/CCAligner

RUN chmod +x ./extract ./parser ./tokenize ./detect ./co1

RUN mkdir -p /app/dataset /app/results

COPY my_runner .

ENV LANGUAGE=java
ENV DATASET_PATH=/app/dataset
ENV WINDOW_SIZE=6
ENV EDIT_DISTANCE=1
ENV SIMILARITY_THRESHOLD=0.6

CMD bash ./my_runner