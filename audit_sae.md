# Audit des Exigences - SAE 2.01

Ce document compare l'état actuel de notre projet avec les exigences dictées dans le document `cmF.pdf` afin d'identifier les tâches restantes avant le rendu final (27 mai 12h20).

## 1. Structure du Rendu
- [x] **Un seul rendu par groupe** : À gérer lors du dépôt sur Moodle.
- [ ] **Archive (.zip/.rar)** : Le rendu final doit être une archive contenant le rapport PDF et les requêtes SQL. *(Action requise : Créer l'archive à la toute fin).*
- [ ] **Fichier des commandes SQL (.txt)** : Généré automatiquement par notre script sous le nom `requetes.txt`. *(Action requise : Vérifier son contenu final et le glisser dans l'archive).*
- [ ] **Rapport (.pdf)** : Le rapport final doit être converti en PDF. *(Action requise : Exporter le rapport final au format PDF).*

## 2. Format du Rapport
- [ ] **Page de garde** : Doit contenir :
  - [ ] Nom de la SAE
  - [ ] Nom de la formation, semestre et année
  - [ ] Noms et prénoms des membres du groupe
  - [ ] Logos de l'IUT et du département SD
- [ ] **Pages numérotées** : *(Action requise : Configurer le logiciel de traitement de texte).*
- [ ] **Table des matières** : Présente dans le brouillon, doit être générée automatiquement dans le document final.
- [ ] **Pas de captures d'écran de code** : Les requêtes SQL doivent être insérées sous forme de texte brut avec une police spécifique (type code). *(Action requise : Copier/coller depuis `requetes.txt` vers le rapport final).*
- [x] **Inserts pour les formules et requêtes** : Notre brouillon de rapport respecte déjà ce format Markdown.

## 3. Contenu du Rapport
- [x] **Problématique** : Rédigée dans l'introduction du brouillon.
- [x] **Présentation des données** : Explicitement détaillée.
- [x] **Dépendances fonctionnelles (DF)** : Définies rigoureusement pour justifier la normalisation.
- [x] **Normalisations avec justifications** : L'explication du passage en 1NF, 2NF et 3NF est rédigée.
- [x] **Présentation de la BDD et schéma relationnel** : Le texte est présent. *(Action requise : Générer un joli diagramme conceptuel/relationnel visuel avec draw.io ou DBeaver et l'insérer à la place du placeholder).*
- [x] **Visualisations et Analyse** : De nombreux graphiques pertinents ont été générés et expliqués.
- [x] **Difficultés rencontrées et moyens mis en œuvre** : Rédigés en conclusion.

## 4. Implémentation Technique
- [x] **SGBD Relationnel** : SQLite a été utilisé, avec succès.
- [x] **Normalisation** : Les données ont été normalisées (séparation Vol/Aeronef, séparation Capteurs/Message).
- [x] **Insertion des données pré-traitées** : Le script `build_db.py` s'occupe de lire les CSV/Excel et de peupler la BDD proprement.
- [x] **Visualisations pertinentes** : 20 requêtes métier complexes ont été produites (Statistiques, croisements avancés, activité temporelle).

---

## 🔴 Plan d'action pour finaliser (Ce qu'il reste à faire)
1. Ouvrir Word, LibreOffice, ou Notion.
2. Créer la **page de garde** officielle avec les bons logos et prénoms.
3. Copier le contenu de `brouillon_rapport.md` dans ce document.
4. Remplacer les textes *[Insérer l'image graph_X]* par les vraies images générées par le script.
5. Créer un schéma relationnel propre (diagramme visuel) et l'insérer à la section 4.
6. Formater proprement les encarts de code SQL.
7. Ajouter une table des matières automatique et numéroter les pages.
8. Exporter ce rapport final au format **PDF**.
9. Zipper ce PDF avec le fichier `requetes.txt` pour créer l'archive de rendu finale.
