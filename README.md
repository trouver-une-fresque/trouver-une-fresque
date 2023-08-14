# trouver-une-fresque

Trouver une Fresque est un outil open source permettant de détecter les ateliers disponibles dans votre département.

## Lancer le scraping

Le scrapping est effectué en utilisant Selenium, qui s'appuie sur [geckodriver](https://github.com/mozilla/geckodriver/releases) pour afficher les données à récupérer. Téléchargez la version la plus récente, puis extrayez le binaire `geckodriver` dans un dossier `bin/`. Renseignez le chemin absolu vers `bin/geckodriver` dans le fichier de configuration `config.json`.

```console
make install
make scrape
```

## Signaler un problème, une idée de modification

Ouvrez une [issue Github](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) si vous souhaitez signaler un problème.

## Comment Contribuer

Pour proposer une modification, un ajout, ou décrire un bug sur l'outil de détection, vous pouvez ouvrir une [issue](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) ou une [Pull Request](https://github.com/thomas-bouvier/trouver-une-fresque/pulls) avec vos modifications. 

Pour le code en Python, veillez à respecter le standard PEP8 avant de soumettre une Pull Request.

La plupart des IDEs et éditeurs de code moderne proposent des outils permettant de mettre en page votre code en suivant ce standard automatiquement.

## Ateliers supportés

| Atelier       | Lien           | Source | Supporté  |
| ------------- |:-------------:| :-----:| :-----:|
| Fresque du Climat | https://fresqueduclimat.org/participer-a-un-atelier-grand-public | Scraping fdc | Non supporté pour le moment |
| 2tonnes | https://www.eventbrite.fr/o/2-tonnes-29470123869 | Scraping Eventbrite | OK |
| Fresque de la Biodiversité | https://www.fresquedelabiodiversite.org/#participer | Scraping Billetweb | OK |
| Fresque Océane | https://www.billetweb.fr/pro/billetteriefo | Scraping Billetweb | OK |
| Fresque Agri'Alim | https://www.billetweb.fr/pro/fresqueagrialim | Scraping Billetweb | OK |
| Fresque du Numérique | https://www.fresquedunumerique.org/#participer | Scraping Billetweb | OK |
| Fresque des Nouveaux Récits | https://www.billetweb.fr/pro/fdnr | Scraping Billetweb | OK |
| Fresque de la Mobilité | https://www.billetweb.fr/pro/fresquedelamobilite | Scraping Billetweb | OK |
| Fresque de l'Alimentation | https://www.billetweb.fr/pro/fresquealimentation | Scraping Billetweb | OK |
| Fresque de la Construction | https://www.billetweb.fr/pro/fresquedelaconstruction | Scraping Billetweb | OK |
| Fresque du Sexisme | https://www.billetweb.fr/pro/fresque-du-sexisme | Scraping Billetweb | OK |
| Atelier OGRE | https://www.billetweb.fr/pro/atelierogre | Scraping Billetweb | OK |
| Fresque Nos Vies Bas Carbone | https://www.nosviesbascarbone.org/participer-a-un-atelier | Scraping Billetweb | OK |
| Fresque de la Forêt | https://all4trees.org/agir/fresque-foret/evenements | | Pas prévu pour le moment |
| Fresque de l'Économie Circulaire | https://www.lafresquedeleconomiecirculaire.com | | Pas prévu pour le moment |
| Fresque des Déchets | https://greendonut.org/dechets/ | | Pas prévu pour le moment |
| Fresque du Textile | https://greendonut.org/textile/ | | Pas prévu pour le moment |
| Fresque des Frontières Planétaires | https://fresquefrontieresplanetaires.earth/ | | Pas prévu pour le moment |
| Horizons Décarbonés | https://www.horizons-decarbones.earth/ | | Pas prévu pour le moment |

## Dev

### Supabase setup

Login to the CLI and start the database. When starting the database, if file `supabase/seed.sql` is present, the `INSERT` statements will be executed to populate the database with testing data. 

```console
supabase login
supabase init
supabase start
```

The `supabase/tables.sql` contains SQL statements allowing to create the required tables. 

To push some data into the database, use the following command:

```console
python push_to_db.py --input results/output.json
```

https://supabase.com/docs/guides/cli/local-development