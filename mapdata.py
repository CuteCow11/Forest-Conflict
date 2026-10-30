import osmnx as ox
import geopandas as gpd

# Core zone — Tadoba National Park
core = ox.geocode_to_gdf("Tadoba National Park, Chandrapur, Maharashtra, India")
core["zone"] = "core"
print("✅ Core found:", core.geometry.values)

# Full reserve as buffer zone
buffer = ox.geocode_to_gdf("Tadoba Andhari Tiger Reserve, Maharashtra, India")
buffer["zone"] = "buffer"
print("✅ Buffer found:", buffer.geometry.values)

# Combine and save
combined = gpd.GeoDataFrame(
    gpd.pd.concat([buffer, core], ignore_index=True),
    crs=core.crs
)
combined.to_file("data/tadoba.geojson", driver="GeoJSON")
print("✅ Both zones saved!")