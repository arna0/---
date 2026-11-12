"""Make an English copy of the OpenAPI schema for the docs site.

Descriptions, summaries, titles and tag names are translated with en.json.
Enum values, defaults and examples are left alone, because they are the real
values the API accepts.
Usage: python docs-site/translate_openapi.py site/openapi.json site/openapi.en.json
"""
import json
import sys
from pathlib import Path

KEEP = {"enum", "default", "example", "examples", "const"}
EN = json.loads((Path(__file__).parent / "en.json").read_text(encoding="utf-8"))
missing = set()


def tr(s):
    if s in EN:
        return EN[s]
    if any("Ѐ" <= ch <= "ӿ" for ch in s):
        missing.add(s)
    return s


def walk(node, key=None):
    if key in KEEP:
        return node
    if isinstance(node, dict):
        return {k: walk(v, k) for k, v in node.items()}
    if isinstance(node, list):
        return [walk(v) for v in node]
    if isinstance(node, str):
        return tr(node)
    return node


src, dst = sys.argv[1], sys.argv[2]
schema = json.loads(Path(src).read_text(encoding="utf-8"))
Path(dst).write_text(json.dumps(walk(schema), ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {dst}; untranslated strings: {len(missing)}")
for s in sorted(missing):
    print("  -", s)
