FROM ubuntu:20.04

RUN apt-get update 
RUN apt-get install -y git python3-pip

WORKDIR /app

RUN echo "downloading CCStokener-fork (adaptation of CCStokener)"
RUN git clone https://github.com/mmmmarryyy/CCStokener-fork.git

WORKDIR /app/CCStokener-fork

RUN python3 -m pip install -r requirements.txt

ENV QUERY_FILE="snippet.java"

CMD bash ./ccstokener_runner.sh /data/dataset 0.6 0.4 0.55 --query_file "/data/dataset/${QUERY_FILE}" ./results

