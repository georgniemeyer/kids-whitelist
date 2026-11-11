#!/usr/bin/env python3
"""
FRITZ!Box Whitelist Research Script
-----------------------------------
Periodically checks active external sources (fragFINN, HaGeZi) AND parses RSS feeds
from renowned pedagogical parent guides (Internet-ABC, Klicksafe, Seitenstark)
to discover new kid-safe domain candidates while tracking their original source.
"""

import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# --- CONFIGURATION ---
LOCAL_WHITELIST_PATH = "whitelist.txt"
OUTPUT_REPORT_PATH = "suggestions.md"
FRITZBOX_DOMAIN_LIMIT = 500

# 1. Active Community & Technical Allowlist Sources
EXTERNAL_SOURCES = [
    {
        "name": "fragFINN (eBlocker)",
        "url": "https://raw.githubusercontent.com/eblocker/eblocker-lists/main/fragFINN-whitelist.txt",
    },
    {
        "name": "HaGeZi Allowlist",
        "url": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/whitelists/referral-sites.txt",
    },
]

# 2. Editorial RSS Feeds from Educational & Media Competence Portals
EDITORIAL_FEEDS = [
    {
        "name": "Internet-ABC",
        "url": "https://www.internet-abc.de/kinder/rss.xml",
    },
    {
        "name": "Klicksafe",
        "url": "https://www.klicksafe.de/service/newsfeed.xml",
    },
    {
        "name": "Seitenstark",
        "url": "https://seitenstark.de/rss.xml",
    },
]

IGNORED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com",
    "google.com", "google.de", "bing.com", "t.co", "bit.ly", "w3.org"
}


def sanitize_domain(raw_entry: str) -> str:
    """Cleans raw text input/URLs and extracts a normalized base domain."""
    entry = raw_entry.strip().lower()
    
    if not entry or entry.startswith("#"):
        return ""
    
    if not entry.startswith(("http://", "https://")):
        entry = "http://" + entry
        
    try:
        parsed = urlparse(entry)
        hostname = parsed.hostname
        if not hostname:
            return ""
        
        hostname = hostname.rstrip(".")
        
        if "." in hostname and not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname):
            if hostname not in IGNORED_DOMAINS and not hostname.startswith("www."):
                return hostname
            elif hostname.startswith("www."):
                base_domain = hostname[4:]
                if base_domain not in IGNORED_DOMAINS:
                    return base_domain
    except Exception:
        pass
    
    return ""


def load_local_whitelist(file_path: str) -> set:
    """Reads the existing local whitelist and returns a set of unique domains."""
    domains = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                domain = sanitize_domain(line)
                if domain:
                    domains.add(domain)
    return domains


def fetch_remote_domains(source_url: str) -> set:
    """Fetches raw domain list from a remote text file location."""
    found_domains = set()
    req = urllib.request.Request(
        source_url, 
        headers={"User-Agent": "Mozilla/5.0 (FRITZBox-Whitelist-Researcher/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode("utf-8")
            for line in content.splitlines():
                domain = sanitize_domain(line)
                if domain:
                    found_domains.add(domain)
    except Exception as err:
        print(f"[Warning] Failed to fetch text source '{source_url}': {err}")
    return found_domains


def parse_rss_feed(feed_url: str) -> set:
    """Parses an RSS XML feed and extracts linked external domains."""
    found_domains = set()
    req = urllib.request.Request(
        feed_url, 
        headers={"User-Agent": "Mozilla/5.0 (FRITZBox-Whitelist-Researcher/1.0)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            for item in root.findall(".//item"):
                link_elem = item.find("link")
                if link_elem is not None and link_elem.text:
                    domain = sanitize_domain(link_elem.text)
                    if domain:
                        found_domains.add(domain)
                desc_elem = item.find("description")
                if desc_elem is not None and desc_elem.text:
                    urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', desc_elem.text)
                    for url in urls:
                        domain = sanitize_domain(url)
                        if domain:
                            found_domains.add(domain)
    except Exception as err:
        print(f"[Warning] Failed to parse RSS feed '{feed_url}': {err}")
    return found_domains


def main():
    print("Starting FRITZ!Box Whitelist Research Process...")
    
    local_domains = load_local_whitelist(LOCAL_WHITELIST_PATH)
    active_count = len(local_domains)
    remaining_budget = FRITZBOX_DOMAIN_LIMIT - active_count
    
    # Dictionary mapping domain -> set of source names
    candidates_with_sources = {}

    # 1. Process Text Repositories
    for source in EXTERNAL_SOURCES:
        print(f"Scanning repository: {source['name']}...")
        remote_domains = fetch_remote_domains(source["url"])
        for domain in remote_domains:
            if domain not in local_domains:
                candidates_with_sources.setdefault(domain, set()).add(source["name"])

    # 2. Process RSS Feeds
    for feed in EDITORIAL_FEEDS:
        print(f"Parsing RSS feed: {feed['name']}...")
        rss_domains = parse_rss_feed(feed["url"])
        for domain in rss_domains:
            if domain not in local_domains:
                candidates_with_sources.setdefault(domain, set()).add(feed["name"])

    sorted_domains = sorted(candidates_with_sources.keys())
    
    # 3. Write Report
    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as report:
        report.write("## 🔍 Weekly FRITZ!Box Whitelist Research Report\n\n")
        report.write("### 📊 Current Whitelist Capacity Status\n")
        report.write(f"- **Active Whitelisted Domains:** `{active_count}` / `{FRITZBOX_DOMAIN_LIMIT}`\n")
        report.write(f"- **Remaining Slot Capacity:** `{remaining_budget}` slots\n\n")
        report.write("---\n\n")
        report.write("### 💡 Recommended Domain Additions\n")
        
        if sorted_domains:
            report.write(
                "Check the boxes for domains you want to add. When done, **close this Issue** "
                "or comment `/apply` to automatically merge checked items into `whitelist.txt`:\n\n"
            )
            for domain in sorted_domains:
                sources_str = ", ".join(sorted(candidates_with_sources[domain]))
                report.write(f"- [ ] `{domain}` *(Source: {sources_str})*\n")
                
            report.write(
                "\n> **Note:** Please verify you do not exceed your "
                f"**{remaining_budget}** remaining slots."
            )
        else:
            report.write("✅ No new unique domain proposals found this week. Your whitelist is up to date!")
            
    print(f"Research complete. Generated '{OUTPUT_REPORT_PATH}' with {len(sorted_domains)} proposals.")


if __name__ == "__main__":
    main()
