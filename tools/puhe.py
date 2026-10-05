#!/usr/bin/env python3
"""Turns today's new gigs into a short English sentence for an iOS Shortcut (uudet.txt).

Usage: python3 tools/puhe.py new.json uudet.txt [YYYY-MM-DD]
new.json = list of gigs: {band, date, ...}. Only headliner names are spoken.
"""
import json, re, sys

MAX_NAMES = 12


def headliner(name):
    n = re.sub(r"\([^)]*\)", "", name)                      # (USA), (levyjulkkarit)
    n = re.split(r"\s+[–—-]\s+|:\s|\s+\+\s+|\s+presents\b|\s+w/\s+|,", n, maxsplit=1, flags=re.I)[0]
    n = n.replace("&", "and").replace("*", "").strip(" ,.")
    if n.isupper() and " " in n:                            # HECTOR 60V TAITEILIJAJUHLA -> Hector 60V Taiteilijajuhla
        n = " ".join(w if any(c.isdigit() for c in w) else w.capitalize() for w in n.split())
    return re.sub(r"\s+", " ", n)


def join_names(names):
    if len(names) == 1:
        return names[0]
    if len(names) == 2:
        return f"{names[0]} and {names[1]}"
    return ", ".join(names[:-1]) + ", and " + names[-1]


def sentence(gigs):
    gigs = sorted(gigs, key=lambda g: (g.get("date") or "9999", g.get("time") or ""))
    names = []
    for g in gigs:
        h = headliner(g.get("band", ""))
        if h and h.lower() not in (x.lower() for x in names):
            names.append(h)
    if not names:
        return "No new gigs in Helsinki today."
    if len(names) == 1:
        return f"There's one new gig coming up in Helsinki: {names[0]}."
    shown, rest = names[:MAX_NAMES], len(names) - MAX_NAMES
    lead = f"There are {len(names)} new gigs coming up in Helsinki: "
    if rest > 0:
        return lead + ", ".join(shown) + f", and {rest} more."
    return lead + join_names(shown) + "."


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    with open(src, encoding="utf-8") as f:
        out = sentence(json.load(f))
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out + "\n")
    print(out)
