#!/usr/bin/env bash
# Deleting all log and json files
cd results
rm -rv record/*
rm -rv save/*
rm -rv checkpoints/*
rm -rv rs/*

find . -type f \( -name "*.log" -or -name "*.json" \) -delete

cd ..