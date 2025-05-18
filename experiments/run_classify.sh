#!/bin/bash

## sometimes the script hangs.. so let's try executing a lot of times
for i in $(seq 1 100)
do
  timeout 500 ./classify.py
  mv results.json results/results$i.json
done;

