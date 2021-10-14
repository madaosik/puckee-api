#!/bin/bash
set -euo pipefail

if ! [ -v DEV_MODE ]; then
  exec python run.py
  exit 0
fi

echo "-- Making sure the database is up-to-date --"
cd app && alembic upgrade head
exec python ../run.py


