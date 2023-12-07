# trouver-une-fresque

Trouver une Fresque est un outil open source permettant de détecter les ateliers disponibles dans votre département.

## Installation

Le scrapping est effectué en utilisant Selenium, qui s'appuie sur [geckodriver](https://github.com/mozilla/geckodriver/releases) pour afficher les données à récupérer. Téléchargez la version la plus récente, puis extrayez le binaire `geckodriver` dans un dossier `bin/`. Renseignez le chemin absolu vers `bin/geckodriver` dans le fichier de configuration `config.json`.

```console
apt-get install firefox-esr libpq-dev python3-dev
make install
```

Le scraper peut être installé sur un Raspberry Pi sans problème.

## Lancer le scraping

```console
python scrape.py
```

Option `--headless` runs the scraping in headless mode, and `--push-to-db` pushes the results of the output json file into the database using the credentials defined in `config.json`.

## Signaler un problème, une idée de modification

Si vous êtes l'organisateur d'un atelier Fresque et que votre évènement n'apparaît pas sur la plateforme Trouver une Fresque, merci de lire le [tutoriel à destination des organisateurs de fresques](https://github.com/trouver-une-fresque/trouver-une-fresque/blob/main/TUTORIAL.md).

Ouvrez une [issue Github](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) si vous souhaitez signaler un problème.

## Comment Contribuer

Pour proposer une modification, un ajout, ou décrire un bug sur l'outil de détection, vous pouvez ouvrir une [issue](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) ou une [Pull Request](https://github.com/thomas-bouvier/trouver-une-fresque/pulls) avec vos modifications. 

Pour le code en Python, veillez à respecter le standard PEP8 avant de soumettre une Pull Request.

La plupart des IDEs et éditeurs de code moderne proposent des outils permettant de mettre en page votre code en suivant ce standard automatiquement.

## Ateliers supportés

| Atelier       | Lien           | Source | Supporté  |
| ------------- |:-------------:| :-----:| :-----:|
| Fresque du Climat | https://fresqueduclimat.org/participer-a-un-atelier-grand-public | Scraping fdc | OK |
| Atelier 2tonnes | https://www.eventbrite.fr/o/2-tonnes-29470123869 | Scraping Eventbrite | OK |
| Fresque de la Biodiversité | https://www.fresquedelabiodiversite.org/#participer | Scraping Billetweb | [Issue #3](https://github.com/trouver-une-fresque/trouver-une-fresque/issues/3) |
| Fresque Océane | https://www.billetweb.fr/pro/billetteriefo | Scraping Billetweb | OK |
| Fresque Agri'Alim | https://www.billetweb.fr/pro/fresqueagrialim | Scraping Billetweb | OK |
| Fresque du Numérique | https://www.fresquedunumerique.org/#participer | Scraping Billetweb | [Issue #3](https://github.com/trouver-une-fresque/trouver-une-fresque/issues/3) |
| Fresque des Nouveaux Récits | https://www.billetweb.fr/pro/fdnr | Scraping Billetweb | [Issue #3](https://github.com/trouver-une-fresque/trouver-une-fresque/issues/3) |
| Fresque de la Mobilité | https://www.billetweb.fr/pro/fresquedelamobilite | Scraping Billetweb | OK |
| Fresque de l'Alimentation | https://www.billetweb.fr/pro/fresquealimentation | Scraping Billetweb | OK |
| Fresque de la Construction | https://www.billetweb.fr/pro/fresquedelaconstruction | Scraping Billetweb | OK |
| Fresque du Sexisme | https://www.billetweb.fr/pro/fresque-du-sexisme | Scraping Billetweb | [Issue #3](https://github.com/trouver-une-fresque/trouver-une-fresque/issues/3) |
| Atelier OGRE | https://www.billetweb.fr/pro/atelierogre | Scraping Billetweb | OK |
| Fresque Nos Vies Bas Carbone | https://www.billetweb.fr/multi_event.php?user=132897 | Scraping Billetweb | OK |
| Fresque de l'Eau | https://www.billetweb.fr/multi_event.php?user=138110 | Scraping Billetweb | OK |
| Atelier futurs proches | https://www.billetweb.fr/pro/futursproches | Scraping Billetweb | OK |
| Fresque de la Diversité | https://www.billetweb.fr/multi_event.php?user=168799 | Scraping Billetweb | OK |
| Fresque de l'Économie Circulaire | https://www.lafresquedeleconomiecirculaire.com | Scaping WIX | OK |
| Fresque du Textile | https://www.billetweb.fr/multi_event.php?user=166793 | Scraping Billetweb | OK |
| Fresque des Déchets | https://www.billetweb.fr/multi_event.php?user=166793 | Scraping Billetweb | OK |
| Fresque des Frontières Planétaires | https://1erdegre.glide.page/dl/6471c6 | Scraping Glide Pages | OK |
| Atelier Horizons Décarbonés | https://1erdegre.glide.page/dl/6471c6 | Scraping Glide Pages | OK |
| 2030 Glorieuses | https://www.2030glorieuses.org/event | API | OK |
| Fresque de la Forêt | https://all4trees.org/agir/fresque-foret/evenements | Scraping site custom | Prévu, priorité 1 |
| Atelier Découverte de la Renaissance Écologique | https://renaissanceecologique.org/ | Scraping site custom | Prévu, priorité 1 |
| Fresque des Possibles | https://www.helloasso.com/associations/le-lieu-dit | Scraping HelloAsso | Prévu, priorité 2 |
| Éco-challenge Little Big Impact | https://www.billetweb.fr/pro/lbi-quiz-sedd | Scraping Billetweb | Prévu, priorité 2 |
| Fresque des Entreprises Inclusives | https://www.helloasso.com/associations/tous-tes-possibles/evenements/fresque-des-entreprises-inclusives| Scraping HelloAsso | En réflexion |

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

### Hoppscotch.io

Follow these steps:

- Install our Browser Extension.
- Click on the Hoppscotch extension icon from Browser's toolbar to add your localhost origins to the Active Origins list. This corresponds to the `API URL` returned by Supabase on startup.
- Refresh the Hoppscotch.io app.
- Change interceptor to Browser Extension in the settings.

```
http://localhost:54321/rest/v1/events?start_date=gte.now
```