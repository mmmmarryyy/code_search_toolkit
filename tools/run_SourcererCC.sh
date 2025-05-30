#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <worker_id>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
WORKER_ID="$4"

IMAGE_NAME="sourcerercc-detector-$WORKER_ID"
CONTAINER_NAME="sourcerercc-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/SourcererCC"
mkdir -p "$OUTPUT_DIR"

docker run -d -it --quiet \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -v "$DATASET_PATH:/data/dataset:ro" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"  >/dev/null
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/SourcererCC/clone-detector/output/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

if docker cp "$CONTAINER_NAME":/app/SourcererCC/tokenizers/block-level/file_block_stats/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Statistics copied to: $OUTPUT_DIR"
else
  echo "Error: No statistics directory to copy"
fi

docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
