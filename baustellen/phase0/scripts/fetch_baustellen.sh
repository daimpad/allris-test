#!/bin/sh
# Abruf mit Wiederholung (Dienst antwortet sporadisch mit 400 {}); Ablage mit Zeitstempel
OUT=$(dirname "$0")/../dl/baustellen; mkdir -p "$OUT"
TS=$(date -u +%Y%m%dT%H%M%SZ)
for t in 14403 14698 14755; do
  for i in 1 2 3 4 5 6 7 8 9 10; do
    code=$(curl -sS -m 60 -o "$OUT/thema_${t}_$TS.geojson" -w "%{http_code}" "https://stadtplan.bonn.de/geojson?Thema=$t")
    [ "$code" = 200 ] && break; sleep 2
  done
  echo "Thema=$t versuch=$i http=$code bytes=$(wc -c < "$OUT/thema_${t}_$TS.geojson") ts=$TS"
done
