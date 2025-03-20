#!/bin/bash

# Usage: ./run_ccaligner.sh <dataset_path> <result_folder>
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <dataset_path> <result_folder>"
    exit 1
fi

DATASET_PATH=$1
RESULT_FOLDER=$2

# creatind folder for results
mkdir -p "$RESULT_FOLDER/CCAligner"

cd CCAligner

docker run -it \
 --platform linux/amd64 \
 -v "$DATASET_PATH":/app/dataset \
 -v "$RESULT_FOLDER/CCAligner":/app/CCAligner/output/ \
 --name ccaligner-container \
 ccaligner-detector

docker wait ccaligner-container

docker rm ccaligner-container
