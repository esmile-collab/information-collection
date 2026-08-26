#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
TOOLS_DIR="$WORKSPACE/.tools"
SOURCE_VENV="$TOOLS_DIR/source-tools-venv"
XHS_DIR="$TOOLS_DIR/vendor/XHS-Downloader"
WITH_XHS=0

usage() {
  printf '用法：%s [--with-xhs]\n' "$0"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --with-xhs)
      WITH_XHS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
done

mkdir -p "$TOOLS_DIR/vendor"
python3 -m venv "$SOURCE_VENV"
"$SOURCE_VENV/bin/python" -m pip install --upgrade pip
"$SOURCE_VENV/bin/python" -m pip install -r "$WORKSPACE/requirements-source-tools.txt"

if [ "$WITH_XHS" -eq 1 ]; then
  if [ ! -d "$XHS_DIR/.git" ]; then
    git clone --depth 1 https://github.com/JoeanAmier/XHS-Downloader.git "$XHS_DIR"
  fi

  if command -v uv >/dev/null 2>&1; then
    (cd "$XHS_DIR" && uv sync --no-dev)
  else
    python3 -m venv "$XHS_DIR/.venv"
    "$XHS_DIR/.venv/bin/python" -m pip install --upgrade pip
    "$XHS_DIR/.venv/bin/python" -m pip install -r "$XHS_DIR/requirements.txt"
  fi
fi

"$SCRIPT_DIR/check-source-tools.sh" all || true
