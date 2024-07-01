#!/bin/bash

for i in {1..64}; do
  ./ukvm-bin test_serverless.ukvm &
done

