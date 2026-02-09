#!/usr/bin/env bash
set -euo pipefail

# Project-level skill bootstrap for the drone project.
# Creates symlinks in .claude/skills/ and .agents/skills/ so that
# Claude Code and Codex discover skills defined in support/skills/.
#
# Idempotent — safe to run repeatedly.
# Usage: ./ensure-skills.sh

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

SKILL_SOURCE="$SCRIPT_DIR/support/skills"

TARGETS=(
  "$SCRIPT_DIR/.claude/skills"
  "$SCRIPT_DIR/.agents/skills"
)

created=0
skipped=0
warnings=0

if [[ ! -d "$SKILL_SOURCE" ]]; then
  echo "No skills directory found at $SKILL_SOURCE"
  exit 0
fi

for skill_dir in "$SKILL_SOURCE"/*/; do
  [[ -f "$skill_dir/SKILL.md" ]] || continue
  skill_name="$(basename "$skill_dir")"
  source_real="$(cd "$skill_dir" && pwd -P)"

  for target_base in "${TARGETS[@]}"; do
    target="$target_base/$skill_name"
    mkdir -p "$target_base"

    if [[ -e "$target" ]]; then
      if [[ -d "$target" ]]; then
        existing_real="$(cd "$target" && pwd -P)"
        if [[ "$existing_real" == "$source_real" ]]; then
          : $((skipped++))
          continue
        fi
      fi
      echo "WARN: $target exists but points elsewhere, skipping"
      : $((warnings++))
      continue
    fi

    ln -s "$skill_dir" "$target"
    echo "  created: $target -> $skill_dir"
    : $((created++))
  done
done

echo ""
echo "Done: created=$created  skipped=$skipped  warnings=$warnings"
