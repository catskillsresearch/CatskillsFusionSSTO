import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

# 1. Load the world map geometry
# We pull directly from Natural Earth's public shapefiles to ensure reliable, up-to-date data.
url = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"
try:
    world = gpd.read_file(url)
except Exception:
    # Fallback to geopandas built-in lowres dataset if offline or the URL is restricted
    import warnings
    warnings.filterwarnings("ignore", category=FutureWarning)
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# 2. Define the clusters using ISO 3-Letter Country Codes (ISO_A3)
western_aligned = [
    'USA', 'CAN', 'GBR', 'DEU', 'FRA', 'ITA', 'JPN', 'AUS', 'KOR', 'NZL', 
    'ESP', 'PRT', 'NLD', 'BEL', 'CHE', 'SWE', 'NOR', 'FIN', 'DNK', 'AUT', 
    'IRL', 'GRC', 'POL', 'CZE', 'SVK', 'HUN', 'ROU', 'BGR'
]

eastern_aligned = [
    'RUS', 'CHN', 'IRN', 'PRK', 'BLR', 'VEN', 'CUB', 'SYR'
]

neutral_connectors = [
    'IND', 'VNM', 'MEX', 'TUR', 'ARE', 'IDN', 'ZAF', 'BRA', 'MAR', 'SAU', 'SGP'
]

# 3. Categorize each country in the dataframe
def get_bloc(row):
    iso = row.get('ISO_A3', '')
    name = row.get('NAME', '')
    
    if iso in western_aligned or name in ['United States of America', 'United Kingdom']:
        return 'Western-Aligned'
    elif iso in eastern_aligned or name in ['Russia', 'China']:
        return 'Eastern-Aligned / Sanctioned'
    elif iso in neutral_connectors or name in ['India', 'Mexico']:
        return 'Neutral Connectors'
    else:
        return 'Other / Unclassified'

world['bloc'] = world.apply(get_bloc, axis=1)

# 4. Assign Hex colors to each categorized bloc
colors = {
    'Western-Aligned': '#2b5c8f',            # Soft Steel Blue
    'Eastern-Aligned / Sanctioned': '#c83737',  # Soft Terracotta Red
    'Neutral Connectors': '#e69f00',            # Muted Orange/Ochre
    'Other / Unclassified': '#e0e0e0'           # Neutral Light Grey
}
world['color'] = world['bloc'].map(colors)

# 5. Set up the plotting window
fig, ax = plt.subplots(figsize=(16, 9), dpi=150)
ax.set_facecolor('#fafafa')  # Very light gray canvas background

# Plot the geographic map
world.plot(color=world['color'], edgecolor='#ffffff', linewidth=0.4, ax=ax)

# Create a clean, custom legend
legend_elements = [
    Patch(facecolor='#2b5c8f', label='Western-Aligned (G7, NATO, Key Allies)'),
    Patch(facecolor='#c83737', label='Eastern-Aligned / Sanctioned (Russia, China, Iran, etc.)'),
    Patch(facecolor='#e69f00', label='Neutral Connectors (India, Mexico, Vietnam, etc.)'),
    Patch(facecolor='#e0e0e0', label='Other / Unclassified')
]
ax.legend(
    handles=legend_elements, 
    loc='lower left', 
    frameon=True, 
    facecolor='#ffffff', 
    edgecolor='none', 
    fontsize=10,
    title="Economic Clumps",
    title_fontsize=11
)

# Title and cleaning up borders
plt.title('Geoeconomic Fragmentation: Nearest Neighbor Clusters of Global Economies', fontsize=15, fontweight='bold', pad=20)
plt.axis('off')

# Render the layout
plt.tight_layout()
plt.show()
