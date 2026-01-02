#!/bin/bash
# Wrapper script to run uvicorn with venv activated
PROJECT_DIR="/Users/ayushanand/Developer/insta-automation"
cd "$PROJECT_DIR"
source venv/bin/activate
exec uvicorn "$@"

