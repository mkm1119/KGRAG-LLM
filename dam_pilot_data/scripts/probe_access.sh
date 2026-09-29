#!/bin/bash
# Access probe: records HTTP status, size, time for each official source host
OUT=${1:-04_reports/access_probe.tsv}
echo -e "retrieval_time_utc\tsource\turl\thttp_code\tbytes\ttime_s\tcontent_type\terror" > $OUT
probe(){ name="$1"; url="$2"
  t=$(date -u +%FT%TZ)
  r=$(curl -sS -L -m 30 -o /tmp/probe_body -w "%{http_code}\t%{size_download}\t%{time_total}\t%{content_type}" "$url" 2>/tmp/probe_err) 
  e=$(tr '\n' ' ' </tmp/probe_err | cut -c1-150)
  echo -e "$t\t$name\t$url\t$r\t$e" >> $OUT
}
probe WAMIS_main "http://www.wamis.go.kr/"
probe WAMIS_https "https://www.wamis.go.kr/"
probe WAMIS_dam_info "http://www.wamis.go.kr/ENG/Main.aspx"
probe HRFCO_main "https://www.hrfco.go.kr/"
probe HRFCO_api "https://api.hrfco.go.kr/"
probe HRFCO_dam_page "https://www.hrfco.go.kr/web/sample/damsummary.do"
probe DATAGO_main "https://www.data.go.kr/"
probe DATAGO_apis "https://apis.data.go.kr/"
probe KHNP_main "https://www.khnp.co.kr/"
probe KHNP_hydro "https://www.khnp.co.kr/main/contents.do?key=1189"
probe KWATER_main "https://www.kwater.or.kr/"
probe MYWATER "https://www.water.or.kr/"
probe MYWATER_alt "https://www.water.or.kr/main/main.do"
probe KMA_main "https://www.kma.go.kr/"
probe KMA_data "https://data.kma.go.kr/"
probe KMA_apihub "https://apihub.kma.go.kr/"
probe LAW_main "https://www.law.go.kr/"
probe LAW_open "https://open.law.go.kr/"
probe LAW_api "http://www.law.go.kr/DRF/lawSearch.do?OC=test&target=law&type=XML&query=%EB%8C%90"
probe ME_main "https://www.me.go.kr/"
probe HANGANG_flood "https://www.hrfco.go.kr/web/main/main.do"
probe GOOGLE_control "https://www.google.com/"
