#!/usr/bin/env python3
"""Version cloud (GitHub Actions) : une vérification par exécution."""
import os
import re
import sys

import requests

URL_RECHERCHE = "https://trouverunlogement.lescrous.fr/tools/48/search?bounds=0.1362825_48.0358733_0.2550938_47.927977&locationName=Le+Mans"
NTFY_SUJET = os.environ.get("NTFY_SUJET", "")
MOT_CLE_RESIDENCE = "vaurouz"
MARQUEURS_AUCUN_LOGEMENT = ["aucun logement", "0 logement"]
HEADERS = {"User-Agent": "Mozilla/5.0 (alerte perso logement etudiant)"}


def notifier(titre, message):
    requests.post(
        f"https://ntfy.sh/{NTFY_SUJET}",
        data=message.encode("utf-8"),
        headers={"Title": titre.encode("utf-8"), "Priority": "high",
                 "Tags": "house", "Click": URL_RECHERCHE},
        timeout=15,
    )


def main():
    if not NTFY_SUJET:
        sys.exit("Secret NTFY_SUJET manquant.")
    if os.environ.get("TEST") == "1":
        notifier("Test alerte Crous", "Le cloud GitHub fonctionne.")
    r = requests.get(URL_RECHERCHE, headers=HEADERS, timeout=30)
    r.raise_for_status()
    texte = re.sub(r"<script.*?</script>|<style.*?</style>", " ", r.text, flags=re.S)
    texte = re.sub(r"<[^>]+>", " ", texte)
    texte = re.sub(r"\s+", " ", texte).strip().lower()
    vide = any(m in texte for m in MARQUEURS_AUCUN_LOGEMENT)
    if not vide and MOT_CLE_RESIDENCE in texte:
        print("dispo")
        notifier("Logement Crous disponible à Vaurouzé !",
                 "Dépêche-toi, ouvre la page pour réserver.")
    else:
        print("vide")


if __name__ == "__main__":
    main()
