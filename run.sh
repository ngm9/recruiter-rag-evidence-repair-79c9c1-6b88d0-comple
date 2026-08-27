#!/usr/bin/env bash
set -e

cd /root/task

echo "Installing Python dependencies..."
python3 -m pip install -q -r /root/task/requirements.txt

echo "Starting pgvector datastore..."
docker compose -f /root/task/docker-compose.yml up -d

export DATABASE_URL="postgresql://raguser:ragpass@localhost:5432/ragdb"

echo "Waiting for PostgreSQL and pgvector extension..."
for i in $(seq 1 60); do
  if docker compose -f /root/task/docker-compose.yml exec -T db pg_isready -U raguser -d ragdb >/dev/null 2>&1; then
    if docker compose -f /root/task/docker-compose.yml exec -T db psql -U raguser -d ragdb -tAc "SELECT 1 FROM pg_extension WHERE extname='vector'" | grep -q 1; then
      break
    fi
  fi
  if [ "$i" -eq 60 ]; then
    echo "Database did not become ready with pgvector enabled."
    exit 1
  fi
  sleep 1
done

echo "Validating starter schema..."
docker compose -f /root/task/docker-compose.yml exec -T db psql -U raguser -d ragdb -tAc "SELECT to_regclass('public.source_documents'), to_regclass('public.document_chunks')" | grep -q source_documents

echo "Checking Python package imports..."
python3 -m compileall -q /root/task/app
python3 -c "import app; import app.config; import app.retrieval; import app.generation"

echo "Readiness check complete. The invariant tests are available but are not run by this script."
