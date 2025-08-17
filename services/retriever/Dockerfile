FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../../shared ./shared

ENV PYTHONUNBUFFERED=1
ENV SEED_CORPUS_PATH=/seeds/corpus/seeds.json

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]