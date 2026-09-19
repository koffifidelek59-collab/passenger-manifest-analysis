# Insights clés

**Manifeste passagers, 418 enregistrements** · KOUAME Koffi Fidele · Stage d'analyse de données

---

## Indicateurs principaux

| KPI | Valeur |
| :--- | ---: |
| Passagers | 418 |
| Part de femmes | 36,4 % |
| Âge médian | 26,0 ans |
| Tarif médian | 14,45 £ |
| 3ᵉ classe | 52,2 % |
| Voyageaient seuls | 60,5 % |
| Cabine renseignée | 21,8 % |

---

## 1. La colonne cible est inutilisable — c'est le constat principal

`Survived` coïncide avec `Sex` sur **100,0 % des lignes**. Les 266 hommes
portent 0 et les 152 femmes portent 1. Deux des quatre cellules du tableau de
contingence sont vides.

C'est une **fuite de cible** (*target leakage*) : une colonne censée être prédite
est dérivable d'une autre. Un modèle entraîné dessus score 100 % et n'a rien
appris. Cela échappe à un audit de valeurs manquantes.

**Recommandation.** Retracer la colonne jusqu'à sa source avant tout travail de
modélisation. Si les labels ont été remplis par une règle, les vrais doivent être
récupérés. S'il s'agit d'une erreur d'extraction, elle affecte tout export du même
système.

---

## 2. Les trois quarts de la colonne cabine manquent — et le trou est le signal

`Cabin` est absent sur **78,2 %** des lignes, et l'absence n'est pas aléatoire :
un numéro a été enregistré pour **74,8 %** de la 1ʳᵉ classe contre **1,8 %** de
la 3ᵉ. La colonne mesure autant la tenue des registres que l'hébergement.

**Recommandation.** Utiliser le flag dérivé `Has_Cabin` comme proxy de classe.
Imputer `Cabin` fabriquerait 327 valeurs et détruirait le signal porté par
l'absence.

---

## 3. Le tarif est la description la plus claire du navire

La 1ʳᵉ classe a payé un tarif médian **7,6 fois** celui de la 3ᵉ, et l'étendue
couvre trois ordres de grandeur (de 0 à 512,33 £). Âge, port et taille de famille
varient tous avec la classe : celle-ci est la variable la plus informative du
manifeste.

**Recommandation.** Segmenter toute offre ou analyse par classe en premier, puis
par port d'embarquement.

---

## 4. Cherbourg embarque le clientèle la plus aisée

Le tarif médian à Cherbourg (≈ 28 £) dépasse nettement Southampton (≈ 14 £) et
Queenstown (≈ 8 £), alors que Cherbourg ne représente qu'environ 24 % des
passagers. Ce n'est pas un effet de volume : c'est un mix social différent.

---

## 5. Les femmes paient plus — principalement via la classe

Le tarif médian des femmes est supérieur d'environ 27 % à celui des hommes.
L'écart s'explique en grande partie par une sur-représentation relative en
classes supérieures, pas par un prix au genre.

---

## Synthèse pour la direction

| Priorité | Action |
| :--- | :--- |
| Critique | Ne jamais modéliser la survie sur ce fichier tant que `Survived` n'est pas corrigé |
| Haute | Traiter l'absence de cabine comme information, pas comme trou à combler |
| Haute | Structurer les analyses et les offres par classe, puis par port |
| Moyenne | Améliorer la collecte (cabine, famille) pour les prochains manifests |
