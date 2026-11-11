# 🛡️ Kid-Safe FRITZ!Box Whitelist Automation

This repository manages and automates a child-safe domain whitelist (with a limit of 500 entries) for the FRITZ!Box. It combines weekly research on renowned pedagogical portals with a structured master list and a fully automated FRITZ!Box export file.

> ⚠️ **Regional Note:** The initial whitelist is currently tailored primarily towards **Northern Germany** (e.g., regional educational initiatives, local cultural projects, and state media authorities). If you are using this whitelist in other regions, we recommend adjusting and expanding the categories in `whitelist.txt` or your `custom_whitelist.txt` to fit your local requirements during the initial setup.
---

## 📂 Project Structure

- **`whitelist.txt`**: The master file, neatly sorted into 11 pedagogical and technical categories, including your personal custom domains.
- **`whitelist_export.txt`**: The flat, comment-free export file. This file is automatically updated on every change and can be **directly** copied into your FRITZ!Box.
- **`custom_whitelist.txt`**: Your personal section in the root directory for custom allowances (one domain per line).
- **`.github/workflows/`**: Contains the GitHub Actions for weekly research and automatic processing of approvals when issues are closed.

---

## 📥 Guide: How to Apply Allowed Internet Sites in the FRITZ!Box

The management of the whitelist in the FRITZ!Box parental control profile depends on your installed **FRITZ!OS version**. Please use the appropriate guide for your system:

### For FRITZ!OS 8.2.5 & 8.5 (Current Versions)

1. **Access the Export File:** 
   * Open the file **`whitelist_export.txt`** in this repository (or copy its raw content to your clipboard using the "Raw" button).
2. **Open the User Interface:** 
   * Go to `http://fritz.box` in your browser and log in as an administrator.
3. **Open Filter Settings:** 
   * Navigate to **Internet** -> **Filters** -> **Parental Controls** tab.
4. **Edit Profile:** 
   * Click the **Edit (pencil) icon** next to the desired child profile.
5. **Open Allowance List:** 
   * Scroll down to the **Internet Sites** or **Access Restrictions** section.
   * Select the option **"Filter internet sites (Whitelist / Allowance list active)"**.
6. **Insert Domains:** 
   * Paste the copied domains from `whitelist_export.txt` as a block into the designated text field (*Allowed internet sites*). 
   * *Note:* FRITZ!OS 8.2.5+ processes block copies and pure domain lists extremely reliably. Since the export file contains no comments or blank lines, you can paste the entire content without any errors.
7. **Save:** 
   * Click **Apply** at the bottom. The allowance will take effect immediately for the assigned device.

**Pro Recommendation (DNS Security):** 
   * To maximize safety alongside the whitelist, it is highly recommended to set up a family-friendly DNS server in your FRITZ!Box network settings (`Internet` -> `Account Information` -> `DNS Servers`). We recommend using **[Cloudflare 1.1.1.1 for Families](https://developers.cloudflare.com/1.1.1.1/setup/#1111-for-families)** (Malware Blocking + Adult Content: Primary `1.1.1.3`, Secondary `1.0.0.3`) to automatically protect all devices at the network level.

---

## ⚙️ How the Automation Works

1. **Weekly Scan:** Every Monday, the system scans RSS feeds (e.g., Seitenstark, Internet-ABC, Klicksafe) and verified allowlists for new, child-safe domains.
2. **Review via GitHub Issue:** An issue is automatically created containing all proposals with clickable links.
3. **Review & Approval:** You inspect the sites via a click (opening in a new tab), check the boxes for the desired domains, and **close the issue**.
4. **Automated Sync:** A script automatically sorts the new domains into the appropriate categories of `whitelist.txt` and updates `whitelist_export.txt` in seconds.

---

## 📄 License

This repository is licensed under the [MIT License](./LICENSE). Feel free to share, adapt, and build upon it!
