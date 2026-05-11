import csv
import sqlite3
import ast
import os
import openpyxl

# --- Configuration ---
DB_NAME = "aviation.db"
SQL_SCHEMA = "create_tables.sql"
REQUETES_FILE = "requetes.txt"

# Chemins des fichiers
AIRCRAFT_TYPES_CSV = "0-typeaircraft/AircraftTypes.csv"
FLIGHT_SAMPLE_CSV = "0-flightsample/flight_sample_2022-09-01.csv"
AIRBUS_TREE_CSV = "0-airbustree/airbus_tree.csv"
SENSOR_XLSX = "1-dataSensor/part_1.xlsx"

# --- Fonctions simples pour nettoyer les données ---
def clean(val):
    if val is None: return None
    v = str(val).strip()
    return v if v != "" and v != "NA" else None

def to_f(val):
    v = clean(val)
    try: return float(v) if v else None
    except: return None

def to_i(val):
    v = clean(val)
    try: return int(float(v)) if v else None
    except: return None

def to_bool_int(val):
    v = clean(val)
    if v is None: return None
    if isinstance(val, bool): return 1 if val else 0
    return 1 if str(v).lower() == "true" or v == "1" else 0

def main():
    print("Début du traitement...")

    # Connexion à la base de données
    if os.path.exists(DB_NAME): os.remove(DB_NAME)
    conn = sqlite3.connect(DB_NAME)
    
    # Étape 1 : Création des tables
    with open(SQL_SCHEMA, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    print("Tables créées.")

    # Étape 2 : AircraftTypes
    print("Traitement AircraftTypes...")
    with open(AIRCRAFT_TYPES_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        vu = set()
        for row in reader:
            desig = row["Designator"].strip()
            if desig not in vu:
                vu.add(desig)
                conn.execute("INSERT INTO AircraftType VALUES (?,?,?,?,?,?,?,?)", (
                    desig, clean(row["AircraftDescription"]), clean(row["Description"]),
                    to_i(row["EngineCount"]), clean(row["EngineType"]),
                    clean(row["ManufacturerCode"]), clean(row["ModelFullName"]), clean(row["WTC"])
                ))
    conn.commit()

    # Étape 3 : flight_sample (Aeronef et Vol)
    print("Traitement flight_sample...")
    with open(FLIGHT_SAMPLE_CSV, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = [col.strip() for col in next(reader)]
        vu_avions = set()
        for line in reader:
            row = dict(zip(header, line))
            reg = clean(row.get("registration"))
            
            # Table Aeronef
            if reg and reg not in vu_avions:
                vu_avions.add(reg)
                conn.execute("INSERT INTO Aeronef VALUES (?,?,?,?)", 
                             (reg, clean(row.get("icao24")), clean(row.get("model")), clean(row.get("typecode"))))
            
            # Table Vol
            conn.execute("INSERT INTO Vol (icao24, firstseen, takeofftime, lastseen, landingtime, callsign, estdepartureairport, airportofdeparture, estarrivalairport, airportofdestination, registration) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                         (clean(row.get("icao24")), to_f(row.get("firstseen")), to_f(row.get("takeofftime")), 
                          to_f(row.get("lastseen")), to_f(row.get("landingtime")), clean(row.get("callsign")),
                          clean(row.get("estdepartureairport")), clean(row.get("airportofdeparture")),
                          clean(row.get("estarrivalairport")), clean(row.get("airportofdestination")), reg))
    conn.commit()

    # Étape 4 : airbus_tree
    print("Traitement airbus_tree...")
    with open(AIRBUS_TREE_CSV, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute("INSERT INTO VecteurEtat (time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (to_i(row["time"]), clean(row["icao24"]), to_f(row["lat"]), to_f(row["lon"]), to_f(row["velocity"]),
                          to_f(row["heading"]), to_f(row["vertrate"]), clean(row["callsign"]), to_bool_int(row["onground"]),
                          to_bool_int(row["alert"]), to_bool_int(row["spi"]), clean(row["squawk"]), to_f(row["baroaltitude"]),
                          to_f(row["geoaltitude"]), to_f(row["lastposupdate"]), to_f(row["lastcontact"]), to_i(row["hour"])))
    conn.commit()

    # Étape 5 : dataSensor (Excel)
    print("Traitement des capteurs (Excel)...")
    wb = openpyxl.load_workbook(SENSOR_XLSX, read_only=True)
    ws = wb.active
    msg_id = 0
    it = ws.iter_rows(values_only=True)
    next(it) # skip header
    for row in it:
        msg_id += 1
        # Capteurs
        if row[0]:
            try:
                for s in ast.literal_eval(str(row[0])):
                    conn.execute("INSERT INTO CapteurReception (id_message, serial, minTime, maxTime) VALUES (?,?,?,?)",
                                 (msg_id, s.get("serial"), s.get("minTime"), s.get("maxTime")))
            except: pass
        
        # Message TCAS
        conn.execute("INSERT INTO MessageTCAS (rawMsg, minTime, maxTime, msgCount, icao24, isLongFormat, isAirborne, hasCrossLinkCapability, sensitivityLevel, replyInformation, altitude, hasValidRAC, activeResolutionAdvisories, resolutionAdvisoryComplement, noPassBelow, noPassAbove, noTurnLeft, noTurnRight, hasTerminated, hasMultipleThreats) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (clean(row[1]), to_f(row[2]), to_f(row[3]), to_i(row[4]), clean(row[5]), to_bool_int(row[6]),
                      to_bool_int(row[7]), to_bool_int(row[8]), to_i(row[9]), to_i(row[10]), to_f(row[11]),
                      to_bool_int(row[12]), to_i(row[13]), to_i(row[14]), to_bool_int(row[15]), to_bool_int(row[16]),
                      to_bool_int(row[17]), to_bool_int(row[18]), to_bool_int(row[19]), to_bool_int(row[20])))
        if msg_id % 100000 == 0: print(f"  ... {msg_id} messages traités")
    conn.commit()
    wb.close()

    # Étape 6 : Export des requêtes
    print("Génération du fichier de requêtes...")
    with open(REQUETES_FILE, "w", encoding="utf-8") as f:
        f.write("-- REQUÊTES SQL SAE 2.01\n\n")
        with open(SQL_SCHEMA, "r", encoding="utf-8") as schema:
            f.write(schema.read())
        f.write("\n\n-- Exemple de requête : Vols par type de moteur\n")
        f.write("SELECT at.EngineType, COUNT(*) FROM Vol v JOIN Aeronef a ON v.registration = a.registration JOIN AircraftType at ON a.typecode = at.Designator GROUP BY at.EngineType;\n")

    conn.close()
    print("Terminé. Base de données créée : aviation.db")

if __name__ == "__main__":
    main()
