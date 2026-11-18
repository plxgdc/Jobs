#!/usr/bin/env python3
"""Seen-index helper for the job-search routine.

The index (seen/index.csv) is the duplicate check: one row per posting that was
ever reported or deliberately excluded. Runs check every finalist against it
before reporting, then append what they reported or excluded.

Usage
  python3 tools/seen.py check --title T --employer E [--url U] [--id ID]
  python3 tools/seen.py batch candidates.csv      # columns: title,employer,url,id
  python3 tools/seen.py add --status reported --title T --employer E --url U \
        [--id ID] [--location L] [--posted D] [--deadline D] [--reason R]
  python3 tools/seen.py stats

check / batch exit codes: 0 = new, 1 = already seen (hard match), 2 = review
(only the employer or only the title matched; read the earlier row and decide).

Standard library only. Run from the repo root.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import os
import re
import sys
import unicodedata

INDEX = os.path.join("seen", "index.csv")
FIELDS = ["logged", "status", "title", "employer", "location", "url", "id",
          "posted", "deadline", "reason"]

# Gender / inclusive-language tags common on German, Austrian and Swiss boards.
_GENDER_PAREN = re.compile(
    r"\((?:[mwfdxa]\s*[/|,]\s*)+[mwfdxa]\*?\)|\((?:all genders?|alle geschlechter|a\*|agw\*|gn|w/m/gn|m/w/gn|d/m/w|m/f/d|m/f/x|w/m/d|m/w/d|m/w/x)\)",
    re.IGNORECASE,
)
_GENDER_SUFFIX = re.compile(r"(?<=\w)(?:\*|:|_|/-?|-)in(?:nen)?\b", re.IGNORECASE)
_LEGAL = re.compile(
    r"\b(gmbh\s*&\s*co\.?\s*kg|gmbh|ggmbh|mbh|ag|se|kg|ohg|ug|e\.?\s?v\.?|gbr|ltd|limited|llc|inc|plc|"
    r"b\.?v\.?|n\.?v\.?|s\.?a\.?|s\.?r\.?l\.?|s\.?l\.?|sa|sarl|srl|aps|a/s|ab|oy|as|kft|sp\.?\s?z\.?\s?o\.?\s?o\.?)\b",
    re.IGNORECASE,
)
_TRANSLIT = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "æ": "ae", "ø": "oe", "å": "aa"})


def _fold(s: str) -> str:
    s = (s or "").lower().translate(_TRANSLIT)
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c))


def norm_title(s: str) -> str:
    s = _GENDER_PAREN.sub(" ", s or "")
    s = _GENDER_SUFFIX.sub("", s)
    s = _fold(s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


def norm_employer(s: str) -> str:
    s = _fold(s)
    s = s.replace("&", " ").replace("+", " ")
    s = _LEGAL.sub(" ", s)
    # Compare without spaces or punctuation: "W&S Digitalagentur" == "WS Digitalagentur".
    return re.sub(r"[^a-z0-9]+", "", s)


def norm_url(u: str) -> str:
    u = (u or "").strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = re.sub(r"^www\.", "", u)
    u = re.sub(r"[?#].*$", "", u) if "arbeitsagentur" not in u else u
    return u.rstrip("/")


def load() -> list[dict]:
    if not os.path.exists(INDEX):
        sys.exit(f"{INDEX} not found - run from the repo root")
    with open(INDEX, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def find(rows, title, employer, url="", pid=""):
    t, e, u = norm_title(title), norm_employer(employer), norm_url(url)
    hard, soft = [], []
    for r in rows:
        rt, re_, ru = norm_title(r["title"]), norm_employer(r["employer"]), norm_url(r["url"])
        why = []
        if u and ru and u == ru:
            why.append("same URL")
        if pid and r.get("id") and pid.strip().lower() == r["id"].strip().lower():
            why.append("same id")
        if t and e and t == rt and e == re_:
            why.append("same title + employer")
        if why:
            hard.append((r, why))
            continue
        if e and re_ and (e == re_ or (len(e) > 5 and (e in re_ or re_ in e))):
            soft.append((r, ["same employer"]))
        elif t and t == rt:
            soft.append((r, ["same title"]))
    return hard, soft


def _show(label, matches):
    for r, why in matches:
        print(f"  {label} [{', '.join(why)}] {r['logged']} {r['status']}: "
              f"{r['title']} - {r['employer']} - {r['url']}"
              + (f" ({r['reason']})" if r.get("reason") else ""))


def cmd_check(a) -> int:
    hard, soft = find(load(), a.title, a.employer, a.url or "", a.id or "")
    if hard:
        print("SEEN - do not report")
        _show("match", hard)
        return 1
    if soft:
        print("REVIEW - employer or title seen before; read these rows and decide")
        _show("near", soft)
        return 2
    print("NEW")
    return 0


def cmd_batch(a) -> int:
    rows = load()
    worst = 0
    with open(a.file, newline="", encoding="utf-8") as f:
        for c in csv.DictReader(f):
            hard, soft = find(rows, c.get("title", ""), c.get("employer", ""),
                              c.get("url", ""), c.get("id", ""))
            verdict = "SEEN" if hard else "REVIEW" if soft else "NEW"
            worst = max(worst, 1 if hard else 2 if soft else 0)
            print(f"{verdict}\t{c.get('title','')}\t{c.get('employer','')}\t{c.get('url','')}")
            _show("match", hard)
            _show("near", soft)
    return worst


def cmd_add(a) -> int:
    rows = load()
    hard, _ = find(rows, a.title, a.employer, a.url or "", a.id or "")
    if hard and not a.force:
        print("Already in the index - not added (use --force to add anyway):")
        _show("match", hard)
        return 1
    row = {
        "logged": a.logged or dt.date.today().isoformat(), "status": a.status,
        "title": a.title, "employer": a.employer, "location": a.location or "",
        "url": a.url or "", "id": a.id or "", "posted": a.posted or "not stated",
        "deadline": a.deadline or "not stated", "reason": a.reason or "",
    }
    with open(INDEX, "a", newline="", encoding="utf-8") as f:
        csv.DictWriter(f, fieldnames=FIELDS).writerow(row)
    print(f"added: {a.status} - {a.title} - {a.employer}")
    return 0


def cmd_stats(_a) -> int:
    rows = load()
    by = {}
    for r in rows:
        by[r["status"]] = by.get(r["status"], 0) + 1
    print(f"{len(rows)} rows: " + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    today = dt.date.today().isoformat()
    live = [r for r in rows if r["status"] == "reported" and r["deadline"][:10] >= today
            and re.match(r"\d{4}-\d{2}-\d{2}", r["deadline"])]
    if live:
        print("reported postings whose deadline has not passed:")
        for r in sorted(live, key=lambda r: r["deadline"]):
            print(f"  {r['deadline']}  {r['title']} - {r['employer']} - {r['url']}")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check")
    for f in ("title", "employer"):
        c.add_argument(f"--{f}", required=True)
    c.add_argument("--url")
    c.add_argument("--id")
    c.set_defaults(fn=cmd_check)

    b = sub.add_parser("batch")
    b.add_argument("file")
    b.set_defaults(fn=cmd_batch)

    ad = sub.add_parser("add")
    ad.add_argument("--status", required=True, choices=["reported", "excluded"])
    for f in ("title", "employer"):
        ad.add_argument(f"--{f}", required=True)
    for f in ("url", "id", "location", "posted", "deadline", "reason", "logged"):
        ad.add_argument(f"--{f}")
    ad.add_argument("--force", action="store_true")
    ad.set_defaults(fn=cmd_add)

    s = sub.add_parser("stats")
    s.set_defaults(fn=cmd_stats)

    a = p.parse_args()
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
