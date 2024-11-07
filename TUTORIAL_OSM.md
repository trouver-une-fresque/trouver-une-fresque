# Tutoriel OpenStreetMap (OSM) à destination des organisateurs de fresques

La validité des adresses figurant sur les billeteries des fresques est vérifiée via les données OpenStreetMap (OSM), un projet collaboratif de cartographie en ligne qui vise à constituer une base de données géographiques libre du monde.

Si votre atelier n'apparaît pas sur Trouver une Fresque, il y a de grandes chances que l'adresse renseignée soit invalide, ou non encore connue d'OSM. Voici un diagnostic à effectuer pour corriger le tir.

- Rendez-vous sur [OpenStreetMap.org](https://www.openstreetmap.org).
- Dans le champ de recherche en haut à gauche, copiez-collez l'adresse que vous avez renseignée sur votre atelier. Par exemple: `L'Epicerie d'ADDA, 18 Rue de Savenay, 44000 Nantes, France`.
- Si il n'y a pas de résultat, votre adresse n'est pas reconnue par OSM et c'est la raison pour laquelle votre atelier n'apparaît pas sur notre plateforme.

Merci de parcourir les sections suivantes dans l'ordre pour comprendre comment corriger votre adresse.

## 1) Format de l'adresse

La première chose à vérifier est que votre adresse utilise un format classique, sans informations additionnelles qui devraient figurer ailleurs. Le nom du lieu est une information utile.

| Mauvais format | Correction |
|----------|----------|
| Chez moi, 1560 Rue Maurice Jacob, Lyon, France | 1560 Rue Maurice Jacob, Lyon, France |
| Le Grand Bain, 20 Allée de la Maison Rouge, Nantes - Accessible aux PMR | Le Grand Bain, 20 Allée de la Maison Rouge, Nantes |
| La Capsule, 1er étage, Bâtiment le Churchill, 3 rue du Président Rooselvelt 51100 Reims | La Capsule, Bâtiment le Churchill, 3 rue du Président Rooselvelt 51100 Reims |
| La Ruche près du petit ruisseau, 24 Rue de l'Est 75020 Paris | La Ruche près du petit ruisseau, 24 Rue de l'Est 75020 Paris |
| 84 Av. de Grammont, 84 Avenue de Grammont 37000 Tours | 84 Avenue de Grammont 37000 Tours |
| La Galerie du Zéro Déchet, entrée Place Dulcie September, 5 Rue Fénelon, 44000 Nantes, France | La Galerie du Zéro Déchet, 5 Rue Fénelon, 44000 Nantes, France |

## 2) bis/ter

Si votre adresse contient une particule bis ou ter, merci de formatter votre adresse comme suit :

| Mauvais format | Correction |
|----------|----------|
| Mille club, 5T Rue Paul Serusier, Morlaix, France | Mille club, 5 ter Rue Paul Serusier, Morlaix, France |
| Le Grand Bain, 20B Allée de la Maison Rouge, Nantes | Le Grand Bain, 20 bis Allée de la Maison Rouge, Nantes |

## 3) Abbréviations

Si votre adresse contient des abbrévations, essayez d'utiliser le(s) mot(s) complet(s).

| Mauvais format | Correction |
|----------|----------|
| Palais du travail, 9 Pl. du Dr Lazare Goujon, 69100 Villeurbanne, France | Palais du travail, 9 Place du Docteur Lazare Goujon, 69100 Villeurbanne, France |
| Melting Coop, 229 Cr Emile Zola, 69100 Villeurbanne, France | Melting Coop, 229 Cours Emile Zola, 69100 Villeurbanne, France |

## 4) Nom du lieu

Peut-être que le nom du lieu n'est pas rattaché à l'adresse sur OSM. Pour le vérifier, tapez votre adresse sans le nom. Par exemple, si votre adresse est `Melting Coop, 229 Cours Emile Zinzolin, 69100 Villeurbanne, France`, tapez plutôt `229 Cours Emile Zinzolin, 69100 Villeurbanne, France`.

- Si vous n'obtenez pas de résultat, l'adresse (sans le nom du lieu) n'est pas répertoriée sur OpenStreetMap. Naviguez manuellement à l'adresse en vous déplaçant sur la carte pour récupérer l'adresse telle qu'elle apparaît dans OSM. Dans notre cas, on se rendra compte que l'adresse correcte est `229 Cours Emile Zola, 69100 Villeurbanne, France`.

- Si vous obtenez un résultat, deux cas de figure:

    - Soit, en naviguant manuellement sur la carte, le lieu où l'atelier est organisé est bien répertorié. Dans ce cas, il faut:

        - Si le nom du lieu n'a pas la bonne orthographe par rapport à la carte, ajustez le nom du lieu pour le faire correspondre à l'information de la carte.

        - Si l'orthographe du lieu est correcte dans votre addresse par rapport à la carte, il faut [rattacher une adresse à ce lieu](#rattacher-une-adresse-à-un-lieu-existant).

    - Soit, en naviguant manuellement sur la carte, le lieu où l'atelier est organisé n'apparaît pas. Dans ce cas, il faut [ajouter un nouveau lieu et lui rattacher son adresse](#créer-un-lieu).

### Rattacher une adresse à un lieu existant

Suivre les étapes suivantes:

- Créer un [compte sur OpenStreetMap](https://www.openstreetmap.org/user/new).

- Naviguer manuellement sur la carte jusqu'au lieu auquel une adresse doit être rattachée.

- Cliquer sur "Modifier" en haut à gauche.

- Sur la carte, cliquer sur la petite icône du lieu à modifier.

- Dans le panneau latéral qui s'ouvre à gauche, ajouter l'adresse du lieu. Vous pouvez en profiter pour enrichir les données OSM avec des données supplémentaires comme le numéro de téléphone, le site web, etc.

- Une fois les attributs renseignés, cliquer sur "Sauvegarder" en haut à droite.

- Écrire un message décrivant vos modifications. Par exemple : "Ajout de l'adresse à un lieu existant".

- Cliquer sur "Envoyer".

Merci d'avoir contribué à OpenStreetMap !

Attendre une dizaine de minutes, et relire ce tutoriel depuis le début :)

### Créer un lieu

Suivre les étapes suivantes:

- Créer un [compte sur OpenStreetMap](https://www.openstreetmap.org/user/new).

- Naviguer manuellement sur la carte jusqu'à l'endroit où le lieu doit être ajouté.

- Cliquer sur "Point" en haut au centre.

- Cliquer sur le bâtiment où le lieu doit être ajouté.

- Dans le panneau latéral qui s'ouvre à gauche, choisir un type pour le lieu. Par exemple, `Café`, `Restaurant`, `Espace de coworking`, ou `Centre communautaire` pour un tiers-lieu. Ajouter ensuite le nom et l'adresse du lieu. Vous pouvez en profiter pour enrichir les données OSM avec des données supplémentaires comme le numéro de téléphone, le site web, etc.

- Une fois les attributs renseignés, cliquer sur "Sauvegarder" en haut à droite.

- Écrire un message décrivant vos modifications. Par exemple : "Ajout d'un lieu".

- Cliquer sur "Envoyer".

Merci d'avoir contribué à OpenStreetMap !

Attendre une dizaine de minutes, et relire ce tutoriel depuis le début :)
