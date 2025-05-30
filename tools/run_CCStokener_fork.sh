#!/bin/bash

if [ "$#" -lt 5 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <query_file> <worker_id> [flags]"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
QUERY_FILE="$4"
WORKER_ID="$5"
shift 5

BETA="${BETA}"
THETA="${THETA}"
ETA="${ETA}"

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    beta)
      BETA="$2"; shift 2;;
    theta)
      THETA="$2"; shift 2;;
    eta)
      ETA="$2"; shift 2;;
    *) shift;;
  esac
done

IMAGE_NAME="ccstokener-fork-detector-$WORKER_ID"
CONTAINER_NAME="ccstokener-fork-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/CCStokener-fork"
mkdir -p "$OUTPUT_DIR"

# Проверяем существование файла запроса
if [ ! -f "$DATASET_PATH/$QUERY_FILE" ]; then
    echo "Error: Query file $QUERY_FILE not found in dataset directory!"
    exit 2
fi

echo "before docker run"

docker run -it \
  -v "$DATASET_PATH:/data/dataset:ro" \
  -e QUERY_FILE="$QUERY_FILE" \
  -e BETA="$BETA" \
  -e THETA="$THETA" \
  -e ETA="$ETA" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/CCStokener-fork/results/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

docker rm -f "$CONTAINER_NAME"

echo "Results saved to: $OUTPUT_DIR"
