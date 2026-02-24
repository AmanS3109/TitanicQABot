#!/bin/bash

# Start FastAPI backend in the background
echo "🚀 Starting FastAPI Backend..."
uvicorn backend:app --host 0.0.0.0 --port 8000 &

# Start Streamlit frontend
echo "🚢 Starting Streamlit Frontend..."
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
