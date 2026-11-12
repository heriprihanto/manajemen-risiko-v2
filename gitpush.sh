#!/bin/bash

set -e

if [ $# -eq 0 ]; then
    echo "Usage: $0 \"nama commit\""
    exit 1
fi

git add .
git commit -m "$*"
git push origin main

echo "✓ Commit dan push berhasil!"
