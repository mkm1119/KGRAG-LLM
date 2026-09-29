# Raw archive (MyWater bulk JSON)
원본 JSON(수정 없음)을 45MB 단위로 분할 압축. 복원:
```
cat mywater_period.tar.gz.part_* | tar xz    # -> 01_raw/KWater/mywater_period/...
cat mywater_station.tar.gz.part_* | tar xz   # -> 01_raw/KWater/mywater_station/...
```
파일별 sha256/크기/요청 파라미터: ../02_metadata/mywater_fetch_manifest.csv, mywater_station_fetch_manifest.csv, FINAL_MANIFEST.csv
