#!/usr/bin/env python3
"""Разовый конвертер бэкофилла: md-выпуски Музагрегата -> content/ Hugo-сайта."""
import re, sys, yaml
from pathlib import Path

SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("..")
OUT = Path(__file__).resolve().parent.parent / "content"

CHARTS = {
    "Музагрегат — Чарт · Январь 2026.md":  ("2026-01", "Чарт · Январь 2026", True),
    "Музагрегат — Чарт · Февраль 2026.md": ("2026-02", "Чарт · Февраль 2026", False),
    "Музагрегат — Чарт · Март 2026.md":    ("2026-03", "Чарт · Март 2026", False),
    "Музагрегат — Чарт · Апрель 2026.md":  ("2026-04", "Чарт · Апрель 2026", False),
    "Музагрегат — Чарт · Май 2026.md":     ("2026-05", "Чарт · Май 2026", False),
}
DISC = ("Музагрегат — Диск Q1 (январь–март 2026).md", "2026-q1", "Диск Q1 · Январь–март 2026")

FLAGMAP = {"⚙": "ai", "⚑": "foreign_agent"}

def clean_track(cell):
    """'⚙ SDP — «Сыпь, гармонь!»' -> (flags, artist, track)"""
    flags = [FLAGMAP[ch] for ch in FLAGMAP if ch in cell]
    for ch in FLAGMAP: cell = cell.replace(ch, "")
    cell = cell.strip()
    if " — " in cell:
        artist, track = cell.split(" — ", 1)
    else:
        artist, track = cell, ""
    return flags, artist.strip(), track.strip().strip("«»").replace("»", "").strip()

def parse_move(cell):
    if "NEW" in cell: return None
    m = re.search(r"\((?:янв|фев|мар|апр|мая|май|июн)[а-я]*\.?\s*(\d+)\)", cell)
    return int(m.group(1)) if m else None

def body_overview(text):
    m = re.search(r"(## Обзор.*?)\n## Чарт", text, re.S)
    return (m.group(1).strip() + "\n") if m else ""

def table_rows(text):
    rows = []
    for line in text.splitlines():
        if re.match(r"\|\s*\d+\s*\|", line):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows

def convert_chart(fn, period, title, baseline):
    text = (SRC / fn).read_text(encoding="utf-8")
    positions = []
    for cells in table_rows(text):
        if baseline:  # январь: # | трек | тип | лейбл | дата | ист.
            rank, trackcell, typ, label, date, srcs = cells[:6]
            prev = None
        else:         # фев–май: # | движ | трек | тип | лейбл | дата | ист.
            rank, move, trackcell, typ, label, date, srcs = cells[:7]
            prev = parse_move(move)
        flags, artist, track = clean_track(trackcell)
        pos = {"rank": int(rank), "artist": artist, "track": track,
               "type": typ, "date": date, "sources": srcs}
        if prev is not None: pos["prev"] = prev
        if label and label != "—": pos["label"] = label
        if flags: pos["flags"] = flags
        positions.append(pos)
    fm = {"title": title, "type": "chart", "period": period,
          "date": f"{period}-01", "description": f"Музагрегат: {title.lower()} — что на самом деле звучало в стране."}
    if baseline: fm["no_movement"] = True
    fm["positions"] = positions
    write(OUT / "chart" / f"{period}.md", fm, body_overview(text))
    return len(positions)

def convert_disc():
    fn, period, title = DISC
    text = (SRC / fn).read_text(encoding="utf-8")
    positions = []
    for cells in table_rows(text):
        # # | тайм-код | трек | стаж | роль | полн->диск | правка
        rank, time, trackcell, tenure, role = cells[:5]
        flags, artist, track = clean_track(trackcell)
        pos = {"rank": int(rank), "time": time, "artist": artist, "track": track,
               "tenure": tenure.count("✦"), "role": role}
        if flags: pos["flags"] = flags
        positions.append(pos)
    intro = text.split("## Треклист")[0]
    intro = re.sub(r"^# .*?\n", "", intro).strip()
    # хвост после таблицы (драматургия и т.п.)
    tail_m = re.split(r"\n(?=## )", text.split("## Треклист", 1)[1], 1)
    tail = tail_m[1].strip() if len(tail_m) > 1 else ""
    body = intro + ("\n\n" + tail if tail else "")
    fm = {"title": title, "type": "disc", "period": period, "date": "2026-03-31",
          "description": "Музагрегат: квартальная компиляция — 25 треков первого квартала, которые слушаются подряд.",
          "positions": positions}
    write(OUT / "disc" / f"{period}.md", fm, body)
    return len(positions)

def write(path, fm, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    y = yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000)
    path.write_text(f"---\n{y}---\n\n{body}\n", encoding="utf-8")
    print(f"  {path.name}: ok")

if __name__ == "__main__":
    for fn, (period, title, base) in CHARTS.items():
        n = convert_chart(fn, period, title, base)
        print(f"{period}: {n} позиций")
    print(f"диск: {convert_disc()} позиций")
