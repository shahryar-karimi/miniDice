#!/bin/bash
set -e

function exit_with_error {
    echo "Error: $1"
    exit 1
}

echo "Starting telegram bot server..."
python telegram_bot_run.py