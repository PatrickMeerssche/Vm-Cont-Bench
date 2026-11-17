#!/usr/bin/env python3
"""
Gera diagramas visuais e ilustracoes em alta resolucao para enriquecer os slides:
1. Renderizacao estetica do Fractal de Mandelbrot
2. Diagrama arquitetural: Bare-Metal vs Docker vs VirtualBox
3. Fluxograma do External Merge Sort (Fase de Split e K-way Merge)
4. Infografico de especificacoes de Hardware e Metricas-chave
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.gridspec import GridSpec

VISUALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "visuals")
os.makedirs(VISUALS_DIR, exist_ok=True)

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 1.0


def generate_mandelbrot():
    print("[*] Gerando visual do Fractal de Mandelbrot...")
    w, h = 1200, 800
    x = np.linspace(-2.0, 0.5, w)
    y = np.linspace(-1.25, 1.25, h)
    X, Y = np.meshgrid(x, y)
    C = X + 1j * Y
    Z = np.zeros_like(C)
    div_time = np.zeros(C.shape, dtype=int)
    m = np.full(C.shape, True, dtype=bool)

    for i in range(150):
        Z[m] = Z[m]**2 + C[m]
        diverged = np.greater(np.abs(Z), 2.0, where=m)
        div_time[diverged & m] = i
        m[np.abs(Z) > 2.0] = False

    fig, ax = plt.subplots(figsize=(10, 6.5), facecolor='#0f172a')
    ax.set_facecolor('#0f172a')
    im = ax.imshow(div_time, extent=[-2.0, 0.5, -1.25, 1.25], cmap='twilight_shifted', origin='lower')
    ax.axis('off')

    # Titulo e formula dentro da imagem
    fig.text(0.5, 0.92, "Fractal de Mandelbrot", ha='center', color='#f8fafc', fontsize=18, fontweight='bold')
    fig.text(0.5, 0.86, r"$z_{n+1} = z_n^2 + c$   |   Operações Puras de Ponto Flutuante (CPU / ULA)",
             ha='center', color='#94a3b8', fontsize=12)

    # Box de informacao tecnica
    bbox_props = dict(boxstyle="round,pad=0.6", fc="#1e293b", ec="#38bdf8", lw=1.5, alpha=0.9)
    info_text = (
        "• 100% de uso de CPU em modo usuário\n"
        "• Zero I/O de disco durante a computação\n"
        "• Cache L1/L2 e Registradores vetoriais"
    )
    ax.text(0.04, 0.12, info_text, transform=ax.transAxes, color='#e2e8f0',
            fontsize=10.5, bbox=bbox_props, va='bottom', family='monospace')

    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "mandelbrot_fractal.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight', facecolor='#0f172a')
    plt.close()
    print(f" -> Salvo: {out_path}")


def generate_architecture_diagram():
    print("[*] Gerando diagrama arquitetural dos 3 ambientes...")
    fig, ax = plt.subplots(figsize=(12, 6.5), facecolor='#ffffff')
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 7.5)
    ax.axis('off')

    # Titulo
    ax.text(6, 7.1, "Comparativo Arquitetural: Pilhas de Execução", ha='center', fontsize=17, fontweight='bold', color='#0f172a')
    ax.text(6, 6.7, "Relação entre Código do Usuário, Camadas de Virtualização e Hardware Físico", ha='center', fontsize=11, color='#64748b')

    # Colunas
    cols = [
        {"name": "Bare-Metal (Nativo)", "x": 0.8, "color": "#10b981", "sub": "Desempenho Bruto / Sem Abstração"},
        {"name": "Contêiner (Docker)", "x": 4.6, "color": "#0284c7", "sub": "Kernel Compartilhado / Namespaces"},
        {"name": "Máquina Virtual (VirtualBox)", "x": 8.4, "color": "#e11d48", "sub": "Hipervisor Tipo 2 / SO Guest"}
    ]

    col_w = 2.8

    for c in cols:
        x0 = c["x"]
        # Header box
        ax.add_patch(patches.FancyBboxPatch((x0, 5.7), col_w, 0.7, boxstyle="round,pad=0.08",
                                            facecolor=c["color"], edgecolor="none"))
        ax.text(x0 + col_w/2, 6.18, c["name"], ha='center', va='center', color='white', fontsize=11.5, fontweight='bold')
        ax.text(x0 + col_w/2, 5.88, c["sub"], ha='center', va='center', color='#f1f5f9', fontsize=8)

        # Base Hardware (comum a todos)
        ax.add_patch(patches.FancyBboxPatch((x0, 0.5), col_w, 0.7, boxstyle="round,pad=0.05",
                                            facecolor='#1e293b', edgecolor='#334155'))
        ax.text(x0 + col_w/2, 0.85, "Hardware Físico\n(i5-13450HX, 24GB, SSD NVMe)", ha='center', va='center',
                color='#f8fafc', fontsize=9, fontweight='bold')

    # Pilha 1: Bare-Metal
    # Kernel Host
    ax.add_patch(patches.FancyBboxPatch((0.8, 1.4), col_w, 1.6, boxstyle="round,pad=0.05",
                                        facecolor='#d1fae5', edgecolor='#10b981', lw=1.5))
    ax.text(0.8 + col_w/2, 2.2, "Kernel Linux Host (6.1)\n• Gerenciador de Processos\n• Page Cache / ext4\n• Driver NVMe Direto",
            ha='center', va='center', color='#065f46', fontsize=9)

    # Processo Nativo
    ax.add_patch(patches.FancyBboxPatch((0.8, 3.2), col_w, 2.2, boxstyle="round,pad=0.05",
                                        facecolor='#ecfdf5', edgecolor='#10b981', lw=2))
    ax.text(0.8 + col_w/2, 4.3, "Aplicação C\n(Mandelbrot / Sort)\n\n• Execução direta na CPU\n• Syscalls diretas ao kernel\n• Overhead zero (0%)",
            ha='center', va='center', color='#047857', fontsize=9.5, fontweight='bold')

    # Pilha 2: Docker
    # Kernel Host
    ax.add_patch(patches.FancyBboxPatch((4.6, 1.4), col_w, 1.2, boxstyle="round,pad=0.05",
                                        facecolor='#e0f2fe', edgecolor='#0284c7', lw=1.5))
    ax.text(4.6 + col_w/2, 2.0, "Kernel Linux Host Compartilhado\n• Namespaces (PID, Mount, Net)\n• Control Groups (cgroups v2)",
            ha='center', va='center', color='#0369a1', fontsize=9)

    # Docker Engine / Camada Storage
    ax.add_patch(patches.FancyBboxPatch((4.6, 2.8), col_w, 0.9, boxstyle="round,pad=0.05",
                                        facecolor='#bae6fd', edgecolor='#0284c7', lw=1.5))
    ax.text(4.6 + col_w/2, 3.25, "Docker Runtime / Overlay2\n• Isolamento de filesystem\n• Baixíssimo overhead de I/O",
            ha='center', va='center', color='#0c4a6e', fontsize=8.5)

    # Contêiner App
    ax.add_patch(patches.FancyBboxPatch((4.6, 3.9), col_w, 1.5, boxstyle="round,pad=0.05",
                                        facecolor='#f0f9ff', edgecolor='#0284c7', lw=2))
    ax.text(4.6 + col_w/2, 4.65, "Contêiner App\n(Ubuntu 22.04)\n\n• CPU: nativa (~0% overhead)\n• E/S: quase nativa (< 5%)",
            ha='center', va='center', color='#0369a1', fontsize=9.5, fontweight='bold')

    # Pilha 3: VirtualBox
    # Kernel Host
    ax.add_patch(patches.FancyBboxPatch((8.4, 1.4), col_w, 0.7, boxstyle="round,pad=0.05",
                                        facecolor='#ffe4e6', edgecolor='#e11d48', lw=1))
    ax.text(8.4 + col_w/2, 1.75, "Kernel Host / SO Principal", ha='center', va='center', color='#9f1239', fontsize=8.5)

    # Hipervisor Type-2
    ax.add_patch(patches.FancyBboxPatch((8.4, 2.2), col_w, 0.9, boxstyle="round,pad=0.05",
                                        facecolor='#fecdd3', edgecolor='#e11d48', lw=1.5))
    ax.text(8.4 + col_w/2, 2.65, "Hipervisor VirtualBox\n• Emulação de hardware (SATA/IDE)\n• Tradução de I/O em arquivo .vdi",
            ha='center', va='center', color='#881337', fontsize=8.5, fontweight='bold')

    # Guest Kernel
    ax.add_patch(patches.FancyBboxPatch((8.4, 3.2), col_w, 0.9, boxstyle="round,pad=0.05",
                                        facecolor='#fda4af', edgecolor='#e11d48', lw=1.5))
    ax.text(8.4 + col_w/2, 3.65, "Kernel Linux Guest (VM)\n• Gerencia memória e disco virtual",
            ha='center', va='center', color='#4c0519', fontsize=8.5)

    # App na VM
    ax.add_patch(patches.FancyBboxPatch((8.4, 4.2), col_w, 1.2, boxstyle="round,pad=0.05",
                                        facecolor='#fff1f2', edgecolor='#e11d48', lw=2))
    ax.text(8.4 + col_w/2, 4.8, "Aplicação na VM\n\n• CPU: VT-x (~0% overhead)\n• E/S: GARGALO (+160%)",
            ha='center', va='center', color='#9f1239', fontsize=9.5, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "architecture_comparison.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f" -> Salvo: {out_path}")


def generate_external_sort_flow():
    print("[*] Gerando fluxograma do External Merge Sort...")
    fig, ax = plt.subplots(figsize=(11, 5.5), facecolor='#ffffff')
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 6)
    ax.axis('off')

    ax.text(5.5, 5.5, "Fluxo de Execução: External Merge Sort", ha='center', fontsize=16, fontweight='bold', color='#0f172a')
    ax.text(5.5, 5.15, "Como o algoritmo supera o limite de RAM de 16 MB e força estresse contínuo de disco", ha='center', fontsize=10.5, color='#64748b')

    # Caixa 1: Arquivo Inicial
    ax.add_patch(patches.FancyBboxPatch((0.5, 2.0), 2.0, 2.4, boxstyle="round,pad=0.08", facecolor='#f1f5f9', edgecolor='#94a3b8', lw=1.5))
    ax.text(1.5, 3.9, "Arquivo Bruto\n(64 MB / 128 MB)", ha='center', color='#0f172a', fontsize=10, fontweight='bold')
    ax.text(1.5, 3.1, "Milhões de inteiros\nuint64 desordenados\nem disco", ha='center', color='#475569', fontsize=8.5)
    ax.text(1.5, 2.3, "Entrada Sequencial", ha='center', color='#2563eb', fontsize=8, fontweight='bold')

    # Seta 1
    ax.annotate('', xy=(3.0, 3.2), xytext=(2.6, 3.2), arrowprops=dict(facecolor='#0284c7', shrink=0.05, width=2, headwidth=7))

    # Caixa 2: Fase 1 (Split & Sort)
    ax.add_patch(patches.FancyBboxPatch((3.1, 1.8), 2.5, 2.8, boxstyle="round,pad=0.08", facecolor='#e0f2fe', edgecolor='#0284c7', lw=1.5))
    ax.text(4.35, 4.2, "Fase 1: Divisão & RAM", ha='center', color='#0369a1', fontsize=10, fontweight='bold')
    ax.text(4.35, 3.3, "1. Lê pedaços de 16 MB\n2. qsort() em RAM\n3. Salva chunk_N.tmp\n4. Força fsync()", ha='center', color='#0f172a', fontsize=8.5)
    ax.text(4.35, 2.1, "Múltiplas Gravações", ha='center', color='#b91c1c', fontsize=8, fontweight='bold')

    # Seta 2
    ax.annotate('', xy=(6.1, 3.2), xytext=(5.7, 3.2), arrowprops=dict(facecolor='#0284c7', shrink=0.05, width=2, headwidth=7))

    # Caixa 3: Fase 2 (K-way Merge)
    ax.add_patch(patches.FancyBboxPatch((6.2, 1.8), 2.5, 2.8, boxstyle="round,pad=0.08", facecolor='#fef3c7', edgecolor='#d97706', lw=1.5))
    ax.text(7.45, 4.2, "Fase 2: K-Way Merge", ha='center', color='#b45309', fontsize=10, fontweight='bold')
    ax.text(7.45, 3.3, "• Abre todos chunks\n• Min-Heap de tamanho K\n• Lê concorrentemente\n• Escreve dados ordenados", ha='center', color='#0f172a', fontsize=8.5)
    ax.text(7.45, 2.1, "Leitura & Escrita Mista", ha='center', color='#b91c1c', fontsize=8, fontweight='bold')

    # Seta 3
    ax.annotate('', xy=(9.2, 3.2), xytext=(8.8, 3.2), arrowprops=dict(facecolor='#0284c7', shrink=0.05, width=2, headwidth=7))

    # Caixa 4: Arquivo Final
    ax.add_patch(patches.FancyBboxPatch((9.3, 2.0), 1.5, 2.4, boxstyle="round,pad=0.08", facecolor='#dcfce7', edgecolor='#16a34a', lw=1.5))
    ax.text(10.05, 3.9, "Saída\nFinal", ha='center', color='#15803d', fontsize=10, fontweight='bold')
    ax.text(10.05, 3.1, "Arquivo 100%\nordenado\n+ fsync()\n+ validação", ha='center', color='#166534', fontsize=8.5)
    ax.text(10.05, 2.3, "Sucesso", ha='center', color='#15803d', fontsize=8, fontweight='bold')

    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "external_sort_flow.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f" -> Salvo: {out_path}")


def generate_key_takeaways_card():
    print("[*] Gerando cards visuais com metricas-chave...")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), facecolor='#ffffff')

    for ax in [ax1, ax2]:
        ax.axis('off')

    # Card 1: CPU
    ax1.add_patch(patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.05", facecolor='#f0fdf4', edgecolor='#22c55e', lw=2))
    ax1.text(0.5, 0.82, "CARGA CPU (Mandelbrot)", ha='center', fontsize=13, fontweight='bold', color='#15803d')
    ax1.text(0.5, 0.55, "< 1%", ha='center', fontsize=36, fontweight='bold', color='#16a34a')
    ax1.text(0.5, 0.42, "Overhead Máximo Medido", ha='center', fontsize=10, fontweight='bold', color='#475569')
    ax1.text(0.5, 0.22, "• Instruções nativas via Intel VT-x\n• Desempenho idêntico entre os 3 ambientes\n• Sem impacto de virtualização",
             ha='center', fontsize=9.5, color='#1e293b')

    # Card 2: I/O
    ax2.add_patch(patches.FancyBboxPatch((0.05, 0.05), 0.9, 0.9, boxstyle="round,pad=0.05", facecolor='#fff1f2', edgecolor='#f43f5e', lw=2))
    ax2.text(0.5, 0.82, "CARGA E/S (External Sort)", ha='center', fontsize=13, fontweight='bold', color='#be123c')
    ax2.text(0.5, 0.55, "+160%", ha='center', fontsize=36, fontweight='bold', color='#e11d48')
    ax2.text(0.5, 0.42, "Sobretaxa na VM (VirtualBox)", ha='center', fontsize=10, fontweight='bold', color='#475569')
    ax2.text(0.5, 0.22, "• Docker opera com apenas ~1.5% a 4.6%\n• VM sofre com emulação e chamadas fsync()\n• Throughput cai de 222 para 84 MB/s",
             ha='center', fontsize=9.5, color='#1e293b')

    plt.tight_layout()
    out_path = os.path.join(VISUALS_DIR, "stat_cards.png")
    plt.savefig(out_path, dpi=200, bbox_inches='tight')
    plt.close()
    print(f" -> Salvo: {out_path}")


if __name__ == "__main__":
    generate_mandelbrot()
    generate_architecture_diagram()
    generate_external_sort_flow()
    generate_key_takeaways_card()
    print("[*] Todos os visuais gerados com sucesso!")
