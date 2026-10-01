#!/bin/sh
set -e

echo "Garantindo que o schema do banco exista..."
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

echo "Injetando seeds de dados..."
python -m app.db.seed

echo "Migrations e Seeds finalizados com sucesso!"
