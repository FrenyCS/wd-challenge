FROM python:3.12.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .
RUN make install

EXPOSE 8000