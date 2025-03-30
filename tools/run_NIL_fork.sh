#!/bin/bash

if [ "$#" -ne 4 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language> <query_file>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"
QUERY_FILE="$4"

OUTPUT_DIR="$RESULT_FOLDER/NIL-fork"
mkdir -p "$OUTPUT_DIR"

# Проверяем существование файла запроса
if [ ! -f "$DATASET_PATH/$QUERY_FILE" ]; then
    echo "Error: Query file $QUERY_FILE not found in dataset directory!"
    exit 2
fi

docker run -it \
  -v "$DATASET_PATH:/data/dataset:ro" \
  -e LANGUAGE="$LANGUAGE" \
  -e QUERY_FILE="$QUERY_FILE" \
  --name nil-fork-container \
  nil-fork-detector

docker wait nil-fork-container
docker cp nil-fork-container:/app/NIL-fork/results/. "$OUTPUT_DIR"
# docker cp nil-fork-container:/app/NIL-fork "$OUTPUT_DIR"
docker rm -f nil-fork-container

echo "Results saved to: $OUTPUT_DIR"
