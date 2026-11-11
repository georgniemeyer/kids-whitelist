#!/usr/bin/env python3
"""
Applies checked domains from a GitHub Issue into whitelist.txt,
classifies them into 11 distinct pedagogical & technical categories,
integrates personal custom domains from custom_whitelist.txt,
and generates a clean, comment-free export file for FRITZ!Box import.
"""

import os
import re

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
WHITELIST_PATH = "whitelist.txt"
CUSTOM_WHITELIST_PATH = "custom_whitelist.txt"
EXPORT_PATH = "whitelist_export.txt"

# 11 disjunkte, saubere Kategorien mit entsprechenden Erkennungs-Keywords
CATEGORIES = {
    "01. Kinder-Suchmaschinen & Jugendschutz": [
        "fragfinn", "blindekuh", "klicksafe", "internet-abc", "jugendschutz"
    ],
    "02. Geprüfte Schul- und Lernportale": [
        "schule", "lernen", "unterricht", "lo-net", "moodle", "maus.schule", 
        "Antolin", "alphabet", "ki-kindgerecht"
    ],
    "03. Allgemeines Wissen & Lexika": [
        "wissen", "lexikon", "hanisauland", "blinde-kuh", "helles-koepfchen"
    ],
    "04. Nachrichten für Kinder, ÖRR & Medien": [
        "duda", "news", "nachrichten", "logo", "kika", "wdr", "zdftivi", 
        "radio", "reporter", "medienkompetenz", "frieden", "politik"
    ],
    "05. Bücher, Lesen, Hörspiele & Musik": [
        "lesen", "antolin", "buch", "bibliothek", "hoerspiel", "musik", 
        "klassik", "junge-klassik", "ohrenkuss"
    ],
    "06. Hobby, Sport, Tiere & Natur": [
        "sport", "tier", "natur", "naturpark", "detektive", "garten", "pferd", "fussball"
    ],
    "07. Kreatives, Basteln & Gaming (Sicher)": [
        "basteln", "malen", "kreativ", "spiel", "spielaffe", "kinderspiele"
    ],
    "08. Verlage, Comics & Unterhaltung": [
        "verlag", "comic", "micky", "maus", "unterhaltung", "carlsen", "ravenstein"
    ],
    "09. Kindermuseen, Theater & Kultur": [
        "museum", "theater", "kultur", "kunst", "oper", "ballett", "jugendkunst"
    ],
    "10. Regionales, Heimat & Norddeutschland": [
        "norddeutschland", "hamburg", "schleswig", "bremen", "niedersachsen", 
        "heimat", "region", "loki-schmidt"
    ],
    "11. Technische Infrastruktur & CDNs": [
        "cdn", "static", "assets", "fonts", "api", "cloudfront", 
        "akamai", "fastly", "cloudflare", "jsdelivr", "unpkg", "storage"
    ],
    "12. Persönliche Custom Domains": [
        # is used exclusivly for custom_whitelist.txt
    ]
}


def classify_domain(domain: str) -> str:
    """Weist eine Domain basierend auf Schlüsselwörtern einer passenden Kategorie zu."""
    d_lower = domain.lower()
    for cat_name, keywords in CATEGORIES.items():
        if cat_name in ["12. Persönliche Custom Domains", "03. Allgemeines Wissen & Lexika"]:
            # Allgemeine Lexika als sanfter Fallback vor dem ultimativen Rest
            continue
        for kw in keywords:
            if kw in d_lower:
                return cat_name
    
    # Fallback für sonstige Wissens-/Allgemeinseiten
    return "03. Allgemeines Wissen & Lexika"


def clean_domain_line(line: str) -> str:
    """Entfernt Kommentare und Formatierungen, um die reine Domain zu erhalten."""
    cleaned = line.strip().lower()
    if not cleaned or cleaned.startswith("#"):
        return ""
    cleaned = re.sub(r'[`\[\]()]', '', cleaned).strip()
    return cleaned


def main():
    # 1. Checked Domains aus dem Issue auslesen (falls vorhanden)
    selected_domains = []
    if ISSUE_BODY:
        checked_pattern = re.compile(
            r'-\s*\[[xX]\]\s*(?:\[)?\s*`([^`]+)`\s*(?:\]\s*\([^)]+\))?',
            re.DOTALL
        )
        selected_domains = checked_pattern.findall(ISSUE_BODY)

    cleaned_new_domains = [d.strip().lower() for d in selected_domains if d.strip()]

    # Speicher für alle Domains nach Kategorie
    all_domains_by_category = {cat: set() for cat in CATEGORIES.keys()}

    # 2. Bestehende Master-Whitelist einlesen (bestehende Kategorien bewahren)
    if os.path.exists(WHITELIST_PATH):
        current_cat = "03. Allgemeines Wissen & Lexika"
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("#") and "KATEGORIE:" in line_str:
                    for cat in CATEGORIES.keys():
                        if cat.lower() in line_str.lower():
                            current_cat = cat
                            break
                    continue
                
                d = clean_domain_line(line)
                if d:
                    # Wenn es in Custom liegt, dort lassen, sonst neu klassifizieren
                    if current_cat == "12. Persönliche Custom Domains":
                        all_domains_by_category["12. Persönliche Custom Domains"].add(d)
                    else:
                        assigned_cat = classify_domain(d)
                        all_domains_by_category[assigned_cat].add(d)

    # 3. Custom-Whitelist einlesen (custom_whitelist.txt im Main-Verzeichnis)
    if os.path.exists(CUSTOM_WHITELIST_PATH):
        with open(CUSTOM_WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                d = clean_domain_line(line)
                if d:
                    all_domains_by_category["12. Persönliche Custom Domains"].add(d)
    else:
        with open(CUSTOM_WHITELIST_PATH, "w", encoding="utf-8") as f:
            f.write("# Please list here any domain that you want to add to the global whitelist.\n")
            f.write("# Only one per line.\n")

    # 4. Neue Domains aus dem Issue einsortieren
    for domain in cleaned_new_domains:
        target_cat = classify_domain(domain)
        exists_already = any(domain in domain_set for domain_set in all_domains_by_category.values())
        if not exists_already:
            all_domains_by_category[target_cat].add(domain)
            print(f"Added '{domain}' to category '{target_cat}'")

    # 5. Master-Whitelist formatiert mit den neuen Kategorien neu schreiben
    with open(WHITELIST_PATH, "w", encoding="utf-8") as master:
        master.write("# ==========================================\n")
        master.write("# FRITZ!Box Master Whitelist (Kindersicher)\n")
        master.write("# ==========================================\n\n")

        for cat_name, domain_set in all_domains_by_category.items():
            if domain_set:
                master.write(f"# ==========================================\n")
                master.write(f"# KATEGORIE: {cat_name}\n")
                master.write(f"# ==========================================\n")
                for domain in sorted(domain_set):
                    master.write(f"{domain}\n")
                master.write("\n")

    # 6. Saubere FRITZ!Box Export-Datei generieren (flach, alphabetisch, keine Kommentare)
    all_flat_domains = set()
    for domain_set in all_domains_by_category.values():
        all_flat_domains.update(domain_set)

    with open(EXPORT_PATH, "w", encoding="utf-8") as exp:
        for domain in sorted(all_flat_domains):
            exp.write(f"{domain}\n")

    print(f"Successfully updated master categories and generated '{EXPORT_PATH}' with {len(all_flat_domains)} total domains.")


if __name__ == "__main__":
    main()
