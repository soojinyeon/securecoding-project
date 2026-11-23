FROM python:3.11-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends iputils-ping \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV CAMPUSHUB_DB=/app/data/campushub.db
ENV CAMPUSHUB_UPLOADS=/app/uploads
ENV CAMPUSHUB_HOST=0.0.0.0
ENV CAMPUSHUB_PORT=5000
ENV CAMPUSHUB_DEBUG=1

RUN mkdir -p /app/data /app/uploads

CMD ["sh", "-c", "python seed.py --reset && python app.py"]

EXPOSE 5000
