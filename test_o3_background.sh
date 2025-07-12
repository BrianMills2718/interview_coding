#!/bin/bash
# Test O3 methodology with optimizations in background

echo "Starting O3 methodology test in background..."
echo "Logs will be written to: test_o3_background.log"

# Activate virtual environment and run O3
source venv/bin/activate
nohup bash -c "
cd scripts/o3
echo 'Testing O3 with batch processing...'
echo 'Running deductive analysis...'
python deductive_runner.py --transcript-dir ../../data/processed
echo 'Running inductive analysis...'
python inductive_runner.py --transcript-dir ../../data/processed
echo 'O3 test complete'
" > test_o3_background.log 2>&1 &

echo $! > test_o3.pid
echo "O3 test started with PID: $(cat test_o3.pid)"
echo "Monitor with: tail -f test_o3_background.log"