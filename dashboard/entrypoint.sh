#!/bin/bash
set -e

function exit_with_error {
    echo "Error: $1"
    exit 1
}

echo "Starting Dashboard ..."
streamlit run app.py --server.port 8501