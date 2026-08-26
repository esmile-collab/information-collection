#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_VENV="$WORKSPACE/.tools/source-tools-venv"
XHS_DIR="$WORKSPACE/.tools/vendor/XHS-Downloader"
MODE="${1:-all}"
MISSING_REQUIRED=0

case "$MODE" in
  all|video|social|reddit) ;;
  *)
    printf '用法：%s [all|video|social|reddit]\n' "$0" >&2
    exit 2
    ;;
esac

check_command() {
  local name="$1"
  local level="${2:-required}"
  if command -v "$name" >/dev/null 2>&1; then
    printf 'OK  %s  %s\n' "$name" "$(command -v "$name")"
  else
    printf '%s %s\n' "$( [ "$level" = required ] && printf 'MISS' || printf 'WARN' )" "$name"
    if [ "$level" = required ]; then
      MISSING_REQUIRED=1
    fi
  fi
}

check_venv_command() {
  local name="$1"
  local level="${2:-required}"
  local path="$SOURCE_VENV/bin/$name"
  if [ -x "$path" ]; then
    printf 'OK  %s  %s\n' "$name" "$("$path" --version 2>/dev/null | head -1)"
  else
    printf '%s %s  run ./scripts/bootstrap-source-tools.sh\n' \
      "$( [ "$level" = required ] && printf 'MISS' || printf 'WARN' )" "$name"
    if [ "$level" = required ]; then
      MISSING_REQUIRED=1
    fi
  fi
}

check_command rg

if [ "$MODE" = all ] || [ "$MODE" = video ]; then
  check_command ffmpeg
  check_command ffprobe
  check_command node optional
  check_venv_command yt-dlp
  check_venv_command youtube_transcript_api optional
fi

if [ "$MODE" = all ] || [ "$MODE" = social ]; then
  check_venv_command gallery-dl
  check_command swift optional
  if [ -f "$XHS_DIR/main.py" ]; then
    printf 'OK  XHS-Downloader  %s\n' "$(git -C "$XHS_DIR" rev-parse --short HEAD 2>/dev/null || printf unknown)"
  else
    printf 'WARN XHS-Downloader  run ./scripts/bootstrap-source-tools.sh --with-xhs\n'
  fi
fi

if [ "$MODE" = all ] || [ "$MODE" = reddit ]; then
  check_command opencli
  check_command agent-reach optional
fi

if [ "$MODE" = all ] || [ "$MODE" = social ] || [ "$MODE" = reddit ]; then
  WEBBRIDGE_BIN="${KIMI_WEBBRIDGE_BIN:-}"
  if [ -z "$WEBBRIDGE_BIN" ] && command -v kimi-webbridge >/dev/null 2>&1; then
    WEBBRIDGE_BIN="$(command -v kimi-webbridge)"
  fi
  if [ -z "$WEBBRIDGE_BIN" ] && [ -x "${HOME:?}/.kimi-webbridge/bin/kimi-webbridge" ]; then
    WEBBRIDGE_BIN="${HOME:?}/.kimi-webbridge/bin/kimi-webbridge"
  fi
  if [ -n "$WEBBRIDGE_BIN" ]; then
    printf 'OK  Kimi WebBridge  %s\n' "$WEBBRIDGE_BIN"
  else
    printf 'WARN Kimi WebBridge\n'
  fi
fi

exit "$MISSING_REQUIRED"
