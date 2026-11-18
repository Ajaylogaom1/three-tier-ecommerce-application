FROM python:3.9-slim AS builder

WORKDIR /app/backend

COPY requirements.txt .

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config \
    && pip install --no-cache-dir --prefix=/install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

FROM python:3.9-slim

WORKDIR /app/backend

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 5000

CMD ["python3", "app.py"]
