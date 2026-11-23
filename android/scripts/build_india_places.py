"""Builds a compact India places dataset (state/district/city/lat/lon)
from GeoNames cities500 + admin1/admin2 code files, for bundling into the
Android app as an offline place picker (CLAUDE.md 5.1: "offline GeoNames
... database, no paid API").

This is a one-off generator, not run at app build time -- its output
(india_places.json) is committed directly to app/src/main/assets/. Re-run
it only if you want to regenerate that file (e.g. to pick up a newer
GeoNames export).

Before running, download these three files from
https://download.geonames.org/export/dump/ into this same directory:
  - cities500.zip (unzip it too, so cities500.txt sits next to this script)
  - admin1CodesASCII.txt
  - admin2Codes.txt

Run with: python build_india_places.py
Produces: india_places.json (array of {n: name, s: state, d: district,
lat, lon, p: population}) and india_states.json (list of state names),
for every GeoNames "populated place" in India with population >= 500
(7,324 places across all 36 states/UTs as of the November 2026 export).
GeoNames data is CC BY 4.0 (https://www.geonames.org/export/).
"""

import json

admin1_names = {}
with open("admin1CodesASCII.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        code, name = parts[0], parts[1]
        if code.startswith("IN."):
            admin1_names[code] = name

admin2_names = {}
with open("admin2Codes.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.rstrip("\n").split("\t")
        code, name = parts[0], parts[1]
        if code.startswith("IN."):
            admin2_names[code] = name

places = []
with open("cities500.txt", encoding="utf-8") as f:
    for line in f:
        cols = line.rstrip("\n").split("\t")
        # geonameid,name,asciiname,alternatenames,lat,lon,feature_class,
        # feature_code,country_code,cc2,admin1,admin2,admin3,admin4,
        # population,elevation,dem,timezone,modification_date
        if cols[8] != "IN":
            continue
        name = cols[2] or cols[1]
        lat = float(cols[4])
        lon = float(cols[5])
        admin1 = cols[10]
        admin2 = cols[11]
        population = int(cols[14]) if cols[14] else 0

        state = admin1_names.get(f"IN.{admin1}", "")
        district = admin2_names.get(f"IN.{admin1}.{admin2}", "")

        if not state:
            continue

        places.append(
            {
                "n": name,
                "s": state,
                "d": district,
                "lat": round(lat, 4),
                "lon": round(lon, 4),
                "p": population,
            }
        )

print(f"Total India places: {len(places)}")

states = sorted({p["s"] for p in places})
print(f"Total states/UTs: {len(states)}")
print(states)

with open("india_places.json", "w", encoding="utf-8") as f:
    json.dump(places, f, ensure_ascii=False, separators=(",", ":"))

with open("india_states.json", "w", encoding="utf-8") as f:
    json.dump(states, f, ensure_ascii=False, separators=(",", ":"))

import os

print("india_places.json size:", os.path.getsize("india_places.json"), "bytes")
