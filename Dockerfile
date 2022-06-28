FROM python:3
ENV TZ="Europe/Warsaw"

RUN mkdir -p /app/config

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "./src/main.py"]
