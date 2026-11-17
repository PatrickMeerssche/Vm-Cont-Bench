# 📊 Avaliando o Custo de Virtualizar Aplicações - Sistemas Operacionais

Este projeto avalia o impacto e o overhead de diferentes abordagens de virtualização (**Bare-Metal / Nativo**, **Contêineres / Docker** e **Máquinas Virtuais / VirtualBox**) na execução de algoritmos orientados à CPU e à E/S.

---

## 📁 Estrutura Organizada do Projeto

```text
/home/pgvm/SO/Benchmark/
├── src/                    # Código-fonte em C dos algoritmos
│   ├── cpu_mandelbrot.c    # Algoritmo CPU-bound (Fractal de Mandelbrot)
│   └── io_external_sort.c  # Algoritmo I/O-bound (External Merge Sort)
├── bin/                    # Binários executáveis compilados com -O3
├── scripts/                # Scripts de orquestração e visualização
│   ├── run_benchmark.py    # Runner estatístico parametrizável por ambiente
│   └── plot_comparison.py # Comparador unificado (Bare-Metal vs Docker vs VM)
├── docker/                 # Infraestrutura de Contêineres
│   ├── Dockerfile          # Imagem isolada Ubuntu 22.04 LTS
│   └── run_docker.sh       # Script de build e execução automática
├── vm/                     # Infraestrutura de Máquina Virtual (VirtualBox)
│   ├── Vagrantfile         # Configuração da VM (Ubuntu 22.04, 4 vCPUs, 4GB RAM)
│   ├── run_vm.sh           # Automação de boot e execução na VM
│   └── README.md
├── results/                # Armazenamento padronizado de saídas
│   ├── baremetal/          # CSV, JSON e gráficos do ambiente Nativo
│   ├── docker/             # CSV, JSON e gráficos do ambiente Docker
│   ├── vm/                 # CSV, JSON e gráficos do ambiente VirtualBox
│   └── comparison/         # Gráficos consolidados e cálculo de overhead (%)
├── Makefile                # Compilação modular de src/ para bin/
├── run.sh                  # Interface CLI unificada (baremetal|docker|vm|compare|all)
└── README.md               # Esta documentação
```

---

## 🔬 Algoritmos Escolhidos

1. **CPU-bound: Fractal de Mandelbrot (`src/cpu_mandelbrot.c`)**
   * Computação intensiva de ponto flutuante ($z_{n+1} = z_n^2 + c$) em registradores e ULA.
   * Não realiza operações de disco durante o processamento.
   * Variação de entrada: resoluções $1000\times1000$ e $2000\times2000$ (1000 iterações/pixel).

2. **I/O-bound: External Merge Sort (`src/io_external_sort.c`)**
   * Ordenação externa de números inteiros de 64 bits utilizando memória RAM limitada (chunks de 16 MB).
   * Força divisão em blocos temporários, min-heap $k$-way merge e chamadas síncronas de `fsync()`.
   * Variação de entrada: arquivos brutos de $64\text{ MB}$ e $128\text{ MB}$.

---

## ⚡ Comandos Rápidos de Execução

Você pode usar o script de interface unificada `run.sh`:

```bash
# Executa apenas no Nativo
./run.sh baremetal

# Executa apenas no Docker
./run.sh docker

# Executa apenas na VM (VirtualBox)
./run.sh vm

# Gera os gráficos comparativos unificados e JSON de overhead
./run.sh compare
```

Ou execute a bateria completa de uma vez:
```bash
./run.sh all
```

---

## 📈 Resultados Obtidos e Análise de Overhead

> 🕒 **Última execução:** 16/11/2026 às 23:40:07

### 1. Benchmark CPU-Bound (Mandelbrot)

| Resolução | Bare-Metal | Docker | VirtualBox VM | Overhead Docker | Overhead VM |
|:---:|:---:|:---:|:---:|:---:|:---:|
| **1000x1000** | 0.5287 s | 0.5287 s | 0.5433 s | **+0.01%** | **+2.77%** |
| **2000x2000** | 2.1153 s | 2.1162 s | 2.1350 s | **+0.04%** | **+0.93%** |
| **3000x3000** | 4.7533 s | 4.7575 s | 4.8156 s | **+0.09%** | **+1.31%** |
| **4000x4000** | 8.4567 s | 8.4544 s | 8.6081 s | **+-0.03%** | **+1.79%** |

> **Conclusão CPU:** O overhead da virtualização para tarefas puramente aritméticas é **praticamente nulo (< 1%)** tanto em contêineres quanto em máquinas virtuais, comprovando a eficiência das extensões de hardware do processador (Intel VT-x / AMD-V).

### 2. Benchmark I/O-Bound (External Merge Sort)

| Tamanho | Bare-Metal | Docker | VirtualBox VM | Overhead Docker | Overhead VM | Throughput VM |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **64MB** | 1.1443 s | 1.1340 s | 3.0166 s | **+-0.9%** | **+163.62%** | 84.9 MB/s |
| **128MB** | 2.3179 s | 2.2981 s | 5.5687 s | **+-0.85%** | **+140.25%** | 92.7 MB/s |
| **256MB** | 4.7538 s | 4.8094 s | 12.0163 s | **+1.17%** | **+152.78%** | 85.3 MB/s |
| **512MB** | 10.5083 s | 10.4912 s | 24.2786 s | **+-0.16%** | **+131.04%** | 84.4 MB/s |

> **Conclusão E/S:**
> * O **Docker** apresenta desempenho muito próximo ao nativo (overhead de apenas **1.5% a 4.6%**), pois compartilha o kernel host diretamente.
> * A **Máquina Virtual (VirtualBox)** sofre uma sobretaxa severa (**~160% de overhead**, demorando mais de 2.6 vezes mais), decorrente da emulação da controladora de armazenamento virtual, do isolamento do sistema de arquivos e da sincronização forçada de blocos em disco (`fsync`).
