#!/usr/bin/env bash
# Example: sh docker/find-digest.sh ghcr.io/astral-sh/uv:python3.12-bookworm-slim
set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <image-tag>" >&2
    echo "Example: $0 ghcr.io/astral-sh/uv:python3.12-bookworm-slim" >&2
    exit 1
fi

IMAGE_TAG="$1"

podman manifest inspect "${IMAGE_TAG}" | \
    python3 -c "
import sys, json
manifests = json.load(sys.stdin).get('manifests', [])
for m in manifests:
    print(m['digest'], m['platform'])
"
