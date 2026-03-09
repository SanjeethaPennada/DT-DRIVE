# !/usr/bin/env bash

# prepare data bucket
mkdir -p data-bucket/


# clean existing results
./scripts/clean_results.sh

# repetitions
for i in $(seq 0 5)
do
    export REP=$i

    ./scripts/start_detdrive_experiment.sh True 20

    # Skip saving the warm-up i.e., 1st repetition
    if [ "$i" -gt 0 ]; then
        mkdir -p data-bucket/rep$((i-1))/
        cp -rv results/* data-bucket/rep$((i-1))/
    fi

    ./scripts/clean_results.sh
done

echo "All done"
