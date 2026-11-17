#!/usr/bin/env python3
"""
Orquestrador de Benchmarks de Desempenho (Sistemas Operacionais)
Compara execuções Bare-metal, Docker e VM variando o tamanho de entrada.

Executa:
1. Mandelbrot (CPU-bound) variando resolução (largura x altura)
2. External Merge Sort (I/O-bound) variando tamanho do arquivo em MB

Calcula média, desvio padrão e salva relatórios em CSV, JSON e gráficos PNG em results/<env>/.
"""

import argparse
import csv
import json
import os
import subprocess
import sys
from statistics import mean, stdev

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
BIN_DIR = os.path.join(PROJECT_ROOT, "bin")
CPU_BIN = os.path.join(BIN_DIR, "cpu_mandelbrot")
IO_BIN = os.path.join(BIN_DIR, "io_external_sort")


def ensure_binaries():
    if not os.path.exists(CPU_BIN) or not os.path.exists(IO_BIN):
        print("[*] Binarios ausentes. Compilando...")
        subprocess.check_call(["make", "-C", PROJECT_ROOT])


def run_cpu_once(width, height, max_iter):
    cmd = [CPU_BIN, str(width), str(height), str(max_iter)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        if line.startswith("JSON_OUTPUT:"):
            return json.loads(line[len("JSON_OUTPUT:"):].strip())
    raise RuntimeError(f"JSON_OUTPUT nao encontrado: {proc.stdout}")


def run_io_once(total_mb, chunk_mb, do_fsync, tmp_dir):
    os.makedirs(tmp_dir, exist_ok=True)
    cmd = [IO_BIN, str(total_mb), str(chunk_mb), tmp_dir, str(do_fsync)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    for line in proc.stdout.splitlines():
        if line.startswith("JSON_OUTPUT:"):
            return json.loads(line[len("JSON_OUTPUT:"):].strip())
    raise RuntimeError(f"JSON_OUTPUT nao encontrado: {proc.stdout}")


def run_benchmarks(env_name, runs, cpu_sizes, io_sizes, max_iter, chunk_mb, do_fsync, output_dir):
    ensure_binaries()
    os.makedirs(output_dir, exist_ok=True)
    tmp_io_dir = os.path.join(output_dir, "tmp_io")

    raw_results = []
    summary = {"env": env_name, "runs_per_config": runs, "cpu": {}, "io": {}}

    print("=" * 65)
    print(f" INICIANDO BATERIA DE BENCHMARKS - AMBIENTE: {env_name.upper()}")
    print(f" Repeticoes por configuracao: {runs}")
    print(f" Diretorio de saida: {output_dir}")
    print("=" * 65)

    # 1. Mandelbrot (CPU)
    print("\n>>> [1/2] Executando Benchmark CPU-Bound (Mandelbrot)...")
    for size in cpu_sizes:
        print(f"\n[-] Resolucao {size}x{size} (Iteracoes max: {max_iter}):")
        times = []
        user_times = []
        sys_times = []

        for r in range(1, runs + 1):
            res = run_cpu_once(size, size, max_iter)
            res["env"] = env_name
            res["run"] = r
            raw_results.append(res)
            w_time = res["wall_time"]
            times.append(w_time)
            user_times.append(res["user_time"])
            sys_times.append(res["sys_time"])
            print(f"    Rodada {r}/{runs}: {w_time:.4f}s (user: {res['user_time']:.4f}s, sys: {res['sys_time']:.4f}s)")

        avg = mean(times)
        sd = stdev(times) if len(times) > 1 else 0.0
        summary["cpu"][f"{size}x{size}"] = {
            "size": size,
            "mean_wall_time": avg,
            "stdev_wall_time": sd,
            "min_wall_time": min(times),
            "max_wall_time": max(times),
            "mean_user_time": mean(user_times),
            "mean_sys_time": mean(sys_times)
        }
        print(f"  -> Media: {avg:.4f}s (+- {sd:.4f}s)")

    # 2. External Merge Sort (I/O)
    print("\n>>> [2/2] Executando Benchmark I/O-Bound (External Merge Sort)...")
    for total_mb in io_sizes:
        print(f"\n[-] Tamanho arquivo: {total_mb} MB (Chunk RAM: {chunk_mb} MB, fsync: {do_fsync}):")
        sort_times = []
        total_times = []
        throughputs = []
        user_times = []
        sys_times = []

        for r in range(1, runs + 1):
            res = run_io_once(total_mb, chunk_mb, do_fsync, tmp_io_dir)
            res["env"] = env_name
            res["run"] = r
            raw_results.append(res)
            s_time = res["sort_time"]
            sort_times.append(s_time)
            total_times.append(res["total_time"])
            throughputs.append(res["throughput_mb_s"])
            user_times.append(res["user_time"])
            sys_times.append(res["sys_time"])
            print(f"    Rodada {r}/{runs}: Sort: {s_time:.4f}s | Throughput: {res['throughput_mb_s']:.1f} MB/s (sys: {res['sys_time']:.4f}s)")

        avg_sort = mean(sort_times)
        sd_sort = stdev(sort_times) if len(sort_times) > 1 else 0.0
        summary["io"][f"{total_mb}MB"] = {
            "total_mb": total_mb,
            "mean_sort_time": avg_sort,
            "stdev_sort_time": sd_sort,
            "min_sort_time": min(sort_times),
            "max_sort_time": max(sort_times),
            "mean_total_time": mean(total_times),
            "mean_throughput_mb_s": mean(throughputs),
            "mean_user_time": mean(user_times),
            "mean_sys_time": mean(sys_times)
        }
        print(f"  -> Media Sort: {avg_sort:.4f}s (+- {sd_sort:.4f}s) | Throughput: {mean(throughputs):.1f} MB/s")

    # Limpa temporarios
    if os.path.exists(tmp_io_dir):
        import shutil
        shutil.rmtree(tmp_io_dir, ignore_errors=True)

    # Salva CSV
    csv_path = os.path.join(output_dir, f"results_{env_name}.csv")
    with open(csv_path, "w", newline="") as f:
        if raw_results:
            keys = sorted({k for row in raw_results for k in row.keys()})
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(raw_results)

    # Salva JSON
    json_path = os.path.join(output_dir, f"summary_{env_name}.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 65)
    print(" BATERIA CONCLUIDA COM SUCESSO!")
    print(f" - Dados brutos (CSV): {csv_path}")
    print(f" - Resumo estatistico (JSON): {json_path}")
    print("=" * 65)

    generate_plots(summary, output_dir, env_name)


def generate_plots(summary, output_dir, env_name):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("[!] Matplotlib nao disponivel, pulando grafico individual.")
        return

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    # CPU
    cpu_data = summary["cpu"]
    resolutions = [v["size"] for v in cpu_data.values()]
    means_cpu = [v["mean_wall_time"] for v in cpu_data.values()]
    errs_cpu = [v["stdev_wall_time"] for v in cpu_data.values()]

    ax1.errorbar(resolutions, means_cpu, yerr=errs_cpu, fmt='-o', color='#1f77b4', capsize=5, lw=2)
    ax1.set_title(f"CPU-Bound: Mandelbrot ({env_name.upper()})", fontsize=12, fontweight='bold')
    ax1.set_xlabel("Resolucao (NxN pixels)")
    ax1.set_ylabel("Tempo de Execucao (s)")
    ax1.grid(True, linestyle="--", alpha=0.6)

    # I/O
    io_data = summary["io"]
    sizes_mb = [v["total_mb"] for v in io_data.values()]
    means_io = [v["mean_sort_time"] for v in io_data.values()]
    errs_io = [v["stdev_sort_time"] for v in io_data.values()]

    ax2.errorbar(sizes_mb, means_io, yerr=errs_io, fmt='-s', color='#d62728', capsize=5, lw=2)
    ax2.set_title(f"I/O-Bound: External Merge Sort ({env_name.upper()})", fontsize=12, fontweight='bold')
    ax2.set_xlabel("Tamanho dos Dados (MB)")
    ax2.set_ylabel("Tempo de Ordenacao (s)")
    ax2.grid(True, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plot_path = os.path.join(output_dir, f"plot_{env_name}.png")
    plt.savefig(plot_path, dpi=150)
    plt.close()
    print(f" - Grafico gerado: {plot_path}")


def main():
    parser = argparse.ArgumentParser(description="Runner de Benchmarks para SO")
    parser.add_argument("--env", default="baremetal", help="Nome do ambiente (baremetal, docker, vm)")
    parser.add_argument("--runs", type=int, default=3, help="Numero de repeticoes por configuracao (padrao: 3)")
    parser.add_argument("--cpu-sizes", nargs="+", type=int, default=[1000, 2000, 3000, 4000],
                        help="Tamanhos de resolucao para Mandelbrot")
    parser.add_argument("--max-iter", type=int, default=1000, help="Iteracoes maximas do Mandelbrot")
    parser.add_argument("--io-sizes", nargs="+", type=int, default=[64, 128, 256, 512],
                        help="Tamanhos em MB para External Sort")
    parser.add_argument("--chunk-mb", type=int, default=16, help="Tamanho do chunk em RAM em MB")
    parser.add_argument("--no-fsync", action="store_true", help="Desativa fsync nas operacoes de disco")
    parser.add_argument("--output-dir", default=None, help="Diretorio de saida customizado")

    args = parser.parse_args()
    out_dir = args.output_dir or os.path.join(PROJECT_ROOT, "results", args.env)

    run_benchmarks(
        env_name=args.env,
        runs=args.runs,
        cpu_sizes=args.cpu_sizes,
        io_sizes=args.io_sizes,
        max_iter=args.max_iter,
        chunk_mb=args.chunk_mb,
        do_fsync=0 if args.no_fsync else 1,
        output_dir=out_dir
    )


if __name__ == "__main__":
    main()
