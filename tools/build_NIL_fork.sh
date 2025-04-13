#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <worker_id>"
  exit 1
fi

WORKER_ID="$1"

cd ../NIL-fork || { echo "ERROR: каталог NIL-fork не найден"; exit 1; }

docker build -t nil-fork-detector-"$WORKER_ID" .
if [ $? -ne 0 ]; then
  echo "ERROR: сборка образа nil-fork-detector-$WORKER_ID завершилась неудачей"
  exit 1
fi

echo "INFO: NIL-fork image успешно собран (nil-fork-detector-$WORKER_ID)"
