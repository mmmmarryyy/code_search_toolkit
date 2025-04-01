#!/bin/bash

if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <dataset_path> <result_folder> <language>"
    exit 1
fi

DATASET_PATH=$(realpath "$1")
RESULT_FOLDER=$(realpath "$2")
LANGUAGE="$3"

OUTPUT_DIR="$RESULT_FOLDER/CCSTokener"
mkdir -p "$OUTPUT_DIR"

docker run -d -it --quiet \
  --platform darwin/amd64 \
  -e LANGUAGE="$LANGUAGE" \
  -v "$DATASET_PATH:/data/input:ro" \
  --name ccstokener-runner-container \
  ccstokener-runner >/dev/null

docker wait ccstokener-runner-container  >/dev/null

docker cp ccstokener-runner-container:/app/CCStokener/ccstokener/results/. "$OUTPUT_DIR"  >/dev/null

docker rm -f ccstokener-runner-container >/dev/null

echo "Results saved to: $OUTPUT_DIR"
