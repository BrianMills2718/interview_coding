#!/bin/bash
# Test Opus methodology in background

echo "Starting Opus methodology test in background..."
echo "Logs will be written to: test_opus_background.log"

# Activate virtual environment and run Opus
source venv/bin/activate
nohup python scripts/opus/enhanced_analyzer.py --transcript-dir data/processed > test_opus_background.log 2>&1 &

echo $! > test_opus.pid
echo "Opus test started with PID: $(cat test_opus.pid)"
echo "Monitor with: tail -f test_opus_background.log"