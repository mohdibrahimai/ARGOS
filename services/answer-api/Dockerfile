FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../../shared ./shared
COPY ../../eval ./eval

ENV PYTHONUNBUFFERED=1
ENV RETRIEVER_URL=http://retriever:8001/v1/search
ENV VERIFIER_URL=http://verifier:8002/v1/verify

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]