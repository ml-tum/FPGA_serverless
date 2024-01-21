#!/bin/bash

find . -maxdepth 1 -iname "*.yml" -exec faas-cli deploy -f "{}" \;
