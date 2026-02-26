#!/bin/bash

# Start FastAPI backend on a fixed internal port
echo "🚀 Starting FastAPI Backend..."
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend on Render's $PORT (defaults to 8501 locally)
echo "🚢 Starting Streamlit Frontend..."
streamlit run app.py --server.port ${PORT:-8501} --server.address 0.0.0.0
