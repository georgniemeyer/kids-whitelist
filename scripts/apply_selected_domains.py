#!/usr/bin/env python3
"""
Applies checked domains from a GitHub Issue into whitelist.txt,
intelligently sorting them into meaningful pedagogical categories,
and generates a clean, comment-free export file for FRITZ!Box import.
"""

import os
import re

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
WHITELIST_PATH = "whitelist.txt"
EXPORT_PATH = "whitelist_export.txt"

# Definierte, sprechende Kategorien mit Schlüsselwörtern zur automatischen Zuordnung
CATEGORIES = {
    "Schule, Lernen & Medienkompetenz": [
        "schule", "lernen", "recht", "fragfinn", "klicksafe", "antolin", 
        "alphabet", "internet-abc", "ki-kindgerecht"
    ],
    "Wissen, Lexikon & Nachrichten": [
        "duda", "news", "nachrichten", "wissen", "lexikon", "radio", 
        "reporter", "klassik", "frieden", "naturpark", "detektive"
    ],
    "Kinderseiten, Spiele & Kreativität": [
        # Standard-Fallback für alle anderen geprüften Kinderportale
    ]
}


def classify_domain(domain: str) -> str:
    """Weist eine Domain basierend auf Schlüsselwörtern einer passenden Kategorie zu."""
    d_lower = domain.lower()
    for cat_name, keywords in CATEGORIES.items():
        if cat_name == "Kinderseiten, Spiele & Kreativität":
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
    if not ISSUE_BODY:
        print("No issue body found.")
        return

    # Regex zum Extrahieren der angehakten Domains aus dem Issue
    checked_pattern = re.compile(
        r'-\s*\[[xX]\]\s*(?:\[)?\s*`([^`]+)`\s*(?:\]\s*\([^)]+\))?',
        re.DOTALL
    )
    selected_domains = checked_pattern.findall(ISSUE_BODY)

    if not selected_domains:
        print("No checked domains found in issue body.")
        return

    cleaned_new_domains = [d.strip().lower() for d in selected_domains if d.strip()]
    print(f"Found {len(cleaned_new_domains)} checked domains to add: {cleaned_new_domains}")

    # 1. Alle bisherigen Domains aus der Master-Whitelist einlesen (bestehende behalten)
    all_domains_by_category = {cat: set() for cat in CATEGORIES.keys()}
    
    if os.path.exists(WHITELIST_PATH):
        current_cat = "Kinderseiten, Spiele & Kreativität"
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line_str = line.strip()
                # Versuche bestehende Kategorien aus Kommentaren zu erkennen
                if line_str.startswith("#") and "KATEGORIE:" in line_str:
                    for cat in CATEGORIES.keys():
                        if cat.lower() in line_str.lower():
                            current_cat = cat
                            break
                    continue
                
                d = clean_domain_line(line)
                if d:
                    # In welche Kategorie gehörte sie bisher oder neu einteilen?
                    assigned_cat = classify_domain(d)
                    # Falls die alte Kategorie spezifischer war, behalten wir sie bei, ansonsten neu klassifizieren
                    all_domains_by_category.setdefault(assigned_cat, set()).add(d)

    # 2. Neue Domains hinzufügen und intelligent einsortieren
    added_count = 0
    for domain in cleaned_new_domains:
        target_cat = classify_domain(domain)
        # Prüfen, ob Domain global schon existiert
        exists_already = any(domain in domain_set for domain_set in all_domains_by_category.values())
        if not exists_already:
            all_domains_by_category.setdefault(target_cat, set()).add(domain)
            print(f"Added '{domain}' to category '{target_cat}'")
            added_count += 1

    if added_count == 0:
        print("No new unique domains were added (all already present).")

    # 3. Master-Whitelist formatiert mit sprechenden Kategorien neu schreiben
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

    # 4. Saubere FRITZ!Box Export-Datei generieren (flach, alphabetisch, keine Kommentare)
    all_flat_domains = set()
    for domain_set in all_domains_by_category.values():
        all_flat_domains.update(domain_set)

    with open(EXPORT_PATH, "w", encoding="utf-8") as exp:
        for domain in sorted(all_flat_domains):
            exp.write(f"{domain}\n")

    print(f"Successfully updated master categories and generated '{EXPORT_PATH}' with {len(all_flat_domains)} total domains.")


if __name__ == "__main__":
    main()
