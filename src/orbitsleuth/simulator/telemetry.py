
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd
from sgp4.api import Satrec, jday

TLE_PATH = Path("data/raw/iss.tle")
OUTPUT_PATH = Path("data/processed/iss_telemetry.csv")

# Read the downloaded TLE
lines = TLE_PATH.read_text().strip().splitlines()

name = lines[0].strip()
line1 = lines[1].strip()
line2 = lines[2].strip()

satellite = Satrec.twoline2rv(line1, line2)

# Generate 24 hours of observations
start = datetime.now(timezone.utc).replace(microsecond=0)
duration = timedelta(hours=24)
interval = timedelta(seconds=60)

rows = []
current = start
end = start + duration

while current <= end:
    jd, fr = jday(
        current.year,
        current.month,
        current.day,
        current.hour,
        current.minute,
        current.second,
    )

    error, position, velocity = satellite.sgp4(jd, fr)

    if error == 0:
        x, y, z = position
        vx, vy, vz = velocity

        radius = (x**2 + y**2 + z**2) ** 0.5

        rows.append({
            "timestamp": current.isoformat(),
            "satellite_id": "25544",
            "satellite_name": name,
            "x_km": x,
            "y_km": y,
            "z_km": z,
            "vx_km_s": vx,
            "vy_km_s": vy,
            "vz_km_s": vz,
            "radius_km": radius,
        })
    else:
        print(f"SGP4 error {error} at {current}")

    current += interval

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_PATH, index=False)

print(f"Generated {len(df)} observations")
print(df.head())
print(f"Saved to {OUTPUT_PATH}")
