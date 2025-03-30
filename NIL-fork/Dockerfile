FROM openjdk:21-jdk-slim

RUN apt-get update && apt-get install -y git python3-pip

WORKDIR /app

RUN git clone https://github.com/mmmmarryyy/NIL-fork.git

WORKDIR /app/NIL-fork

# Build NIL
RUN ./gradlew ShadowJar

RUN mkdir results

VOLUME /data/dataset

ENV LANGUAGE=java
ENV PARALLELISM=1
ENV QUERY_FILE="snippet.java"

CMD java -jar ./build/libs/NIL-all.jar \
    -s /data/dataset \
    -q "/data/dataset/${QUERY_FILE}" \
    -o "results/output.txt" \
    -l $LANGUAGE \
    -p $PARALLELISM
