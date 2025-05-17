#!/bin/bash

QUERY_PATH="/Users/suyeon/Desktop/Finfusion/query_set_base.json"

python main.py --ticker NKE --query_set $QUERY_PATH --limit 2 >> nike.log 2>&1 &
python main.py --ticker SBUX --query_set $QUERY_PATH --limit 2 >> sbux.log 2>&1 &
python main.py --ticker COST --query_set $QUERY_PATH --limit 2 >> cost.log 2>&1 &
python main.py --ticker V --query_set $QUERY_PATH --limit 2 >> visa.log 2>&1 &
python main.py --ticker UBER --query_set $QUERY_PATH --limit 2 >> uber.log 2>&1 &