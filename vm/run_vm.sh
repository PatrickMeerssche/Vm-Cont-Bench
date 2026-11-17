#!/usr/bin/env bash
# ====================================================================
# Script de automacao para execucao do benchmark na VM (VirtualBox/Vagrant)
# ====================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

echo "=== [1/3] Iniciando/Verificando a Máquina Virtual (VirtualBox via Vagrant) ==="
vagrant up --provider=virtualbox

mkdir -p "$PROJECT_ROOT/results/vm"

echo "=== [2/3] Compilando e executando bateria na VM ==="
vagrant ssh -c "cd /benchmark && make all && python3 scripts/run_benchmark.py --env vm $*"

echo "=== [3/3] Concluído! Resultados salvos em: results/vm/ ==="
