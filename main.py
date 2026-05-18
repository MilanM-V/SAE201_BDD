import csv
import sqlite3
import ast
import os
import openpyxl
import matplotlib.pyplot as plt

"""Configuration"""
dbName="aviation.db"
sqlSchema="create_tables.sql"
requetesFile="requetes.txt"

"""Chemins des fichiers"""
aircraftTypesCsv="0-typeaircraft/AircraftTypes.csv"
flightSampleCsv="0-flightsample/flight_sample_2022-09-01.csv"
airbusTreeCsv="0-airbustree/airbus_tree.csv"
sensorXlsx="1-dataSensor/part_1.xlsx"

"""Fonctions simples pour nettoyer les données"""
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
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print("Début du traitement...")

    """Connexion à la base de données"""
    if os.path.exists(dbName):os.remove(dbName)
    conn=sqlite3.connect(dbName)
    
    """Etape 1 : Création des tables"""
    with open(sqlSchema,"r",encoding="utf-8") as f:
        conn.executescript(f.read())
    print("Tables créées.")

    """Etape 2 : AircraftTypes"""
    print("Traitement AircraftTypes...")
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

    """Etape 3 : flight_sample (Aeronef et Vol)"""
    print("Traitement flight_sample...")
    with open(flightSampleCsv,"r",encoding="utf-8") as f:
        reader=csv.reader(f)
        header=[col.strip() for col in next(reader)]
        vuAvions=set()
        for line in reader:
            row=dict(zip(header,line))
            reg=clean(row.get("registration"))
            
            """Table Aeronef"""
            if reg and reg not in vuAvions:
                vuAvions.add(reg)
                conn.execute("INSERT INTO Aeronef VALUES (?,?,?)", 
                             (reg,clean(row.get("icao24")),clean(row.get("typecode"))))
            
            """Table Vol"""
            conn.execute("INSERT INTO Vol (firstseen, takeofftime, lastseen, landingtime, callsign, estdepartureairport, airportofdeparture, estarrivalairport, airportofdestination, registration) VALUES (?,?,?,?,?,?,?,?,?,?)",
                         (toF(row.get("firstseen")),toF(row.get("takeofftime")), 
                          toF(row.get("lastseen")),toF(row.get("landingtime")),clean(row.get("callsign")),
                          clean(row.get("estdepartureairport")),clean(row.get("airportofdeparture")),
                          clean(row.get("estarrivalairport")),clean(row.get("airportofdestination")),reg))
    conn.commit()

    """Etape 4 : airbus_tree"""
    print("Traitement airbus_tree...")
    with open(airbusTreeCsv,"r",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        for row in reader:
            conn.execute("INSERT INTO VecteurEtat (time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (toI(row["time"]),clean(row["icao24"]),toF(row["lat"]),toF(row["lon"]),toF(row["velocity"]),
                          toF(row["heading"]),toF(row["vertrate"]),clean(row["callsign"]),toBoolInt(row["onground"]),
                          toBoolInt(row["alert"]),toBoolInt(row["spi"]),clean(row["squawk"]),toF(row["baroaltitude"]),
                          toF(row["geoaltitude"]),toF(row["lastposupdate"]),toF(row["lastcontact"]),toI(row["hour"])))
    conn.commit()

    """Etape 5 : dataSensor (Excel)"""
    print("Traitement des capteurs (Excel)...")
    wb=openpyxl.load_workbook(sensorXlsx,read_only=True)
    ws=wb.active
    msgId=0
    it=ws.iter_rows(values_only=True)
    next(it)
    for row in it:
        msgId+=1
        """Capteurs"""
        if row[0]:
            try:
                for s in ast.literal_eval(str(row[0])):
                    conn.execute("INSERT INTO CapteurReception (id_message, serial, minTime, maxTime) VALUES (?,?,?,?)",
                                 (msgId,s.get("serial"),s.get("minTime"),s.get("maxTime")))
            except:pass
        
        """Message TCAS"""
        conn.execute("INSERT INTO MessageTCAS (rawMsg, minTime, maxTime, msgCount, icao24, isLongFormat, isAirborne, hasCrossLinkCapability, sensitivityLevel, replyInformation, altitude, hasValidRAC, activeResolutionAdvisories, resolutionAdvisoryComplement, noPassBelow, noPassAbove, noTurnLeft, noTurnRight, hasTerminated, hasMultipleThreats) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (clean(row[1]),toF(row[2]),toF(row[3]),toI(row[4]),clean(row[5]),toBoolInt(row[6]),
                      toBoolInt(row[7]),toBoolInt(row[8]),toI(row[9]),toI(row[10]),toF(row[11]),
                      toBoolInt(row[12]),toI(row[13]),toI(row[14]),toBoolInt(row[15]),toBoolInt(row[16]),
                      toBoolInt(row[17]),toBoolInt(row[18]),toBoolInt(row[19]),toBoolInt(row[20])))
        if msgId%100000==0:print(f"  ... {msgId} messages traités")
    conn.commit()
    wb.close()

    """Etape 6 : Export des requêtes"""
    print("Génération du fichier de requêtes...")
    req1="SELECT at.EngineType, COUNT(*) FROM Vol v JOIN Aeronef a ON v.registration = a.registration JOIN AircraftType at ON a.typecode = at.Designator GROUP BY at.EngineType;"
    req2="SELECT at.WTC, COUNT(a.registration) FROM Aeronef a JOIN AircraftType at ON a.typecode = at.Designator GROUP BY at.WTC;"
    with open(requetesFile,"w",encoding="utf-8") as f:
        f.write("-- REQUÊTES SQL SAE 2.01\n\n")
        with open(sqlSchema,"r",encoding="utf-8") as schema:
            f.write(schema.read())
        f.write("\n\n-- Requête pour la visualisation 1 : Vols par type de moteur\n")
        f.write(req1+"\n")
        f.write("\n-- Requête pour la visualisation 2 : Avions par WTC\n")
        f.write(req2+"\n")

    """Etape 7 : Visualisations"""
    print("Création des graphiques...")
    cursor=conn.cursor()
    cursor.execute(req1)
    lignes1=cursor.fetchall()
    typesMots=[ligne[0] for ligne in lignes1 if ligne[0]!=None]
    nbVols=[ligne[1] for ligne in lignes1 if ligne[0]!=None]
    
    plt.figure(figsize=(10,6))
    plt.bar(typesMots,nbVols,color='skyblue')
    plt.xlabel("Type de moteur")
    plt.ylabel("Nombre de vols")
    plt.title("Vols par type de moteur")
    plt.savefig("graph_moteurs.png")
    plt.close()

    cursor.execute(req2)
    lignes2=cursor.fetchall()
    wtcList=[ligne[0] for ligne in lignes2 if ligne[0]!=None]
    nbAvions=[ligne[1] for ligne in lignes2 if ligne[0]!=None]
    
    plt.figure(figsize=(8,8))
    plt.pie(nbAvions,labels=wtcList,autopct='%1.1f%%')
    plt.title("Répartition des avions selon la catégorie WTC")
    plt.savefig("graph_wtc.png")
    plt.close()

    conn.close()
    print("Terminé. Base de données créée : aviation.db")

if __name__=="__main__":
    main()
