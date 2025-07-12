#!/bin/bash
# Run the full analysis pipeline in the background

echo "Starting analysis pipeline in background..."
echo "Logs will be written to: background_analysis.log"
echo "PID will be saved to: analysis.pid"

# Activate virtual environment and run the pipeline
source venv/bin/activate
nohup python scripts/run_all_methodologies.py > background_analysis.log 2>&1 &

# Save the PID
echo $! > analysis.pid

echo "Analysis started with PID: $(cat analysis.pid)"
echo "To check status: tail -f background_analysis.log"
echo "To check if still running: ps -p $(cat analysis.pid)"
echo "To stop: kill $(cat analysis.pid)"