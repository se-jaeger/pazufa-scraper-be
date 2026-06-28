# Handling the `Dockerfile`s

`podman` / `docker` cli should be interchangable. Using `podman` here by default.

## Default route (macOS)

```bash
brew install podman
podman machine init
podman machine start
podman build -t pazufa-scraper-be .
mkdir -p .cache .errors .scrapy/httpcache
podman run --rm \
   -v "$(pwd)/.cache:/scraper/.cache" \
   -v "$(pwd)/.errors:/scraper/.errors" \
   -v "$(pwd)/.scrapy/httpcache:/scraper/.scrapy/httpcache" \
   pazufa-scraper-be \
   runspider pazufa_scraper_be/spiders/gesetz_vorgang.py
```

## Updating digests

If any digest needs updating [find-digest.sh](./find-digest.sh) can help, e.g. via

```bash
sh docker/find-digest.sh ghcr.io/astral-sh/uv:python3.12-bookworm-slim
```

## Troubleshooting

To run with tracing

```bash
podman run --rm \
   -v "$(pwd)/.cache:/scraper/.cache" \
   -v "$(pwd)/.errors:/scraper/.errors" \
   -v "$(pwd)/.scrapy/httpcache:/scraper/httpcache" \
   -e PYTHONFAULTHANDLER=1 \
   pazufa-scraper-be-main \
   runspider pazufa_scraper_be/spiders/gesetz_vorgang.py
```

On macOS with podman the above can produce the error in [error.txt](./error.txt). Source TBD, likely related to the cryptography package. For this specific issue you can alternatively you `docker/Dockerfile.mac`.

## `docker/Dockerfile.mac`

A rudimentary version with only the essentials to be running on macOS.

Build via

```bash
podman build -f docker/mac.Dockerfile -t pazufa-scraper-be-mac .
```

Run via

```bash
podman run --rm \
    -e PAZUFA_API_BASE_URL=http://host.containers.internal:8080 \
    -e PAZUFA_API_TOKEN=your_api_token \
    -e PAZUFA_LLM_TOKEN=your_llm_token \
    -e PAZUFA_LLM_MODEL=openrouter/openai/gpt-5-nano \
    -e WAHLPERIODE=19 \
    -v "$(pwd)/.cache:/scraper/.cache" \
    -v "$(pwd)/.errors:/scraper/.errors" \
    -v "$(pwd)/.scrapy/httpcache:/scraper/httpcache" \
    pazufa-scraper-be-mac
```

To debug use

```bash
podman run --rm \
    -e PAZUFA_API_BASE_URL=http://host.containers.internal:8080 \
    -e WAHLPERIODE=19 \
    -e LOG_LEVEL=DEBUG \
    -e PYTHONFAULTHANDLER=1 \
    pazufa-scraper-be-mac \
    /bin/sh -c 'uv run --no-dev --frozen scrapy runspider \
        -s LOG_LEVEL=DEBUG -s WAHLPERIODE=19 \
        pazufa_scraper_be/spiders/gesetz_vorgang.py 2>&1; echo "Exit: $?"'
```

`PYTHONFAULTHANDLER=1` tells Python to print a full traceback to stderr when it receives SIGILL/SIGSEGV/etc., so you'll see exactly which C extension is crashing. This should reveal any culprit.
