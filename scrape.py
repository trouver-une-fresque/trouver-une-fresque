import argparse

from scraper import main

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--headless",
        action="store_true",
        default=False,
        help="run scraping in headless mode",
    )
    parser.add_argument(
        "--push-to-db",
        action="store_true",
        default=False,
        help="push the scraped results to db",
    )
    args = parser.parse_args()

    kwargs = {key: value for key, value in vars(args).items() if value is not None}
    main(**kwargs)
