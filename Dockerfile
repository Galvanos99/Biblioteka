FROM python:3

WORKDIR /app

COPY . /app

RUN pip install sqlalchemy   # Instaluje sqlalchemy, jeśli jest potrzebny
RUN apt-get update && \
    apt-get install -y sqlite3  #Do przeglądania bazy danych
RUN pip install bcrypt #Do hahowania haseł
# Dodaj kolejne polecenia `pip install`, aby zainstalować inne potrzebne pakiety

CMD ["python", "library-app.py"]

