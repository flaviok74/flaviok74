#!/bin/bash
# SessionStart hook: prepare the environment for Claude Code on the web.
# - Installs Python dependencies so the Flask app can run.
# - Ensures the Remotion agent skill is installed (idempotent).
set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(pwd)}"

# 1. Python dependencies for the RFQ Price Analyzer Flask app.
#    --ignore-installed blinker: skip uninstalling the Debian-managed blinker,
#    which pip cannot remove (no RECORD file).
if [ -f requirements.txt ]; then
  pip install --quiet --disable-pip-version-check --ignore-installed blinker -r requirements.txt
fi

# 2. Remotion agent skill — install/update from the official repo.
#    Safe to re-run; the skills CLI is idempotent and uses skills-lock.json.
npx --yes skills add remotion-dev/skills --yes >/dev/null 2>&1 || true

echo "SessionStart hook complete: Python deps installed, Remotion skill ensured."
