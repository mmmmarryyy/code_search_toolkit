FROM --platform=linux/amd64 ubuntu:20.04 AS build_amd64

RUN apt-get update && apt-get install -y git python3-pip

RUN python3 -m pip install setuptools==45.2.0
RUN python3 -m pip install tree-sitter==0.20.1
RUN python3 -m pip install mmh3==5.0.1
RUN python3 -m pip install gdown==5.2.0

WORKDIR /app

RUN git clone https://github.com/mmmmarryyy/CCAligner-fork.git

WORKDIR /app/CCAligner-fork

RUN git clone https://github.com/tree-sitter/tree-sitter-python.git
RUN git clone https://github.com/tree-sitter/tree-sitter-java.git

ENV LANGUAGE=java
ENV QUERY_FILE="snippet.java"

RUN ls

CMD python3 ./src/ccaligner.py -from /data/dataset -l $LANGUAGE --query_file "/data/dataset/${QUERY_FILE}"
