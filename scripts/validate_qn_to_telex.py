"""Sanity-check qn_to_telex by spot-checking against existing dict entries.

Strategy: many existing dict comments START with the QN reading (e.g.
'người ấy', 'ngày nay'). For single-syllable rows, we can compare the
converted comment-prefix to the row's telex code and see how often they match.

This is approximate — comments aren't always clean readings — so we only
report rate, not pass/fail.
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from analyze_pua import qn_to_telex  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DICT = Path(__file__).resolve().parent.parent / "nom_viet.dict.yaml"

total = 0
match = 0
mismatches: list[tuple[str, str, str, str]] = []

in_body = False
with DICT.open("r", encoding="utf-8") as f:
    for line in f:
        if not in_body:
            if line.startswith("..."):
                in_body = True
            continue
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 4:
            continue
        text, code, weight, comment = parts[0], parts[1], parts[2], parts[3]
        # Single-syllable code: no space
        if " " in code:
            continue
        # Take first whitespace-delimited word of the comment as candidate QN
        candidate = comment.strip().split()[0] if comment.strip() else ""
        # Strip punctuation
        candidate = candidate.rstrip(",.;:!?…")
        if not candidate or any(c.isascii() and not c.isalpha() for c in candidate):
            continue
        # Skip comments that don't look like QN (e.g. start with digit, or are Han)
        if not any(c.isalpha() for c in candidate):
            continue
        try:
            converted = qn_to_telex(candidate)
        except Exception:
            continue
        total += 1
        if converted == code:
            match += 1
        else:
            if len(mismatches) < 30:
                mismatches.append((text, code, candidate, converted))

print(f"Sampled rows: {total:,}")
if total:
    print(f"Match rate: {match:,} / {total:,} = {100*match/total:.1f}%")
print("\nFirst 30 mismatches (text, dict_code, comment_candidate, converted):")
for row in mismatches:
    print(f"  {row[0]}\t{row[1]}\t{row[2]}\t{row[3]}")
