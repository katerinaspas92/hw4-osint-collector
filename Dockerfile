FROM python:3.14-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY api.py database.py collector.py ./

RUN mkdir -p /data && ln -s /data/osint_data.db /app/osint_data.db

CMD ["python", "collector.py"]
