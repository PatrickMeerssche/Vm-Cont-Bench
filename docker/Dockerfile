FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3 \
    python3-matplotlib \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia estrutura do benchmark
COPY Makefile /app/
COPY src/ /app/src/
COPY scripts/ /app/scripts/

RUN make clean && make

ENTRYPOINT ["python3", "scripts/run_benchmark.py", "--env", "docker"]
