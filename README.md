# `pazufa-scraper-be` — Abgeordnetenhaus von Berlin

## Setup

Requires Python 3.12+.

```bash
uv install

# NOTE: this is temporary and will be replaced by this: https://codeberg.org/PaZuFa/pazufa-openapi
openapi-python-client generate --url https://codeberg.org/PaZuFa/parlamentszusammenfasser/raw/branch/main/openapi.yml --meta uv --config openapi-python-client-config.yaml
```

## Usage

```bash
# run a spider for current 'wahlperiode'
scrapy runspider pazufa_scraper_be/spiders/gesetz_vorgang.py

# run a spider for specific 'wahlperiode'
scrapy runspider -s WAHLPERIODE=18 pazufa_scraper_be/spiders/gesetz_vorgang.py
```


## Testing

Unit and integration tests are organized as 

```text
tests
├── integration
└── unit
    └── pazufa_scraper_be
```

To run unit tests use

```bash
pytest
pytest tests/unit
```

Note: Below is yet to be implemented.

To run integration tests use

```bash
pytest -m integration
```

Note: Integration tests are marked with `@pytest.mark.integration` and only executed when explicitly requested.
