# trouver-une-fresque

Trouver une Fresque est un outil open source permettant de détecter les ateliers disponibles dans votre département.

Les données sont extraites des billetteries officielles via la technique du scraping. La validité des adresses est vérifiée en utilisant les données d'OpenStreetMap.

Si vous utilisez ce code, merci de respecter la [charte de Nominatim](https://operations.osmfoundation.org/policies/nominatim/).

## 🌍 Organisateurs: signaler un problème

Si vous êtes l'organisateur d'un atelier Fresque et que votre évènement n'apparaît pas sur la plateforme Trouver une Fresque, merci de lire le [tutoriel à destination des organisateurs de fresques](https://github.com/trouver-une-fresque/trouver-une-fresque/blob/main/TUTORIAL.md).

Ouvrez une [issue Github](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) si vous souhaitez signaler un problème non couvert dans le tutoriel.

Les ateliers actuellement supportés sont listés sur la [feuille de route](WORKSHOPS.md).

## Installation

Le scrapping est effectué en utilisant Selenium, qui s'appuie sur [geckodriver](https://github.com/mozilla/geckodriver/releases) pour afficher les données à récupérer. Téléchargez la version la plus récente, puis extrayez le binaire `geckodriver` dans un dossier `bin/`. Renommer le fichier de configuration `config.json.dist` en `config.json`.

```console
apt-get install firefox-esr libpq-dev python3-dev
make install
```

Le scraper peut être installé sur un Raspberry Pi sans problème.

### Lancer le scraping

À la fin du scraping, un fichier JSON nommé avec le format `events_20230814_153752.json` est créé dans le dossier `results/`.

```console
python scrape.py
```

Option `--headless` runs the scraping in headless mode, and `--push-to-db` pushes the results of the output json file into the database using the credentials defined in `config.json`.

### Base de données

Nous utilisons [Supabase](https://supabase.com/docs/guides/cli/local-development) pour persister les données scrapées, une alternative open source à Firebase qui fournit une base de données Postgres gratuitement.

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

This command will perform the following actions:

- All events are inserted into the historical table `events_scraped`. Setting `most_recent=False`, but maybe the call to `update_most_recent()` below will change this.
- Delete all events from `events_future` before inserting them again, so that they are updated. Setting `most_recent=True`.
- The `most_recent` attribute of events in `events_scraped` are set to `True` if the following conditions are met:
    - A query identifies rows in the `events_scraped` table that do not have a corresponding entry in the `events_future` table.
    - For these rows, it finds the most recent `scrape_date` for each `id` and `workshop_type`.
    - It then updates the `most_recent` column to `TRUE` for these rows, but only if the `start_date` of the event is in the past.

## Comment Contribuer

Pour proposer une modification, un ajout, ou décrire un bug sur l'outil de détection, vous pouvez ouvrir une [issue](https://github.com/thomas-bouvier/trouver-une-fresque/issues/new) ou une [Pull Request](https://github.com/thomas-bouvier/trouver-une-fresque/pulls) avec vos modifications.

Avant de développer, merci d'installer le hook git en suivant les instructions listées dans le fichier [CONTRIBUTING](https://github.com/trouver-une-fresque/trouver-une-fresque/blob/main/CONTRIBUTING.md). Pour le code en Python, veillez à respecter le standard PEP8 avant de soumettre une Pull Request. La plupart des IDEs et éditeurs de code modernes proposent des outils permettant de mettre en page votre code en suivant ce standard automatiquement.
