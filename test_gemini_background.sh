#!/bin/bash
# Test Gemini methodology with serialization fix in background

echo "Starting Gemini methodology test in background..."
echo "Logs will be written to: test_gemini_background.log"

# Activate virtual environment and run Gemini
source venv/bin/activate
nohup python scripts/gemini25/main.py --transcript-dir data/processed > test_gemini_background.log 2>&1 &

echo $! > test_gemini.pid
echo "Gemini test started with PID: $(cat test_gemini.pid)"
echo "Monitor with: tail -f test_gemini_background.log"