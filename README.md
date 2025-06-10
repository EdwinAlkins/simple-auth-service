# Backend

## Description

This is the backend for the Stripe use demo.

## Installation

```bash
pip install .[dev]
```

## Generate SECRET_KEY for the .env file

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Run with docker

```bash
docker compose up --build
```

## Import env variables

```bash
source .env
# or
export $(grep -v '^\s*#' .env | xargs -d '\n')
```

### Get env variables names
```bash
grep -v '^\s*#' .env | grep -E '^\s*[A-Za-z0-9_]+=.*' | sed -E 's/^\s*([A-Za-z0-9_]+)=.*/\1/'
```
Explication :
- `^\s*` : To ignore the spaces at the beginning of the line
- `([A-Za-z0-9_]+)` : To capture the first word composed of letters, numbers or _ (standard env variable name)
- `=.*` : To capture everything after the =
- `\1` : To keep only the name of the variable

### Unset env variables
```bash
unset $(grep -v '^\s*#' .env | grep -E '^\s*[A-Za-z0-9_]+=.*' | sed -E 's/^\s*([A-Za-z0-9_]+)=.*/\1/')
```

## Run

```bash
python -m auth_service
```

```bash
authapi
```

## Format code

```bash
black .
```

## Certificat

```bash
mkdir -p certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/key.pem -out certs/cert.pem -subj "/CD=localhost"
```
