#!/bin/bash

if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <worker_id> [flags]"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
WORKER_ID="$4"
shift 4

THRESHOLD="${THRESHOLD}"
MIN_SIZE="${MIN_SIZE}"
MAX_SIZE="${MAX_SIZE}"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    threshold)
      THRESHOLD="$2"; shift 2;;
    min_size)
      MIN_SIZE="$2"; shift 2;;
    max_size)
      MAX_SIZE="$2"; shift 2;;
    *) shift;;
  esac
done

IMAGE_NAME="nicad-detector-$WORKER_ID"
CONTAINER_NAME="nicad-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/NiCad"
mkdir -p "$OUTPUT_DIR"

docker run -d -it --quiet \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -e THRESHOLD="$THRESHOLD" \
  -e MIN_SIZE="$MIN_SIZE" \
  -e MAX_SIZE="$MAX_SIZE" \
  -v "$DATASET_PATH:/data/dataset:ro" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"  >/dev/null
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/nicad-7.0.1-linux-x86_64/nicadclones/dataset/dataset_functions-blind-abstract-clones/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
