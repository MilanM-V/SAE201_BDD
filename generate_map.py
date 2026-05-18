import sqlite3
import json
import os
import folium

dbName = "aviation.db"
airportsJson = "0-typeaircraft/airports.json"
outputMap = "Graphiques/carte_vols.html"

def main():
    print("="*50)
    print("Génération de la Carte Interactive Folium")
    print("="*50)

    # 1. Charger les coordonnées des aéroports
    print("[1/4] Chargement des coordonnées aéroportuaires...")
    airport_coords = {}
    if os.path.exists(airportsJson):
        with open(airportsJson, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                if v.get("icao") and v.get("lat") and v.get("lon"):
                    airport_coords[v["icao"]] = (v["lat"], v["lon"])
    else:
        print("[!] airports.json introuvable.")
        return

    # 2. Création de la carte
    print("[2/4] Initialisation de la carte...")
    # On centre sur l'Europe (où le trafic semble concentré)
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=4, tiles="CartoDB dark_matter")

    conn = sqlite3.connect(dbName)
    cur = conn.cursor()

    # 3. Top Aéroports (Départs)
    print("[3/4] Traitement des aéroports les plus fréquentés...")
    cur.execute("""
        SELECT airportofdeparture, COUNT(*) as nb 
        FROM Vol 
        WHERE airportofdeparture IS NOT NULL 
        GROUP BY airportofdeparture 
        ORDER BY nb DESC 
        LIMIT 50
    """)
    top_airports = cur.fetchall()

    for row in top_airports:
        icao, count = row
        if icao in airport_coords:
            lat, lon = airport_coords[icao]
            radius = min(max(count / 20, 3), 15)
            folium.CircleMarker(
                location=(lat, lon),
                radius=radius,
                popup=f"<b>Aéroport : {icao}</b><br>Nb Départs : {count}",
                color="#00BCD4",
                fill=True,
                fillColor="#00BCD4",
                fillOpacity=0.7
            ).add_to(m)

    # 4. Trajets (Routes)
    print("[4/4] Traitement des trajets d'avions (routes)...")
    cur.execute("""
        SELECT airportofdeparture, airportofdestination, COUNT(*) as nb 
        FROM Vol 
        WHERE airportofdeparture IS NOT NULL AND airportofdestination IS NOT NULL 
        GROUP BY airportofdeparture, airportofdestination 
        ORDER BY nb DESC 
        LIMIT 100
    """)
    routes = cur.fetchall()

    for row in routes:
        dep, arr, count = row
        if dep in airport_coords and arr in airport_coords:
            p1 = airport_coords[dep]
            p2 = airport_coords[arr]
            folium.PolyLine(
                locations=[p1, p2],
                weight=min(max(count / 5, 1), 5),
                color="#FF9800",
                opacity=0.4
            ).add_to(m)

    # 5. Trajectoire réelle avec VecteurEtat (Le plus actif)
    print("      Bonus : Trajectoire réelle de l'avion le plus actif...")
    cur.execute("""
        SELECT icao24, COUNT(*) as nb 
        FROM VecteurEtat 
        WHERE lat IS NOT NULL AND lon IS NOT NULL
        GROUP BY icao24 
        ORDER BY nb DESC 
        LIMIT 1
    """)
    top_avion = cur.fetchone()
    if top_avion:
        icao_max = top_avion[0]
        cur.execute("SELECT lat, lon FROM VecteurEtat WHERE icao24=? AND lat IS NOT NULL AND lon IS NOT NULL ORDER BY time", (icao_max,))
        points = cur.fetchall()
        if points:
            folium.PolyLine(
                locations=points,
                weight=3,
                color="#E91E63",
                opacity=0.8,
                popup=f"Trajectoire réelle (Sapin Airbus A380 - icao24: {icao_max})"
            ).add_to(m)
            # Marqueur de départ
            folium.Marker(points[0], popup="Départ", icon=folium.Icon(color="green", icon="plane")).add_to(m)
            # Marqueur de fin
            folium.Marker(points[-1], popup="Fin", icon=folium.Icon(color="red", icon="flag")).add_to(m)

    # 6. Ajout de la Légende
    legend_html = '''
     <div style="position: fixed; 
     bottom: 50px; left: 50px; width: 280px; height: 160px; 
     border:2px solid grey; z-index:9999; font-size:14px;
     background-color:rgba(255, 255, 255, 0.9); padding: 10px; border-radius: 5px; color: black;">
     <b><i class="fa fa-map"></i> Légende de la carte</b><br>
     <i class="fa fa-circle" style="color:#00BCD4"></i> Top 50 Aéroports (Départs)<br>
     <i class="fa fa-minus" style="color:#FF9800"></i> Top 100 Routes Aériennes<br>
     <i class="fa fa-minus" style="color:#E91E63"></i> Trajectoire (Sapin Airbus A380)<br>
     <i class="fa fa-plane" style="color:green"></i> Départ du vol test<br>
     <i class="fa fa-flag" style="color:red"></i> Arrivée du vol test
     </div>
     '''
    m.get_root().html.add_child(folium.Element(legend_html))

    os.makedirs("Graphiques", exist_ok=True)
    m.save(outputMap)
    conn.close()

    print("="*50)
    print(f"Carte générée avec succès : {outputMap}")
    print("="*50)

if __name__ == "__main__":
    main()
