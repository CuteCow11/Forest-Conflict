import folium
from folium.plugins import HeatMap
import json


LEGEND_HTML = """
<div style="position:fixed;bottom:40px;right:40px;z-index:9999;
background:#fff;padding:14px 18px;border-radius:10px;
border:1.5px solid #ccc;font-family:sans-serif;
font-size:13px;color:#111;box-shadow:2px 2px 6px rgba(0,0,0,0.15);">
  <div style="font-weight:700;margin-bottom:8px;">Animal Type</div>
  <div>🔴 &nbsp;Tiger</div>
  <div>🟠 &nbsp;Leopard</div>
  <div>⚫ &nbsp;Elephant</div>
  <div>🟢 &nbsp;Wild Boar</div>
  <div>🟣 &nbsp;Sloth Bear</div>
  <div style="font-weight:700;margin:10px 0 6px;">Forest Zones</div>
  <div><span style="color:#1b4332;font-size:16px;">■</span> &nbsp;Core (Tadoba NP)</div>
  <div><span style="color:#2d6a4f;font-size:16px;">■</span> &nbsp;Buffer (Andhari WS)</div>
</div>
"""


def add_boundaries(m: folium.Map) -> folium.Map:
    with open("data/tadoba.geojson", "r") as f:
        geojson_data = json.load(f)

    # Separate the two zones
    buffer_features = [f for f in geojson_data["features"]
                       if f["properties"].get("zone") == "buffer"]
    core_features   = [f for f in geojson_data["features"]
                       if f["properties"].get("zone") == "core"]

    # Draw buffer FIRST (so core appears on top)
    folium.GeoJson(
        {"type": "FeatureCollection", "features": buffer_features},
        style_function=lambda x: {
            "fillColor":  "#52b788",
            "color":      "#2d6a4f",
            "weight":      2,
            "fillOpacity": 0.15,
            "dashArray":  "6 4",   # dashed border for buffer
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["zone"],
            aliases=["Zone:"],
            style="font-family:sans-serif;font-size:13px;color:#111"
        )
    ).add_to(m)

    # Draw core ON TOP of buffer
    folium.GeoJson(
        {"type": "FeatureCollection", "features": core_features},
        style_function=lambda x: {
            "fillColor":  "#40916c",
            "color":      "#1b4332",
            "weight":      2.5,
            "fillOpacity": 0.25,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["zone"],
            aliases=["Zone:"],
            style="font-family:sans-serif;font-size:13px;color:#111"
        )
    ).add_to(m)

    return m


def build_incident_map(df) -> folium.Map:
    """Build color-coded incident map with popups and legend."""
    m = folium.Map(
        location=[20.25, 79.38],
        zoom_start=11,
        tiles="OpenStreetMap"
    )
    m = add_boundaries(m)

    # Safety check if the dataframe is empty
    if df.empty:
        m.get_root().html.add_child(folium.Element(LEGEND_HTML))
        return m

    # Find the index of the absolute latest incident
    latest_idx = df.index[-1]

    for idx, row in df.iterrows():
        is_latest = (idx == latest_idx)

        # Draw alert rings ONLY for the latest incident
        if is_latest:
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=18,
                color="black",
                weight=2,
                fill=False,
                dash_array="5, 5"
            ).add_to(m)
            
            folium.CircleMarker(
                location=[row["lat"], row["lon"]],
                radius=24,
                color="#facc15",
                weight=3,
                fill=False
            ).add_to(m)

        # Draw the main marker (applies to all, but styled differently if latest)
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=10 if is_latest else 8,
            color="white" if is_latest else row["color"],
            weight=3 if is_latest else 1,
            fill=True,
            fill_color=row["color"],
            fill_opacity=1.0 if is_latest else 0.8,
            popup=folium.Popup(
                f"<div style='font-family:sans-serif;font-size:13px;color:#111'>"
                f"{'<div style=\"background:#ef4444;color:white;padding:3px;border-radius:4px;margin-bottom:4px;font-weight:bold;text-align:center;\">🚨 LATEST</div>' if is_latest else ''}"
                f"<b>{row['animal']}</b><br>"
                f"{row['incident']}<br>"
                f"Village: {row['village']}<br>"
                f"Date: {str(row['date'])[:10]}<br>"
                f"Severity: <b>{row['severity']}</b>"
                f"</div>",
                max_width=220
            )
        ).add_to(m)

    m.get_root().html.add_child(folium.Element(LEGEND_HTML))
    return m


def build_heatmap(df) -> folium.Map:
    """Build heatmap showing conflict density."""
    m = folium.Map(
        location=[20.25, 79.38],
        zoom_start=11,
        tiles="CartoDB dark_matter"
    )
    m = add_boundaries(m)

    heat_data = [[row["lat"], row["lon"]] for _, row in df.iterrows()]
    HeatMap(
        heat_data,
        radius=25,
        blur=20,
        gradient={"0.2": "blue", "0.5": "lime",
                  "0.8": "orange", "1.0": "red"}
    ).add_to(m)

    return m


def build_prediction_map(pred_animal, pred_village, confidence, lat, lon,
                         village_history, color_map) -> folium.Map:
    """Build map showing predicted hotspot + village history."""
    m = folium.Map(
        location=[lat, lon],
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    m = add_boundaries(m)

    # Predicted hotspot marker
    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(
            f"<div style='font-family:sans-serif;color:#111'>"
            f"<b>Predicted: {pred_animal}</b><br>"
            f"Village: {pred_village}<br>"
            f"Confidence: {confidence}%"
            f"</div>",
            max_width=200
        ),
        icon=folium.Icon(
            color=color_map.get(pred_animal, "blue"),
            icon="exclamation-sign"
        )
    ).add_to(m)

    # Historical incidents for the selected village
    for _, row in village_history.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            color=row["color"],
            fill=True,
            fill_opacity=0.5,
            popup=folium.Popup(
                f"<div style='color:#111'>"
                f"{row['animal']}<br>"
                f"{row['incident']}<br>"
                f"{str(row['date'])[:10]}"
                f"</div>",
                max_width=180
            )
        ).add_to(m)

    return m