FROM python:3
ENV TZ="Europe/Warsaw"

RUN mkdir -p /mqtt-to-graphite/config

WORKDIR /mqtt-to-graphite

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main/main.py"]
