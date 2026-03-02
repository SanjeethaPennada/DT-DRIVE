# !/usr/bin/env bash
conda create --name metadrive --file ./metadrive.txt

conda activate metadrive

python run_flaky_check.py
echo "All done!"