install:
	python -m pip install --upgrade pip &&\
		pip install -r requirements.txt
format:
	black ./**/*.py app/*.py tests/*.py
lint:
	pylint --disable=R,C app/*.py tests/*.py
test:
	#python -m pytest -vv --cov=app tests/*.py
build:
	docker build -t deploy-fastapi .
run:
	docker run -p 127.0.0.1:8080:8080 deploy-fastapi
all: install format lint test build run
