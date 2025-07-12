#!/bin/bash
# Test Sonnet methodology with multi-model fix in background

echo "Starting Sonnet methodology test in background..."
echo "Logs will be written to: test_sonnet_background.log"

# Activate virtual environment and run Sonnet
source venv/bin/activate
nohup python scripts/sonnet/run_sonnet_analysis.py --transcript-dir data/processed > test_sonnet_background.log 2>&1 &

echo $! > test_sonnet.pid
echo "Sonnet test started with PID: $(cat test_sonnet.pid)"
echo "Monitor with: tail -f test_sonnet_background.log"