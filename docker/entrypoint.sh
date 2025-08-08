#!/bin/bash
set -e

if [ -z "$OPENAI_API_KEY" ]; then
  echo "ERROR: OPENAI_API_KEY is not set. Configure it in .env or environment." >&2
  exit 1
fi

export PYTHONPATH=/app:$PYTHONPATH

exec python main.py "$@"
