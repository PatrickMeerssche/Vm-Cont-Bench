#!/usr/bin/env bash
# ====================================================================
# Interface Unificada de Execucao dos Benchmarks de Sistemas Operacionais
# Ambientes suportados: Bare-Metal, Docker e VM (VirtualBox)
# ====================================================================
set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

RUNS=${RUNS:-3}
CPU_SIZES=${CPU_SIZES:-"1000 2000 3000 4000"}
IO_SIZES=${IO_SIZES:-"64 128 256 512"}

case "$1" in
    baremetal)
        echo ">>> Executando Benchmark em Bare-Metal..."
        make all
        python3 scripts/run_benchmark.py --env baremetal --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        python3 scripts/plot_comparison.py
        python3 scripts/update_readme.py
        ;;
    docker)
        echo ">>> Executando Benchmark em Contêiner Docker..."
        ./docker/run_docker.sh --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        python3 scripts/plot_comparison.py
        python3 scripts/update_readme.py
        ;;
    vm)
        echo ">>> Executando Benchmark em Máquina Virtual..."
        if [ -f "vm/run_vm.sh" ]; then
            ./vm/run_vm.sh --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        else
            python3 scripts/run_benchmark.py --env vm --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        fi
        python3 scripts/plot_comparison.py
        python3 scripts/update_readme.py
        ;;
    compare)
        echo ">>> Gerando relatórios e gráficos comparativos unificados..."
        python3 scripts/plot_comparison.py
        python3 scripts/update_readme.py
        ;;
    all)
        echo ">>> Executando bateria completa: Bare-Metal -> Docker -> VM -> Comparacao -> Atualizacao do README..."
        make all
        python3 scripts/run_benchmark.py --env baremetal --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        ./docker/run_docker.sh --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        if [ -f "vm/run_vm.sh" ]; then
            ./vm/run_vm.sh --runs "$RUNS" --cpu-sizes $CPU_SIZES --io-sizes $IO_SIZES
        fi
        python3 scripts/plot_comparison.py
        python3 scripts/update_readme.py
        echo ">>> Bateria completa concluída e README.md atualizado!"
        ;;
    *)
        echo "Uso: $0 [baremetal | docker | vm | compare | all]"
        echo ""
        echo "Exemplos:"
        echo "  $0 baremetal    # Executa bateria nativa"
        echo "  $0 docker       # Executa bateria em Docker"
        echo "  $0 vm           # Executa bateria em VM"
        echo "  $0 compare      # Compara os resultados gerados em results/"
        echo "  $0 all          # Roda bare-metal, docker e vm, gerando gráficos e atualizando README"
        exit 1
        ;;
esac
