#!/usr/bin/env python3
"""
Applies checked domains from a GitHub Issue body directly into whitelist.txt,
handling both plain backtick formats and markdown clickable links.
"""

import os
import re

ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
WHITELIST_PATH = "whitelist.txt"


def main():
    if not ISSUE_BODY:
        print("No issue body found.")
        return

    # Regex to match checked items supporting both formats:
    # - [x] `domain.tld` or - [x] [`domain.tld`](https://domain.tld)
    checked_pattern = re.compile(r'-\s*\[[xX]\]\s*(?:\[)?`([^`]+)`(?:\]\([^)]+\))?')
    selected_domains = checked_pattern.findall(ISSUE_BODY)

    if not selected_domains:
        print("No checked domains found in issue body.")
        return

    # Clean and normalize domains
    cleaned_domains = [d.strip().lower() for d in selected_domains if d.strip()]
    print(f"Found {len(cleaned_domains)} checked domains to add: {cleaned_domains}")

    # Read current whitelist lines
    existing_lines = []
    existing_domains = set()
    if os.path.exists(WHITELIST_PATH):
        with open(WHITELIST_PATH, "r", encoding="utf-8") as f:
            for line in f:
                existing_lines.append(line)
                stripped = line.strip().lower()
                if stripped and not stripped.startswith("#"):
                    existing_domains.add(stripped)

    # Filter out domains that are already whitelisted
    new_domains_to_add = [d for d in cleaned_domains if d not in existing_domains]

    if not new_domains_to_add:
        print("All checked domains are already in whitelist.txt.")
        return

    with open(WHITELIST_PATH, "a", encoding="utf-8") as f:
        f.write("\n# --- APPROVED VIA AUTOMATED ISSUE --- \n")
        for domain in sorted(set(new_domains_to_add)):
            f.write(f"{domain}\n")
            print(f"Added: {domain}")

    print(f"Successfully added {len(set(new_domains_to_add))} new domains to {WHITELIST_PATH}.")


if __name__ == "__main__":
    main()
