#!/usr/bin/env python3
"""
Applies checked domains from GitHub Issues (both weekly research and 
child requests) into whitelist.txt, classifies them into 11 distinct categories,
integrates personal custom domains, and generates the FRITZ!Box export.
"""

import os
import re
from urllib.parse import urlparse

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
WHITELIST_PATH = "whitelist.txt"
CUSTOM_WHITELIST_PATH = "custom_whitelist.txt"
EXPORT_PATH = "whitelist_export.txt"

# 11 disjunkte Kategorien
CATEGORIES = {
    "01. Kinder-Suchmaschinen & Jugendschutz": [
        "fragfinn", "blindekuh", "klicksafe", "internet-abc", "jugendschutz"
    ],
    "02. Geprüfte Schul- und Lernportale": [
        "schule", "lernen", "unterricht", "lo-net", "moodle", "maus.schule", 
        "antolin", "alphabet", "ki-kindgerecht"
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
    "12. Persönliche Custom Domains": []
}


def get_base_domain(hostname: str) -> str:
    parts = hostname.split(".")
    if len(parts) <= 2:
        return hostname
    if len(parts) >= 3 and parts[-2] in ("schule", "gov", "edu", "mil") and len(parts[-1]) == 2:
        if len(parts) >= 4:
            return f"{parts[-3]}.{parts[-2]}.{parts[-1]}"
    return f"{parts[-2]}.{parts[-1]}"


def sanitize_domain(raw_entry: str) -> str:
    entry = raw_entry.strip().lower()
    if not entry or entry.startswith(("#", "javascript:", "mailto:")):
        return ""
    if not entry.startswith(("http://", "https://")):
        entry = "http://" + entry
    try:
        parsed = urlparse(entry)
        hostname = parsed.hostname
        if not hostname:
            return ""
        hostname = hostname.rstrip(".")
        if hostname.startswith("www."):
            hostname = hostname[4:]
        if "." in hostname and not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
            return get_base_domain(hostname)
    except Exception:
        pass
    return ""


def classify_domain(domain: str) -> str:
    d_lower = domain.lower()
    for cat_name, keywords in CATEGORIES.items():
        if cat_name in ["12. Persönliche Custom Domains", "03. Allgemeines Wissen & Lexika"]:
            continue
        for kw in keywords:
            if kw in d_lower:
                return cat_name
    return "03. Allgemeines Wissen & Lexika"


def clean_domain_line(line: str) -> str:
    cleaned = line.strip().lower()
    if not cleaned or cleaned.startswith("#"):
        return ""
    return re.sub(r'[`\[\]()]', '', cleaned).strip()


def main():
    selected_domains = []
    if ISSUE_BODY:
        # 1. Haken aus normalen Recherche-Issues abfangen (z.B. - [x] `domain.de`)
        checked_pattern = re.compile(r'-\s*\[[xX]\]\s*(?:\[)?\s*`([^`]+)`', re.DOTALL)
        selected_domains.extend(checked_pattern.findall(ISSUE_BODY))

        # 2. Direkte Eingaben aus dem Kinder-Wunsch-Formular abfangen
        # Das yml-Formular schreibt den Text direkt unter die Überschrift
        for line in ISSUE_BODY.splitlines():
            cleaned_line = sanitize_domain(line)
            if cleaned_line:
                selected_domains.append(cleaned_line)

    cleaned_new_domains = [sanitize_domain(d) for d in selected_domains if sanitize_domain(d)]
    cleaned_new_domains = list(set(cleaned_new_domains)) # Duplikate entfernen

    all_domains_by_category = {cat: set() for cat in CATEGORIES.keys()}

    # Master-Whitelist einlesen
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
                    base_d = sanitize_domain(d)
                    if base_d:
                        if current_cat == "12. Persönliche Custom Domains":
                            all_domains_by_category["12. Persönliche Custom Domains"].add(base_d)
                        else:
                            assigned_cat = classify_domain(base_d)
                            all_domains_by_category[assigned_cat].add(base_d)

    # Custom-Whitelist einlesen
    if os.path.exists(CUSTOM_WHITELIST_PATH):
        with open(CUSTOM_WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                d = clean_domain_line(line)
                base_d = sanitize_domain(d)
                if base_d:
                    all_domains_by_category["12. Persönliche Custom Domains"].add(base_d)

    # Neue Domains einsortieren
    for domain in cleaned_new_domains:
        target_cat = classify_domain(domain)
        exists_already = any(domain in domain_set for domain_set in all_domains_by_category.values())
        if not exists_already:
            all_domains_by_category[target_cat].add(domain)
            print(f"Added requested domain '{domain}' to category '{target_cat}'")

    # Master-Whitelist schreiben
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

    # Export schreiben
    all_flat_domains = set()
    for domain_set in all_domains_by_category.values():
        all_flat_domains.update(domain_set)

    with open(EXPORT_PATH, "w", encoding="utf-8") as exp:
        for domain in sorted(all_flat_domains):
            exp.write(f"{domain}\n")

    print(f"Successfully processed request and generated '{EXPORT_PATH}' with {len(all_flat_domains)} domains.")


if __name__ == "__main__":
    main()
