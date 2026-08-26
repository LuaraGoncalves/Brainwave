#!/bin/sh
set -e

echo "Limpando migrations antigas..."
rm -rf /app/alembic/versions/*

echo "Gerando nova migration inicial..."
alembic revision --autogenerate -m "init"

echo "Aplicando migrations..."
alembic upgrade head

echo "Injetando seeds de dados..."
python -m app.db.seed

echo "Migrations e Seeds finalizados com sucesso!"
