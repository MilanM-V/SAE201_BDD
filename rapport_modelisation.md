# Phase 2 : Modélisation Théorique

## 1. Dictionnaire des Données

Afin de modéliser correctement la base de données, nous avons recensé les attributs pertinents issus des fichiers de données initiaux (vols, capteurs, et informations constructeurs).

**A. Informations sur les modèles d'avions (Catalogue)**
* `Designator` : Code ICAO du type d'avion (ex: A306)
* `ModelFullName` : Nom complet du modèle (ex: A300 F4-622R)
* `ManufacturerCode` : Nom du constructeur (ex: AIRBUS)
* `AircraftDescription` : Catégorie de l'appareil (ex: LandPlane, Helicopter)
* `EngineCount` : Nombre de moteurs
* `EngineType` : Type de moteur (ex: Jet, Piston)
* `WTC` : Catégorie de turbulence de sillage (Wake Turbulence Category)

**B. Informations sur les vols physiques**
* `icao24` : Identifiant unique mondial du transpondeur de l'avion
* `registration` : Immatriculation (ex: N172UP)
* `callsign` : Indicatif d'appel / Nom du vol (ex: UPS312)
* `firstseen` / `takeofftime` : Heure de début du vol / décollage
* `lastseen` / `landingtime` : Heure de fin du vol / atterrissage
* `estdepartureairport` : Aéroport de départ estimé
* `estarrivalairport` : Aéroport d'arrivée estimé

**C. Informations de suivi (Tracking / Capteurs)**
* `time` : Horodatage exact du relevé
* `lat` / `lon` : Latitude et Longitude
* `velocity` : Vitesse de l'appareil
* `geoaltitude` : Altitude géométrique
* `heading` : Cap

---

## 2. Dépendances Fonctionnelles (DF)

L'analyse de nos données nous a permis de dégager les règles logiques suivantes :

**DF1 : Identification de l'avion physique**
*   **Règle :** `icao24 -> registration, ModelFullName`
*   **Justification :** L'adresse physique du transpondeur (`icao24`) est unique à chaque appareil dans le monde. La connaissance de cet identifiant nous donne immédiatement son immatriculation et son modèle de façon certaine.

**DF2 : Caractéristiques techniques (Catalogue)**
*   **Règle :** `ModelFullName -> ManufacturerCode, Designator, AircraftDescription, EngineCount, EngineType, WTC`
*   **Justification :** Un nom de modèle spécifique (ex: *A300 F4-622R*) appartient toujours à un seul constructeur (Airbus) et possède des caractéristiques techniques fixes en sortie d'usine.

**DF3 : La gestion des vols**
*   **Règle :** `callsign, firstseen -> icao24, estdepartureairport, estarrivalairport`
*   **Justification :** L'indicatif du vol (ex: *UPS312*) associé à sa date/heure de départ précise permet d'identifier formellement l'avion utilisé (`icao24`) et ses aéroports de départ et d'arrivée.

**DF4 : Les relevés de position**
*   **Règle :** `icao24, time -> lat, lon, geoaltitude, velocity, heading`
*   **Justification :** À un instant *T* précis, un avion donné (`icao24`) ne peut se trouver qu'à une seule position géographique et rouler à une seule vitesse.

---

## 3. Clés Candidates et Clés Primaires

De ces DF découlent les clés primaires de nos entités :
1.  **Table AVION** : Clé primaire `icao24`.
2.  **Table MODELE** : Clé primaire `ModelFullName`.
3.  **Table VOL** : Clé primaire composée de `callsign` et `firstseen`.
4.  **Table POSITION** : Clé primaire composée de `icao24` et `time`.

---

## 4. Normalisation de la base de données

La normalisation garantit l'intégrité de la base de données et prévient les redondances.

**4.1. Première Forme Normale (1NF) : Atomicité**
Nos données brutes respectent la 1NF. Chaque attribut contient une donnée unique et non multivaluée (ex: une seule vitesse par champ, un seul constructeur).

**4.2. Deuxième Forme Normale (2NF) : Dépendance Totale à la Clé**
Nos tables respectent la 2NF. Pour les tables possédant une clé primaire composée (ex: `POSITION` avec `icao24, time`), les attributs non-clés (comme la latitude ou la vitesse) dépendent bien de la totalité de cette clé (il faut l'avion ET l'heure pour définir la position). Pour les tables à clé simple, la 2NF est respectée par défaut.

**4.3. Troisième Forme Normale (3NF) : Pas de Dépendance Transitive**
C'est ici que nous séparons les données brutes. 
Si nous laissions tout dans une table unique, nous aurions la dépendance transitive suivante : 
`icao24 -> ModelFullName -> ManufacturerCode`
Dans cette table unique, le constructeur dépendrait du modèle, et non directement de la clé primaire `icao24`. Cela créerait une redondance massive (répétition des attributs techniques pour chaque ligne de position de chaque vol de l'A320). 
En séparant les entités (Avion, Modèle, Vol, Position), nous respectons la 3NF et supprimons ces dépendances transitives.

---

## 5. Schéma Relationnel Final

En appliquant rigoureusement la 3NF, nous obtenons les 4 tables suivantes (les clés primaires sont **soulignées** et les clés étrangères sont précédées d'un `#`) :

*   **MODELE** (<u>ModelFullName</u>, ManufacturerCode, Designator, AircraftDescription, EngineCount, EngineType, WTC)
*   **AVION** (<u>icao24</u>, registration, #ModelFullName)
*   **VOL** (<u>callsign</u>, <u>firstseen</u>, lastseen, estdepartureairport, estarrivalairport, #icao24)
*   **POSITION** (<u>#icao24</u>, <u>time</u>, lat, lon, geoaltitude, velocity, heading)

**Conclusion**
Ce schéma en 3NF nous assure une base de données sans redondance, facile à requêter et protégeant l'intégrité des informations lors des mises à jour.
