# `scraper_BE` — Abgeordnetenhaus von Berlin

## Setup

Requires Python 3.12+.

```bash
uv install

# NOTE: this is temporary and will be replaced by this: https://codeberg.org/PaZuFa/pazufa-openapi
openapi-python-client generate --url https://codeberg.org/PaZuFa/parlamentszusammenfasser/raw/branch/main/docs/specs/openapi.yml --meta uv --output-path pazufa_api_client
```

## Usage

```bash
# run a spider for current 'wahlperiode'
scrapy runspider scraper_BE/spiders/gesetz_vorgang.py

# run a spider for specific 'wahlperiode'
scrapy runspider -a wahlperiode=18 scraper_BE/spiders/gesetz_vorgang.py
```
