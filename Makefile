URL =

install: ## sets up package and its dependencies
	scripts/install

scrape: ## runs the full scraping experience
	scripts/scrape $(URL)