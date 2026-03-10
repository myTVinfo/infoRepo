#!/usr/bin/env python3
import re
import sys
import urllib.request

SOURCES = [
    ("iptv-org", "https://iptv-org.github.io/iptv/index.m3u"),
    ("Free-TV", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"),
    ("Webcam FR", "https://raw.githubusercontent.com/El-cam0s/camo/main/camFR.m3u"),
]

OUTFILE = "playlist-final.m3u"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (GitHub Actions)"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def normalize_m3u(text: str) -> str:
    # Normalize newlines and ensure header exists
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in text.split("\n") if ln.strip() != ""]
    if not lines:
        return "#EXTM3U\n"
    if lines[0] != "#EXTM3U":
        lines.insert(0, "#EXTM3U")
    return "\n".join(lines) + "\n"


def iter_entries(lines):
    # Yields (#EXTINF line, url line) pairs
    extinf = None
    for ln in lines:
        if ln.startswith("#EXTINF:"):
            extinf = ln
            continue
        if ln.startswith("http://") or ln.startswith("https://"):
            if extinf:
                yield extinf, ln
            extinf = None


def key_for(extinf: str, url: str) -> str:
    # Prefer tvg-id if present, else url
    m = re.search(r'tvg-id="([^"]+)"', extinf)
    if m and m.group(1).strip():
        return "tvgid:" + m.group(1).strip().lower()
    return "url:" + url.strip().lower()


def main():
    merged = ["#EXTM3U"]
    seen = set()
    total = 0
    kept = 0

    for name, url in SOURCES:
        try:
            raw = fetch(url)
        except Exception as e:
            print(f"[WARN] Failed to fetch {name}: {url} ({e})", file=sys.stderr)
            continue

        norm = normalize_m3u(raw)
        lines = norm.split("\n")
        for extinf, media_url in iter_entries(lines):
            total += 1
            k = key_for(extinf, media_url)
            if k in seen:
                continue
            seen.add(k)
            merged.append(extinf)
            merged.append(media_url)
            kept += 1

    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write("\n".join(merged).strip() + "\n")

    print(f"[OK] Wrote {OUTFILE}: kept={kept} total_seen={total}")

if __name__ == "__main__":
    main()
