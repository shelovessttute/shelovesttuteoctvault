import os, re, sys, unicodedata
from pathlib import Path
from collections import defaultdict

SRC = Path(os.environ.get("SRC", Path.home() / "Desktop" / "BEATS OCTUBRE"))
EXT = {".mp3", ".wav", ".m4a", ".flac"}
COLLABS = ["fuckyousmly", "casio5k", "maizzeno", "yvngrobv", "rocha999nda"]
APPLY = "--apply" in sys.argv
ALT = "|".join(COLLABS)


def parse(stem):
    s = unicodedata.normalize("NFC", stem)
    s = re.sub(r"rocha[\s_.-]*999[\s_.-]*nda", "rocha999nda", s, flags=re.I)
    s = re.sub(r"@?shelovesttute", " ", s, flags=re.I)
    pat = r"(?<![A-Za-z0-9])@?(" + ALT + r")(?![A-Za-z0-9])"
    handles = []
    for m in re.finditer(pat, s, re.I):
        h = m.group(1).lower()
        if h not in handles:
            handles.append(h)
    s = re.sub(pat, " ", s, flags=re.I)
    flags = []
    for h in re.findall(r"@([A-Za-z0-9.]*[A-Za-z0-9])", s):
        flags.append(f"@ desconocido: @{h} (lo dejo como credito)")
        if h.lower() not in handles:
            handles.append(h.lower())
    s = re.sub(r"@[A-Za-z0-9.]*", " ", s)
    bpm = None
    m = re.search(r"(?<!\d)(\d{2,3})\s*bpm", s, re.I)
    if m:
        bpm = m.group(1)
    else:
        for n in re.findall(r"(?<!\d)(\d{2,3})(?!\d)", s):
            if 60 <= int(n) <= 220:
                bpm = n
                break
    if not bpm:
        flags.append("no encontre BPM")
    return bpm, handles, flags


def build(num, bpm, handles):
    parts = ["BEAT"] + ([str(num)] if num else []) + ([f"{bpm}BPM"] if bpm else [])
    return " ".join(parts + ["@shelovesttute"] + ["@" + h for h in handles])


if not SRC.exists():
    raise SystemExit(f"No existe {SRC}")
items = []
for p in sorted(p for p in SRC.rglob("*") if p.is_file() and p.suffix.lower() in EXT):
    b, h, f = parse(p.stem)
    items.append(dict(p=p, b=b, h=h, f=f, n=None))

groups = defaultdict(list)
for it in items:
    groups[build(None, it["b"], it["h"])].append(it)
for g in groups.values():
    if len(g) > 1:
        for i, it in enumerate(g, 1):
            it["n"] = i
            it["f"].append(f"nombre repetido, le puse numero {i}")

print(f"\nCarpeta: {SRC}\nModo: {'APLICANDO' if APPLY else 'SOLO VISTA PREVIA (no cambia nada)'}\n")
log = []
for it in items:
    new = build(it["n"], it["b"], it["h"]) + it["p"].suffix.lower()
    print(f'  {it["p"].name}\n   -> {new}')
    for f in it["f"]:
        print(f"      ! {f}")
    if APPLY and new != it["p"].name:
        it["p"].rename(it["p"].with_name(new))
        log.append(f'{it["p"].name} => {new}')
if APPLY:
    lp = SRC.parent / "BEATS_OCTUBRE_rename_log.txt"
    lp.write_text("\n".join(log) + "\n")
    print(f"\nRenombrados: {len(log)}. Log para deshacer: {lp}")
else:
    print("\nSi se ve bien: python3 renombrar.py --apply")
