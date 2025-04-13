#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <worker_id>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
WORKER_ID="$4"

IMAGE_NAME="ccaligner-detector-$WORKER_ID"
CONTAINER_NAME="ccaligner-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/CCAligner"
mkdir -p "$OUTPUT_DIR"

docker run -it \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -v "$DATASET_PATH:/app/dataset:ro" \
  -v "$OUTPUT_DIR:/app/results" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME" >/dev/null
docker cp "$CONTAINER_NAME":/app/CCAligner/output/. "$OUTPUT_DIR" >/dev/null
docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
