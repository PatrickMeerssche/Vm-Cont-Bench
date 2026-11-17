CC = gcc
CFLAGS = -O3 -Wall -Wextra -std=c11
LDFLAGS = -lm

SRC_DIR = src
BIN_DIR = bin

TARGETS = $(BIN_DIR)/cpu_mandelbrot $(BIN_DIR)/io_external_sort

all: $(BIN_DIR) $(TARGETS)

$(BIN_DIR):
	mkdir -p $(BIN_DIR)

$(BIN_DIR)/cpu_mandelbrot: $(SRC_DIR)/cpu_mandelbrot.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

$(BIN_DIR)/io_external_sort: $(SRC_DIR)/io_external_sort.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -rf $(BIN_DIR)/* tmp_io data_tmp *.o

.PHONY: all clean
