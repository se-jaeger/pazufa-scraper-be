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

## Development

### Code hygene

If you want to make use of git hooks run

```bash
prek install
```

to install and

```bash
prek run --all-files
```

to run all hooks for all files.

For more fine-grained control use

```bash
# linting
prek run ruff-check --all-files
# formatting
prek run formatting --all-files
# type checking
prek run ty --all-files
# testing
prek run test --all-files
```

### Testing

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
