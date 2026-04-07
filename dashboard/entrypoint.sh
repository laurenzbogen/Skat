#!/bin/sh
echo "Waiting for Grist API to be ready..."
until curl -sf http://grist:8484/api/docs > /dev/null 2>&1; do
  echo "Grist not ready yet, retrying in 2s..."
  sleep 2
done
echo "Grist is ready, starting dashboard..."
exec python chart.py
