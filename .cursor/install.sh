#!/usr/bin/env bash
# Cloud Agent install script for NeoScaffold.
# Runs from /workspace after the repository is checked out. Idempotent: safe to
# re-run to refresh dependencies. Installs the Python 3.10 backend (via uv) and
# the Node 18 Ember frontend (via nvm). PATHs are set explicitly so this works
# regardless of the base image's default shell profile.
set -euo pipefail

# --- Backend: Python 3.10 managed by uv ---
command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh \
  | env INSTALLER_NO_MODIFY_PATH=1 sh
export PATH="$HOME/.local/bin:$PATH"

cd /workspace/server
[ -d .venv ] || uv venv --python 3.10
uv sync
# Dev tooling the repo uses for tests/lint but does not pin in the runtime lockfile.
uv pip install pytest ruff mypy

# --- Frontend: Node 18 (Ember CLI) managed by nvm ---
export NVM_DIR="$HOME/.nvm"
if [ ! -s "$NVM_DIR/nvm.sh" ]; then
  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm install 18 >/dev/null
export PATH="$(dirname "$(nvm which 18)"):$PATH"

cd /workspace/neoscaffold
npm ci --no-audit --no-fund

echo "install.sh complete: python=$(/workspace/server/.venv/bin/python --version) node=$(node --version)"
