#!/bin/bash
cd "$(dirname "$0")/.."
while pgrep -f run_kwater_all.sh >/dev/null; do sleep 20; done
python3 scripts/fetch_kwater_station.py hydr rain hydr_flood10
