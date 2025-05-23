#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../SourcererCC || { echo "ERROR: каталог SourcererCC не найден"; exit 1; }

docker build --platform=amd64 -t sourcerercc-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа sourcerercc-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: SourcererCC image успешно собран (sourcerercc-detector-$WORKER_ID)"
