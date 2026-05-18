# [Page de Garde]
**SAÉ 2.01 - Conception et implémentation d’une base de données relationnelle**
**B.U.T. Sciences des Données - Semestre 2 - Année 2025/2026**
**Étudiants :** [Nom 1], [Nom 2]
**Logos :** [Insérer Logo IUT] [Insérer Logo SD]

---

# Table des Matières
1. Introduction et Problématique
2. Présentation des Données
3. Dépendances Fonctionnelles et Normalisation
4. Schéma Relationnel et Présentation de la BDD
5. Visualisations et Analyse
6. Difficultés Rencontrées et Conclusion

---

# 1. Introduction et Problématique
Dans le cadre de la SAÉ 2.01, nous avons été chargés de concevoir et d'implémenter une base de données relationnelle robuste à partir de jeux de données issus du réseau collaboratif OpenSky Network. L'objectif est de structurer, normaliser et stocker efficacement des informations de suivi aérien, de caractéristiques d'aéronefs, ainsi que des données de capteurs, pour en permettre une exploitation analytique optimale.

# 2. Présentation des Données
Nos données sources sont réparties dans plusieurs fichiers (CSV et Excel) :
- **AircraftTypes** : Informations descriptives sur les modèles d'aéronefs (moteurs, constructeur, etc.).
- **flightSample** : Informations de suivi de vols (aéroports de départ/arrivée, horaires, immatriculation).
- **airbus_tree** : Relevés réguliers des vecteurs d'état des aéronefs (position GPS, vitesse, altitude).
- **Données spécifiques (Capteurs / part_1.xlsx)** : Messages TCAS et informations de réception par des capteurs.

Ces données brutes présentaient des redondances et des structures non atomiques (listes) nécessitant un nettoyage et une normalisation.

# 3. Dépendances Fonctionnelles et Normalisation

Pour garantir la cohérence des données, nous avons défini plusieurs dépendances fonctionnelles et normalisé nos tables :

### 3.1 Normalisation de la table des Vols (Passage en 3NF)

La table initiale `flightSample` contenait à la fois les données relatives au vol (horaires, aéroports) et les données relatives à l'avion lui-même (immatriculation, modèle, code type). Nous avons procédé à une normalisation rigoureuse pour l'amener jusqu'en Troisième Forme Normale (3NF).

**Étape 1 : Première Forme Normale (1NF)**
La table `flightSample` respecte d'emblée la 1NF car tous ses attributs sont atomiques (pas de listes ou de valeurs multiples dans une même case).

**Étape 2 : Deuxième Forme Normale (2NF)**
Pour identifier un vol unique, la clé candidate logique est composite : `{icao24, firstseen}` (l'identifiant de l'avion + l'heure de début du vol). 
Cependant, des attributs comme `registration`, `model` et `typecode` ne dépendent que d'une partie de cette clé (ils dépendent uniquement de l'avion `icao24`, et non de l'heure du vol `firstseen`). Il y a donc une **dépendance partielle**.
Pour atteindre la 2NF, nous devons séparer ces informations. Nous avons donc créé :
- Une table **Vol** avec une clé primaire artificielle `id_vol` (pour simplifier les jointures) où tous les attributs temporels et géographiques dépendent pleinement du vol.
- Une table **Aeronef** ayant pour clé primaire `registration` (l'immatriculation unique de l'avion).

**Étape 3 : Troisième Forme Normale (3NF)**
La 3NF exige qu'il n'y ait aucune **dépendance transitive** entre des attributs non clés.
Dans la table `flightSample` originale, nous pouvions observer les dépendances fonctionnelles (DF) suivantes :
- `{registration} → {model, typecode}`
- `{model} → {typecode}`

On remarque que `typecode` dépend de `model`, qui dépend lui-même de `registration`. De plus, le `typecode` correspond à la clé `Designator` de la table `AircraftType`, qui dicte toutes les caractéristiques techniques de l'appareil (`{Designator} → {EngineCount, EngineType, ModelFullName, WTC}`).

Pour respecter scrupuleusement la 3NF, nous avons structuré nos tables ainsi pour éliminer ces redondances :

1. **Table AircraftType (Catalogue des types d'avions)**
   - **Clé primaire :** `Designator`
   - **DF :** `{Designator} → {AircraftDescription, Description, EngineCount, EngineType, ManufacturerCode, ModelFullName, WTC}`
   - *Justification :* Les caractéristiques techniques dépendent uniquement du type d'appareil.

2. **Table Aeronef (Les avions physiques)**
   - **Clé primaire :** `registration`
   - **DF :** `{registration} → {icao24, typecode}`
   - **Clé étrangère :** `typecode` vers `AircraftType(Designator)`
   - *Justification :* Chaque avion physique (identifié par son immatriculation) possède un identifiant de transpondeur (icao24) et correspond à un type d'appareil. L'attribut `model` a été supprimé pour respecter la 3NF, car il dépendait de `typecode` (DF transitive).

3. **Table Vol (Les trajets effectués)**
   - **Clé primaire :** `id_vol` (Auto-incrément)
   - **DF :** `{id_vol} → {registration, firstseen, takeofftime, landingtime, callsign, aéroports...}`
   - **Clé étrangère :** `registration` vers `Aeronef(registration)`
   - *Justification :* Les horaires et aéroports dépendent du vol lui-même. L'attribut `icao24` a été supprimé de cette table pour respecter la 3NF car il est déjà défini par la `registration`. Lier le vol à l'aéronef évite la duplication d'information à chaque trajet.

### 3.2 Normalisation des Capteurs (1NF)
Les données du fichier Excel contenaient une colonne `sensors` multi-valuée (liste de capteurs sous forme de dictionnaire). Pour respecter la 1ère Forme Normale (atomicité des attributs), nous avons créé deux tables :
- **Table MessageTCAS** : Contient les informations uniques du message.
- **Table CapteurReception** : Isole la liste des capteurs associés à chaque message (Relation 1:N).

# 4. Schéma Relationnel et Présentation de la BDD

La base de données finale a été implémentée sous **SQLite**.

**Schéma Relationnel :**
* AircraftType (**Designator**, AircraftDescription, Description, EngineCount, EngineType, ManufacturerCode, ModelFullName, WTC)
* Aeronef (**registration**, icao24, #typecode)
* Vol (**id_vol**, #registration, firstseen, takeofftime, lastseen, landingtime, callsign, estdepartureairport, airportofdeparture, estarrivalairport, airportofdestination)
* VecteurEtat (**id_etat**, time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour)
* MessageTCAS (**id_message**, rawMsg, minTime, maxTime, msgCount, icao24, isLongFormat, isAirborne, ...)
* CapteurReception (**id_reception**, #id_message, serial, minTime, maxTime)

*[Insérer ici une capture d'image propre du schéma de la BDD généré via un outil (ex: DBeaver, draw.io)]*

# 5. Visualisations et Analyse

Afin d'exploiter notre base de données, nous avons réalisé les visualisations suivantes :

### 5.1 Répartition des vols par type de moteur
Cette requête nous permet de comprendre quelle motorisation est la plus fréquente dans notre échantillon.
```sql
SELECT at.EngineType, COUNT(*) 
FROM Vol v 
JOIN Aeronef a ON v.registration = a.registration 
JOIN AircraftType at ON a.typecode = at.Designator 
GROUP BY at.EngineType;
```
*[Insérer l'image `graph_moteurs.png`]*
**Analyse :** Ce graphique en barres met en évidence la forte prédominance des avions à réacteurs ("Jet") dans les vols commerciaux de notre échantillon, comparativement aux autres types de moteurs (comme "Turboprop").

### 5.2 Répartition des avions selon la catégorie WTC
```sql
SELECT at.WTC, COUNT(a.registration) 
FROM Aeronef a 
JOIN AircraftType at ON a.typecode = at.Designator 
GROUP BY at.WTC;
```
*[Insérer l'image `graph_wtc.png`]*
**Analyse :** Le diagramme circulaire montre la proportion des catégories WTC (Wake Turbulence Category). Cela nous permet d'évaluer le gabarit global des aéronefs de notre base de données (catégorie M "Medium", H "Heavy", etc.).

# 6. Difficultés Rencontrées et Conclusion

**Moyens mis en œuvre :** Utilisation de Python pour le nettoyage et l'insertion en masse (librairies `csv`, `sqlite3`, `openpyxl`).
**Difficultés :** 
- Le traitement du fichier Excel (lecture de données imbriquées de type dictionnaire dans la colonne `sensors`). Nous avons utilisé `ast.literal_eval` pour extraire proprement les entités.
- La gestion des clés primaires sur les vols (nécessité de créer une clé artificielle `id_vol` car plusieurs aéronefs peuvent théoriquement avoir le même `icao24` à des `firstseen` différents).

En conclusion, la base obtenue est normalisée et exempte d'anomalies de modification. Elle nous permet d'exécuter des requêtes analytiques croisant la technique des aéronefs avec les signaux TCAS de manière performante.
