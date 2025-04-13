#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../CCStokener || { echo "ERROR: каталог CCStokener не найден"; exit 1; }

docker build --platform=amd64 -t ccstokener-runner-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа ccstokener-runner-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: CCStokener image успешно собран (ccstokener-runner-$WORKER_ID)"
