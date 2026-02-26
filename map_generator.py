"""
map_generator.py — Bellissimo AI Labs City Map Generator
=========================================================

WHAT IT DOES:
    Generates a dark, futuristic city map showing every building footprint
    in a target city — rendered in cyan on a near-black background.
    Used for guerrilla marketing: "We see your city. We'd like to see your business."

DEPENDENCIES (install once):
    pip install osmnx geopandas matplotlib contextily

USAGE:
    python map_generator.py
    → Generates maps for all cities in CITIES list
    → Saves as high-res PNG in /map_outputs/

HOW IT WORKS:
    1. Downloads building footprint data from OpenStreetMap (free, no API key)
    2. Renders with matplotlib: dark background + cyan buildings
    3. Optionally overlays a water layer (rivers, bays, etc.)
    4. Adds Bellissimo AI Labs watermark
    5. Exports at 300 DPI for print quality

ADDING A NEW CITY:
    Add an entry to the CITIES dict with name and OSM search string.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import warnings
warnings.filterwarnings("ignore")

# Try importing the geo libraries — give clear error if not installed
try:
    import osmnx as ox
    import geopandas as gpd
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Run: pip install osmnx geopandas matplotlib contextily")
    exit(1)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Cities to generate maps for
# Format: "Display Name" : "OpenStreetMap search string"
CITIES = {
    "Huntington, WV": "Huntington, West Virginia, USA",
    "Bradenton, FL": "Bradenton, Florida, USA",
}

# Color palette — matches BRAND_STYLE_GUIDE.md map palette
COLORS = {
    "background":      "#0D1117",   # Near black
    "buildings":       "#00C2E0",   # Cyan — primary building fill
    "buildings_edge":  "#0090A8",   # Darker cyan border
    "water":           "#0A1628",   # Very dark navy for water bodies
    "roads":           "#1A2535",   # Subtle dark roads (optional)
    "watermark_text":  "#C9A44A",   # Bellissimo Gold
    "label_text":      "#FAF8F4",   # Warm white
}

# Output settings
OUTPUT_DIR = "map_outputs"
DPI = 300           # 300 DPI = print quality. Use 150 for web/preview.
FIGSIZE = (16, 12)  # Width x Height in inches at DPI

# Bellissimo watermark text
WATERMARK = "BELLISSIMO AI LABS"
TAGLINE = "bellissimo.ai"


# =============================================================================
# MAP GENERATION
# =============================================================================

def generate_city_map(city_name: str, osm_query: str) -> str:
    """
    Generate a dark city map for a given location.

    Args:
        city_name: Display name (used in filename + label)
        osm_query: OpenStreetMap place query string

    Returns:
        Path to saved PNG file
    """
    print(f"\n[Map Generator] Processing: {city_name}")

    # --- Download building footprints ---
    print(f"  → Downloading building footprints from OpenStreetMap...")
    try:
        buildings = ox.features_from_place(osm_query, tags={"building": True})
        print(f"  ← Found {len(buildings):,} buildings")
    except Exception as e:
        print(f"  ERROR downloading buildings: {e}")
        return None

    # --- Download water features ---
    print(f"  → Downloading water features...")
    try:
        water = ox.features_from_place(osm_query, tags={"natural": "water"})
        has_water = len(water) > 0
        print(f"  ← Found {len(water):,} water features")
    except Exception:
        has_water = False
        print(f"  ← No water features found (continuing)")

    # --- Project to a local coordinate reference system ---
    # WHY: OSM data is in lat/lon (degrees). We need meters for accurate rendering.
    buildings_proj = buildings.to_crs(buildings.estimate_utm_crs())
    if has_water:
        water_proj = water.to_crs(buildings_proj.crs)

    # --- Set up the figure ---
    fig, ax = plt.subplots(figsize=FIGSIZE)
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])

    # --- Draw water layer (behind buildings) ---
    if has_water:
        try:
            water_proj.plot(
                ax=ax,
                color=COLORS["water"],
                linewidth=0,
            )
        except Exception:
            pass  # Water rendering is optional — don't fail the whole map

    # --- Draw buildings ---
    buildings_proj.plot(
        ax=ax,
        color=COLORS["buildings"],
        edgecolor=COLORS["buildings_edge"],
        linewidth=0.2,
        alpha=0.9,
    )

    # --- Style the axes ---
    ax.set_axis_off()
    ax.margins(0.02)

    # --- Add city name label (top left) ---
    ax.text(
        0.03, 0.97,
        city_name.upper(),
        transform=ax.transAxes,
        fontsize=18,
        fontweight="bold",
        color=COLORS["label_text"],
        fontfamily="monospace",
        verticalalignment="top",
        alpha=0.9,
    )

    # --- Add Bellissimo watermark (bottom left) ---
    ax.text(
        0.03, 0.04,
        WATERMARK,
        transform=ax.transAxes,
        fontsize=10,
        fontweight="bold",
        color=COLORS["watermark_text"],
        fontfamily="monospace",
        verticalalignment="bottom",
        alpha=0.95,
        letterspacing=2,
    )
    ax.text(
        0.03, 0.015,
        TAGLINE,
        transform=ax.transAxes,
        fontsize=8,
        color=COLORS["watermark_text"],
        fontfamily="monospace",
        verticalalignment="bottom",
        alpha=0.7,
    )

    # --- Add building count (bottom right, subtle) ---
    ax.text(
        0.97, 0.015,
        f"{len(buildings):,} structures mapped",
        transform=ax.transAxes,
        fontsize=7,
        color=COLORS["label_text"],
        fontfamily="monospace",
        verticalalignment="bottom",
        horizontalalignment="right",
        alpha=0.4,
    )

    # --- Save the figure ---
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    safe_name = city_name.replace(", ", "_").replace(" ", "_").lower()
    output_path = os.path.join(OUTPUT_DIR, f"bellissimo_map_{safe_name}.png")

    plt.savefig(
        output_path,
        dpi=DPI,
        bbox_inches="tight",
        pad_inches=0.1,
        facecolor=COLORS["background"],
    )
    plt.close()

    print(f"  ✓ Saved: {output_path}")
    return output_path


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("=" * 60)
    print("Bellissimo AI Labs — City Map Generator")
    print("=" * 60)

    generated = []

    for city_name, osm_query in CITIES.items():
        path = generate_city_map(city_name, osm_query)
        if path:
            generated.append(path)

    print(f"\n{'=' * 60}")
    print(f"Complete. Generated {len(generated)} map(s):")
    for path in generated:
        print(f"  → {path}")
    print(f"\nNext steps:")
    print(f"  1. Open maps in /map_outputs/")
    print(f"  2. Add to Canva/Figma for postcard layout")
    print(f"  3. Add tagline: 'We see your city. We'd like to see your business.'")
    print(f"  4. Add QR code linking to bellissimo.ai/reveal")


if __name__ == "__main__":
    main()
