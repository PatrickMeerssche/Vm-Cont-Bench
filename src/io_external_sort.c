#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/resource.h>

/*
 * Benchmark I/O-bound: External Merge Sort
 * 
 * Ordena um arquivo de inteiros de 64 bits utilizando memória RAM limitada,
 * forçando constante leitura, divisão em blocos, escrita de arquivos temporários,
 * k-way merge e sincronização em disco (fsync).
 *
 * Parâmetros:
 *   argv[1]: tamanho total dos dados em MB (ex: 128, 256, 512, 1024)
 *   argv[2]: tamanho do bloco em RAM em MB (ex: 16)
 *   argv[3]: diretório de trabalho/temporários [padrão: ./tmp_io]
 *   argv[4]: usar_fsync (1 = sim, 0 = não) [padrão: 1]
 */

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

static int compare_uint64(const void *a, const void *b) {
    uint64_t va = *(const uint64_t *)a;
    uint64_t vb = *(const uint64_t *)b;
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
}

// Estrutura para o Min-Heap do K-way Merge
typedef struct {
    uint64_t value;
    int chunk_index;
} HeapNode;

static void heapify(HeapNode *heap, int n, int i) {
    int smallest = i;
    int left = 2 * i + 1;
    int right = 2 * i + 2;

    if (left < n && heap[left].value < heap[smallest].value)
        smallest = left;
    if (right < n && heap[right].value < heap[smallest].value)
        smallest = right;

    if (smallest != i) {
        HeapNode temp = heap[i];
        heap[i] = heap[smallest];
        heap[smallest] = temp;
        heapify(heap, n, smallest);
    }
}

// Pseudo-gerador rápido de números pseudo-aleatórios (Xorshift64)
static inline uint64_t xorshift64(uint64_t *state) {
    uint64_t x = *state;
    x ^= x << 13;
    x ^= x >> 7;
    x ^= x << 17;
    return *state = x;
}

int main(int argc, char *argv[]) {
    int total_mb = (argc > 1) ? atoi(argv[1]) : 128;
    int chunk_mb = (argc > 2) ? atoi(argv[2]) : 16;
    const char *work_dir = (argc > 3) ? argv[3] : "./tmp_io";
    int do_fsync = (argc > 4) ? atoi(argv[4]) : 1;

    if (total_mb <= 0 || chunk_mb <= 0 || chunk_mb > total_mb) {
        fprintf(stderr, "Uso: %s [total_mb] [chunk_mb] [dir_tmp] [do_fsync]\n", argv[0]);
        return 1;
    }

    mkdir(work_dir, 0777);

    size_t total_elements = (size_t)total_mb * (1024 * 1024 / sizeof(uint64_t));
    size_t chunk_elements = (size_t)chunk_mb * (1024 * 1024 / sizeof(uint64_t));
    int num_chunks = (total_elements + chunk_elements - 1) / chunk_elements;

    char input_path[512], output_path[512];
    snprintf(input_path, sizeof(input_path), "%s/input.bin", work_dir);
    snprintf(output_path, sizeof(output_path), "%s/output_sorted.bin", work_dir);

    printf("=== CONFIGURACAO I/O (External Merge Sort) ===\n");
    printf("Tamanho total: %d MB (%lu inteiros uint64)\n", total_mb, total_elements);
    printf("Tamanho do bloco em RAM: %d MB (%lu inteiros uint64)\n", chunk_mb, chunk_elements);
    printf("Numero de blocos (chunks): %d\n", num_chunks);
    printf("Diretorio temporario: %s\n", work_dir);
    printf("Sincronizacao fsync: %s\n", do_fsync ? "ATIVADA" : "DESATIVADA");

    struct rusage ru_start, ru_end;
    getrusage(RUSAGE_SELF, &ru_start);
    double t_total_start = get_time_sec();

    // -------------------------------------------------------------
    // ETAPA 1: Geracao do arquivo inicial em disco
    // -------------------------------------------------------------
    double t0 = get_time_sec();
    FILE *f_in = fopen(input_path, "wb");
    if (!f_in) {
        perror("Erro ao criar input.bin");
        return 1;
    }

    uint64_t *gen_buffer = malloc(chunk_elements * sizeof(uint64_t));
    if (!gen_buffer) {
        fprintf(stderr, "Falha ao alocar buffer de geracao!\n");
        return 1;
    }

    uint64_t rng_state = 0xdeadbeef12345678ULL;
    size_t remaining = total_elements;
    while (remaining > 0) {
        size_t to_write = (remaining > chunk_elements) ? chunk_elements : remaining;
        for (size_t i = 0; i < to_write; i++) {
            gen_buffer[i] = xorshift64(&rng_state);
        }
        if (fwrite(gen_buffer, sizeof(uint64_t), to_write, f_in) != to_write) {
            perror("Erro ao escrever no input.bin");
            return 1;
        }
        remaining -= to_write;
    }
    fflush(f_in);
    if (do_fsync) fsync(fileno(f_in));
    fclose(f_in);
    free(gen_buffer);
    double t_gen = get_time_sec() - t0;

    // -------------------------------------------------------------
    // ETAPA 2: Fase de Divisao e Ordenacao dos Chunks (Pass 1)
    // -------------------------------------------------------------
    double t_phase1_start = get_time_sec();
    f_in = fopen(input_path, "rb");
    if (!f_in) {
        perror("Erro ao abrir input.bin para leitura");
        return 1;
    }

    uint64_t *chunk_buffer = malloc(chunk_elements * sizeof(uint64_t));
    if (!chunk_buffer) {
        fprintf(stderr, "Falha ao alocar chunk_buffer!\n");
        return 1;
    }

    for (int c = 0; c < num_chunks; c++) {
        size_t count = fread(chunk_buffer, sizeof(uint64_t), chunk_elements, f_in);
        if (count == 0) break;

        qsort(chunk_buffer, count, sizeof(uint64_t), compare_uint64);

        char chunk_path[512];
        snprintf(chunk_path, sizeof(chunk_path), "%s/chunk_%04d.tmp", work_dir, c);
        FILE *f_chunk = fopen(chunk_path, "wb");
        if (!f_chunk) {
            perror("Erro ao criar arquivo de chunk");
            return 1;
        }
        if (fwrite(chunk_buffer, sizeof(uint64_t), count, f_chunk) != count) {
            perror("Erro ao escrever chunk");
            return 1;
        }
        fflush(f_chunk);
        if (do_fsync) fsync(fileno(f_chunk));
        fclose(f_chunk);
    }
    fclose(f_in);
    free(chunk_buffer);
    double t_phase1 = get_time_sec() - t_phase1_start;

    // -------------------------------------------------------------
    // ETAPA 3: K-Way Merge dos Chunks (Pass 2)
    // -------------------------------------------------------------
    double t_phase2_start = get_time_sec();
    FILE **chunk_files = malloc(num_chunks * sizeof(FILE *));
    HeapNode *heap = malloc(num_chunks * sizeof(HeapNode));
    int active_chunks = 0;

    for (int c = 0; c < num_chunks; c++) {
        char chunk_path[512];
        snprintf(chunk_path, sizeof(chunk_path), "%s/chunk_%04d.tmp", work_dir, c);
        chunk_files[c] = fopen(chunk_path, "rb");
        if (!chunk_files[c]) {
            perror("Erro ao abrir chunk para merge");
            return 1;
        }
        uint64_t val;
        if (fread(&val, sizeof(uint64_t), 1, chunk_files[c]) == 1) {
            heap[active_chunks].value = val;
            heap[active_chunks].chunk_index = c;
            active_chunks++;
        }
    }

    // Constroi min-heap inicial
    for (int i = (active_chunks - 1) / 2; i >= 0; i--) {
        heapify(heap, active_chunks, i);
    }

    FILE *f_out = fopen(output_path, "wb");
    if (!f_out) {
        perror("Erro ao criar output_sorted.bin");
        return 1;
    }

    const size_t out_buf_size = 65536; // buffer de escrita para o arquivo final (512 KB)
    uint64_t *out_buffer = malloc(out_buf_size * sizeof(uint64_t));
    size_t out_pos = 0;

    while (active_chunks > 0) {
        HeapNode root = heap[0];
        out_buffer[out_pos++] = root.value;
        if (out_pos == out_buf_size) {
            if (fwrite(out_buffer, sizeof(uint64_t), out_pos, f_out) != out_pos) {
                perror("Erro na escrita do merge");
                return 1;
            }
            out_pos = 0;
        }

        int c = root.chunk_index;
        uint64_t next_val;
        if (fread(&next_val, sizeof(uint64_t), 1, chunk_files[c]) == 1) {
            heap[0].value = next_val;
            heap[0].chunk_index = c;
        } else {
            heap[0] = heap[active_chunks - 1];
            active_chunks--;
        }
        if (active_chunks > 0) {
            heapify(heap, active_chunks, 0);
        }
    }

    if (out_pos > 0) {
        if (fwrite(out_buffer, sizeof(uint64_t), out_pos, f_out) != out_pos) {
            perror("Erro no flush final do output");
            return 1;
        }
    }
    fflush(f_out);
    if (do_fsync) fsync(fileno(f_out));
    fclose(f_out);

    // Fecha e remove chunks temporarios
    for (int c = 0; c < num_chunks; c++) {
        fclose(chunk_files[c]);
        char chunk_path[512];
        snprintf(chunk_path, sizeof(chunk_path), "%s/chunk_%04d.tmp", work_dir, c);
        unlink(chunk_path);
    }
    free(chunk_files);
    free(heap);
    free(out_buffer);
    double t_phase2 = get_time_sec() - t_phase2_start;

    // -------------------------------------------------------------
    // ETAPA 4: Validacao da ordenacao
    // -------------------------------------------------------------
    f_out = fopen(output_path, "rb");
    int sorted_ok = 1;
    if (f_out) {
        uint64_t prev = 0, curr;
        if (fread(&prev, sizeof(uint64_t), 1, f_out) == 1) {
            while (fread(&curr, sizeof(uint64_t), 1, f_out) == 1) {
                if (curr < prev) {
                    sorted_ok = 0;
                    break;
                }
                prev = curr;
            }
        }
        fclose(f_out);
    }
    // Remove arquivos para liberar espaco
    unlink(input_path);
    unlink(output_path);

    double t_total = get_time_sec() - t_total_start;
    getrusage(RUSAGE_SELF, &ru_end);

    double user_cpu = (ru_end.ru_utime.tv_sec - ru_start.ru_utime.tv_sec) +
                      (ru_end.ru_utime.tv_usec - ru_start.ru_utime.tv_usec) * 1e-6;
    double sys_cpu  = (ru_end.ru_stime.tv_sec - ru_start.ru_stime.tv_sec) +
                      (ru_end.ru_stime.tv_usec - ru_start.ru_stime.tv_usec) * 1e-6;

    double total_io_mb = (double)total_mb * 4.0; // write input + read input + write chunks + read chunks + write output
    double io_throughput = total_io_mb / (t_phase1 + t_phase2);

    printf("\n=== RESULTADOS I/O (External Merge Sort) ===\n");
    printf("Status de validacao:     %s\n", sorted_ok ? "SUCESSO (Ordenado corretamente)" : "FALHA");
    printf("Tempo geracao input:     %.4f s\n", t_gen);
    printf("Tempo Fase 1 (Split):    %.4f s\n", t_phase1);
    printf("Tempo Fase 2 (Merge):    %.4f s\n", t_phase2);
    printf("Tempo Ordenacao (1+2):   %.4f s\n", t_phase1 + t_phase2);
    printf("Tempo Total (c/ geracao):%.4f s\n", t_total);
    printf("User CPU time:           %.4f s\n", user_cpu);
    printf("System CPU time:         %.4f s (alto devido a syscalls de I/O)\n", sys_cpu);
    printf("Throughput efetivo I/O:  %.2f MB/s\n", io_throughput);
    printf("JSON_OUTPUT: {\"benchmark\": \"external_sort\", \"total_mb\": %d, \"chunk_mb\": %d, \"do_fsync\": %d, \"gen_time\": %.6f, \"phase1_time\": %.6f, \"phase2_time\": %.6f, \"sort_time\": %.6f, \"total_time\": %.6f, \"user_time\": %.6f, \"sys_time\": %.6f, \"sorted_ok\": %d, \"throughput_mb_s\": %.2f}\n",
           total_mb, chunk_mb, do_fsync, t_gen, t_phase1, t_phase2, t_phase1 + t_phase2, t_total, user_cpu, sys_cpu, sorted_ok, io_throughput);

    return sorted_ok ? 0 : 1;
}
