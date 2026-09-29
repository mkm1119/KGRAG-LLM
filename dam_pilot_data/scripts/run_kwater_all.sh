#!/bin/bash
cd "$(dirname "$0")/.."
END=2026-09-28
# daily, all three groups
for g in 1 2 3; do python3 scripts/fetch_kwater_mywater.py D1 $g 2021-01-01 $END; done
# hourly, all three groups
for g in 1 2 3; do python3 scripts/fetch_kwater_mywater.py H1 $g 2021-01-01 $END; done
# 10-minute: flood season (6/21-9/30) each year, group 1 (multipurpose dams)
for y in 2021 2022 2023 2024 2025; do python3 scripts/fetch_kwater_mywater.py M1 1 $y-06-21 $y-09-30; done
