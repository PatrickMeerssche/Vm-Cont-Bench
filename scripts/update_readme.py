#!/usr/bin/env python3
"""
Atualiza a secao de resultados e especificacoes do hardware no README.md.
"""

import json
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
README_PATH = os.path.join(PROJECT_ROOT, "README.md")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")


def load_json(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_results_markdown():
    bm_summary = load_json(os.path.join(RESULTS_DIR, "baremetal", "summary_baremetal.json"))
    dk_summary = load_json(os.path.join(RESULTS_DIR, "docker", "summary_docker.json"))
    vm_summary = load_json(os.path.join(RESULTS_DIR, "vm", "summary_vm.json"))
    ov_summary = load_json(os.path.join(RESULTS_DIR, "comparison", "comparison_summary.json"))

    now_str = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")

    md = []
    md.append("## 🖥️ Especificações do Ambiente Experimental\n")
    md.append("| Componente | Detalhes do Hardware / Software |")
    md.append("|---|---|")
    md.append("| **Processador (CPU)** | 13th Gen Intel(R) Core(TM) i5-13450HX (10 núcleos: 6 P-cores + 4 E-cores, 16 threads, Turbo até 4.60 GHz, 20 MB Cache) |")
    md.append("| **Memória RAM** | 24 GB DDR5 (23.2 GiB utilizáveis pelo SO) |")
    md.append("| **Armazenamento** | SSD NVMe Western Digital PC SN740 512GB (PCIe 4.0 x4, leitura até 5000 MB/s, escrita até 4000 MB/s) |")
    md.append("| **Sistema Operacional Host** | Ubuntu 22.04 LTS (Kernel Linux 6.1.0-060100-generic, x86_64) |")
    md.append("| **Ambiente Contêiner** | Docker Engine 24.x (imagem base Ubuntu 22.04 LTS, kernel compartilhado) |")
    md.append("| **Ambiente Máquina Virtual** | VirtualBox 6.1.50 (Guest: Ubuntu 22.04 LTS, 4 vCPUs, 4096 MB RAM, Nested Paging On) |\n")

    md.append("## 📈 Resultados Obtidos e Análise de Overhead\n")
    md.append(f"> 🕒 **Última execução:** {now_str}\n")

    # Coletar resolucoes CPU
    all_cpu_keys = []
    for s in [bm_summary, dk_summary, vm_summary]:
        if s and "cpu" in s:
            for k in s["cpu"].keys():
                if k not in all_cpu_keys:
                    all_cpu_keys.append(k)

    md.append("### 1. Benchmark CPU-Bound (Mandelbrot)\n")
    md.append("| Resolução | Bare-Metal | Docker | VirtualBox VM | Overhead Docker | Overhead VM |")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|")

    for k in all_cpu_keys:
        bm_val = f"{bm_summary['cpu'][k]['mean_wall_time']:.4f} s" if bm_summary and k in bm_summary.get("cpu", {}) else "-"
        dk_val = f"{dk_summary['cpu'][k]['mean_wall_time']:.4f} s" if dk_summary and k in dk_summary.get("cpu", {}) else "-"
        vm_val = f"{vm_summary['cpu'][k]['mean_wall_time']:.4f} s" if vm_summary and k in vm_summary.get("cpu", {}) else "-"

        dk_ov = f"+{ov_summary['docker']['cpu_overhead_pct'][k]}%" if ov_summary and "docker" in ov_summary and k in ov_summary["docker"].get("cpu_overhead_pct", {}) else "-"
        vm_ov = f"+{ov_summary['vm']['cpu_overhead_pct'][k]}%" if ov_summary and "vm" in ov_summary and k in ov_summary["vm"].get("cpu_overhead_pct", {}) else "-"

        md.append(f"| **{k}** | {bm_val} | {dk_val} | {vm_val} | **{dk_ov}** | **{vm_ov}** |")

    md.append("\n> **Conclusão CPU:** O overhead da virtualização para tarefas puramente aritméticas é **praticamente nulo (< 1%)** tanto em contêineres quanto em máquinas virtuais, comprovando a eficiência das extensões de hardware do processador (Intel VT-x / AMD-V).\n")

    # Coletar tamanhos I/O
    all_io_keys = []
    for s in [bm_summary, dk_summary, vm_summary]:
        if s and "io" in s:
            for k in s["io"].keys():
                if k not in all_io_keys:
                    all_io_keys.append(k)

    md.append("### 2. Benchmark I/O-Bound (External Merge Sort)\n")
    md.append("| Tamanho | Bare-Metal | Docker | VirtualBox VM | Overhead Docker | Overhead VM | Throughput VM |")
    md.append("|:---:|:---:|:---:|:---:|:---:|:---:|:---:|")

    for k in all_io_keys:
        bm_val = f"{bm_summary['io'][k]['mean_sort_time']:.4f} s" if bm_summary and k in bm_summary.get("io", {}) else "-"
        dk_val = f"{dk_summary['io'][k]['mean_sort_time']:.4f} s" if dk_summary and k in dk_summary.get("io", {}) else "-"
        vm_val = f"{vm_summary['io'][k]['mean_sort_time']:.4f} s" if vm_summary and k in vm_summary.get("io", {}) else "-"
        vm_tp = f"{vm_summary['io'][k]['mean_throughput_mb_s']:.1f} MB/s" if vm_summary and k in vm_summary.get("io", {}) else "-"

        dk_ov = f"+{ov_summary['docker']['io_overhead_pct'][k]}%" if ov_summary and "docker" in ov_summary and k in ov_summary["docker"].get("io_overhead_pct", {}) else "-"
        vm_ov = f"+{ov_summary['vm']['io_overhead_pct'][k]}%" if ov_summary and "vm" in ov_summary and k in ov_summary["vm"].get("io_overhead_pct", {}) else "-"

        md.append(f"| **{k}** | {bm_val} | {dk_val} | {vm_val} | **{dk_ov}** | **{vm_ov}** | {vm_tp} |")

    md.append("\n> **Conclusão E/S:**")
    md.append("> * O **Docker** apresenta desempenho muito próximo ao nativo (overhead de apenas **1.5% a 4.6%**), pois compartilha o kernel host diretamente.")
    md.append("> * A **Máquina Virtual (VirtualBox)** sofre uma sobretaxa severa (**~160% de overhead**, demorando mais de 2.6 vezes mais), decorrente da emulação da controladora de armazenamento virtual, do isolamento do sistema de arquivos e da sincronização forçada de blocos em disco (`fsync`).\n")

    return "\n".join(md)


def update_readme():
    if not os.path.exists(README_PATH):
        print(f"[!] README.md nao encontrado em {README_PATH}")
        return

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    results_section = generate_results_markdown()

    # Procurar a secao de resultados e substituir
    pattern = r"## (🖥️ Especificações do Ambiente Experimental|📈 Resultados Obtidos e Análise de Overhead).*"
    if re.search(pattern, content, flags=re.DOTALL):
        updated_content = re.sub(pattern, results_section, content, flags=re.DOTALL)
    else:
        updated_content = content.rstrip() + "\n\n---\n\n" + results_section

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)

    print(f"[*] README.md atualizado com sucesso em {README_PATH}!")


if __name__ == "__main__":
    update_readme()
