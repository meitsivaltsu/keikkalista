#!/usr/bin/env python3
"""Muuttaa uudet keikat ääneen luettavaksi tekstiksi (uudet.txt).

Käyttö: python3 tools/puhe.py uudet.json uudet.txt [YYYY-MM-DD]
uudet.json = lista keikkoja: {band, date, time, venue, genre, availability}
"""
import json, sys, datetime, re

MAX_LUETTAVAT = 8
PAIVAT = ["maanantaina", "tiistaina", "keskiviikkona", "torstaina", "perjantaina", "lauantaina", "sunnuntaina"]
KUUT = ["tammikuuta", "helmikuuta", "maaliskuuta", "huhtikuuta", "toukokuuta", "kesäkuuta",
        "heinäkuuta", "elokuuta", "syyskuuta", "lokakuuta", "marraskuuta", "joulukuuta"]
PAIKAT = {  # paikka sisäpaikallissijassa
    "Tavastia Klubi": "Tavastialla", "Semifinal": "Semifinalissa", "On the Rocks": "On the Rocksissa",
    "Kulttuuritalo": "Kulttuuritalolla", "G Livelab Helsinki": "G Livelabissa", "Bar Loose": "Bar Loosessa",
    "Helsingin Jäähalli": "Jäähallissa", "Veikkaus Areena": "Veikkaus Areenalla",
}
LIPUT = {"sold_out": "loppuunmyyty", "low": "liput loppumassa", "cancelled": "peruttu"}
LUVUT = ["Ei", "Yksi", "Kaksi", "Kolme", "Neljä", "Viisi", "Kuusi", "Seitsemän", "Kahdeksan", "Yhdeksän", "Kymmenen"]


def siisti(nimi):
    nimi = re.sub(r"\((?:[A-Z]{2,3})\)", "", nimi)          # (USA), (SWE)
    nimi = re.sub(r"\(([^)]*)\)", r", \1", nimi)            # (levyjulkkarit) -> , levyjulkkarit
    nimi = nimi.replace("&", " ja ").replace("–", ",").replace(":", ",")
    return re.sub(r"\s+", " ", re.sub(r"\s*,\s*", ", ", nimi)).strip(" ,")


def paiva(iso, tanaan):
    d = datetime.date.fromisoformat(iso)
    ero = (d - tanaan).days
    if ero == 0:
        return "tänään"
    if ero == 1:
        return "huomenna"
    s = f"{PAIVAT[d.weekday()]} {d.day}. {KUUT[d.month - 1]}"
    return s + (f" {d.year}" if d.year != tanaan.year else "")


def lukumaara(n):
    return LUVUT[n] if n < len(LUVUT) else str(n)


def teksti(keikat, tanaan):
    keikat = sorted(keikat, key=lambda g: (g.get("date") or "9999", g.get("time") or ""))
    n = len(keikat)
    if n == 0:
        return "Ei uusia keikkoja tänään."
    alku = "Yksi uusi keikka." if n == 1 else f"{lukumaara(n)} uutta keikkaa."
    lauseet = [alku]
    for g in keikat[:MAX_LUETTAVAT]:
        osat = [paiva(g["date"], tanaan) if g.get("date") else "", PAIKAT.get(g.get("venue"), g.get("venue", ""))]
        alku = " ".join(o for o in osat if o)
        lause = alku[:1].upper() + alku[1:] + " " + siisti(g["band"])
        if g.get("genre"):
            lause += ", " + g["genre"].replace("dj/disko", "DJ-ilta")
        if g.get("availability") in LIPUT:
            lause += ", " + LIPUT[g["availability"]]
        lauseet.append(lause + ".")
    if n > MAX_LUETTAVAT:
        loput = n - MAX_LUETTAVAT
        lauseet.append(f"Lisäksi {lukumaara(loput).lower()} muuta. Katso koko lista Keikkalistasta.")
    return " ".join(lauseet)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    tanaan = datetime.date.fromisoformat(sys.argv[3]) if len(sys.argv) > 3 else datetime.date.today()
    with open(src, encoding="utf-8") as f:
        keikat = json.load(f)
    out = teksti(keikat, tanaan)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(out + "\n")
    print(out)
