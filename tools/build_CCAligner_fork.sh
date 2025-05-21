#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../CCAligner-fork || { echo "ERROR: каталог CCAligner-fork не найден"; exit 1; }

docker build --platform=amd64 -t ccaligner-fork-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа ccaligner-fork-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: CCAligner-fork image успешно собран (ccaligner-fork-detector-$WORKER_ID)"
