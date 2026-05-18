import os
import sqlite3
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('Agg')

dbName="aviation.db"
requetesFile="requetes.txt"

PAL=['#2196F3','#4CAF50','#FF9800','#E91E63','#9C27B0',
     '#00BCD4','#FF5722','#607D8B','#795548','#CDDC39',
     '#3F51B5','#8BC34A','#FFC107','#F44336','#009688']

def graphique(cur, sql, typ, titre, xlab, ylab, fich, top=None):
    cur.execute(sql)
    data=cur.fetchall()
    if not data:
        print(f"  [!] Pas de données : {titre}")
        return
    labels=[str(r[0]) if r[0] else "Inconnu" for r in data]
    vals=[r[1] for r in data]
    if top and len(labels)>top:
        labels=labels[:top]
        vals=vals[:top]
    plt.figure(figsize=(10,6))
    if typ=="bar":
        plt.bar(labels,vals,color=PAL[:len(labels)])
        plt.xlabel(xlab); plt.ylabel(ylab)
        plt.xticks(rotation=45,ha='right')
    elif typ=="barh":
        plt.barh(labels[::-1],vals[::-1],color=PAL[:len(labels)])
        plt.xlabel(ylab); plt.ylabel(xlab)
    elif typ=="pie":
        if len(labels)>7:
            autres=sum(vals[6:])
            labels=labels[:6]+["Autres"]
            vals=vals[:6]+[autres]
        plt.pie(vals,labels=labels,autopct='%1.1f%%',colors=PAL[:len(labels)])
    elif typ=="line":
        plt.plot(labels,vals,marker='o',color=PAL[0],linewidth=2)
        plt.xlabel(xlab); plt.ylabel(ylab)
        plt.xticks(rotation=45,ha='right')
        plt.grid(True,alpha=0.3)
    plt.title(titre,fontsize=13,fontweight='bold')
    plt.tight_layout()
    plt.savefig(fich,dpi=150)
    plt.close()
    print(f"  OK {fich}")

def main():
    print("="*50)
    print("SAE 2.01 - Génération des Analyses et Graphiques")
    print("="*50)

    conn=sqlite3.connect(dbName)
    
    """Etape 1 : Création des vues (VIEW)"""
    print("[1/3] Création des vues...")
    conn.execute("""CREATE VIEW IF NOT EXISTS vue_type_aeronef AS
SELECT AircraftDescription, COUNT(*) as nb
FROM AircraftType
WHERE AircraftDescription IS NOT NULL
GROUP BY AircraftDescription
ORDER BY nb DESC""")

    conn.execute("""CREATE VIEW IF NOT EXISTS vue_statut_vol AS
SELECT CASE WHEN onground = 1 THEN 'Au sol' ELSE 'En vol' END as statut,
       COUNT(*) as nb
FROM VecteurEtat
GROUP BY onground""")

    conn.execute("""CREATE VIEW IF NOT EXISTS vue_stats_aeroport AS
SELECT COALESCE(ar.ville, v.airportofdeparture) as nom_depart,
       COUNT(*) as nb_departs,
       COUNT(DISTINCT v.registration) as nb_avions_distincts,
       COUNT(DISTINCT v.airportofdestination) as nb_destinations
FROM Vol v
LEFT JOIN Aeroport_Ref ar ON v.airportofdeparture = ar.code_oaci
WHERE v.airportofdeparture IS NOT NULL
GROUP BY nom_depart""")

    conn.execute("""CREATE VIEW IF NOT EXISTS vue_icao24_aeronef AS
SELECT a.icao24, a.registration, at.AircraftDescription, at.ManufacturerCode, at.ModelFullName
FROM Aeronef a
JOIN AircraftType at ON a.typecode = at.Designator
WHERE a.icao24 IS NOT NULL AND a.icao24 != ''""")
    conn.commit()

    # ================================================================
    # DÉFINITION DES 20 REQUÊTES
    # ================================================================
    REQUETES = []

    REQUETES.append(("Requête 1 (SELECT+JOIN) : Nombre de vols par type de moteur",
"""SELECT at.EngineType, COUNT(*) as nb_vols
FROM Vol v
JOIN Aeronef a ON v.registration = a.registration
JOIN AircraftType at ON a.typecode = at.Designator
WHERE at.EngineType IS NOT NULL
GROUP BY at.EngineType
ORDER BY nb_vols DESC""",
    "bar","Type de moteur","Nombre de vols","graph_01_vols_moteur.png"))

    REQUETES.append(("Requête 2 (SELECT+JOIN) : Répartition des avions par catégorie WTC",
"""SELECT at.WTC, COUNT(a.registration) as nb_avions
FROM Aeronef a
JOIN AircraftType at ON a.typecode = at.Designator
WHERE at.WTC IS NOT NULL
GROUP BY at.WTC
ORDER BY nb_avions DESC""",
    "bar","Catégorie WTC","Nombre d'avions","graph_02_avions_wtc.png"))

    REQUETES.append(("Requête 3 (SELECT+JOIN) : Top 10 des villes de départ",
"""SELECT COALESCE(ar.ville, v.airportofdeparture) as ville_depart, COUNT(*) as nb_vols
FROM Vol v
LEFT JOIN Aeroport_Ref ar ON v.airportofdeparture = ar.code_oaci
WHERE v.airportofdeparture IS NOT NULL
GROUP BY ville_depart
ORDER BY nb_vols DESC
LIMIT 10""",
    "barh","Ville","Nombre de vols","graph_03_top_aeroports.png"))

    REQUETES.append(("Requête 4 (SELECT) : Top 10 constructeurs par nombre de modèles",
"""SELECT ManufacturerCode, COUNT(*) as nb_modeles
FROM AircraftType
WHERE ManufacturerCode IS NOT NULL
GROUP BY ManufacturerCode
ORDER BY nb_modeles DESC
LIMIT 10""",
    "barh","Constructeur","Nombre de modèles","graph_04_top_constructeurs.png"))

    REQUETES.append(("Requête 5 (SELECT+JOIN) : Avions par nombre de moteurs",
"""SELECT at.EngineCount, COUNT(DISTINCT a.registration) as nb_avions
FROM Aeronef a
JOIN AircraftType at ON a.typecode = at.Designator
WHERE at.EngineCount IS NOT NULL
GROUP BY at.EngineCount
ORDER BY at.EngineCount""",
    "bar","Nombre de moteurs","Nombre d'avions","graph_05_nb_moteurs.png"))

    REQUETES.append(("Requête 6 (CTE) : Durée moyenne des vols (heures) par catégorie WTC",
"""WITH duree_vol AS (
    SELECT (v.landingtime - v.takeofftime) / 3600.0 as duree_h, at.WTC
    FROM Vol v
    JOIN Aeronef a ON v.registration = a.registration
    JOIN AircraftType at ON a.typecode = at.Designator
    WHERE v.landingtime IS NOT NULL AND v.takeofftime IS NOT NULL
      AND v.landingtime > v.takeofftime AND at.WTC IS NOT NULL
)
SELECT WTC, ROUND(AVG(duree_h), 2) as duree_moyenne_h
FROM duree_vol
GROUP BY WTC
ORDER BY duree_moyenne_h DESC""",
    "bar","Catégorie WTC","Durée moyenne (h)","graph_06_duree_wtc.png"))

    REQUETES.append(("Requête 7 (CTE) : Top 10 des aéronefs les plus actifs",
"""WITH activite AS (
    SELECT registration, COUNT(*) as nb_vols
    FROM Vol
    WHERE registration IS NOT NULL
    GROUP BY registration
)
SELECT registration, nb_vols
FROM activite
ORDER BY nb_vols DESC
LIMIT 10""",
    "barh","Immatriculation","Nombre de vols","graph_07_top_aeronefs.png"))

    REQUETES.append(("Requête 8 (CTE+JOIN) : Top 10 des routes aériennes les plus empruntées",
"""WITH routes AS (
    SELECT COALESCE(ar1.ville, v.airportofdeparture) || ' -> ' || COALESCE(ar2.ville, v.airportofdestination) as route,
           COUNT(*) as nb_vols
    FROM Vol v
    LEFT JOIN Aeroport_Ref ar1 ON v.airportofdeparture = ar1.code_oaci
    LEFT JOIN Aeroport_Ref ar2 ON v.airportofdestination = ar2.code_oaci
    WHERE v.airportofdeparture IS NOT NULL AND v.airportofdestination IS NOT NULL
    GROUP BY v.airportofdeparture, v.airportofdestination
)
SELECT route, nb_vols
FROM routes
ORDER BY nb_vols DESC
LIMIT 10""",
    "barh","Route","Nombre de vols","graph_08_top_routes.png"))

    REQUETES.append(("Requête 9 (CTE) : Vitesse moyenne par tranche d'altitude",
"""WITH tranches AS (
    SELECT CAST(baroaltitude / 2000 AS INTEGER) * 2000 as tranche,
           velocity
    FROM VecteurEtat
    WHERE baroaltitude IS NOT NULL AND velocity IS NOT NULL AND onground = 0
)
SELECT tranche || 'm' as tranche_alt, ROUND(AVG(velocity), 1) as vitesse_moy
FROM tranches
GROUP BY tranche
ORDER BY tranche""",
    "line","Tranche d'altitude","Vitesse moyenne (m/s)","graph_09_vitesse_altitude.png"))

    REQUETES.append(("Requête 10 (VIEW) : Répartition par type d'aéronef (vue_type_aeronef)",
"""SELECT AircraftDescription, nb
FROM vue_type_aeronef
ORDER BY nb DESC""",
    "barh","Type d'aéronef","Nombre","graph_10_types_aeronef.png"))

    REQUETES.append(("Requête 11 (CTE) : Durée moyenne des vols par Constructeur",
"""WITH duree_vol AS (
    SELECT (v.landingtime - v.takeofftime) / 3600.0 as duree_h, at.ManufacturerCode
    FROM Vol v
    JOIN Aeronef a ON v.registration = a.registration
    JOIN AircraftType at ON a.typecode = at.Designator
    WHERE v.landingtime IS NOT NULL AND v.takeofftime IS NOT NULL
      AND v.landingtime > v.takeofftime AND at.ManufacturerCode IS NOT NULL
)
SELECT ManufacturerCode, ROUND(AVG(duree_h), 2) as duree_moyenne_h
FROM duree_vol
GROUP BY ManufacturerCode
ORDER BY duree_moyenne_h DESC
LIMIT 10""",
    "barh","Constructeur","Durée moyenne (h)","graph_11_duree_constructeur.png"))

    REQUETES.append(("Requête 12 (VIEW) : Top 10 villes de départ par nombre de destinations",
"""SELECT nom_depart, nb_destinations
FROM vue_stats_aeroport
ORDER BY nb_destinations DESC
LIMIT 10""",
    "barh","Ville","Nb destinations distinctes","graph_12_aeroports_destinations.png"))

    REQUETES.append(("Requête 13 (SELECT+CASE) : Distribution des altitudes barométriques",
"""SELECT
    CASE
        WHEN baroaltitude < 1000 THEN '0-1km'
        WHEN baroaltitude < 3000 THEN '1-3km'
        WHEN baroaltitude < 6000 THEN '3-6km'
        WHEN baroaltitude < 9000 THEN '6-9km'
        ELSE '9km+'
    END as tranche,
    COUNT(*) as nb_mesures
FROM VecteurEtat
WHERE baroaltitude IS NOT NULL
GROUP BY tranche
ORDER BY MIN(baroaltitude)""",
    "bar","Tranche d'altitude","Nombre de mesures","graph_13_distrib_altitude.png"))

    REQUETES.append(("Requête 14 (CTE) : Messages TCAS par niveau de sensibilité",
"""WITH stats_tcas AS (
    SELECT sensitivityLevel, COUNT(*) as nb_messages
    FROM MessageTCAS
    WHERE sensitivityLevel IS NOT NULL
    GROUP BY sensitivityLevel
)
SELECT sensitivityLevel, nb_messages
FROM stats_tcas
ORDER BY sensitivityLevel""",
    "bar","Niveau de sensibilité","Nombre de messages","graph_14_tcas_sensibilite.png"))

    # Graph 15 : Décollages par tranche horaire (sur 1 jour)
    REQUETES.append(("Requête 15 (CTE) : Décollages par tranche horaire (01 Sept 2022)",
"""WITH heures AS (
    SELECT CAST(strftime('%H', datetime(takeofftime, 'unixepoch')) AS INTEGER) as heure
    FROM Vol
    WHERE takeofftime IS NOT NULL
)
SELECT heure || 'h' as tranche, COUNT(*) as nb_vols
FROM heures
GROUP BY heure
ORDER BY heure""",
    "bar","Heure (UTC - 01 Sept 2022)","Nombre de décollages","graph_15_vols_par_heure.png"))

    REQUETES.append(("Requête 16 (SELECT+JOIN) : Nombre de messages TCAS par constructeur",
"""SELECT v.ManufacturerCode, COUNT(m.id_message) as nb_messages
FROM MessageTCAS m
JOIN vue_icao24_aeronef v ON m.icao24 = v.icao24
WHERE v.ManufacturerCode IS NOT NULL
GROUP BY v.ManufacturerCode
ORDER BY nb_messages DESC
LIMIT 10""",
    "barh","Constructeur","Nombre de messages TCAS","graph_16_tcas_constructeur.png"))

    REQUETES.append(("Requête 17 (CTE+JOIN) : Altitude moyenne (TCAS) par type d'aéronef",
"""WITH stat_alt AS (
    SELECT v.AircraftDescription, AVG(m.altitude) as alt_moy
    FROM MessageTCAS m
    JOIN vue_icao24_aeronef v ON m.icao24 = v.icao24
    WHERE m.altitude IS NOT NULL
    GROUP BY v.AircraftDescription
)
SELECT AircraftDescription, ROUND(alt_moy, 1) as altitude_moyenne
FROM stat_alt
ORDER BY altitude_moyenne DESC""",
    "barh","Type d'aéronef","Altitude moyenne (ft)","graph_17_altitude_type.png"))

    REQUETES.append(("Requête 18 (SELECT) : Top 10 des codes Squawk les plus utilisés",
"""SELECT squawk, COUNT(*) as nb_occurrences
FROM VecteurEtat
WHERE squawk IS NOT NULL AND squawk != '0000' AND squawk != 'false'
GROUP BY squawk
ORDER BY nb_occurrences DESC
LIMIT 10""",
    "bar","Code Squawk","Nombre d'occurrences","graph_18_top_squawk.png"))

    REQUETES.append(("Requête 19 (SELECT) : Menaces multiples (TCAS) selon la sensibilité",
"""SELECT sensitivityLevel, COUNT(*) as nb_menaces
FROM MessageTCAS
WHERE hasMultipleThreats = 1 AND sensitivityLevel IS NOT NULL
GROUP BY sensitivityLevel
ORDER BY sensitivityLevel""",
    "bar","Niveau de sensibilité","Nb Menaces Multiples","graph_19_tcas_menaces.png"))

    REQUETES.append(("Requête 20 (CTE) : Part des alertes VecteurEtat par tranche d'altitude",
"""WITH tranches AS (
    SELECT 
        CASE 
            WHEN baroaltitude < 3000 THEN '0-3000m'
            WHEN baroaltitude < 6000 THEN '3000-6000m'
            WHEN baroaltitude < 9000 THEN '6000-9000m'
            ELSE '+9000m' 
        END as tranche,
        alert
    FROM VecteurEtat
    WHERE baroaltitude IS NOT NULL AND alert = 1
)
SELECT tranche, COUNT(*) as nb_alertes
FROM tranches
GROUP BY tranche
ORDER BY MIN(tranche)""",
    "bar","Tranche d'altitude","Nombre d'alertes","graph_20_alertes_altitude.png"))

    # ================================================================
    # Etape 2 : Export de toutes les requêtes dans requetes.txt
    # ================================================================
    print("[2/3] Export des requêtes dans requetes.txt...")
    with open(requetesFile,"w",encoding="utf-8") as f:
        f.write("-- REQUÊTES SQL SAE 2.01\n")
        f.write("-- 20 requêtes : SELECT, JOIN, CTE (WITH), VIEW, CASE\n\n")
        f.write("-- ============================================================\n")
        f.write("-- SCHEMA DE LA BASE DE DONNEES\n")
        f.write("-- ============================================================\n\n")
        with open("create_tables.sql","r",encoding="utf-8") as schema:
            f.write(schema.read())
        f.write("\n\n-- ============================================================\n")
        f.write("-- CREATION DES VUES\n")
        f.write("-- ============================================================\n\n")
        f.write("-- Vue 1 : Répartition par type d'aéronef\n")
        f.write("""CREATE VIEW IF NOT EXISTS vue_type_aeronef AS
SELECT AircraftDescription, COUNT(*) as nb
FROM AircraftType
WHERE AircraftDescription IS NOT NULL
GROUP BY AircraftDescription
ORDER BY nb DESC;\n\n""")
        f.write("-- Vue 2 : Proportion en vol vs au sol\n")
        f.write("""CREATE VIEW IF NOT EXISTS vue_statut_vol AS
SELECT CASE WHEN onground = 1 THEN 'Au sol' ELSE 'En vol' END as statut,
       COUNT(*) as nb
FROM VecteurEtat
GROUP BY onground;\n\n""")
        f.write("-- Vue 3 : Statistiques par aéroport de départ\n")
        f.write("""CREATE VIEW IF NOT EXISTS vue_stats_aeroport AS
SELECT COALESCE(ar.ville, v.airportofdeparture) as nom_depart,
       COUNT(*) as nb_departs,
       COUNT(DISTINCT v.registration) as nb_avions_distincts,
       COUNT(DISTINCT v.airportofdestination) as nb_destinations
FROM Vol v
LEFT JOIN Aeroport_Ref ar ON v.airportofdeparture = ar.code_oaci
WHERE v.airportofdeparture IS NOT NULL
GROUP BY nom_depart;\n\n""")
        f.write("-- Vue 4 : Correspondance ICAO24 et informations aéronefs\n")
        f.write("""CREATE VIEW IF NOT EXISTS vue_icao24_aeronef AS
SELECT a.icao24, a.registration, at.AircraftDescription, at.ManufacturerCode, at.ModelFullName
FROM Aeronef a
JOIN AircraftType at ON a.typecode = at.Designator
WHERE a.icao24 IS NOT NULL AND a.icao24 != '';\n\n""")
        f.write("-- ============================================================\n")
        f.write("-- LES 20 REQUETES\n")
        f.write("-- ============================================================\n")
        for i,(nom,sql,_,_,_,_) in enumerate(REQUETES,1):
            f.write(f"\n-- {nom}\n")
            f.write(sql+";\n")
    print("  OK requetes.txt")

    # ================================================================
    # Etape 3 : Génération des graphiques
    # ================================================================
    print("[3/3] Génération des 20 graphiques...")
    os.makedirs("Graphiques", exist_ok=True)
    cursor=conn.cursor()
    for nom,sql,typ,xlab,ylab,fich in REQUETES:
        print(f"  -> {nom}")
        chemin_complet = os.path.join("Graphiques", fich)
        graphique(cursor,sql,typ,nom.split(': ',1)[1] if ': ' in nom else nom,xlab,ylab,chemin_complet)

    conn.close()
    print("="*50)
    print("Terminé !")

if __name__=="__main__":
    main()
