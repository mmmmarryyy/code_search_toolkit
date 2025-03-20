FROM --platform=linux/amd64 ubuntu:20.04

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y flex
RUN apt-get install -y git python3-pip
RUN apt-get install -y libboost-all-dev

RUN git clone https://github.com/PCWcn/CCAligner.git

WORKDIR /app/CCAligner

RUN chmod +x ./extract
RUN chmod +x ./parser
RUN chmod +x ./tokenize
RUN chmod +x ./detect
RUN chmod +x ./co1

COPY my_runner .

CMD bash ./my_runner
