#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../CCStokener-fork || { echo "ERROR: каталог CCStokener-fork не найден"; exit 1; }

docker build -t ccstokener-fork-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа ccstokener-fork-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: CCStokener-fork image успешно собран (ccstokener-fork-detector-$WORKER_ID)"
