"""Merge missing PUA entries from DVN dictionaries into nom_viet.dict.yaml.

Output:
  - Backs up original to nom_viet.dict.yaml.bak (only on first run)
  - Appends new entries inside a clearly-marked block:
      # >>> DVN-PUA-MERGE-BEGIN
      ... entries ...
      # <<< DVN-PUA-MERGE-END
    so the merge can be reverted with a single regex-edit later.
  - Bumps the version field in the YAML header.

Weight policy:
  - 55 if pair appears in BOTH gdnhv and tdcndg (two-source agreement)
  - 50 otherwise

Comment format: "<qn_reading> [<source>]"
  e.g. "đắt [gdnhv]" or "chăm [gdnhv+tdcndg]"
"""
from __future__ import annotations

import io
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_pua import (  # noqa: E402
    _is_han_or_pua,
    extract_gdnhv,
    extract_tdcndg,
    qn_to_bare,
    qn_to_telex,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
DICT_PATH = REPO / "nom_viet.dict.yaml"
BACKUP_PATH = REPO / "nom_viet.dict.yaml.bak"
BEGIN_MARKER = "# >>> DVN-PUA-MERGE-BEGIN"
END_MARKER = "# <<< DVN-PUA-MERGE-END"


def load_existing_pairs_and_index() -> tuple[set[tuple[str, str]], dict[str, set[str]]]:
    pairs: set[tuple[str, str]] = set()
    bare_index: dict[str, set[str]] = {}
    in_body = False
    with DICT_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            if not in_body:
                if line.startswith("..."):
                    in_body = True
                continue
            line = line.rstrip("\n")
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            text, code = parts[0], parts[1]
            pairs.add((text, code))
            # Index by bare reading for fuzzy "is this char already covered for this reading?"
            for syl in code.split():
                bare = "".join(c for c in syl if c.isalpha() and c not in "sfrxj")
                # Strip telex compounds to bare letters
                bare = (bare
                        .replace("aa", "a").replace("aw", "a")
                        .replace("ee", "e")
                        .replace("oo", "o").replace("ow", "o")
                        .replace("uw", "u")
                        .replace("dd", "d"))
                bare_index.setdefault(bare, set()).add(text)
    return pairs, bare_index


def remove_existing_merge_block(content: str) -> str:
    """If a previous merge block exists, strip it so we can re-merge cleanly."""
    pattern = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER) + r"\n?",
        re.DOTALL,
    )
    return pattern.sub("", content)


def main() -> int:
    # Pull pair sources, preserving original QN reading per source
    gdnhv_pairs = extract_gdnhv()  # list[(reading, char)]
    tdcndg_pairs = extract_tdcndg()
    print(f"gdnhv PUA pairs:  {len(gdnhv_pairs):,}")
    print(f"tdcndg PUA pairs: {len(tdcndg_pairs):,}")

    # Group by (qn_reading, char) -> sources, where reading keeps diacritics.
    # For pairs where bare-readings match across sources but spelling differs slightly,
    # we treat them as separate entries (rare; safer than guessing equivalence).
    by_pair: dict[tuple[str, str], dict[str, str | set[str]]] = {}
    for reading, text in gdnhv_pairs:
        key = (reading, text)
        by_pair.setdefault(key, {"reading": reading, "sources": set()})["sources"].add("gdnhv")  # type: ignore[union-attr]
    for reading, text in tdcndg_pairs:
        key = (reading, text)
        by_pair.setdefault(key, {"reading": reading, "sources": set()})["sources"].add("tdcndg")  # type: ignore[union-attr]
    print(f"Combined unique (reading, char) pairs: {len(by_pair):,}")

    # Two-source agreement check uses bare-reading match across sources for the same char.
    # Build a per-char bare-reading-source map.
    char_bare_sources: dict[str, dict[str, set[str]]] = {}
    for (reading, text), info in by_pair.items():
        bare = qn_to_bare(reading)
        char_bare_sources.setdefault(text, {}).setdefault(bare, set()).update(info["sources"])  # type: ignore[arg-type]

    existing_pairs, existing_bare_index = load_existing_pairs_and_index()
    print(f"Existing dict entries: {len(existing_pairs):,}")

    # Build new entries, deduped by (text, telex_code)
    seen_out: set[tuple[str, str]] = set()
    rows: list[tuple[str, str, int, str]] = []  # text, code, weight, comment
    skipped_already = 0
    for (reading, text), info in by_pair.items():
        # Skip if no PUA char in text (defensive — extractors already filter)
        if not any(_is_han_or_pua(c) for c in text):
            continue
        bare = qn_to_bare(reading)
        # Skip if bare-reading + char already covered in existing dict
        if bare in existing_bare_index and text in existing_bare_index[bare]:
            skipped_already += 1
            continue
        telex = qn_to_telex(reading)
        if (text, telex) in existing_pairs:
            skipped_already += 1
            continue
        if (text, telex) in seen_out:
            continue
        seen_out.add((text, telex))
        # Two-source agreement on bare-reading for this char → weight 55
        sources = info["sources"]  # type: ignore[assignment]
        agreed = len(char_bare_sources[text].get(bare, set())) >= 2
        weight = 55 if agreed else 50
        src_tag = "+".join(sorted(sources))  # type: ignore[arg-type]
        comment = f"{reading} [{src_tag}]"
        rows.append((text, telex, weight, comment))

    print(f"Skipped (already covered in existing dict): {skipped_already:,}")
    print(f"New entries to append: {len(rows):,}")

    # Backup once
    if not BACKUP_PATH.exists():
        shutil.copy2(DICT_PATH, BACKUP_PATH)
        print(f"Backed up original to: {BACKUP_PATH.name}")
    else:
        print(f"Backup already exists at {BACKUP_PATH.name} (left untouched)")

    # Read, strip any prior merge block, bump version, append new block
    content = DICT_PATH.read_text(encoding="utf-8")
    content = remove_existing_merge_block(content)
    # Bump minor version: "1.0" → "1.1", "1.1" → "1.2", etc.
    # Falls back to appending +dvn1 if the version isn't a recognizable major.minor.
    def bump_version(m: re.Match) -> str:
        v = m.group(1)
        mm = re.fullmatch(r"(\d+)\.(\d+)", v)
        if mm:
            major, minor = mm.group(1), int(mm.group(2))
            return f'version: "{major}.{minor + 1}"'
        return f'version: "{v}+dvn1"'
    content, n_subst = re.subn(r'version:\s*"([^"]+)"', bump_version, content, count=1)
    if n_subst != 1:
        print("WARNING: could not bump version field — appending without version change")

    # Build appended block
    block_lines = [
        "",
        BEGIN_MARKER,
        f"# Auto-merged {len(rows):,} PUA entries from Digitizing Vietnam dictionaries",
        "# (gdnhv = Giúp đọc Nôm và Hán Việt; tdcndg = Từ điển Chữ Nôm Dẫn Giải).",
        "# Weight 55 = both sources agree on reading; 50 = single source.",
        "# To revert: delete everything between BEGIN/END markers (including markers).",
    ]
    for text, code, weight, comment in rows:
        block_lines.append(f"{text}\t{code}\t{weight}\t{comment}")
    block_lines.append(END_MARKER)
    block_lines.append("")

    if not content.endswith("\n"):
        content += "\n"
    content += "\n".join(block_lines)

    DICT_PATH.write_text(content, encoding="utf-8")
    print(f"Wrote {DICT_PATH.name} ({len(rows):,} new entries inside marked block)")

    # Counts breakdown
    w55 = sum(1 for _, _, w, _ in rows if w == 55)
    w50 = sum(1 for _, _, w, _ in rows if w == 50)
    print(f"  weight 55 (multi-source agreement): {w55:,}")
    print(f"  weight 50 (single source):          {w50:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
