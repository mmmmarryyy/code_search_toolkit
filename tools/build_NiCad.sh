#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../NiCad || { echo "ERROR: каталог NiCad не найден"; exit 1; }

docker build --platform=amd64 -t nicad-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа nicad-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: NiCad image успешно собран (nicad-detector-$WORKER_ID)"
