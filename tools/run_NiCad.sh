#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <worker_id>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
WORKER_ID="$4"

IMAGE_NAME="nicad-detector-$WORKER_ID"
CONTAINER_NAME="nicad-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/NiCad"
mkdir -p "$OUTPUT_DIR"

docker run -d -it --quiet \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -v "$DATASET_PATH:/data/dataset:ro" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"  >/dev/null

docker cp "$CONTAINER_NAME":/app/nicad-7.0.1-linux-x86_64/nicadclones/dataset/dataset_functions-blind-abstract-clones/. "$OUTPUT_DIR"  >/dev/null

docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
