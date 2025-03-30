#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"

OUTPUT_DIR="$RESULT_FOLDER/CCAligner"
mkdir -p "$OUTPUT_DIR"

docker run -it \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -v "$DATASET_PATH:/app/dataset:ro" \
  -v "$OUTPUT_DIR:/app/results" \
  --name ccaligner-container \
  ccaligner-detector >/dev/null

docker wait ccaligner-container >/dev/null
docker cp ccaligner-container:/app/CCAligner/output/. "$OUTPUT_DIR" >/dev/null
docker rm -f ccaligner-container >/dev/null

echo "Results saved to: $OUTPUT_DIR"
