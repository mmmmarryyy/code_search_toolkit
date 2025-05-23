#!/bin/bash
set -e

echo "=== Запуск SourcererCC entrypoint ==="

cd /app/SourcererCC/tokenizers/block-level

echo "--- Устанавливаем zip (если вдруг не установлено) и упаковываем /data/input → projects/dataset.zip ---"

if ! command -v zip &>/dev/null; then
  apt-get update && apt-get install -y zip
fi

rm -f projects/dataset.zip

zip -r projects/dataset.zip /data/dataset/*

echo "projects/dataset.zip создан."

echo "--- Шаг 2: Устанавливаем python3-pip и запускаем tokenizer.py на Python 3 ---"

python3 -m pip install --upgrade pip
python3 -m pip install javalang

python3 tokenizer.py zipblocks

echo "Tokenization completed: blocks_tokens/ → blocks.file"

apt-get remove -y python3
apt-get remove -y --auto-remove python3
apt-get purge -y python3
apt-get purge -y --auto-remove python3

cat blocks_tokens/* > blocks.file

echo "Сформирован единый blocks.file (строк: $(wc -l < blocks.file))."

cd /app/SourcererCC/clone-detector

echo "--- Устанавливаем ant (если вдруг не установлено) и готовим input/dataset ---"

if ! command -v ant &>/dev/null; then
  apt-get update && apt-get install -y ant
fi

mkdir -p input/dataset
cp /app/SourcererCC/tokenizers/block-level/blocks.file input/dataset/

echo "Файл blocks.file скопирован → input/dataset/blocks.file"

echo "--- Шаг 4: Запуск controller.py (на Python 2) ---"

python controller.py

echo "Clone-detector завершил работу (NODE_*/output8.0/query_*)."

mkdir -p output
cat NODE_*/output8.0/query_* > output/results.pairs

echo "Результаты собраны в output/results.pairs (строк: $(wc -l < output/results.pairs))."

echo "=== Entrypoint завершён, контейнер может завершить работу ==="
exit 0
