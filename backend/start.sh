# #!/bin/sh
# set -e

# echo "Checking Pokemon database..."

# python -c "from app.catalog import count; exit(0 if count() > 0 else 1)" || {
#     echo "Downloading Pokemon database..."
#     python sync_catalog.py --languages en ja
# }

# echo "Starting DeckFlow..."
# exec uvicorn app.main:app --host 0.0.0.0 --port 8000
