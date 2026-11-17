#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
#include <sys/resource.h>
#include <sys/time.h>
#include <string.h>

/*
 * Benchmark CPU-bound: Cálculo do Fractal de Mandelbrot
 * 
 * Executa computação matemática pura em ponto flutuante (ULA e registradores).
 * Quase zero acesso a disco durante o processamento.
 *
 * Parâmetros de entrada:
 *   argv[1]: largura (width) [padrão: 4000]
 *   argv[2]: altura (height) [padrão: 4000]
 *   argv[3]: max_iter        [padrão: 1000]
 */

static double get_time_sec(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec * 1e-9;
}

int main(int argc, char *argv[]) {
    int width = (argc > 1) ? atoi(argv[1]) : 4000;
    int height = (argc > 2) ? atoi(argv[2]) : 4000;
    int max_iter = (argc > 3) ? atoi(argv[3]) : 1000;

    if (width <= 0 || height <= 0 || max_iter <= 0) {
        fprintf(stderr, "Uso: %s [largura] [altura] [max_iter]\n", argv[0]);
        return 1;
    }

    const double xmin = -2.0;
    const double xmax = 0.5;
    const double ymin = -1.25;
    const double ymax = 1.25;

    double dx = (xmax - xmin) / (double)width;
    double dy = (ymax - ymin) / (double)height;

    struct rusage ru_start, ru_end;
    getrusage(RUSAGE_SELF, &ru_start);
    double t_start = get_time_sec();

    uint64_t total_iterations = 0;
    uint64_t checksum = 0;

    for (int j = 0; j < height; j++) {
        double ci = ymin + j * dy;
        for (int i = 0; i < width; i++) {
            double cr = xmin + i * dx;
            double zr = 0.0;
            double zi = 0.0;
            int iter = 0;

            while (zr * zr + zi * zi <= 4.0 && iter < max_iter) {
                double temp = zr * zr - zi * zi + cr;
                zi = 2.0 * zr * zi + ci;
                zr = temp;
                iter++;
            }

            total_iterations += iter;
            checksum = checksum * 33 + iter;
        }
    }

    double t_end = get_time_sec();
    getrusage(RUSAGE_SELF, &ru_end);

    double wall_time = t_end - t_start;
    double user_cpu = (ru_end.ru_utime.tv_sec - ru_start.ru_utime.tv_sec) +
                      (ru_end.ru_utime.tv_usec - ru_start.ru_utime.tv_usec) * 1e-6;
    double sys_cpu  = (ru_end.ru_stime.tv_sec - ru_start.ru_stime.tv_sec) +
                      (ru_end.ru_stime.tv_usec - ru_start.ru_stime.tv_usec) * 1e-6;

    double mflops_proxy = (total_iterations * 6.0) / (wall_time * 1e6); // ~6 ops aritméticas por iteração

    printf("=== RESULTADO CPU (Mandelbrot) ===\n");
    printf("Resolucao: %dx%d (Total de pixels: %ld)\n", width, height, (long)width * height);
    printf("Max iteracoes: %d\n", max_iter);
    printf("Iteracoes computadas: %lu\n", total_iterations);
    printf("Checksum de validacao: 0x%016lx\n", checksum);
    printf("Wall clock time: %.6f s\n", wall_time);
    printf("User CPU time:   %.6f s\n", user_cpu);
    printf("System CPU time: %.6f s\n", sys_cpu);
    printf("MFLOPS aprox.:   %.2f\n", mflops_proxy);
    printf("JSON_OUTPUT: {\"benchmark\": \"mandelbrot\", \"width\": %d, \"height\": %d, \"max_iter\": %d, \"wall_time\": %.6f, \"user_time\": %.6f, \"sys_time\": %.6f, \"total_iterations\": %lu, \"checksum\": \"%016lx\"}\n",
           width, height, max_iter, wall_time, user_cpu, sys_cpu, total_iterations, checksum);

    return 0;
}
