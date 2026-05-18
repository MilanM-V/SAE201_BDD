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
*(Note : Les clés primaires, assurant l'unicité des enregistrements, sont en gras. Les clés étrangères, permettant les jointures, sont précédées d'un hashtag #).*

* AircraftType (**Designator**, AircraftDescription, Description, EngineCount, EngineType, ManufacturerCode, ModelFullName, WTC)
* Aeronef (**registration**, icao24, #typecode)
* Vol (**id_vol**, #registration, firstseen, takeofftime, lastseen, landingtime, callsign, estdepartureairport, airportofdeparture, estarrivalairport, airportofdestination)
* VecteurEtat (**id_etat**, time, icao24, lat, lon, velocity, heading, vertrate, callsign, onground, alert, spi, squawk, baroaltitude, geoaltitude, lastposupdate, lastcontact, hour)
* MessageTCAS (**id_message**, rawMsg, minTime, maxTime, msgCount, icao24, isLongFormat, isAirborne, ...)
* CapteurReception (**id_reception**, #id_message, serial, minTime, maxTime)
* Aeroport_Ref (**code_oaci**, nom, ville, pays)

```mermaid
flowchart LR
    %% Définition des tables avec détails
    AircraftType["<b>AircraftType</b><br/><hr/><br/><b>PK</b> Designator<br/>AircraftDescription<br/>EngineCount<br/>EngineType<br/>ManufacturerCode<br/>ModelFullName<br/>WTC"]
    
    Aeronef["<b>Aeronef</b><br/><hr/><br/><b>PK</b> registration<br/>icao24<br/><b>FK</b> typecode"]
    
    Vol["<b>Vol</b><br/><hr/><br/><b>PK</b> id_vol<br/><b>FK</b> registration<br/>firstseen, lastseen<br/>takeofftime, landingtime<br/>airportofdeparture<br/>airportofdestination<br/>callsign"]
    
    VecteurEtat["<b>VecteurEtat</b><br/><hr/><br/><b>PK</b> id_etat<br/>time, icao24<br/>lat, lon<br/>velocity, heading<br/>vertrate, baroaltitude<br/>alert, onground"]
    
    MessageTCAS["<b>MessageTCAS</b><br/><hr/><br/><b>PK</b> id_message<br/>icao24, rawMsg<br/>sensitivityLevel<br/>altitude, isAirborne<br/>hasMultipleThreats"]
    
    CapteurReception["<b>CapteurReception</b><br/><hr/><br/><b>PK</b> id_reception<br/><b>FK</b> id_message<br/>serial<br/>minTime, maxTime"]
    
    Aeroport_Ref["<b>Aeroport_Ref</b><br/><hr/><br/><b>PK</b> code_oaci<br/>nom<br/>ville<br/>pays"]

    %% Relations (Flèches)
    AircraftType -->|Possède| Aeronef
    Aeronef -->|Effectue| Vol
    MessageTCAS -->|Est reçu par| CapteurReception

    %% Couleurs et Design
    style AircraftType fill:#e1f5fe,stroke:#01579b,stroke-width:2px,color:#000
    style Aeronef fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
    style Vol fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px,color:#000
    style VecteurEtat fill:#f3e5f5,stroke:#4a148c,stroke-width:2px,color:#000
    style MessageTCAS fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style CapteurReception fill:#ffebee,stroke:#b71c1c,stroke-width:2px,color:#000
    style Aeroport_Ref fill:#eceff1,stroke:#263238,stroke-width:2px,color:#000
```

# 5. Visualisations, Requêtes SQL et Analyse

**Ce qu'on veut montrer :**
L'objectif de cette section est de démontrer comment notre architecture normalisée permet d'extraire des indicateurs métiers complexes à partir de la télémétrie brute. Nous voulons analyser les performances des flottes, l'intensité du trafic aéroportuaire et la sécurité des vols (via le TCAS).

**Ce qu'on montre :**
Nous présentons ci-dessous une sélection d'analyses visuelles obtenues grâce à des **requêtes SQL** avancées (combinant des `JOIN`, des vues `VIEW`, et des clauses `WITH` ou `CASE`). L'intégralité de nos 20 requêtes SQL est disponible dans le fichier `requetes.txt` fourni dans l'archive.

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
![Répartition des vols par type de moteur](Graphiques/graph_01_vols_moteur.png)
**Analyse :** Ce graphique en barres met en évidence la forte prédominance des avions à réacteurs ("Jet") dans les vols commerciaux de notre échantillon, comparativement aux autres types de moteurs (comme "Turboprop").

### 5.2 Répartition des avions selon la catégorie WTC
```sql
SELECT at.WTC, COUNT(a.registration) 
FROM Aeronef a 
JOIN AircraftType at ON a.typecode = at.Designator 
GROUP BY at.WTC;
```
![Répartition des avions selon la catégorie WTC](Graphiques/graph_02_avions_wtc.png)
**Analyse :** Le diagramme en barres montre la proportion des catégories WTC (Wake Turbulence Category). Cela nous permet d'évaluer le gabarit global des aéronefs de notre base de données (catégorie M "Medium", H "Heavy", etc.).

### 5.3 Croisement des données et Enrichissement

Pour enrichir notre analyse et exploiter toute la richesse du jeu de données, nous avons mis en œuvre deux axes majeurs d'amélioration :

**1. L'enrichissement géographique (Vrais noms de villes) :**
Plutôt que d'afficher des codes OACI bruts (ex: LFPG, EGLL) souvent illisibles pour un public non initié, nous avons intégré un jeu de données public (Open Source) recensant les aéroports mondiaux. En créant la table `Aeroport_Ref`, nous avons pu utiliser des requêtes de jointure (ex: `LEFT JOIN Aeroport_Ref`) pour convertir automatiquement les codes aéroportuaires en véritables noms de villes dans nos graphiques (ex: Paris, Londres). 
De plus, cette méthode permet de regrouper intelligemment l'activité par ville. Par exemple, les vols au départ de Paris-CDG (LFPG) et de Paris-Orly (LFPO) sont tous deux comptabilisés sous la même entité "Paris", ce qui donne une vision macroscopique bien plus claire du trafic aérien.

**2. Le croisement ICAO24 (Vues et Jointures Avancées) :**
Nous avons mis en évidence la correspondance `icao24` (l'identifiant unique du transpondeur) qui agit comme un pont naturel entre les données de trajectoire (`VecteurEtat`), les signaux d'alerte (`MessageTCAS`) et les caractéristiques physiques des avions (`Aeronef` et `AircraftType`).

Pour simplifier ces jointures, nous avons créé une vue dédiée consolidant ces informations :
```sql
CREATE VIEW IF NOT EXISTS vue_icao24_aeronef AS
SELECT a.icao24, a.registration, at.AircraftDescription, at.ManufacturerCode, at.ModelFullName
FROM Aeronef a
JOIN AircraftType at ON a.typecode = at.Designator
WHERE a.icao24 IS NOT NULL AND a.icao24 != '';
```

Grâce à cet enrichissement, nous avons implémenté plusieurs nouvelles analyses pertinentes :
- **Performance des flottes (Requête 11)** : Nous avons calculé la durée moyenne des vols selon le constructeur de l'avion, croisant ainsi les horaires effectifs et la documentation de l'aéronef.
- **Activité par tranche horaire (Requête 15)** : Nous avons généré un graphique affichant le nombre de décollages par heure de la journée. Le jeu de données `flightSample` ne couvrant que la journée du **1er Septembre 2022**, nous l'avons explicitement précisé sur le titre et l'axe du graphique pour éviter toute confusion.
- **Le croisement Constructeur / Messages TCAS (Requête 16)** : En liant `MessageTCAS` à la vue, nous avons pu identifier quels constructeurs émettent le plus de messages TCAS dans notre échantillon.
- **L'altitude moyenne par type d'appareil (Requête 17)** : En croisant les données TCAS avec les caractéristiques techniques, nous mettons en évidence les plafonds de vol réels observés selon la classe de l'aéronef.
- **La distribution des alertes transpondeur (Requêtes 18 et 20)** : Nous analysons les codes Squawk anormaux et observons si les alertes enregistrées (`alert=1` dans `VecteurEtat`) se concentrent sur des tranches d'altitude spécifiques (ex: phases de décollage/atterrissage < 3000m).
- **Complexité des menaces TCAS (Requête 19)** : Remplacement de la simple proportion Air/Sol par l'analyse des menaces multiples simultanées selon le niveau de sensibilité TCAS de l'appareil.

Ces requêtes démontrent la robustesse de notre modèle relationnel, capable de lier des référentiels statiques à des flux de télémétrie massifs pour en extraire des indicateurs métiers pertinents. Notez également que nous avons privilégié les graphiques en barres pour la quasi-totalité des visualisations, évitant ainsi les graphiques circulaires ("camemberts") souvent critiqués pour leur manque de précision visuelle.

### 5.4 Cartographie Interactive (Folium)

Pour aller plus loin que les simples graphiques 2D, nous avons développé un script additionnel (`generate_map.py`) s'appuyant sur la librairie **Folium** pour générer une carte interactive en HTML (`Graphiques/carte_vols.html`). Cette carte tire parti des coordonnées géographiques (latitude/longitude) du fichier `airports.json` et de nos tables SQL pour :
- **Visualiser les pôles d'activité :** Les 50 aéroports enregistrant le plus de départs sont représentés par des cercles proportionnels à leur affluence.
- **Tracer les axes majeurs :** Les 100 routes aériennes les plus fréquentées sont modélisées par des lignes liant les aéroports.
- **Afficher une trajectoire réelle (L'Easter Egg du Sapin Airbus) :** En exploitant la table `VecteurEtat`, nous avons extrait les points GPS de l'aéronef le plus actif de notre base. Le tracé généré révèle une surprise glissée dans le jeu de données (fichier `airbus_tree.csv`) : le célèbre vol de test d'un Airbus A380 (ICAO24 `3807fa`) qui a délibérément volé au-dessus de l'Allemagne en dessinant **un sapin de Noël géant**. Cette trouvaille prouve l'efficacité de nos requêtes de géolocalisation et illustre concrètement l'intérêt d'une télémétrie à haute fréquence.

### 5.5 Catalogue complet des Analyses Visuelles

Voici la compilation complète des autres graphiques générés par notre architecture, organisés sous forme de tableaux de bord thématiques.

#### 🌍 Infrastructures et Réseaux (Aéroports & Routes)

<table style="width: 100%; border-collapse: collapse; border: none;">
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_03_top_aeroports.png" width="90%" />
      <br><em>Top 10 Aéroports de départ</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_08_top_routes.png" width="90%" />
      <br><em>Top 10 Routes Aériennes</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_12_aeroports_destinations.png" width="90%" />
      <br><em>Destinations par Aéroport</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
    </td>
  </tr>
</table>

#### ✈️ Profils et Caractéristiques des Aéronefs

<table style="width: 100%; border-collapse: collapse; border: none;">
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_04_top_constructeurs.png" width="90%" />
      <br><em>Top Constructeurs</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_05_nb_moteurs.png" width="90%" />
      <br><em>Répartition du Nombre de Moteurs</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_07_top_aeronefs.png" width="90%" />
      <br><em>Top 10 Aéronefs Actifs</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_10_types_aeronef.png" width="90%" />
      <br><em>Types d'Aéronefs</em>
    </td>
  </tr>
</table>

#### ⏱️ Performances et Statistiques de Vol

<table style="width: 100%; border-collapse: collapse; border: none;">
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_06_duree_wtc.png" width="90%" />
      <br><em>Durée moyenne par WTC</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_09_vitesse_altitude.png" width="90%" />
      <br><em>Vitesse moyenne selon l'Altitude</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_11_duree_constructeur.png" width="90%" />
      <br><em>Durée moyenne par Constructeur</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_13_distrib_altitude.png" width="90%" />
      <br><em>Distribution de l'Altitude</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_15_vols_par_heure.png" width="90%" />
      <br><em>Décollages par tranche horaire</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
    </td>
  </tr>
</table>

#### 🚨 Sécurité et Télémétrie Avancée (TCAS & Transpondeur)

<table style="width: 100%; border-collapse: collapse; border: none;">
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_14_tcas_sensibilite.png" width="90%" />
      <br><em>Messages TCAS par niveau de Sensibilité</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_16_tcas_constructeur.png" width="90%" />
      <br><em>Messages TCAS par Constructeur</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_17_altitude_type.png" width="90%" />
      <br><em>Altitude moyenne par type d'Aéronef</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_18_top_squawk.png" width="90%" />
      <br><em>Top 10 des codes Squawk</em>
    </td>
  </tr>
  <tr>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_19_tcas_menaces.png" width="90%" />
      <br><em>Sensibilité face aux menaces multiples</em>
    </td>
    <td style="width: 50%; text-align: center; border: none; padding: 10px;">
      <img src="Graphiques/graph_20_alertes_altitude.png" width="90%" />
      <br><em>Part des alertes par tranche d'altitude</em>
    </td>
  </tr>
</table>

# 6. Problèmes Rencontrés, Solutions Apportées et Conclusion

**Travail collaboratif et Outils :**
Nous avons mis en place un dépôt **Git** pour versionner notre code, collaborer efficacement sur les requêtes SQL et structurer le développement. L'extraction et l'insertion en masse ont été réalisées en Python (via les librairies `sqlite3`, `csv`, `openpyxl`, `json`).

### 6.1 Problèmes liés aux Données (Nettoyage et Normalisation)
- **Problème :** Le fichier Excel des capteurs contenait des données imbriquées complexes (listes de dictionnaires dans la colonne `sensors`), violant la première forme normale (1NF).
  - **Solution :** Utilisation de `ast.literal_eval` en Python pour parser ces listes complexes et séparer ces données en deux tables distinctes (`MessageTCAS` et `CapteurReception`) avec une relation 1:N.
- **Problème :** L'impossibilité d'utiliser l'`icao24` (l'identifiant de l'avion) comme clé primaire pour un vol, car un même aéronef effectue plusieurs vols différents dans la même journée (à des `firstseen` différents).
  - **Solution :** Création d'une clé primaire artificielle `id_vol` en auto-incrément pour la table `Vol`.
- **Problème :** Présence de valeurs nulles ou de chaînes aberrantes ("NA") dans les fichiers sources, provoquant des erreurs lors des calculs SQL (comme la fonction `AVG()`).
  - **Solution :** Création de fonctions de nettoyage dédiées en Python (`toF()`, `toI()`, `clean()`) pour filtrer et caster correctement les données avant leur insertion dans le SGBD.

### 6.2 Problèmes liés aux Jointures et Croisements
- **Problème :** Afficher l'activité aéroportuaire de manière compréhensible alors que les grandes agglomérations possèdent plusieurs aéroports (ex: Paris CDG et Paris Orly). Compter les codes OACI séparément faussait la vision de l'intensité du trafic par ville.
  - **Solution :** Intégration d'un jeu de données externe (`airports.json`) pour lier le code OACI à une ville, et utilisation d'une clause `GROUP BY ar.ville`. Cela nous a permis de fusionner dynamiquement LFPG et LFPO sous une même entité globale "Paris".
- **Problème :** Lier les messages d'alerte (TCAS) aux caractéristiques techniques des avions (WTC, Constructeur), alors que ces deux tables n'ont pas de lien direct dans le schéma relationnel de base.
  - **Solution :** Création d'une vue SQL (`vue_icao24_aeronef`) servant de pont (via les clés `icao24` et `typecode`) pour simplifier l'écriture des requêtes d'analyse sans alourdir le code.

### 6.3 Problèmes liés aux Performances (Génération des Graphiques)
- **Problème :** Le script initial effectuait la lecture des gigaoctets de CSV/Excel, construisait la base, exécutait les requêtes et dessinait les graphiques en une seule passe. Cela prenait plus de 10 minutes d'attente à chaque fois que nous souhaitions ajuster un détail visuel (couleur, titre) sur un graphique.
  - **Solution :** Scission de l'architecture logicielle en deux scripts. `build_db.py` gère la phase de construction lourde de façon ponctuelle (ETL). `generate_graphs.py` se contente de lire la base SQLite pour exécuter les requêtes très rapidement, générant nos 20 graphiques en quelques secondes (phase Analytique).

### 6.4 Conclusion

En conclusion, la base obtenue est rigoureusement normalisée et exempte d'anomalies de modification. Elle nous permet d'exécuter des requêtes analytiques croisant la dimension technique des aéronefs avec les signaux de sécurité (TCAS) de manière hautement performante. L'enrichissement de la donnée (vrais noms géographiques, travail sur la temporalité) et la conversion de tous les graphiques circulaires ("camemberts") en diagrammes à barres permettent de restituer des indicateurs fiables et immédiatement compréhensibles pour un professionnel du secteur de l'aviation.
