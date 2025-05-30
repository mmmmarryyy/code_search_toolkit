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

SIMILARITY_THRESHOLD="${SIMILARITY_THRESHOLD}"

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        similarity_threshold)
            SIMILARITY_THRESHOLD="$2"; shift 2;;
        *) shift;;
    esac
done

IMAGE_NAME="ccstokener-runner-$WORKER_ID"
CONTAINER_NAME="ccstokener-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/CCSTokener"
mkdir -p "$OUTPUT_DIR"

docker run -d -it --quiet \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -e SIMILARITY_THRESHOLD="$SIMILARITY_THRESHOLD" \
  -v "$DATASET_PATH:/data/input:ro" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"  >/dev/null
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/CCStokener/ccstokener/results/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

docker rm -f "$CONTAINER_NAME" >/dev/null

echo "Results saved to: $OUTPUT_DIR"
