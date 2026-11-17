#!/usr/bin/env python3
"""
Gera apresentacao profissional em formato 16:9 (PPTX) com design moderno:
- Paleta profissional (Dark Slate Navy + Royal Blue + Emerald + Crimson)
- Cards visuais, badges e tipografia refinada (sem blocos gigantes de texto)
- Diagramas de arquitetura, fluxo e fractal de Mandelbrot integrados
- Tabelas de resultados e cards de metricas-chave
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
VISUALS_DIR = os.path.join(PROJECT_ROOT, "results", "visuals")
COMPARISON_DIR = os.path.join(PROJECT_ROOT, "results", "comparison")
ENTREGA_DIR = os.path.join(PROJECT_ROOT, "ENTREGA")
os.makedirs(ENTREGA_DIR, exist_ok=True)

# Cores do Design System
C_NAVY_BG    = RGBColor(15, 23, 42)     # #0f172a
C_LIGHT_BG   = RGBColor(248, 250, 252) # #f8fafc
C_WHITE      = RGBColor(255, 255, 255)
C_DARK_TEXT  = RGBColor(15, 23, 42)     # #0f172a
C_MUTED_TEXT = RGBColor(100, 116, 139) # #64748b
C_LIGHT_TEXT = RGBColor(241, 245, 249) # #f1f5f9
C_BLUE       = RGBColor(37, 99, 235)    # #2563eb
C_CYAN       = RGBColor(2, 132, 199)    # #0284c7
C_GREEN      = RGBColor(16, 185, 129)   # #10b981
C_ROSE       = RGBColor(225, 29, 72)    # #e11d48
C_CARD_BG    = RGBColor(255, 255, 255)
C_CARD_BORDER= RGBColor(226, 232, 240) # #e2e8f0
C_CARD_DARK  = RGBColor(30, 41, 59)     # #1e293b


def create_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    def add_bg(slide, color):
        shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
        shape.fill.solid()
        shape.fill.fore_color.rgb = color
        shape.line.fill.background()
        return shape

    def add_header(slide, title, category="SISTEMAS OPERACIONAIS — FURG"):
        # Category badge
        tb_cat = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        p_cat = tb_cat.text_frame.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = C_BLUE

        # Main Title
        tb_title = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.6))
        p_title = tb_title.text_frame.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = C_DARK_TEXT

    def add_card(slide, left, top, width, height, bg=C_WHITE, border=C_CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(left), Inches(top), Inches(width), Inches(height))
        card.fill.solid()
        card.fill.fore_color.rgb = bg
        card.line.color.rgb = border
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: Capa (Dark Slate Navy Modern Theme)
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_bg(s1, C_NAVY_BG)

    # Tag superior
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.3), Inches(0.4))
    p = tb.text_frame.paragraphs[0]
    p.text = "UNIVERSIDADE FEDERAL DO RIO GRANDE (FURG) • SISTEMAS OPERACIONAIS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    # Titulo Principal
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(1.3), Inches(11.3), Inches(1.8))
    p = tb.text_frame.paragraphs[0]
    p.text = "Avaliando o Custo de\nVirtualizar Aplicações"
    p.font.size = Pt(40)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    # Subtitulo
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(3.2), Inches(11.3), Inches(0.8))
    p = tb.text_frame.paragraphs[0]
    p.text = "Análise Prática de Desempenho: Bare-Metal vs Contêiner (Docker) vs Máquina Virtual (VirtualBox)"
    p.font.size = Pt(15)
    p.font.color.rgb = RGBColor(148, 163, 184)

    # 4 Cards dos Integrantes
    students = [
        ("Guilherme Burkert", "169504"),
        ("Patrick Meerssche", "169512"),
        ("Rômulo Maciel", "169505"),
        ("Dilson Simões", "166609")
    ]
    card_w = 2.6
    spacing = 0.3
    start_x = 1.0
    for idx, (name, mat) in enumerate(students):
        x = start_x + idx * (card_w + spacing)
        add_card(s1, x, 4.4, card_w, 1.4, bg=C_CARD_DARK, border=RGBColor(51, 65, 85))
        tb_st = s1.shapes.add_textbox(Inches(x + 0.15), Inches(4.55), Inches(card_w - 0.3), Inches(1.1))
        p1 = tb_st.text_frame.paragraphs[0]
        p1.text = name
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = C_WHITE
        p2 = tb_st.text_frame.add_paragraph()
        p2.text = f"Matrícula: {mat}"
        p2.font.size = Pt(11)
        p2.font.color.rgb = C_CYAN

    # Rodape Professor
    tb = s1.shapes.add_textbox(Inches(1.0), Inches(6.3), Inches(11.3), Inches(0.5))
    p = tb.text_frame.paragraphs[0]
    p.text = "Professor: Dr. Pedro de Botelho Marcos  •  Semestre 2026/2"
    p.font.size = Pt(11)
    p.font.color.rgb = RGBColor(100, 116, 139)

    # =========================================================================
    # SLIDE 2: Objetivo do Experimento
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_bg(s2, C_LIGHT_BG)
    add_header(s2, "Objetivo e Motivação do Estudo")

    # Card 1: Pergunta Central
    add_card(s2, 0.8, 1.5, 5.6, 5.2)
    tb = s2.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(5.0), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "A Questão Central"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    points = [
        "A virtualização é a base da infraestrutura moderna (nuvem, CI/CD, microsserviços e isolamento).",
        "Porém, cada camada de abstração impõe um custo de execução.",
        "Qual é o impacto real da virtualização em cargas de trabalho com comportamentos opostos?",
        "A sobretaxa é a mesma para cálculo puro na CPU e para gravações pesadas em disco?"
    ]
    for pt in points:
        p = tf.add_paragraph()
        p.text = f"•  {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK_TEXT
        p.space_after = Pt(12)

    # Card 2: Metodologia
    add_card(s2, 6.8, 1.5, 5.7, 5.2)
    tb = s2.shapes.add_textbox(Inches(7.1), Inches(1.8), Inches(5.1), Inches(4.6))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Nossa Abordagem Prática"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    points2 = [
        "3 Ambientes Avaliados: Bare-Metal (Nativo), Contêiner (Docker) e Máquina Virtual (VirtualBox).",
        "2 Cargas de Trabalho: CPU-bound (Fractal de Mandelbrot) e I/O-bound (External Merge Sort com fsync).",
        "Tamanhos de Entrada Variáveis: de matrizes pequenas a arquivos de 128 MB em disco.",
        "Mesmo Computador Físico: elimina ruídos de hardware e garante comparação justa."
    ]
    for pt in points2:
        p = tf.add_paragraph()
        p.text = f"✔  {pt}"
        p.font.size = Pt(13)
        p.font.color.rgb = C_DARK_TEXT
        p.space_after = Pt(12)

    # =========================================================================
    # SLIDE 3: Arquitetura Comparativa (Visual Diagram)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_bg(s3, C_WHITE)
    add_header(s3, "Visão Arquitetural: Pilhas de Execução")

    # Imagem grande do diagrama de arquitetura
    arch_img = os.path.join(VISUALS_DIR, "architecture_comparison.png")
    if os.path.exists(arch_img):
        s3.shapes.add_picture(arch_img, Inches(0.8), Inches(1.4), width=Inches(11.7))

    # =========================================================================
    # SLIDE 4: Algoritmo CPU-Bound (Mandelbrot)
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_bg(s4, C_LIGHT_BG)
    add_header(s4, "Carga CPU-Bound: Fractal de Mandelbrot")

    # Imagem do fractal a esquerda
    mandel_img = os.path.join(VISUALS_DIR, "mandelbrot_fractal.png")
    if os.path.exists(mandel_img):
        s4.shapes.add_picture(mandel_img, Inches(0.8), Inches(1.5), width=Inches(5.6))

    # Card explicativo a direita
    add_card(s4, 6.7, 1.5, 5.8, 5.3)
    tb = s4.shapes.add_textbox(Inches(7.0), Inches(1.7), Inches(5.2), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Características da Carga de CPU"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    bullets_cpu = [
        ("O que calcula:", "Itera a função complexa z = z² + c até convergência ou limite de 1.000 iterações por pixel."),
        ("Por que é CPU-bound:", "Consome 100% de ciclos em instruções aritméticas de ponto flutuante na ULA e registradores."),
        ("Zero interferência de disco:", "Nenhum arquivo é lido ou gravado durante o processamento. Apenas memória e CPU."),
        ("Tamanhos testados:", "Grades de 1000x1000 (1M pixels) e 2000x2000 (4M pixels)."),
        ("Implementação:", "Escrito em C puro (C11), compilado com otimização máxima (gcc -O3 -lm).")
    ]
    for title, desc in bullets_cpu:
        p = tf.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_DARK_TEXT
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 5: Algoritmo I/O-Bound (External Merge Sort)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_bg(s5, C_LIGHT_BG)
    add_header(s5, "Carga I/O-Bound: External Merge Sort")

    # Imagem do fluxo a esquerda
    sort_img = os.path.join(VISUALS_DIR, "external_sort_flow.png")
    if os.path.exists(sort_img):
        s5.shapes.add_picture(sort_img, Inches(0.8), Inches(1.5), width=Inches(6.0))

    # Card explicativo a direita
    add_card(s5, 7.1, 1.5, 5.4, 5.3)
    tb = s5.shapes.add_textbox(Inches(7.35), Inches(1.7), Inches(4.9), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Características da Carga de E/S"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_ROSE

    bullets_io = [
        ("Objetivo:", "Ordenar volumes massivos de dados que excedem a memória RAM alocada para o processo."),
        ("Por que é I/O-bound:", "O gargalo é a velocidade de leitura, escrita e troca de contexto com o kernel."),
        ("Fase 1 (Divisão):", "Lê blocos de 16 MB da entrada, ordena em RAM via qsort() e grava arquivos temporários em disco."),
        ("Fase 2 (Merge):", "Abre todos os chunks simultaneamente, intercala usando Min-Heap e gera o arquivo final."),
        ("Sincronização com fsync():", "Força o kernel a esvaziar buffers para o disco físico, expondo o custo real do armazenamento virtual."),
        ("Tamanhos testados:", "Arquivos binários de 64 MB e 128 MB (inteiros de 64 bits).")
    ]
    for title, desc in bullets_io:
        p = tf.add_paragraph()
        p.text = f"• {title} "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = C_DARK_TEXT
        run = p.add_run()
        run.text = desc
        run.font.bold = False
        p.space_after = Pt(6)

    # =========================================================================
    # SLIDE 6: Ambiente Experimental & Metodologia
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_bg(s6, C_LIGHT_BG)
    add_header(s6, "Ambiente Experimental e Metodologia de Medição")

    # Card 1: Hardware Real
    add_card(s6, 0.8, 1.5, 5.6, 5.3)
    tb = s6.shapes.add_textbox(Inches(1.1), Inches(1.7), Inches(5.0), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Especificações da Máquina Host"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    hw_specs = [
        ("Processador:", "Intel Core i5-13450HX (13ª Geração)"),
        ("Arquitetura:", "10 Núcleos (6 P-cores + 4 E-cores), 16 Threads"),
        ("Frequência:", "Até 4.60 GHz Turbo, 20 MB Intel Smart Cache"),
        ("Memória RAM:", "24 GB DDR5 (23.2 GiB utilizáveis)"),
        ("Armazenamento:", "SSD NVMe Western Digital PC SN740 512GB (PCIe 4.0 x4)"),
        ("Sistema Operacional:", "Ubuntu 22.04 LTS (Kernel Linux 6.1.0-generic x86_64)")
    ]
    for label, val in hw_specs:
        p = tf.add_paragraph()
        p.text = f"{label} "
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = C_DARK_TEXT
        run = p.add_run()
        run.text = val
        run.font.bold = False
        run.font.color.rgb = C_MUTED_TEXT
        p.space_after = Pt(8)

    # Card 2: Metodologia de Medição
    add_card(s6, 6.8, 1.5, 5.7, 5.3)
    tb = s6.shapes.add_textbox(Inches(7.1), Inches(1.7), Inches(5.1), Inches(4.9))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "Rigor Metodológico"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    method_points = [
        ("Relógio Monotônico:", "clock_gettime(CLOCK_MONOTONIC) garante medição imune a ajustes de NTP ou data do sistema."),
        ("Separação de CPU:", "Uso de getrusage(RUSAGE_SELF) para distinguir tempo em espaço de usuário (cálculo) e kernel (syscalls de E/S)."),
        ("Múltiplas Rodadas:", "Cada teste executado repetidas vezes para filtrar interferências esporádicas do sistema operacional."),
        ("Estatística Formal:", "Cálculo automático de Média (μ), Desvio Padrão (σ), Mínimo e Máximo."),
        ("Configuração da VM:", "VirtualBox 6.1 com 4 vCPUs, 4096 MB de RAM e paginação aninhada (nested paging).")
    ]
    for label, val in method_points:
        p = tf.add_paragraph()
        p.text = f"✔ {label} "
        p.font.size = Pt(11.5)
        p.font.bold = True
        p.font.color.rgb = C_DARK_TEXT
        run = p.add_run()
        run.text = val
        run.font.bold = False
        p.space_after = Pt(8)

    # =========================================================================
    # SLIDE 7: Resultados em CPU (Mandelbrot)
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_bg(s7, C_LIGHT_BG)
    add_header(s7, "Resultados: Desempenho em CPU (Mandelbrot)")

    # Grafico a esquerda
    cpu_plot = os.path.join(COMPARISON_DIR, "comparison_cpu.png")
    if os.path.exists(cpu_plot):
        s7.shapes.add_picture(cpu_plot, Inches(0.8), Inches(1.4), width=Inches(6.2))

    # Tabela e Card a direita
    add_card(s7, 7.3, 1.4, 5.2, 5.4)
    tb = s7.shapes.add_textbox(Inches(7.55), Inches(1.6), Inches(4.7), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Dados Medidos e Conclusões"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    p = tf.add_paragraph()
    p.text = "Resolução 1000x1000 (1M pixels):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEXT
    for env, t, ov in [("Bare-Metal", "0.53 s", "Base"), ("Docker", "0.54 s", "+1.0%"), ("VirtualBox", "0.54 s", "+0.4%")]:
        p = tf.add_paragraph()
        p.text = f"  • {env}: {t}  ({ov})"
        p.font.size = Pt(11)

    p = tf.add_paragraph()
    p.text = "Resolução 2000x2000 (4M pixels):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEXT
    p.space_before = Pt(8)
    for env, t, ov in [("Bare-Metal", "2.13 s", "Base"), ("Docker", "2.14 s", "+0.1%"), ("VirtualBox", "2.14 s", "+0.5%")]:
        p = tf.add_paragraph()
        p.text = f"  • {env}: {t}  ({ov})"
        p.font.size = Pt(11)

    # Callout box
    p = tf.add_paragraph()
    p.text = "Destaques Técnicos:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_GREEN
    p.space_before = Pt(14)

    obs = [
        "Overhead inferior a 1% em ambos os ambientes virtuais.",
        "A aceleração de hardware (Intel VT-x) permite que as instruções da ULA rodem à velocidade nativa.",
        "Crescimento perfeitamente quadrático (4x resolução = 4x tempo de execução)."
    ]
    for o in obs:
        p = tf.add_paragraph()
        p.text = f"✔ {o}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_DARK_TEXT

    # =========================================================================
    # SLIDE 8: Resultados em E/S (External Merge Sort)
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_bg(s8, C_LIGHT_BG)
    add_header(s8, "Resultados: Desempenho em E/S (External Merge Sort)")

    # Grafico a esquerda
    io_plot = os.path.join(COMPARISON_DIR, "comparison_io.png")
    if os.path.exists(io_plot):
        s8.shapes.add_picture(io_plot, Inches(0.8), Inches(1.4), width=Inches(6.2))

    # Tabela e Card a direita
    add_card(s8, 7.3, 1.4, 5.2, 5.4)
    tb = s8.shapes.add_textbox(Inches(7.55), Inches(1.6), Inches(4.7), Inches(5.0))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Dados Medidos e Conclusões"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = C_ROSE

    p = tf.add_paragraph()
    p.text = "Arquivo de 64 MB (8.38M inteiros):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEXT
    for env, t, ov, tp in [("Bare-Metal", "1.15 s", "Base", "222 MB/s"), ("Docker", "1.17 s", "+1.5%", "219 MB/s"), ("VirtualBox", "3.05 s", "+164.8%", "84 MB/s")]:
        p = tf.add_paragraph()
        p.text = f"  • {env}: {t}  ({ov} | {tp})"
        p.font.size = Pt(10.5)

    p = tf.add_paragraph()
    p.text = "Arquivo de 128 MB (16.77M inteiros):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = C_DARK_TEXT
    p.space_before = Pt(8)
    for env, t, ov, tp in [("Bare-Metal", "2.33 s", "Base", "220 MB/s"), ("Docker", "2.44 s", "+4.6%", "210 MB/s"), ("VirtualBox", "6.05 s", "+159.5%", "85 MB/s")]:
        p = tf.add_paragraph()
        p.text = f"  • {env}: {t}  ({ov} | {tp})"
        p.font.size = Pt(10.5)

    # Callout box
    p = tf.add_paragraph()
    p.text = "Destaques Técnicos:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_ROSE
    p.space_before = Pt(14)

    obs_io = [
        "Docker opera com overhead baixíssimo (1.5% a 4.6%), preservando o throughput nativo.",
        "A VM sofre sobretaxa drástica (+160%, demora 2.6x mais tempo).",
        "Motivo: a chamada fsync() força a sincronização entre a controladora virtual do VirtualBox e o host."
    ]
    for o in obs_io:
        p = tf.add_paragraph()
        p.text = f"⚠ {o}"
        p.font.size = Pt(10.5)
        p.font.color.rgb = C_DARK_TEXT

    # =========================================================================
    # SLIDE 9: Cards Visuais com Resumo dos Overheads
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_bg(s9, C_WHITE)
    add_header(s9, "Síntese dos Resultados e Análise Comparativa")

    # Banner visual com os dois cards grandes
    stat_img = os.path.join(VISUALS_DIR, "stat_cards.png")
    if os.path.exists(stat_img):
        s9.shapes.add_picture(stat_img, Inches(1.2), Inches(1.4), width=Inches(10.9))

    # Tabela resumo inferior
    add_card(s9, 1.2, 5.0, 10.9, 1.8, bg=C_LIGHT_BG)
    tb = s9.shapes.add_textbox(Inches(1.5), Inches(5.1), Inches(10.3), Inches(1.6))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "Por que existe essa diferença brutal entre CPU e E/S?"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    exps = [
        "CPU: O processador moderno possui modo 'Guest' em hardware (VT-x). As instruções aritméticas rodam direto nos transistores físicos sem tradução de software.",
        "E/S: A escrita em disco na VM depende de interrupções de software, emulação de dispositivo SATA/SCSI e dupla tradução no sistema de arquivos do host."
    ]
    for e in exps:
        p = tf.add_paragraph()
        p.text = f"• {e}"
        p.font.size = Pt(11)
        p.font.color.rgb = C_DARK_TEXT

    # =========================================================================
    # SLIDE 10: Conclusões & Lições Práticas
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_bg(s10, C_LIGHT_BG)
    add_header(s10, "Conclusões e Recomendações Práticas")

    col_w = 3.6
    gap = 0.4
    start_x = 0.8

    # Card 1: Cargas de CPU
    add_card(s10, start_x, 1.5, col_w, 5.2, bg=C_WHITE, border=C_GREEN)
    tb = s10.shapes.add_textbox(Inches(start_x + 0.2), Inches(1.8), Inches(col_w - 0.4), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "1. Cargas de CPU"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_GREEN

    pts1 = [
        "Overhead desprezível (< 1%) em contêineres e máquinas virtuais.",
        "Cálculos matemáticos, renderização, IA e simulações podem ser virtualizados livremente.",
        "A aceleração de hardware moderna neutraliza perdas na ULA."
    ]
    for pt in pts1:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(12)
        p.space_after = Pt(10)

    # Card 2: Cargas de E/S
    add_card(s10, start_x + (col_w + gap), 1.5, col_w, 5.2, bg=C_WHITE, border=C_ROSE)
    tb = s10.shapes.add_textbox(Inches(start_x + (col_w + gap) + 0.2), Inches(1.8), Inches(col_w - 0.4), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "2. Cargas de E/S"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_ROSE

    pts2 = [
        "Docker é o grande vencedor para I/O: preserva mais de 95% do throughput nativo.",
        "VMs tradicionais sofrem perdas severas (> 60% do throughput) quando há chamadas síncronas (fsync).",
        "Aplicações de banco de dados e logs sofrem muito em VMs padrão sem virtio ou raw disk."
    ]
    for pt in pts2:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(12)
        p.space_after = Pt(10)

    # Card 3: Veredito
    add_card(s10, start_x + 2*(col_w + gap), 1.5, col_w, 5.2, bg=C_WHITE, border=C_BLUE)
    tb = s10.shapes.add_textbox(Inches(start_x + 2*(col_w + gap) + 0.2), Inches(1.8), Inches(col_w - 0.4), Inches(4.7))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "3. Veredito da Engenharia"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = C_BLUE

    pts3 = [
        "Contêineres oferecem o melhor equilíbrio entre isolamento ágil e velocidade quase nativa.",
        "Máquinas virtuais continuam essenciais para isolamento de kernel e segurança rigorosa.",
        "Sistemas Operacionais modernos transformaram virtualização de CPU em algo 'gratuito', mas I/O ainda exige cuidado arquitetural."
    ]
    for pt in pts3:
        p = tf.add_paragraph()
        p.text = f"• {pt}"
        p.font.size = Pt(12)
        p.space_after = Pt(10)

    # =========================================================================
    # SLIDE 11: Fechamento / Perguntas
    # =========================================================================
    s11 = prs.slides.add_slide(blank_layout)
    add_bg(s11, C_NAVY_BG)

    tb = s11.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.3), Inches(1.2))
    p = tb.text_frame.paragraphs[0]
    p.text = "Obrigado!"
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = C_WHITE

    p2 = tb.text_frame.add_paragraph()
    p2.text = "Aberto para perguntas e considerações da banca."
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(148, 163, 184)

    # Card Integrantes no fechamento
    add_card(s11, 1.0, 3.0, 11.3, 2.2, bg=C_CARD_DARK, border=RGBColor(51, 65, 85))
    tb = s11.shapes.add_textbox(Inches(1.4), Inches(3.2), Inches(10.5), Inches(1.8))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "Integrantes da Equipe:"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = C_CYAN

    for name, mat in students:
        p = tf.add_paragraph()
        p.text = f"• {name}  —  Matrícula: {mat}"
        p.font.size = Pt(12)
        p.font.color.rgb = C_WHITE

    # Repositorio
    tb = s11.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(0.8))
    p = tb.text_frame.paragraphs[0]
    p.text = "Repositório do Trabalho (Código em C, Scripts e Resultados):"
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(148, 163, 184)
    p2 = tb.text_frame.add_paragraph()
    p2.text = "https://github.com/PatrickMeerssche/Vm-Cont-Bench"
    p2.font.size = Pt(14)
    p2.font.bold = True
    p2.font.color.rgb = C_CYAN

    # Salva o arquivo PPTX
    pptx_path = os.path.join(ENTREGA_DIR, "apresentacao_virtualizacao.pptx")
    prs.save(pptx_path)
    print(f"[*] Apresentação PPTX salva com sucesso em: {pptx_path}")


if __name__ == "__main__":
    create_deck()
