FROM python:3.12.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y make gcc

COPY . .
RUN make install

EXPOSE 8000