import requests
import folium
import webbrowser
import os
from folium.plugins import MiniMap, Fullscreen, MeasureControl


# -----------------------------------------------------
# Coordonnées
# -----------------------------------------------------
VICTORY = (-4.40000, 15.35000)
GARE_CENTRALE = (-4.39000, 15.36000)
DETOUR = (-4.39500, 15.34500)   # Pour route plus longue
POINTS_INTERMEDIAIRES = [
    (-4.3970, 15.3520),
    (-4.3920, 15.3550)
]


# -----------------------------------------------------
# Fonction pour récupérer un itinéraire OSRM
# -----------------------------------------------------
def get_route(start, end):
    try:
        start_str = f"{start[1]},{start[0]}"
        end_str = f"{end[1]},{end[0]}"

        url = (
            f"http://router.project-osrm.org/route/v1/driving/"
            f"{start_str};{end_str}?overview=full&alternatives=true&geometries=geojson"
        )
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        # Retourne tous les itinéraires possibles
        routes = []
        for route in data["routes"]:
            coords = route["geometry"]["coordinates"]
            path = [[lat, lon] for lon, lat in coords]
            dist_km = route["distance"] / 1000
            routes.append((path, dist_km))

        return routes

    except Exception as e:
        print("Erreur OSRM :", e)
        return []


# -----------------------------------------------------
# Récupération des routes depuis OSRM
# -----------------------------------------------------
routes = get_route(VICTORY, GARE_CENTRALE)

if not routes:
    print("Aucun itinéraire trouvé.")
    exit()

shortest_path, shortest_dist = routes[0]   # OSRM renvoie toujours le plus court en premier

# Route la plus longue artisanale
path1, d1 = get_route(VICTORY, DETOUR)[0]
path2, d2 = get_route(DETOUR, GARE_CENTRALE)[0]
longest_path = path1 + path2
longest_dist = d1 + d2


# -----------------------------------------------------
# Création de la carte
# -----------------------------------------------------
center_lat = (VICTORY[0] + GARE_CENTRALE[0]) / 2
center_lon = (VICTORY[1] + GARE_CENTRALE[1]) / 2

m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="OpenStreetMap")

# Ajout plugins
m.add_child(MiniMap())
Fullscreen().add_to(m)
m.add_child(MeasureControl())


# -----------------------------------------------------
# Marqueurs de départ / arrivée
# -----------------------------------------------------
folium.Marker(
    VICTORY, popup="Victory", icon=folium.Icon(color="blue", icon="home")
).add_to(m)

folium.Marker(
    GARE_CENTRALE, popup="Gare Centrale", icon=folium.Icon(color="red", icon="train")
).add_to(m)


# -----------------------------------------------------
# Marqueurs des points intermédiaires
# -----------------------------------------------------
for p in POINTS_INTERMEDIAIRES:
    folium.Marker(
        p, popup="Point intermédiaire", icon=folium.Icon(color="green")
    ).add_to(m)


# -----------------------------------------------------
# Itinéraire le plus court (rouge)
# -----------------------------------------------------
folium.PolyLine(
    shortest_path,
    color="red",
    weight=6,
    opacity=0.8,
    tooltip=f"Route la plus courte ({shortest_dist:.2f} km)"
).add_to(m)


# -----------------------------------------------------
# Itinéraire alternatif OSRM (si disponible)
# -----------------------------------------------------
if len(routes) > 1:
    alt_path, alt_dist = routes[1]
    folium.PolyLine(
        alt_path,
        color="orange",
        weight=5,
        opacity=0.8,
        tooltip=f"Route alternative ({alt_dist:.2f} km)"
    ).add_to(m)


# -----------------------------------------------------
# Itinéraire long (bleu)
# -----------------------------------------------------
folium.PolyLine(
    longest_path,
    color="blue",
    weight=6,
    opacity=0.8,
    tooltip=f"Route la plus longue (via détour) ({longest_dist:.2f} km)"
).add_to(m)


# -----------------------------------------------------
# Zone personnalisée (exemple : carré autour de Victory)
# -----------------------------------------------------
folium.Polygon(
    locations=[
        (-4.4020, 15.3480),
        (-4.4020, 15.3520),
        (-4.3980, 15.3520),
        (-4.3980, 15.3480)
    ],
    color="purple",
    fill=True,
    fill_opacity=0.2,
    tooltip="Zone personnalisée"
).add_to(m)


# -----------------------------------------------------
# Sauvegarde
# -----------------------------------------------------
output = "carte_itineraires_avancee.html"
m.save(output)
webbrowser.open("file://" + os.path.realpath(output))

print("Distance courte :", shortest_dist, "km")
if len(routes) > 1:
    print("Distance alternative :", alt_dist, "km")
print("Distance longue :", longest_dist, "km")
