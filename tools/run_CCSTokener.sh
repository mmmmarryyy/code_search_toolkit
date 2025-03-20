#!/bin/bash

# Usage: ./run_ccstokener.sh <dataset_path> <result_folder>
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <dataset_path> <result_folder>"
    exit 1
fi

DATASET_PATH=$1
RESULT_FOLDER=$2

mkdir -p "$RESULT_FOLDER/CCSTokener"

cd CCStokener

docker run -it \
  --platform linux/amd64 \
  -e DATASET_PATH="${DATASET_PATH}" \
  -e LANGUAGE="java" \
  -v "$RESULT_FOLDER/CCSTokener":/app/CCStokener/ccstokener/results \
  --name ccstokener-runner-container \
  ccstokener-runner

docker wait ccstokener-runner-container

docker rm ccstokener-runner-container
