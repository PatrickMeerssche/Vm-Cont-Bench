# 🖥️ Configuração e Execução em Máquina Virtual (VM)

Para atender ao requisito do trabalho (*"utilizando uma das de máquinas virtuais (VirtualBox ou VMware)"*), este diretório disponibiliza os scripts e orientações para preparar a VM e rodar a mesma bateria de benchmarks.

---

## 📋 Requisitos da VM
* **Hipervisor:** VirtualBox (ou VMware Workstation/Player)
* **Sistema Operacional Guest:** Ubuntu 22.04 LTS (ou Debian 12 / Alpine)
* **Configuração recomendada:**
  * Processador: **4 vCPUs** (com virtualização de hardware habilitada)
  * Memória RAM: **4096 MB (4 GB)**
  * Disco: **20 GB** (formato VDI / VMDK alocado dinamicamente)
  * Pasta Compartilhada (Shared Folder): mapear a pasta `/home/pgvm/SO/Benchmark` do host para `/mnt/benchmark` ou `~/benchmark` na VM.

---

## 🚀 Como Executar o Benchmark dentro da VM

Dentro da VM (após clonar ou montar a pasta compartilhada):

```bash
# 1. Instalar dependências básicas no sistema convidado
sudo apt-get update && sudo apt-get install -y build-essential python3 python3-matplotlib

# 2. Navegar até a pasta do benchmark
cd /mnt/benchmark

# 3. Compilar
make clean && make

# 4. Executar o benchmark com a tag "vm"
python3 scripts/run_benchmark.py --env vm --runs 3
```

---

## 📥 Saídas Esperadas
O runner gravará automaticamente em:
* `results/vm/results_vm.csv`: dados brutos da VM.
* `results/vm/summary_vm.json`: médias e desvios padrão da VM.
* `results/vm/plot_vm.png`: gráficos de desempenho da VM.

Ao final, no host, basta rodar:
```bash
python3 scripts/plot_comparison.py
```
Isso gerará os gráficos comparativos unificados (**Bare-metal vs Docker vs VM**) e a tabela de sobretaxa percentual (`comparison_summary.json`).
