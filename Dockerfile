FROM python:3.12.9-slim

COPY . /
RUN apt-get update && apt-get install -y make
RUN make install

WORKDIR /app
EXPOSE 8080
CMD ["main.py"]
ENTRYPOINT [ "python" ]
