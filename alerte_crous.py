#!/usr/bin/env python3
"""
Alerte logement Crous -> notification sur ton téléphone via ntfy.sh

Mise en place (5 minutes) :
1. Installe l'appli "ntfy" sur ton téléphone (Android / iOS).
2. Dans l'appli, abonne-toi à un sujet secret, ex : crous-alerte-k8f3x9q2
   (choisis un nom long et unique, il sert de "mot de passe").
3. Va sur https://trouverunlogement.lescrous.fr, cherche "Le Mans" (idéalement
   avec le filtre de la résidence Vaurouzé), puis copie l'URL complète dans URL_RECHERCHE.
4. pip install requests
5. Lance : python alerte_crous.py
"""

import hashlib
import re
import time

import requests

# ---------- À MODIFIER ----------
URL_RECHERCHE = "https://trouverunlogement.lescrous.fr/tools/48/search?bounds=0.1362825_48.0358733_0.2550938_47.927977&locationName=Le+Mans"
NTFY_SUJET = "crous-mans-778655990AD"
INTERVALLE_MINUTES = 5
# Résidence surveillée : l'alerte ne part que si ce mot apparaît dans la page
# (Le Mans - Vaurouzé, 16 bd Charles Nicolle). Écrit sans accent final pour couvrir les variantes.
MOT_CLE_RESIDENCE = "vaurouz"
# Phrases affichées par le site quand il n'y a rien (en minuscules).
# Ajuste-les si le texte du site est différent.
MARQUEURS_AUCUN_LOGEMENT = [
    "aucun logement",
    "0 logement",
]
# --------------------------------

HEADERS = {"User-Agent": "Mozilla/5.0 (alerte perso logement etudiant)"}


def notifier(titre: str, message: str) -> None:
    requests.post(
        f"https://ntfy.sh/{NTFY_SUJET}",
        data=message.encode("utf-8"),
        headers={
            "Title": titre.encode("utf-8"),
            "Priority": "high",
            "Tags": "house",
            "Click": URL_RECHERCHE,
        },
        timeout=15,
    )


def lire_page() -> str:
    r = requests.get(URL_RECHERCHE, headers=HEADERS, timeout=30)
    r.raise_for_status()
    texte = re.sub(r"<script.*?</script>|<style.*?</style>", " ", r.text, flags=re.S)
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", texte).strip().lower()


def main() -> None:
    if "COLLE ICI" in URL_RECHERCHE:
        raise SystemExit("Renseigne d'abord URL_RECHERCHE dans le script.")

    dernier_etat = None
    dernier_hash = None
    notifier("Alerte Crous activée", "La surveillance a démarré.")

    while True:
        try:
            texte = lire_page()
            vide = any(m in texte for m in MARQUEURS_AUCUN_LOGEMENT)
            empreinte = hashlib.md5(texte.encode()).hexdigest()
            etat = "dispo" if (not vide and MOT_CLE_RESIDENCE in texte) else "vide"

            if etat == "dispo" and (dernier_etat != "dispo" or empreinte != dernier_hash):
                notifier("Logement Crous disponible à Vaurouzé !", "Dépêche-toi, ouvre la page pour réserver.")
            dernier_etat, dernier_hash = etat, empreinte
            print(time.strftime("%H:%M:%S"), etat)
        except Exception as e:  # le réseau peut avoir des coupures
            print("Erreur :", e)
        time.sleep(INTERVALLE_MINUTES * 60)


if __name__ == "__main__":
    main()
