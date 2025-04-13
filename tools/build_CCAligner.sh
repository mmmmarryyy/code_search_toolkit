#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../CCAligner || { echo "ERROR: каталог CCAligner не найден"; exit 1; }

docker build --platform=amd64 -t ccaligner-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа ccaligner-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: CCAligner image успешно собран (ccaligner-detector-$WORKER_ID)"
