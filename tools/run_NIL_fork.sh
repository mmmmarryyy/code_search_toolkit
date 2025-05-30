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

IMAGE_NAME="nil-fork-detector-$WORKER_ID"
CONTAINER_NAME="nil-fork-container-$WORKER_ID"

OUTPUT_DIR="$RESULT_FOLDER/NIL-fork"
mkdir -p "$OUTPUT_DIR"

# Проверяем существование файла запроса
if [ ! -f "$DATASET_PATH/$QUERY_FILE" ]; then
    echo "Error: Query file $QUERY_FILE not found in dataset directory!"
    exit 2
fi

MIN_LINE="${MIN_LINE}"
MIN_TOKEN="${MIN_TOKEN}"
N_GRAM="${N_GRAM}"
FILTRATION_THRESHOLD="${FILTRATION_THRESHOLD}"
VERIFICATION_THRESHOLD="${VERIFICATION_THRESHOLD}"

while [[ "$#" -gt 0 ]]; do
    case "$1" in
        min_line)
            MIN_LINE="$2"; shift 2;;
        min_token)
            MIN_TOKEN="$2"; shift 2;;
        n_gram)
            N_GRAM="$2"; shift 2;;
        filtration_threshold)
            FILTRATION_THRESHOLD="$2"; shift 2;;
        verification_threshold)
            VERIFICATION_THRESHOLD="$2"; shift 2;;
        *)
            # Unknown flag, forward as is
            EXTRA_FLAGS+=("$1"); shift;;
    esac
done

docker run -it \
  -v "$DATASET_PATH:/data/dataset:ro" \
  -e LANGUAGE="$LANGUAGE" \
  -e QUERY_FILE="$QUERY_FILE" \
  -e MIN_LINE="$MIN_LINE" \
  -e MIN_TOKEN="$MIN_TOKEN" \
  -e N_GRAM="$N_GRAM" \
  -e FILTRATION_THRESHOLD="$FILTRATION_THRESHOLD" \
  -e VERIFICATION_THRESHOLD="$VERIFICATION_THRESHOLD" \
  --name "$CONTAINER_NAME" \
  "$IMAGE_NAME"

docker wait "$CONTAINER_NAME"
docker logs "$CONTAINER_NAME"

if docker cp "$CONTAINER_NAME":/app/NIL-fork/results/. "$OUTPUT_DIR" 2>/dev/null; then
  echo "Results copied to: $OUTPUT_DIR"
else
  echo "Error: No results directory to copy"
fi

docker rm -f "$CONTAINER_NAME"

echo "Results saved to: $OUTPUT_DIR"
