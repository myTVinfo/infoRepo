#!/usr/bin/env python3
import re
import sys
import urllib.request

SOURCES = [
    ("iptv-org", "https://iptv-org.github.io/iptv/index.m3u"),
    ("camo camFR", "https://raw.githubusercontent.com/El-cam0s/camo/main/camFR.m3u"),
]

UA = "Mozilla/5.0 (compatible; infoRepo-m3u-builder/1.0)"

def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")

def is_url(line: str) -> bool:
    return line.startswith("http://") or line.startswith("https://")

def normalize_extinf(line: str) -> str:
    # VLC/iOS: garder un seul champ titre après la virgule.
    # On conserve les attributs (tvg-name, group-title, etc.)
    # Exemple: #EXTINF:-1 tvg-name="X",Titre -> ok
    return line.rstrip()

def main():
    out = []
    out.append("#EXTM3U")

    # dédoublonnage simple par URL de stream (lignes http/https)
    seen_urls = set()

    for (label, src) in SOURCES:
        try:
            text = fetch(src)
        except Exception as e:
            print(f"[WARN] Failed to fetch {label}: {src} ({e})", file=sys.stderr)
            continue

        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.strip().startswith("\ufeff")]
        i = 0
        last_extinf = None
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("#EXTINF"):
                last_extinf = normalize_extinf(ln)
            elif is_url(ln):
                url = ln
                if url not in seen_urls:
                    if last_extinf:
                        out.append(last_extinf)
                    else:
                        out.append(f'#EXTINF:-1 group-title="Sources",{label}')
                    out.append(url)
                    seen_urls.add(url)
                last_extinf = None
            else:
                # ignorer autres tags (EXT-X-*, commentaires, etc.)
                pass
            i += 1

    sys.stdout.write("\n".join(out).strip() + "\n")

if __name__ == "__main__":
    main()
