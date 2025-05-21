#!/bin/bash

if [ "$#" -ne 5 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <query_file> <worker_id>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
QUERY_FILE="$4"
WORKER_ID="$5"

IMAGE_NAME="ccaligner-fork-detector-$WORKER_ID"
CONTAINER_NAME="ccaligner-fork-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/CCAligner-fork"
mkdir -p "$OUTPUT_DIR"

# Проверяем существование файла запроса
if [ ! -f "$DATASET_PATH/$QUERY_FILE" ]; then
    echo "Error: Query file $QUERY_FILE not found in dataset directory!"
    exit 2
fi

echo "before docker run"

docker run -it \
  --platform darwin/amd64 \
  -v "$DATASET_PATH:/data/dataset:ro" \
  -e LANGUAGE="$LANGUAGE" \
  -e QUERY_FILE="$QUERY_FILE" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"
docker cp "$CONTAINER_NAME":/app/CCAligner-fork/results/. "$OUTPUT_DIR"
docker rm -f "$CONTAINER_NAME"

echo "Results saved to: $OUTPUT_DIR"
