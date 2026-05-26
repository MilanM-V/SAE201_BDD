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

def transFloat(val):
    v=clean(val)
    if v:
        try:return float(v)
        except:return None
    return None

def tranfChifre(val):
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
    """Connexion à la base de donnees"""
    if os.path.exists(dbName):os.remove(dbName)
    conn=sqlite3.connect(dbName)
    
    """Creation des table"""
    with open(sqlSchema,"r",encoding="utf-8") as f:
        conn.executescript(f.read())

    """Aeroports (Aeroport_Ref)"""
    if os.path.exists(airportsJson):
        with open(airportsJson,"r",encoding="utf-8") as f:
            airports=json.load(f)
            for key,info in airports.items():
                icao=clean(info.get("icao"))
                if icao:
                    conn.execute("INSERT OR IGNORE INTO Aeroport_Ref VALUES (?,?,?,?)",(icao,clean(info.get("name")),clean(info.get("city")),clean(info.get("country"))))
        conn.commit()

    """AircraftTypes"""
    with open(aircraftTypesCsv,"r",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        vu=set()
        for row in reader:
            desig=row["Designator"].strip()
            if desig not in vu:
                vu.add(desig)
                conn.execute("INSERT INTO AircraftType VALUES (?,?,?,?,?,?,?,?)",(
                    desig,clean(row["AircraftDescription"]),clean(row["Description"]),
                    tranfChifre(row["EngineCount"]),clean(row["EngineType"]),
                    clean(row["ManufacturerCode"]),clean(row["ModelFullName"]),clean(row["WTC"])))
    conn.commit()

    """flight_sample (Aeronef et Vol)"""
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
                         (transFloat(row.get("firstseen")),transFloat(row.get("takeofftime")), 
                          transFloat(row.get("lastseen")),transFloat(row.get("landingtime")),clean(row.get("callsign")),
                          clean(row.get("estdepartureairport")),clean(row.get("airportofdeparture")),
                          clean(row.get("estarrivalairport")),clean(row.get("airportofdestination")),reg))
    conn.commit()

    """airbus_tree"""
    with open(airbusTreeCsv,"r",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        for row in reader:
            conn.execute("INSERT INTO VecteurEtat (time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                         (tranfChifre(row["time"]),clean(row["icao24"]),transFloat(row["lat"]),transFloat(row["lon"]),transFloat(row["velocity"]),
                          transFloat(row["heading"]),transFloat(row["vertrate"]),clean(row["callsign"]),toBoolInt(row["onground"]),
                          toBoolInt(row["alert"]),toBoolInt(row["spi"]),clean(row["squawk"]),transFloat(row["baroaltitude"]),
                          transFloat(row["geoaltitude"]),transFloat(row["lastposupdate"]),transFloat(row["lastcontact"]),tranfChifre(row["hour"])))
    conn.commit()

    """dataSensor"""
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
                    conn.execute("INSERT INTO CapteurReception (id_message, serial, minTime, maxTime) VALUES (?,?,?,?)",(msgId,s.get("serial"),s.get("minTime"),s.get("maxTime")))
            except:pass
        conn.execute("INSERT INTO MessageTCAS (rawMsg,minTime,maxTime,msgCount,icao24,isLongFormat,isAirborne,hasCrossLinkCapability,sensitivityLevel,replyInformation,altitude,hasValidRAC,activeResolutionAdvisories,resolutionAdvisoryComplement,noPassBelow,noPassAbove,noTurnLeft,noTurnRight,hasTerminated,hasMultipleThreats) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                     (clean(row[1]),transFloat(row[2]),transFloat(row[3]),tranfChifre(row[4]),clean(row[5]),toBoolInt(row[6]),
                      toBoolInt(row[7]),toBoolInt(row[8]),tranfChifre(row[9]),tranfChifre(row[10]),transFloat(row[11]),
                      toBoolInt(row[12]),tranfChifre(row[13]),tranfChifre(row[14]),toBoolInt(row[15]),toBoolInt(row[16]),
                      toBoolInt(row[17]),toBoolInt(row[18]),toBoolInt(row[19]),toBoolInt(row[20])))
    conn.commit()
    wb.close()
    
    conn.close()

if __name__=="__main__":
    main()
