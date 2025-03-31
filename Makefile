install:
	poetry lock && poetry install --no-root

format:
	poetry run isort app tests && \
	poetry run black app tests

lint:
	poetry run pylint --disable=R,C -v app/*.py app/**/*.py tests/*.py tests/**/*.py

test:
	poetry run pytest -vv --cov=app tests/unit/*.py

build:
	docker build -t deploy-fastapi .

run:
	docker run -p 127.0.0.1:8080:8080 deploy-fastapi

all: install format lint test build run