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
ENV MIN_LINE=6
ENV MIN_TOKEN=50
ENV N_GRAM=5
ENV FILTRATION_THRESHOLD=10
ENV VERIFICATION_THRESHOLD=70

CMD java -jar ./build/libs/NIL-all.jar \
    -s /data/dataset \
    -q "/data/dataset/${QUERY_FILE}" \
    -o "results/output.txt" \
    -l $LANGUAGE \
    -mil ${MIN_LINE} \
    -mit ${MIN_TOKEN} \
    -n ${N_GRAM} \
    -f ${FILTRATION_THRESHOLD} \
    -v ${VERIFICATION_THRESHOLD} \
    -p $PARALLELISM
