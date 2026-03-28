#!/usr/bin/env python3
import urllib.request

SOURCES = [
    ("iptv-org", "https://iptv-org.github.io/iptv/index.m3u"),
    ("Free-TV", "https://raw.githubusercontent.com/Free-TV/IPTV/master/playlist.m3u8"),
    ("Webcam FR", "https://raw.githubusercontent.com/El-cam0s/camo/main/camFR.m3u"),
]

# === AJOUT DES 3 CHAÎNES ===
DIRECT_CHANNELS = [
    (
        '#EXTINF:-1 group-title="News",BFM-OK',
        "https://viamotionhsi.netplus.ch/live/eds/bfmtv/browser-HLS8/bfmtv.m3u8",
    ),
    (
        '#EXTINF:-1 group-title="News",FranceInfo-OK',
        "https://viamotionhsi.netplus.ch/live/eds/franceinfo/browser-HLS8/franceinfo.m3u8",
    ),
    (
        '#EXTINF:-1 group-title="News",Sky News 1080p',
        "https://linear417-gb-hls1-prd-ak.cdn.skycdp.com/100e/Content/HLS_001_1080_30/Live/channel(skynews)/index_1080-30.m3u8",
    ),
]

OUTFILE = "playlist-final.m3u"


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def parse_m3u(text: str):
    lines = text.replace("\r", "").split("\n")
    entries = []
    current = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("#EXTINF"):
            current = line
        elif not line.startswith("#") and current:
            entries.append((current, line))
            current = None

    return entries


def main():
    output = ["#EXTM3U"]
    seen_urls = set()

    # === SOURCES ===
    for name, url in SOURCES:
        try:
            content = fetch(url)
            entries = parse_m3u(content)

            for extinf, stream in entries:
                if stream not in seen_urls:
                    output.append(extinf)
                    output.append(stream)
                    seen_urls.add(stream)

        except Exception:
            continue

    # === CHAÎNES DIRECTES ===
    for extinf, stream in DIRECT_CHANNELS:
        if stream not in seen_urls:
            output.append(extinf)
            output.append(stream)
            seen_urls.add(stream)

    # === WRITE FILE ===
    with open(OUTFILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output) + "\n")


if __name__ == "__main__":
    main()
