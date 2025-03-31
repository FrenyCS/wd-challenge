FROM python:3.12.9-slim

WORKDIR /app
RUN apt-get update && apt-get install -y curl make gcc python3

ENV POETRY_VERSION=1.8.2
ENV PATH="/root/.local/bin:$PATH"
RUN curl -sSL https://install.python-poetry.org | python3 -

COPY . .
RUN make install

EXPOSE 8000