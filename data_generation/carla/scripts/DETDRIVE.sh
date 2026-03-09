# !/usr/bin/env bash

# prepare data bucket
mkdir -p data-bucket/


# clean existing results
./scripts/clean_results.sh

# repetitions
for i in $(seq 1)
do
    # Run evaluation in EPIC mode in 20FPS (the default)
    ./scripts/start_detdrive_experiment.sh True 20
    
    # save results to data bucket
    mkdir -p data-bucket/rep$i/
    cp -rv results/* data-bucket/rep$i/

    # clean existing results
    ./scripts/clean_results.sh

done

echo "All done"
