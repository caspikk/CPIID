#!/bin/bash

mkdir -p /app/backend/frontend
cp -r /app/frontend_dist/* /app/backend/frontend/

uvicorn backend.main:app --host 0.0.0.0 --port 8000