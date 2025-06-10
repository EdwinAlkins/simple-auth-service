FROM python:3.12-slim AS builder

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY auth_service/ auth_service/

EXPOSE 443

CMD ["python", "-m", "auth_service", "--prod"]

# docker build -t auth_service -f dockers/Dockerfile .
# docker run -p 443:443 -v ./certs:/app/certs -v ./config.toml:/app/config.toml -v ./data:/app/data -e SECRET_KEY=$SECRET_KEY -e AUTH_SERVICE_CONFIG=/app/config.toml -e DATABASE_PATH=/app/data/auth.db -e KEYFILE=/app/certs/key.pem -e CERTFILE=/app/certs/cert.pem auth_service
