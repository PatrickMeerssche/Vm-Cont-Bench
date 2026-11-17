#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== [1/2] Construindo imagem Docker (so-benchmark) ==="
docker build -t so-benchmark -f docker/Dockerfile .

mkdir -p results/docker

echo "=== [2/2] Executando benchmark no container Docker ==="
docker run --rm \
    -v "$PROJECT_ROOT/results/docker:/app/results/docker" \
    so-benchmark "$@"

echo "=== Concluido! Resultados salvos em: results/docker/ ==="
