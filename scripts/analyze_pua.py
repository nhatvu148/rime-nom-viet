"""Analyze PUA coverage in nom_viet.dict.yaml vs digitizing-vietnam dictionaries.

Reports:
  1. PUA entry count in existing dict (BMP PUA, SPUA-A, SPUA-B).
  2. (reading, char) pairs extractable from gdnhv.xml and tdcndg.xml.
  3. Missing PUA pairs that could be added.

No files are modified. Output to stdout; samples to scripts/missing_pua_sample.tsv.
"""
from __future__ import annotations

import io
import re
import sys
import unicodedata
from pathlib import Path
from xml.etree import ElementTree as ET

# Force stdout to UTF-8 so we can print Vietnamese / arrows on Windows cp1252 consoles.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
else:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

REPO = Path(__file__).resolve().parent.parent
DICT_PATH = REPO / "nom_viet.dict.yaml"
DV_ROOT = Path(r"C:\Users\alber\OneDrive\Desktop\Coding\digitizing-vietnam-website-1\data\dictionaries")
GDNHV = DV_ROOT / "giup-doc-nom-va-han-viet" / "gdnhv.xml"
TDCNDG = DV_ROOT / "tu-dien-chu-nom-dan-giai" / "tdcndg.xml"
SAMPLE_OUT = REPO / "scripts" / "missing_pua_sample.tsv"
EXTRACTED_FULL = REPO / "scripts" / "extracted_pua_full.tsv"
EXTRACTED_BY_CHAR = REPO / "scripts" / "extracted_pua_by_char.tsv"
MISSING_FULL = REPO / "scripts" / "missing_pua_full.tsv"


def is_pua(cp: int) -> str | None:
    if 0xE000 <= cp <= 0xF8FF:
        return "BMP"
    if 0xF0000 <= cp <= 0xFFFFD:
        return "SPUA-A"
    if 0x100000 <= cp <= 0x10FFFD:
        return "SPUA-B"
    return None


def chars_with_pua(s: str) -> list[tuple[str, str]]:
    out = []
    # iterate by codepoint (handle surrogate pairs correctly via str)
    for ch in s:
        zone = is_pua(ord(ch))
        if zone:
            out.append((ch, zone))
    return out


def load_existing_dict() -> tuple[set[tuple[str, str]], dict[str, int]]:
    """Return set of (text, code) pairs and PUA zone counts over distinct chars."""
    pairs: set[tuple[str, str]] = set()
    pua_chars: dict[str, str] = {}  # char -> zone
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
            for ch, zone in chars_with_pua(text):
                pua_chars[ch] = zone
    zone_counts: dict[str, int] = {}
    for zone in pua_chars.values():
        zone_counts[zone] = zone_counts.get(zone, 0) + 1
    return pairs, zone_counts


# Telex tone/diacritic stripping for matching readings across sources.
# The dict uses the schema's telex codes (e.g. "nguowfi"); the XML sources use
# Quốc ngữ with diacritics (e.g. "người"). For diff purposes we compare on
# bare-letter normalized form.
TELEX_TONE = set("sfrxj")

def telex_to_bare(s: str) -> str:
    """Strip telex compounds + tones to plain ascii letters. Lossy, used for matching."""
    s = s.lower()
    s = (s
         .replace("aa", "a").replace("aw", "a")
         .replace("ee", "e")
         .replace("oo", "o").replace("ow", "o")
         .replace("uw", "u")
         .replace("dd", "d"))
    return "".join(c for c in s if c.isalpha() and c not in TELEX_TONE)


# --- Quốc ngữ → telex ---------------------------------------------------------
# The schema's telex follows the standard convention used by Vietnamese typists:
#   vowels with circumflex:   â→aa, ê→ee, ô→oo
#   vowels with horn:         ơ→ow, ư→uw
#   vowel with breve:         ă→aw
#   d-with-stroke:            đ→dd
#   tones (suffix on syllable): sắc→s, huyền→f, hỏi→r, ngã→x, nặng→j
# The combining tone is appended at the end of the syllable, after all letters.
# Example: người = ng + ươ + i + huyền  →  ng + uw + ow + i + f  →  "nguowfi"
#                                          (i.e. ư=uw, ơ=ow, then i, then f)
# We process per syllable (whitespace split) so multi-syllable readings work.

_BASE_VOWEL = {
    "a": "a", "ă": "aw", "â": "aa",
    "e": "e", "ê": "ee",
    "i": "i",
    "o": "o", "ô": "oo", "ơ": "ow",
    "u": "u", "ư": "uw",
    "y": "y",
}
# Tone codes from Unicode combining marks
_TONE = {
    "́": "s",  # acute → sắc
    "̀": "f",  # grave → huyền
    "̉": "r",  # hook above → hỏi
    "̃": "x",  # tilde → ngã
    "̣": "j",  # dot below → nặng
}


def qn_syllable_to_telex(syl: str) -> str:
    """Convert one Quốc ngữ syllable to telex. Lowercase, no spaces.

    Tone placement rule (verified against actual dict entries):
      The tone code is emitted immediately after the *toned vowel's* telex
      expansion — not at the end of the syllable. Examples:
        ngày  (a + grave) → ng + a + f + y    = 'ngafy'
        việt  (ê + nặng)  → v + i + ee + j + t = 'vieejt'
        người (ơ + huyền) → ng + uw + ow + f + i = 'nguwowfi'
    """
    syl = syl.lower()
    nfd = unicodedata.normalize("NFD", syl)
    # Walk NFD, group each base char with its (non-tone) combining marks; track tone.
    slots: list[dict] = []  # each: {"base": str, "marks": list[str], "tone": str|None}
    cur: dict | None = None
    pending_tone_idx = -1
    for ch in nfd:
        if unicodedata.combining(ch):
            if ch in _TONE:
                if cur is not None:
                    cur["tone"] = _TONE[ch]
            else:
                if cur is not None:
                    cur["marks"].append(ch)
            continue
        cur = {"base": ch, "marks": [], "tone": None}
        slots.append(cur)
    # Recompose each slot's base+marks via NFC, then expand to telex.
    out = []
    for slot in slots:
        composed = unicodedata.normalize("NFC", slot["base"] + "".join(slot["marks"]))
        if composed == "đ":
            out.append("dd")
        elif composed in _BASE_VOWEL:
            out.append(_BASE_VOWEL[composed])
        else:
            out.append(composed)
        if slot["tone"]:
            out.append(slot["tone"])
    return "".join(out)


def qn_to_telex(s: str) -> str:
    """Convert a (possibly multi-syllable) Quốc ngữ reading to telex.
    Multi-syllable readings get a single space between syllables — that
    matches how the existing dict encodes phrases like 'vieetj nam'."""
    parts = s.strip().split()
    return " ".join(qn_syllable_to_telex(p) for p in parts if p)


def qn_to_bare(s: str) -> str:
    """Strip Vietnamese diacritics from Quốc ngữ to plain ascii letters."""
    s = s.lower().strip()
    # Decompose and drop combining marks
    nfd = unicodedata.normalize("NFD", s)
    stripped = "".join(c for c in nfd if not unicodedata.combining(c))
    # Đ/đ doesn't decompose
    stripped = stripped.replace("đ", "d").replace("Đ", "d")
    return "".join(c for c in stripped if c.isalpha())


def _is_han_or_pua(c: str) -> bool:
    """Match any Han/Nôm character: CJK Unified, all extensions A–I, compatibility,
    radicals, plus all PUA ranges (chunom.org allocations)."""
    cp = ord(c)
    return (
        0x3400  <= cp <= 0x4DBF  or  # CJK Ext A
        0x4E00  <= cp <= 0x9FFF  or  # CJK Unified
        0xF900  <= cp <= 0xFAFF  or  # CJK Compatibility
        0x20000 <= cp <= 0x2A6DF or  # CJK Ext B
        0x2A700 <= cp <= 0x2B73F or  # CJK Ext C
        0x2B740 <= cp <= 0x2B81F or  # CJK Ext D
        0x2B820 <= cp <= 0x2CEAF or  # CJK Ext E
        0x2CEB0 <= cp <= 0x2EBEF or  # CJK Ext F
        0x2EBF0 <= cp <= 0x2EE5F or  # CJK Ext G (BMP-adjacent block)
        0x30000 <= cp <= 0x3134F or  # CJK Ext G
        0x31350 <= cp <= 0x323AF or  # CJK Ext H
        0x323B0 <= cp <= 0x33479 or  # CJK Ext I
        is_pua(cp) is not None
    )


def extract_gdnhv() -> list[tuple[str, str]]:
    """Return list of (qn_reading, char) for every Han/Nôm or PUA orth."""
    out = []
    tree = ET.parse(GDNHV)
    for entry in tree.iterfind(".//entry"):
        hdwd = entry.find("hdwd")
        if hdwd is None or not hdwd.text:
            continue
        reading = hdwd.text.strip()
        ortho = entry.find("orthography")
        if ortho is None:
            continue
        for orth in ortho.findall("orth"):
            if not orth.text:
                continue
            text = orth.text.strip()
            if any(_is_han_or_pua(c) for c in text):
                out.append((reading, text))
    return out


def extract_tdcndg() -> list[tuple[str, str]]:
    out = []
    tree = ET.parse(TDCNDG)
    for entry in tree.iterfind(".//entry"):
        qn = entry.find("qn")
        hn = entry.find("hn")
        if qn is None or hn is None or not qn.text or not hn.text:
            continue
        reading = qn.text.strip()
        text = hn.text.strip()
        if any(_is_han_or_pua(c) for c in text):
            out.append((reading, text))
    return out


def main() -> int:
    print("Loading existing dict...")
    existing_pairs, existing_zone_counts = load_existing_dict()
    print(f"  Existing entries: {len(existing_pairs):,}")
    print(f"  Distinct PUA chars in existing dict: {existing_zone_counts}")

    # Build bare-reading -> set of chars index from existing dict
    existing_bare_index: dict[str, set[str]] = {}
    for text, code in existing_pairs:
        # The dict is keyed by the schema's telex code, but for the diff we want
        # to ask: "is there ANY entry mapping this Nom char to a reading whose
        # bare form matches?". Simpler: index existing pairs by (bare(code), text).
        bare = telex_to_bare(code)
        existing_bare_index.setdefault(bare, set()).add(text)

    print("Extracting gdnhv.xml...")
    g = extract_gdnhv()
    print(f"  PUA-bearing pairs: {len(g):,}")
    print("Extracting tdcndg.xml...")
    t = extract_tdcndg()
    print(f"  PUA-bearing pairs: {len(t):,}")

    # Combine sources, dedup
    combined: dict[tuple[str, str], list[str]] = {}
    for reading, text in g:
        combined.setdefault((qn_to_bare(reading), text), []).append("gdnhv")
    for reading, text in t:
        combined.setdefault((qn_to_bare(reading), text), []).append("tdcndg")
    print(f"  Combined unique (bare-reading, char): {len(combined):,}")

    # Diff
    missing = []
    for (bare, text), sources in combined.items():
        if bare in existing_bare_index and text in existing_bare_index[bare]:
            continue
        missing.append((bare, text, "+".join(sorted(set(sources)))))

    print(f"\nMissing pairs (PUA chars under readings not in existing dict): {len(missing):,}")

    # PUA-zone breakdown of missing
    zone_breakdown: dict[str, int] = {}
    distinct_missing_chars: set[str] = set()
    for _, text, _ in missing:
        for ch, zone in chars_with_pua(text):
            zone_breakdown[zone] = zone_breakdown.get(zone, 0) + 1
            distinct_missing_chars.add(ch)
    print(f"  Distinct missing PUA chars: {len(distinct_missing_chars):,}")
    print(f"  PUA zone breakdown (per-char occurrences): {zone_breakdown}")

    # How many of those distinct chars are NEW (not present anywhere in existing dict)?
    existing_pua_chars: set[str] = set()
    for text, _code in existing_pairs:
        for ch, _z in chars_with_pua(text):
            existing_pua_chars.add(ch)
    truly_new = distinct_missing_chars - existing_pua_chars
    print(f"  Of those, never-seen-before in existing dict: {len(truly_new):,}")

    SAMPLE_OUT.parent.mkdir(parents=True, exist_ok=True)

    # ---- Self-check the qn→telex converter against the existing dict ----------
    # For every (text, code) in the existing dict that has a 'comment' column,
    # we don't have a clean QN reading to round-trip from. Instead we sanity-check
    # by inverting telex → expected QN form and confirming a few known cases below.
    test_cases = [
        ("người", "nguwowfi"),
        ("việt nam", "vieejt nam"),  # actual dict uses 'vieejt' (README has typo)
        ("ngày", "ngafy"),
        ("hoài", "hoafi"),
        ("ăn", "awn"),
        ("đi", "ddi"),
        ("ế", "ees"),
        ("ồ", "oof"),
        ("ờ", "owf"),
        ("ứ", "uws"),
        ("ả", "ar"),
        ("ã", "ax"),
        ("ạ", "aj"),
    ]
    print("\nqn→telex self-check:")
    for qn, expected in test_cases:
        got = qn_to_telex(qn)
        ok = "OK " if got == expected else "MISS"
        print(f"  [{ok}] {qn!r:>20} -> {got!r:<15} (expected {expected!r})")

    # 1. Full extracted catalog: every (reading, char, source) row from both XMLs.
    #    Adds telex_code column derived from the QN reading.
    with EXTRACTED_FULL.open("w", encoding="utf-8") as f:
        f.write("reading\ttelex_code\tchar\tcodepoints\tsource\tin_existing_dict\n")
        for reading, text in g:
            cps = " ".join(f"U+{ord(c):04X}" for c in text)
            telex = qn_to_telex(reading)
            in_dict = "Y" if (qn_to_bare(reading) in existing_bare_index and
                              text in existing_bare_index[qn_to_bare(reading)]) else "N"
            f.write(f"{reading}\t{telex}\t{text}\t{cps}\tgdnhv\t{in_dict}\n")
        for reading, text in t:
            cps = " ".join(f"U+{ord(c):04X}" for c in text)
            telex = qn_to_telex(reading)
            in_dict = "Y" if (qn_to_bare(reading) in existing_bare_index and
                              text in existing_bare_index[qn_to_bare(reading)]) else "N"
            f.write(f"{reading}\t{telex}\t{text}\t{cps}\ttdcndg\t{in_dict}\n")
    print(f"\nWrote full extracted catalog ({len(g) + len(t):,} rows) to: {EXTRACTED_FULL}")

    # 2. Per-character rollup: each PUA char with all readings & sources it appeared under.
    #    Useful for auditing "which readings does U+EFFF actually have?".
    by_char: dict[str, dict[str, set[str]]] = {}  # char -> reading -> {sources}
    for reading, text in g:
        for ch, _zone in chars_with_pua(text):
            by_char.setdefault(ch, {}).setdefault(reading, set()).add("gdnhv")
    for reading, text in t:
        for ch, _zone in chars_with_pua(text):
            by_char.setdefault(ch, {}).setdefault(reading, set()).add("tdcndg")
    with EXTRACTED_BY_CHAR.open("w", encoding="utf-8") as f:
        f.write("char\tcodepoint\tzone\treading_count\treadings_with_sources\tin_existing_dict\n")
        for ch in sorted(by_char):
            cp = ord(ch)
            zone = is_pua(cp) or ""
            readings = by_char[ch]
            cell = "; ".join(
                f"{r}({'+'.join(sorted(srcs))})" for r, srcs in sorted(readings.items())
            )
            in_dict = "Y" if ch in existing_pua_chars else "N"
            f.write(f"{ch}\tU+{cp:04X}\t{zone}\t{len(readings)}\t{cell}\t{in_dict}\n")
    print(f"Wrote per-char rollup ({len(by_char):,} chars) to: {EXTRACTED_BY_CHAR}")

    # 3. Full missing list. Now uses tone-marked telex codes (one row per
    #    (telex_code, char) pair). Multiple readings → multiple rows for the same char.
    missing_with_telex: list[tuple[str, str, str]] = []  # (telex, char, sources)
    seen_pairs_with_telex: set[tuple[str, str]] = set()
    # Re-derive from the source extractions so we keep tone info
    src_pairs: dict[tuple[str, str], set[str]] = {}
    for reading, text in g:
        src_pairs.setdefault((reading, text), set()).add("gdnhv")
    for reading, text in t:
        src_pairs.setdefault((reading, text), set()).add("tdcndg")
    for (reading, text), srcs in src_pairs.items():
        bare = qn_to_bare(reading)
        if bare in existing_bare_index and text in existing_bare_index[bare]:
            continue
        telex = qn_to_telex(reading)
        # Confirm this exact (text, telex) is not already present in the dict
        if (text, telex) in existing_pairs:
            continue
        if (telex, text) in seen_pairs_with_telex:
            continue
        seen_pairs_with_telex.add((telex, text))
        missing_with_telex.append((telex, text, "+".join(sorted(srcs))))

    with MISSING_FULL.open("w", encoding="utf-8") as f:
        f.write("telex_code\tchar\tcodepoints\tsources\n")
        for telex, text, sources in missing_with_telex:
            cps = " ".join(f"U+{ord(c):04X}" for c in text)
            f.write(f"{telex}\t{text}\t{cps}\t{sources}\n")
    print(f"Wrote full missing list with telex codes "
          f"({len(missing_with_telex):,} rows) to: {MISSING_FULL}")

    # 4. Sample (200 rows) for quick eyeballing.
    with SAMPLE_OUT.open("w", encoding="utf-8") as f:
        f.write("telex_code\tchar\tcodepoints\tsources\n")
        for telex, text, sources in missing_with_telex[:200]:
            cps = " ".join(f"U+{ord(c):04X}" for c in text)
            f.write(f"{telex}\t{text}\t{cps}\t{sources}\n")
    print(f"Wrote first 200 missing pairs (sample) to: {SAMPLE_OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
