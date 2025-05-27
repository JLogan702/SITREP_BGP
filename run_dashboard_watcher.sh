#!/bin/bash

watchmedo shell-command \
  --patterns="*.csv" \
  --recursive \
  --command='bash scripts/rebuild_and_push.sh' \
  data/
