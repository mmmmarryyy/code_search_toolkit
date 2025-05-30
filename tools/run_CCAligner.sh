#!/bin/bash

if [ "$#" -lt 4 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <worker_id> [flags]"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
WORKER_ID="$4"
shift 4

WINDOW_SIZE="${WINDOW_SIZE}"
EDIT_DISTANCE="${EDIT_DISTANCE}"
SIMILARITY_THRESHOLD="${SIMILARITY_THRESHOLD}"

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        window_size)
            WINDOW_SIZE="$2"; shift 2;;
        edit_distance)
            EDIT_DISTANCE="$2"; shift 2;;
        similarity_threshold)
            SIMILARITY_THRESHOLD="$2"; shift 2;;
        *) shift;;
    esac
done

echo "window_size = ${WINDOW_SIZE}"
echo "${EDIT_DISTANCE}"
echo "${SIMILARITY_THRESHOLD}"

IMAGE_NAME="ccaligner-detector-$WORKER_ID"
CONTAINER_NAME="ccaligner-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/CCAligner"
mkdir -p "$OUTPUT_DIR"

docker run -it \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -e WINDOW_SIZE="$WINDOW_SIZE" \
  -e EDIT_DISTANCE="$EDIT_DISTANCE" \
  -e SIMILARITY_THRESHOLD="$SIMILARITY_THRESHOLD" \
  -v "$DATASET_PATH:/app/dataset:ro" \
  -v "$OUTPUT_DIR:/app/results" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME" >/dev/null
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/CCAligner/output/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
