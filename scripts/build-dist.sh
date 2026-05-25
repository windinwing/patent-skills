#!/usr/bin/env bash
# 构建 ClawHub 发布用纯净包 → patents/dist/{patent-search,patent-transaction,patent-disclosure}
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DST="$ROOT/dist"

rm -rf "$DST"
mkdir -p "$DST"

copy_skill() {
  local name="$1"
  shift
  local src="$ROOT/$name"
  local out="$DST/$name"
  mkdir -p "$out"
  for f in "$@"; do
    if [[ -f "$src/$f" ]]; then
      cp "$src/$f" "$out/"
    fi
  done
  if [[ -f "$src/.gitignore" ]]; then
    cp "$src/.gitignore" "$out/"
  fi
  cp "$ROOT/LICENSE" "$out/LICENSE"
}

# --- patent-search：仅运行时与文档 ---
copy_skill patent-search \
  main.py patent_api.py patent_skill.py patent_token.py \
  excel_export.py export_deps.py \
  config.example.json SKILL.md README.md CHANGELOG.md COMPLIANCE.md

# --- patent-transaction ---
copy_skill patent-transaction \
  main.py trade_api.py excel_export.py export_deps.py \
  config.example.json SKILL.md README.md due-diligence.md

# --- patent-disclosure ---
copy_skill patent-disclosure \
  main.py docx_export.py export_deps.py \
  template.md checklist.md requirements.txt \
  SKILL.md README.md

cp "$ROOT/README.clawhub.md" "$DST/README.md"
cp "$ROOT/INSTALL.md" "$DST/INSTALL.md"
cp "$ROOT/PUBLISH.md" "$DST/PUBLISH.md"
cp "$ROOT/LICENSE" "$DST/LICENSE"

# 移除开发目录内旧的嵌套 dist
rm -rf "$ROOT/patent-search/dist"

echo "✅ 纯净包已生成: $DST"
echo "   patent-search/       $(find "$DST/patent-search" -type f | wc -l | tr -d ' ') 个文件"
echo "   patent-transaction/  $(find "$DST/patent-transaction" -type f | wc -l | tr -d ' ') 个文件"
echo "   patent-disclosure/   $(find "$DST/patent-disclosure" -type f | wc -l | tr -d ' ') 个文件"
echo ""
echo "发布到 ClawHub：分别上传 dist 下各目录，或见 dist/README.md"
