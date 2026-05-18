import csv
import sqlite3
import ast
import os
import json
import openpyxl

"""Configuration"""
dbName="aviation.db"
sqlSchema="create_tables.sql"

"""Chemins des fichiers"""
aircraftTypesCsv="0-typeaircraft/AircraftTypes.csv"
flightSampleCsv="0-flightsample/flight_sample_2022-09-01.csv"
airbusTreeCsv="0-airbustree/airbus_tree.csv"
sensorXlsx="1-dataSensor/part_1.xlsx"
airportsJson="0-typeaircraft/airports.json"

"""Fonctions de nettoyage"""
def clean(val):
    if val is None:return None
    v=str(val).strip()
    if v!="" and v!="NA":return v
    return None

def toF(val):
    v=clean(val)
    if v:
        try:return float(v)
        except:return None
    return None

def toI(val):
    v=clean(val)
    if v:
        try:return int(float(v))
        except:return None
    return None

def toBoolInt(val):
    v=clean(val)
    if v is None:return None
    if isinstance(val,bool):
        if val:return 1
        return 0
    if str(v).lower()=="true" or v=="1":return 1
    return 0

def main():
    print("="*50)
    print("SAE 2.01 - Construction de la Base de Données")
    print("="*50)

    """Connexion à la base de données"""
    if os.path.exists(dbName):os.remove(dbName)
    conn=sqlite3.connect(dbName)
    
    """Etape 1 : Création des tables"""
    with open(sqlSchema,"r",encoding="utf-8") as f:
        conn.executescript(f.read())
    print("[1/6] Tables créées.")

    """Etape 2 : Aéroports (Aeroport_Ref)"""
    print("[2/6] Traitement Aéroports (JSON)...")
    if os.path.exists(airportsJson):
        with open(airportsJson, "r", encoding="utf-8") as f:
            airports = json.load(f)
            for key, info in airports.items():
                icao = clean(info.get("icao"))
                if icao:
                    conn.execute("INSERT OR IGNORE INTO Aeroport_Ref VALUES (?,?,?,?)",
                                 (icao, clean(info.get("name")), clean(info.get("city")), clean(info.get("country"))))
        conn.commit()
    else:
        print("  [!] Fichier airports.json non trouvé. Les noms d'aéroports ne seront pas renseignés.")

    """Etape 3 : AircraftTypes"""
    print("[3/6] Traitement AircraftTypes...")
    with open(aircraftTypesCsv,"r",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        vu=set()
        for row in reader:
            desig=row["Designator"].strip()
            if desig not in vu:
                vu.add(desig)
                conn.execute("INSERT INTO AircraftType VALUES (?,?,?,?,?,?,?,?)",(
                    desig,clean(row["AircraftDescription"]),clean(row["Description"]),
                    toI(row["EngineCount"]),clean(row["EngineType"]),
                    clean(row["ManufacturerCode"]),clean(row["ModelFullName"]),clean(row["WTC"])
                ))
    conn.commit()

    """Etape 4 : flight_sample (Aeronef et Vol)"""
    print("[4/6] Traitement flight_sample...")
    with open(flightSampleCsv,"r",encoding="utf-8") as f:
        reader=csv.reader(f)
        header=[col.strip() for col in next(reader)]
        vuAvions=set()
        for line in reader:
            row=dict(zip(header,line))
            reg=clean(row.get("registration"))
            if reg and reg not in vuAvions:
                vuAvions.add(reg)
                conn.execute("INSERT INTO Aeronef VALUES (?,?,?)", 
                             (reg,clean(row.get("icao24")),clean(row.get("typecode"))))
            conn.execute("INSERT INTO Vol (firstseen, takeofftime, lastseen, landingtime, callsign, estdepartureairport, airportofdeparture, estarrivalairport, airportofdestination, registration) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (toF(row.get("firstseen")),toF(row.get("takeofftime")), 
                          toF(row.get("lastseen")),toF(row.get("landingtime")),clean(row.get("callsign")),
                          clean(row.get("estdepartureairport")),clean(row.get("airportofdeparture")),
                          clean(row.get("estarrivalairport")),clean(row.get("airportofdestination")),reg))
    conn.commit()

    """Etape 5 : airbus_tree"""
    print("[5/6] Traitement airbus_tree...")
    with open(airbusTreeCsv,"r",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        for row in reader:
            conn.execute("INSERT INTO VecteurEtat (time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (toI(row["time"]),clean(row["icao24"]),toF(row["lat"]),toF(row["lon"]),toF(row["velocity"]),
                          toF(row["heading"]),toF(row["vertrate"]),clean(row["callsign"]),toBoolInt(row["onground"]),
                          toBoolInt(row["alert"]),toBoolInt(row["spi"]),clean(row["squawk"]),toF(row["baroaltitude"]),
                          toF(row["geoaltitude"]),toF(row["lastposupdate"]),toF(row["lastcontact"]),toI(row["hour"])))
    conn.commit()

    """Etape 6 : dataSensor (Excel)"""
    print("[6/6] Traitement des capteurs (Excel)...")
    wb=openpyxl.load_workbook(sensorXlsx,read_only=True)
    ws=wb.active
    msgId=0
    it=ws.iter_rows(values_only=True)
    next(it)
    for row in it:
        msgId+=1
        if row[0]:
            try:
                for s in ast.literal_eval(str(row[0])):
                    conn.execute("INSERT INTO CapteurReception (id_message, serial, minTime, maxTime) VALUES (?,?,?,?)",
                                 (msgId,s.get("serial"),s.get("minTime"),s.get("maxTime")))
            except:pass
        conn.execute("INSERT INTO MessageTCAS (rawMsg, minTime, maxTime, msgCount, icao24, isLongFormat, isAirborne, hasCrossLinkCapability, sensitivityLevel, replyInformation, altitude, hasValidRAC, activeResolutionAdvisories, resolutionAdvisoryComplement, noPassBelow, noPassAbove, noTurnLeft, noTurnRight, hasTerminated, hasMultipleThreats) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (clean(row[1]),toF(row[2]),toF(row[3]),toI(row[4]),clean(row[5]),toBoolInt(row[6]),
                      toBoolInt(row[7]),toBoolInt(row[8]),toI(row[9]),toI(row[10]),toF(row[11]),
                      toBoolInt(row[12]),toI(row[13]),toI(row[14]),toBoolInt(row[15]),toBoolInt(row[16]),
                      toBoolInt(row[17]),toBoolInt(row[18]),toBoolInt(row[19]),toBoolInt(row[20])))
        if msgId%100000==0:print(f"  ... {msgId} messages traités")
    conn.commit()
    wb.close()
    
    conn.close()
    print("="*50)
    print("Construction terminée avec succès !")
    print("Vous pouvez maintenant lancer : python generate_graphs.py")

if __name__=="__main__":
    main()
