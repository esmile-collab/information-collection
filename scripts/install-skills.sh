#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(cd "$SCRIPT_DIR/.." && pwd)"
SOURCE_DIR="$WORKSPACE/.agents/skills"
TARGET_KIND="agents"

usage() {
  printf '用法：%s [--target agents|codex]\n' "$0"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || { usage >&2; exit 2; }
      TARGET_KIND="$2"
      shift 2
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

case "$TARGET_KIND" in
  agents)
    TARGET_DIR="${AGENTS_SKILLS_DIR:-${HOME:?}/.agents/skills}"
    ;;
  codex)
    TARGET_DIR="${CODEX_HOME:-${HOME:?}/.codex}/skills"
    ;;
  *)
    printf '未知目标：%s\n' "$TARGET_KIND" >&2
    usage >&2
    exit 2
    ;;
esac

SKILLS=(
  research-decision-router
  video-source-capture
  social-source-capture
  reddit-source-capture
)

mkdir -p "$TARGET_DIR"

for skill in "${SKILLS[@]}"; do
  source_path="$SOURCE_DIR/$skill"
  target_path="$TARGET_DIR/$skill"
  [ -f "$source_path/SKILL.md" ] || {
    printf '缺少 Skill 真源：%s\n' "$source_path" >&2
    exit 1
  }

  if [ -L "$target_path" ]; then
    current_target="$(readlink "$target_path")"
    if [ "$current_target" = "$source_path" ]; then
      printf 'OK   %s\n' "$target_path"
      continue
    fi
    printf '冲突：%s 已指向 %s\n' "$target_path" "$current_target" >&2
    exit 1
  fi

  if [ -e "$target_path" ]; then
    printf '冲突：%s 已存在，未覆盖\n' "$target_path" >&2
    exit 1
  fi

  ln -s "$source_path" "$target_path"
  printf 'LINK %s -> %s\n' "$target_path" "$source_path"
done

printf '安装完成。请重新启动宿主或新建任务，让 Skill 列表重新扫描。\n'
