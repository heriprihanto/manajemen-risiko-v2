#!/usr/bin/env bash
# Menjalankan API backend Manajemen Risiko.
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt
fi
exec .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8077
