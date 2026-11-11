# 🛡️ FRITZ!Box Whitelist for Kids (Northern Germany)

A curated, clean, domain-only whitelist optimized for the **FRITZ!Box 500-domain limit** (`FRITZ!OS Allow List`). Designed specifically for a 10-year-old child in Northern Germany (Hamburg / Schleswig-Holstein / Lower Saxony).

---

## ✨ Features

* **Strict FRITZ!Box Optimization:** Raw domains only (no `https://`, no sub-paths). Eliminates redundant path entries to respect the 500-domain restriction.
* **Essential Technical CDNs Included:** Pre-configured with required CDNs (`gstatic`, `cloudflare`, `vimeocdn`, KiKa/ZDF assets) so pages, videos, and images load correctly without opening unwanted domains.
* **Educational & Regional Focus:** Combines German pedagogical core sources (*fragFINN*, *Blinde Kuh*, *seitenstark*) with Northern German media, libraries, museums, and specific local school/learning portals (`lerntraining.de`, Mentimeter integration).
* **Automated Weekly Research:** Powered by a GitHub Action (`Weekly Whitelist Researcher`) that periodically checks external sources for relevant new kids' content and proposes updates via Issues.

---

## 🚀 Usage with FRITZ!Box

1. Open your **FRITZ!Box** web interface (`http://fritz.box`).
2. Navigate to **Internet → Filters → Lists** (*Internet → Filter → Listen*).
3. Click on **Allowed Web Pages (Whitelist)** (*Erlaubte Internetseiten*).
4. Open [`whitelist.txt`](./whitelist.txt) in **Raw** mode, copy the full domain list, and paste it into your FRITZ!Box filter list.
5. Assign the profile to your child's device under **Internet → Filters → Access Profiles** (*Zugangsprofile*).

---

## 📄 License

This repository is licensed under the [MIT License](./LICENSE). Feel free to share, adapt, and build upon it!
