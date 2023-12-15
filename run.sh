#!/bin/bash

# Number of times to run the Python script
TOTAL_SAMPLES=618
CHUNK_SIZE=50
NUM_RUNS=$(( (TOTAL_SAMPLES + CHUNK_SIZE - 1) / CHUNK_SIZE ))

echo "Total samples: $TOTAL_SAMPLES"
echo "Chunk size: $CHUNK_SIZE"
echo "Number of runs: $NUM_RUNS"

output=logs
# Path to your Python script
PYTHON_SCRIPT="run.py"

for ((i=3; i<=$NUM_RUNS; i++)); do
    echo "Running Python script, iteration $i"
    python3 "$PYTHON_SCRIPT" --chunk_index=$i --chunk_size=$CHUNK_SIZE &> ${output}/log_chunk_size_${CHUNK_SIZE}_chunk_${i}.txt
    
    if [ $i -lt $NUM_RUNS ]; then
        echo "Waiting for 3 hours before the next run..."
        sleep 10000
    else
        echo "All runs completed."
    fi
done

# TODO:
# run 0th batch, chunk has only ~33 completed
# parse results from text log
