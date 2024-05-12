FROM python:3

WORKDIR /app

COPY requirements.txt /app

RUN apt-get update && \
    apt-get install -y sqlite3 && \
    pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "library-app.py"]


