# !/usr/bin/env bash


# Remove old data bucket if it exists
rm -r data-bucket/

# prepare data bucket
mkdir -p data-bucket/


# clean existing results
./scripts/clean_results.sh

# do repetitions
for i in $(seq 0 9)
do
    # Run evaluation in EPIC mode in 20FPS (the default)
    ./scripts/start_dtdrive_experiment.sh True 20 "$@"
    
    # save results to data bucket
    mkdir -p data-bucket/rep$i/
    cp -rv results/* data-bucket/rep$i/

    # clean existing results
    ./scripts/clean_results.sh
    
    
done

echo "All done"
