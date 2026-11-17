#!/usr/bin/env python3
"""
Gera graficos comparativos unificados: Bare-metal vs Docker vs VM.
Calcula sobretaxa percentual (overhead %) de cada ambiente virtualizado em relacao ao Bare-metal.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
COMP_DIR = os.path.join(RESULTS_DIR, "comparison")


def load_env_summary(env_name):
    p = os.path.join(RESULTS_DIR, env_name, f"summary_{env_name}.json")
    if os.path.exists(p):
        with open(p) as f:
            return json.load(f)
    return None


def generate_comparisons():
    os.makedirs(COMP_DIR, exist_ok=True)
    envs = ["baremetal", "docker", "vm"]
    summaries = {}
    for e in envs:
        s = load_env_summary(e)
        if s:
            summaries[e] = s

    if not summaries:
        print("[!] Nenhum resultado encontrado para comparacao.")
        return

    print(f"[*] Gerando comparacoes para os ambientes: {list(summaries.keys())}")

    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("[!] Matplotlib/numpy ausentes. Pulando graficos.")
        return

    palette = {"baremetal": "#2ca02c", "docker": "#1f77b4", "vm": "#d62728"}
    labels = {"baremetal": "Bare-Metal (Nativo)", "docker": "Contêiner (Docker)", "vm": "Máquina Virtual (VM)"}

    # -------------------------------------------------------------
    # 1. Comparativo CPU (Mandelbrot)
    # -------------------------------------------------------------
    # Coleta todas as resolucoes comuns
    first_cpu = list(summaries.values())[0]["cpu"]
    resolutions = list(first_cpu.keys())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(resolutions))
    width = 0.8 / len(summaries)

    for idx, (env_name, s) in enumerate(summaries.items()):
        means = [s["cpu"].get(res, {}).get("mean_wall_time", 0.0) for res in resolutions]
        errs  = [s["cpu"].get(res, {}).get("stdev_wall_time", 0.0) for res in resolutions]
        offset = (idx - (len(summaries) - 1) / 2) * width
        rects = ax.bar(x + offset, means, width, yerr=errs, capsize=4,
                       label=labels.get(env_name, env_name),
                       color=palette.get(env_name, "#7f7f7f"), alpha=0.9)
        # Adiciona rotulo com valor no topo
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f"{height:.2f}s",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

    ax.set_ylabel("Tempo de Execução (s) - Menor é melhor", fontsize=11)
    ax.set_title("Comparativo CPU-Bound: Fractal de Mandelbrot\n(Bare-Metal vs Docker vs VM)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(resolutions, fontsize=10)
    ax.legend(frameon=True, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    cpu_plot_path = os.path.join(COMP_DIR, "comparison_cpu.png")
    plt.savefig(cpu_plot_path, dpi=200)
    plt.close()
    print(f" -> Grafico CPU salvo em: {cpu_plot_path}")

    # -------------------------------------------------------------
    # 2. Comparativo I/O (External Merge Sort)
    # -------------------------------------------------------------
    first_io = list(summaries.values())[0]["io"]
    io_sizes = list(first_io.keys())

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(io_sizes))
    width = 0.8 / len(summaries)

    for idx, (env_name, s) in enumerate(summaries.items()):
        means = [s["io"].get(size, {}).get("mean_sort_time", 0.0) for size in io_sizes]
        errs  = [s["io"].get(size, {}).get("stdev_sort_time", 0.0) for size in io_sizes]
        offset = (idx - (len(summaries) - 1) / 2) * width
        rects = ax.bar(x + offset, means, width, yerr=errs, capsize=4,
                       label=labels.get(env_name, env_name),
                       color=palette.get(env_name, "#7f7f7f"), alpha=0.9)
        for rect in rects:
            height = rect.get_height()
            if height > 0:
                ax.annotate(f"{height:.2f}s",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=8)

    ax.set_ylabel("Tempo de Ordenação (s) - Menor é melhor", fontsize=11)
    ax.set_title("Comparativo I/O-Bound: External Merge Sort\n(Bare-Metal vs Docker vs VM)", fontsize=13, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(io_sizes, fontsize=10)
    ax.legend(frameon=True, fontsize=10)
    ax.grid(axis="y", linestyle="--", alpha=0.6)
    plt.tight_layout()

    io_plot_path = os.path.join(COMP_DIR, "comparison_io.png")
    plt.savefig(io_plot_path, dpi=200)
    plt.close()
    print(f" -> Grafico I/O salvo em: {io_plot_path}")

    # -------------------------------------------------------------
    # 3. Calculo do Overhead (%) em relacao ao Bare-metal
    # -------------------------------------------------------------
    overhead_report = {}
    if "baremetal" in summaries:
        bm = summaries["baremetal"]
        for env_name in summaries:
            if env_name == "baremetal":
                continue
            curr = summaries[env_name]
            overhead_report[env_name] = {"cpu_overhead_pct": {}, "io_overhead_pct": {}}

            # CPU
            for res, v in curr["cpu"].items():
                if res in bm["cpu"]:
                    base = bm["cpu"][res]["mean_wall_time"]
                    val = v["mean_wall_time"]
                    diff_pct = ((val - base) / base) * 100.0 if base > 0 else 0.0
                    overhead_report[env_name]["cpu_overhead_pct"][res] = round(diff_pct, 2)

            # I/O
            for sz, v in curr["io"].items():
                if sz in bm["io"]:
                    base = bm["io"][sz]["mean_sort_time"]
                    val = v["mean_sort_time"]
                    diff_pct = ((val - base) / base) * 100.0 if base > 0 else 0.0
                    overhead_report[env_name]["io_overhead_pct"][sz] = round(diff_pct, 2)

        out_json = os.path.join(COMP_DIR, "comparison_summary.json")
        with open(out_json, "w") as f:
            json.dump(overhead_report, f, indent=2)
        print(f" -> Resumo de overhead (%) salvo em: {out_json}")


if __name__ == "__main__":
    generate_comparisons()
