# !/usr/bin/env bash

# prepare data bucket
mkdir -p recordings/

# Benchmarking for RQ1-2

# clean existing results
./scripts/clean_results.sh

# do repetitions
for i in $(seq 1)
do
    # Run evaluation in EPIC mode in 20FPS (the default)
    ./scripts/start_recording.sh True 20
    
    # save results to data bucket
    mkdir -p recordings/rep$i/
    cp -rv results/* recordings/rep$i/

    # clean existing results
    ./scripts/clean_results.sh

done

echo "All done"
