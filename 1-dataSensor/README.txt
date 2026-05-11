# OpenSky Resolution Advisory Sample

Les données sont fournies par le réseau **OpenSky Network**.

Le réseau OpenSky est un réseau communautaire de récepteurs qui collecte en continu des données de surveillance du trafic aérien. Contrairement à d’autres réseaux, OpenSky conserve les données collectées et les met à disposition des chercheurs.

Ce fichier contient un échantillon de messages liés aux systèmes TCAS / ACAS (*Traffic Collision Avoidance System*), utilisés pour :
- la détection de conflits entre aéronefs ;
- les alertes de collision ;
- les recommandations d’évitement ;
- les avis de résolution verticale.

Les données sont extraites des messages ADS-B et Mode S décodés par OpenSky.

---

# Contenu des données

Le fichier contient les colonnes suivantes :

```text
sensors
rawMsg
minTime
maxTime
msgCount
icao24
isLongFormat
isAirborne
hasCrossLinkCapability
sensitivityLevel
replyInformation
altitude
hasValidRAC
activeResolutionAdvisories
resolutionAdvisoryComplement
noPassBelow
noPassAbove
noTurnLeft
noTurnRight
hasTerminated
hasMultipleThreats
```

---

# Description des colonnes

## `sensors`

Liste des capteurs OpenSky ayant reçu le message.

Chaque entrée contient :
- l’identifiant du capteur ;
- le premier instant de réception ;
- le dernier instant de réception.

Exemple :

```text
[{'serial': -1408045095,
  'minTime': 1772323717.153,
  'maxTime': 1772323717.153}]
```

---

## `rawMsg`

Message brut ADS-B / Mode S encodé en hexadécimal.

Exemple :

```text
80e1999858cd85a7a09aae93861c
```

---

## `minTime`

Premier horodatage Unix de réception du message.

Exemple :

```text
1772323717.153
```

---

## `maxTime`

Dernier horodatage Unix de réception du message.

Lorsque plusieurs capteurs reçoivent le même message, cette valeur peut différer de `minTime`.

---

## `msgCount`

Nombre de messages regroupés dans l’enregistrement.

Exemple :

```text
1
```

---

## `icao24`

Identifiant ICAO 24 bits de l’aéronef.

Cet identifiant permet de suivre un appareil spécifique.

Exemple :

```text
a9a901
```

---

## `isLongFormat`

Indique si le message utilise le format long ADS-B / Mode S.

Valeurs possibles :

| Valeur | Signification |
|---|---|
| VRAI | Format long |
| FAUX | Format court |

---

## `isAirborne`

Indique si l’aéronef est en vol.

| Valeur | Signification |
|---|---|
| VRAI | En vol |
| FAUX | Au sol |

---

## `hasCrossLinkCapability`

Indique si l’aéronef possède une capacité de liaison ACAS/TCAS.

Cette valeur peut être absente.

---

## `sensitivityLevel`

Niveau de sensibilité TCAS/ACAS utilisé par l’aéronef.

Ce niveau dépend notamment :
- de l’altitude ;
- du contexte de trafic.


---

## `replyInformation`

Code d’information de réponse Mode S.

Ce champ est utilisé dans les échanges TCAS/ACAS.

---

## `altitude`

Altitude de l’aéronef.

Exemple :

```text
12192
```

L’unité dépend du décodage utilisé (généralement pieds ou mètres selon la source).

---

## `hasValidRAC`

Indique si le message contient un RAC (*Resolution Advisory Complement*) valide.

| Valeur | Signification |
|---|---|
| VRAI | RAC valide |
| FAUX | RAC absent/invalide |

---

## `activeResolutionAdvisories`

Code représentant les avis de résolution actifs.

Ces avis correspondent aux recommandations TCAS émises pour éviter une collision.

Exemple :

```text
13153
```

---

## `resolutionAdvisoryComplement`

Complément d’avis de résolution TCAS.

Exemple :

```text
6
```

---

## `noPassBelow`

Indique qu’un aéronef ne doit pas passer sous le trafic conflictuel.

| Valeur | Signification |
|---|---|
| VRAI | Interdiction de passer dessous |
| FAUX | Aucun interdit |

---

## `noPassAbove`

Indique qu’un aéronef ne doit pas passer au-dessus du trafic conflictuel.

---

## `noTurnLeft`

Indique une restriction de virage à gauche.

---

## `noTurnRight`

Indique une restriction de virage à droite.

---

## `hasTerminated`

Indique si l’avis TCAS a été terminé.

| Valeur | Signification |
|---|---|
| 1 | Avis terminé |
| 0 | Avis actif |

---

## `hasMultipleThreats`

Indique la présence de plusieurs menaces simultanées détectées par le système TCAS.

| Valeur | Signification |
|---|---|
| 1 | Plusieurs conflits détectés |
| 0 | Un seul conflit |

---


---

# Source des données

OpenSky Network

https://opensky-network.org/

---

# Documentation complémentaire

## API OpenSky

https://opensky-network.org/apidoc/

---

## Guide Impala OpenSky

https://opensky-network.org/impala-guide

---

## Documentation TCAS / ACAS

https://en.wikipedia.org/wiki/Traffic_collision_avoidance_system
