#!/usr/bin/env python3
"""
FRITZ!Box Whitelist Research Script
-----------------------------------
Periodically checks active external sources (fragFINN, HaGeZi) AND parses RSS feeds
from renowned pedagogical parent guides (Internet-ABC, Klicksafe, Seitenstark)
to discover new kid-safe domain candidates.
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
        "name": "fragFINN Official Whitelist (via eBlocker Mirror)",
        "url": "https://raw.githubusercontent.com/eblocker/eblocker-lists/main/fragFINN-whitelist.txt",
    },
    {
        "name": "HaGeZi Referral Allowlist",
        "url": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/whitelists/referral-sites.txt",
    },
]

# 2. Editorial RSS Feeds from Educational & Media Competence Portals
EDITORIAL_FEEDS = [
    {
        "name": "Internet-ABC Surftipps Feed",
        "url": "https://www.internet-abc.de/kinder/rss.xml",
    },
    {
        "name": "Klicksafe Newsfeed",
        "url": "https://www.klicksafe.de/service/newsfeed.xml",
    },
    {
        "name": "Seitenstark RSS Feed",
        "url": "https://seitenstark.de/rss.xml",
    },
]

# Domains to ignore during extraction (social media, search engines, system domains)
IGNORED_DOMAINS = {
    "facebook.com", "instagram.com", "twitter.com", "x.com", "youtube.com",
    "google.com", "google.de", "bing.com", "t.co", "bit.ly", "w3.org"
}


def sanitize_domain(raw_entry: str) -> str:
    """
    Cleans raw text input, URLs, or paths and extracts a normalized base domain.
    Returns an empty string if the entry is invalid or ignored.
    """
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
        
        # Validate domain structure & exclude generic/ignored hosts
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
    """Reads the existing local whitelist and returns a set of unique normalized domains."""
    domains = set()
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                domain = sanitize_domain(line)
                if domain:
                    domains.add(domain)
    return domains


def fetch_remote_domains(source_url: str) -> set:
    """Fetches and parses raw domain list from a remote text file location."""
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
    """Parses an RSS XML feed and extracts linked external domains from item links and content."""
    found_domains = set()
    req = urllib.request.Request(
        feed_url, 
        headers={"User-Agent": "Mozilla/5.0 (FRITZBox-Whitelist-Researcher/1.0)"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            # Find all links or text content inside RSS items
            for item in root.findall(".//item"):
                # 1. Extract directly from <link>
                link_elem = item.find("link")
                if link_elem is not None and link_elem.text:
                    domain = sanitize_domain(link_elem.text)
                    if domain:
                        found_domains.add(domain)
                
                # 2. Extract embedded URLs inside <description>
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
    
    # 1. Load active local whitelist
    local_domains = load_local_whitelist(LOCAL_WHITELIST_PATH)
    active_count = len(local_domains)
    remaining_budget = FRITZBOX_DOMAIN_LIMIT - active_count
    
    print(f"Loaded {active_count} active domains from local whitelist.")
    print(f"Remaining slot capacity (500 max): {remaining_budget} slots.")

    candidate_domains = set()

    # 2. Fetch candidates from external text repositories
    for source in EXTERNAL_SOURCES:
        print(f"Scanning text repository: {source['name']}...")
        remote_domains = fetch_remote_domains(source["url"])
        for domain in remote_domains:
            if domain not in local_domains:
                candidate_domains.add(domain)

    # 3. Parse candidates from RSS feeds (Parent & Media Guides)
    for feed in EDITORIAL_FEEDS:
        print(f"Parsing RSS feed: {feed['name']}...")
        rss_domains = parse_rss_feed(feed["url"])
        for domain in rss_domains:
            if domain not in local_domains:
                candidate_domains.add(domain)

    new_proposals = sorted(list(candidate_domains))
    
    # 4. Write Markdown Report for GitHub Action Issue
    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as report:
        report.write("## 🔍 Weekly FRITZ!Box Whitelist Research Report\n\n")
        
        report.write("### 📊 Current Whitelist Capacity Status\n")
        report.write(f"- **Active Whitelisted Domains:** `{active_count}` / `{FRITZBOX_DOMAIN_LIMIT}`\n")
        report.write(f"- **Remaining Slot Capacity:** `{remaining_budget}` slots\n\n")
        
        report.write("---\n\n")
        report.write("### 💡 Recommended Domain Additions\n")
        
        if new_proposals:
            report.write(
                "The following kid-friendly domains were discovered in active lists & RSS feeds "
                "and are **not yet included** in your `whitelist.txt`:\n\n"
            )
            for domain in new_proposals:
                report.write(f"- [ ] `{domain}`\n")
                
            report.write(
                "\n> **Note:** Please review candidate appropriateness and verify "
                f"you do not exceed your **{remaining_budget}** remaining slots before adding them."
            )
        else:
            report.write("✅ No new unique domain proposals found this week. Your whitelist is up to date!")
            
    print(f"Research complete. Generated '{OUTPUT_REPORT_PATH}' with {len(new_proposals)} proposals.")


if __name__ == "__main__":
    main()
