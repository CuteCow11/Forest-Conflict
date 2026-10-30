import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

random.seed(42)
np.random.seed(42)

# Villages with ecologically realistic animal tendencies
# Based on proximity to Tadoba core zone and crop land
VILLAGES = [
    ("Moharli",    20.1500, 79.3300, ["Tiger","Tiger","Leopard","Sloth Bear"]),
    ("Navegaon",   20.0900, 79.2900, ["Tiger","Leopard","Leopard","Wild Boar"]),
    ("Kolara",     20.2000, 79.3500, ["Tiger","Tiger","Sloth Bear","Leopard"]),
    ("Jamni",      20.2500, 79.4000, ["Elephant","Elephant","Wild Boar","Tiger"]),
    ("Pangdi",     20.3000, 79.3000, ["Tiger","Tiger","Tiger","Leopard"]),
    ("Madnapur",   20.1800, 79.4500, ["Elephant","Elephant","Leopard","Wild Boar"]),
    ("Khadsangi",  20.3500, 79.5000, ["Elephant","Wild Boar","Wild Boar","Leopard"]),
    ("Agarzari",   20.1200, 79.3800, ["Leopard","Leopard","Wild Boar","Tiger"]),
    ("Zari",       20.2800, 79.2800, ["Tiger","Sloth Bear","Leopard","Tiger"]),
    ("Tadoba",     20.2300, 79.3700, ["Tiger","Tiger","Sloth Bear","Tiger"]),
    ("Devada",     20.3800, 79.4200, ["Elephant","Elephant","Wild Boar","Sloth Bear"]),
    ("Kesalwada",  20.1500, 79.5000, ["Elephant","Wild Boar","Leopard","Elephant"]),
    ("Sindewahi",  20.2800, 79.4800, ["Elephant","Wild Boar","Wild Boar","Leopard"]),
    ("Pombhurna",  20.3500, 79.5200, ["Elephant","Elephant","Wild Boar","Leopard"]),
]

# Seasonal tendencies based on real wildlife behaviour
SEASON_BOOST = {
    "Tiger":      [3, 4, 5, 6],       # summer — prey near water
    "Leopard":    [6, 7, 8, 9],       # monsoon — enters villages
    "Elephant":   [10, 11, 12, 1],    # harvest season — crop raids
    "Wild Boar":  [6, 7, 8, 9, 10],  # monsoon + post-monsoon
    "Sloth Bear": [3, 4, 5],          # summer fruiting season
}

CONFLICT_TYPES = {
    "Tiger":      ["Attack on livestock", "Human injury", "Tiger sighting near village"],
    "Leopard":    ["Leopard near school", "Livestock kill", "Human-leopard conflict"],
    "Elephant":   ["Crop raid", "House damage", "Elephant herd movement"],
    "Wild Boar":  ["Crop damage", "Field destruction", "Wild boar raid"],
    "Sloth Bear": ["Human injury", "Bear sighting", "Beehive raid"],
}

COLOR_MAP = {
    "Tiger":      "red",
    "Leopard":    "orange",
    "Elephant":   "gray",
    "Wild Boar":  "green",
    "Sloth Bear": "purple",
}


def generate_dataset(n_records=600, start_year=2021):
    records = []
    start_date = datetime(start_year, 1, 1)

    for _ in range(n_records):
        village, base_lat, base_lon, likely = random.choice(VILLAGES)
        date  = start_date + timedelta(days=random.randint(0, 1180))
        month = date.month

        # 70% ecologically likely animal, 30% random
        if random.random() < 0.70:
            candidates = likely.copy()
            for animal, months in SEASON_BOOST.items():
                if month in months:
                    candidates += [animal, animal]
            animal = random.choice(candidates)
        else:
            animal = random.choice(list(CONFLICT_TYPES.keys()))

        lat      = round(base_lat + np.random.uniform(-0.02, 0.02), 4)
        lon      = round(base_lon + np.random.uniform(-0.02, 0.02), 4)
        incident = random.choice(CONFLICT_TYPES[animal])
        severity = random.choice(["Low", "Medium", "High"])

        records.append([
            date.strftime("%Y-%m-%d"), village, animal,
            incident, lat, lon, severity, COLOR_MAP[animal]
        ])

    df = pd.DataFrame(records, columns=[
        "date", "village", "animal", "incident",
        "lat", "lon", "severity", "color"
    ])
    df["date"] = pd.to_datetime(df["date"])
    return df


if __name__ == "__main__":
    df = generate_dataset()
    df.to_csv("data/conflict_data.csv", index=False)
    print(f"✅ Generated {len(df)} records")
    print(df["animal"].value_counts())