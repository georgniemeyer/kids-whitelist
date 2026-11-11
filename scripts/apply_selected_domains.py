#!/usr/bin/env python3
"""
Applies checked domains from a GitHub Issue into whitelist.txt,
classifies them into meaningful pedagogical & technical categories,
integrates personal custom domains from custom_whitelist.txt,
and generates a clean, comment-free export file for FRITZ!Box import.
"""

import os
import re

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
WHITELIST_PATH = "whitelist.txt"
CUSTOM_WHITELIST_PATH = "custom_whitelist.txt"
EXPORT_PATH = "whitelist_export.txt"

# Sprechende Kategorien inklusive technischer Infrastruktur & CDNs
CATEGORIES = {
    "Schule, Lernen & Medienkompetenz": [
        "schule", "lernen", "recht", "fragfinn", "klicksafe", "antolin", 
        "alphabet", "internet-abc", "ki-kindgerecht"
    ],
    "Wissen, Lexikon & Nachrichten": [
        "duda", "news", "nachrichten", "wissen", "lexikon", "radio", 
        "reporter", "klassik", "frieden", "naturpark", "detektive"
    ],
    "Technische Infrastruktur & CDNs": [
        "cdn", "static", "assets", "fonts", "api", "cloudfront", 
        "akamai", "fastly", "cloudflare", "jsdelivr", "unpkg", "storage"
    ],
    "Persönliche Custom Domains": [
        # Sammelkategorie für manuell in custom_whitelist.txt hinterlegte Einträge
    ],
    "Kinderseiten, Spiele & Kreativität": [
        # Fallback für alle anderen geprüften Portale
    ]
}


def classify_domain(domain: str) -> str:
    """Weist eine Domain basierend auf Schlüsselwörtern einer passenden Kategorie zu."""
    d_lower = domain.lower()
    for cat_name, keywords in CATEGORIES.items():
        if cat_name in ["Kinderseiten, Spiele & Kreativität", "Persönliche Custom Domains"]:
            continue
        for kw in keywords:
            if kw in d_lower:
                return cat_name
    return "Kinderseiten, Spiele & Kreativität"


def clean_domain_line(line: str) -> str:
    """Entfernt Kommentare und Formatierungen, um die reine Domain zu erhalten."""
    cleaned = line.strip().lower()
    if not cleaned or cleaned.startswith("#"):
        return ""
    cleaned = re.sub(r'[`\[\]()]', '', cleaned).strip()
    return cleaned


def main():
    # 1. Checked Domains aus dem Issue auslesen (falls durchgelaufen)
    selected_domains = []
    if ISSUE_BODY:
        checked_pattern = re.compile(
            r'-\s*\[[xX]\]\s*(?:\[)?\s*`([^`]+)`\s*(?:\]\s*\([^)]+\))?',
            re.DOTALL
        )
        selected_domains = checked_pattern.findall(ISSUE_BODY)

    cleaned_new_domains = [d.strip().lower() for d in selected_domains if d.strip()]
    if cleaned_new_domains:
        print(f"Found {len(cleaned_new_domains)} checked domains from issue: {cleaned_new_domains}")

    # Speicher für alle Domains nach Kategorie
    all_domains_by_category = {cat: set() for cat in CATEGORIES.keys()}

    # 2. Bestehende Master-Whitelist einlesen (falls vorhanden)
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                d = clean_domain_line(line)
                if d:
                    assigned_cat = classify_domain(d)
                    all_domains_by_category[assigned_cat].add(d)

    # 3. Custom-Whitelist einlesen (custom_whitelist.txt im Main-Verzeichnis)
    if os.path.exists(CUSTOM_WHITELIST_PATH):
        print(f"Reading custom domains from '{CUSTOM_WHITELIST_PATH}'...")
        with open(CUSTOM_WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                d = clean_domain_line(line)
                if d:
                    all_domains_by_category["Persönliche Custom Domains"].add(d)
    else:
        # Erstelle eine leere Beispieldatei, falls noch nicht vorhanden
        with open(CUSTOM_WHITELIST_PATH, "w", encoding="utf-8") as f:
            f.write("# Tragen Sie hier Ihre eigenen Custom Domains ein (eine pro Zeile)\n")

    # 4. Neue Domains aus dem Issue einsortieren
    for domain in cleaned_new_domains:
        target_cat = classify_domain(domain)
        # Prüfen, ob Domain global schon existiert
        exists_already = any(domain in domain_set for domain_set in all_domains_by_category.values())
        if not exists_already:
            all_domains_by_category[target_cat].add(domain)
            print(f"Added '{domain}' to category '{target_cat}'")

    # 5. Master-Whitelist formatiert mit allen Kategorien neu schreiben
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

    print(f"Successfully updated master categories, included custom domains, and generated '{EXPORT_PATH}' with {len(all_flat_domains)} total domains.")


if __name__ == "__main__":
    main()
