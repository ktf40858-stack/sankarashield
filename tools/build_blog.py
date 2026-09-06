#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SankaraShield — blog generator.

Reads the raw post archive (one .txt per post, plus its illustration) and emits
static article pages, the blog index, a JSON index and sitemap fragments.

    python tools/build_blog.py

Source of truth for content:  C:\\Users\\Freddy\\Desktop\\Post\\Sankarashield
Nothing outside sankarashield-v2/ is ever written to.
"""

import html
import json
import os
import re
import shutil
import sys
import unicodedata
from datetime import date

from PIL import Image

# --------------------------------------------------------------------------
# paths / config
# --------------------------------------------------------------------------
SRC = r"C:\Users\Freddy\Desktop\Post\Sankarashield"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_DIR = os.path.join(ROOT, "blog")
IMG_DIR = os.path.join(ROOT, "assets", "blog")

SITE = "https://www.sankarashield.com"
BRAND = "SankaraShield"

MONTHS = {
    "Fevrier": 2, "Mars": 3, "Avril": 4, "Mai": 5,
    "Juin": 6, "Juillet": 7, "Aout": 8, "September": 9,
}
YEAR = 2026

MONTH_TOKENS = {
    "january": 1, "february": 2, "fevrier": 2, "march": 3, "mars": 3,
    "april": 4, "avril": 4, "may": 5, "mai": 5, "june": 6, "juin": 6,
    "july": 7, "juillet": 7, "august": 8, "aout": 8,
    "september": 9, "septembre": 9, "october": 10, "novembre": 11, "decembre": 12,
}
WEEKDAYS = ("lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche")

TOPICS = [
    ("Threat Intelligence", ("ransomware", "breach", "extortion", "botnet", "apt",
                             "threat actor", "lazarus", "shinyhunters", "qilin",
                             "medusa", "stole", "leak", "espionage", "indictment",
                             "phishing", "vishing", "scattered", "arrested")),
    ("Vulnerabilities", ("cve-", "zero-day", "zeroday", "cvss", "patch tuesday",
                         "kev", "exploit", "rce", "vulnerabilit", "privilege escalation",
                         "command injection", "sql injection", "traversal", "advisory")),
    ("AI Security", ("ai", "llm", "artificial intelligence", "agentic",
                     "mcp", "copilot", "model context", "litellm", "genai", "chatgpt")),
    ("Cloud & Zero Trust", ("zero trust", "sase", "ztna", "cloud", "azure", "entra",
                            "aws", "saas", "identity", "iam", "okta", "microsegmentation",
                            "segmentation", "hypervisor", "kubernetes")),
    ("Network Infrastructure", ("bgp", "ospf", "routing", "outage", "dns", "fabric",
                                "switch", "router", "wan", "sd-wan", "interconnect",
                                "transit", "wi-fi", "wifi", "latency", "packet", "vlan")),
    ("Security Operations", ("compliance", "nis2", "dora", "cisa", "governance",
                             "awareness", "incident response", "soc", "runbook",
                             "hardening", "certification", "ccnp", "career", "training")),
]

DELIM_RE = re.compile(r"^[\u2500-\u257F\-=_\u2014\u2013]{6,}$")
HASHTAG_RE = re.compile(r"^#\w")
CVE_RE = re.compile(r"\b(CVE-\d{4}-\d{4,7})\b")
LEAD_RE = re.compile(
    r"^([A-Z0-9][A-Z0-9 &/'\u2019\.\-\(\)]{2,58}?)\s*[\u2014\u2013]\s+(.{3,})$", re.S
)

# emoji, dingbats, arrows and geometric bullets: stripped for a sober editorial tone
EMOJI_RE = re.compile(
    "[\U0001F000-\U0001FAFF\u2190-\u21FF\u2300-\u27BF\u2B00-\u2BFF"
    "\u25A0-\u25FF\u2600-\u26FF\uFE0F\u200D\u20E3]+"
)
# drafting notes left in the source files by the writing tool
JUNK_RE = re.compile(
    r"(caract[e\u00E8]res?\s*[\u2014\u2013:-]|voici le post|post\s+final|dans la cible|"
    r"voici la version|version (optimis|finale)|^\s*ok[,\.]?\s*$)", re.I
)


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def read_text(path):
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(path, "r", encoding=enc) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def slugify(text, maxlen=72):
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    if len(text) > maxlen:
        text = text[:maxlen].rsplit("-", 1)[0]
    return text or "post"


def norm_key(name):
    return re.sub(r"[^a-z0-9]", "", name.lower())


MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.S)


def strip_md(text):
    """Flatten leftover markdown emphasis for plain-text contexts."""
    text = MD_BOLD_RE.sub(r"\1", text)
    return text.replace("**", "").strip(" *")


def esc(text):
    return html.escape(strip_md(text), quote=False)


def enrich(text):
    """Inline typography: markdown emphasis, CVE chips."""
    out = html.escape(text, quote=False)
    out = MD_BOLD_RE.sub(r"<strong>\1</strong>", out)
    out = out.replace("**", "")
    out = CVE_RE.sub(r'<span class="cve">\1</span>', out)
    return out


# --------------------------------------------------------------------------
# date + image resolution
# --------------------------------------------------------------------------
def resolve_date(path, month_folder):
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0]
    low = stem.lower()

    month = MONTHS.get(month_folder, 1)
    for token, num in MONTH_TOKENS.items():
        if token in low:
            month = num
            break

    day = None
    m = re.search(r"(?:%s)[_ ]*(\d{1,2})" % "|".join(WEEKDAYS), low)
    if m:
        day = int(m.group(1))
    if day is None:
        m = re.search(r"(?:^|[_\- ])(\d{1,2})[_\- ]*(?:%s)" % "|".join(MONTH_TOKENS), low)
        if m:
            day = int(m.group(1))
    if day is None:
        m = re.search(r"(?:%s)[_\- ]*(\d{1,2})\b" % "|".join(WEEKDAYS), low)
        if m:
            day = int(m.group(1))
    if day is None or not (1 <= day <= 31):
        ts = date.fromtimestamp(os.path.getmtime(path))
        return ts, True
    try:
        return date(YEAR, month, day), False
    except ValueError:
        return date.fromtimestamp(os.path.getmtime(path)), True


def find_image(txt_path, folder_files):
    """Match an illustration to a post, preferring the logo-branded version."""
    stem = os.path.splitext(os.path.basename(txt_path))[0]
    low = stem.lower()
    key = norm_key(stem)

    weekday = next((w for w in WEEKDAYS if w in low), None)
    m = re.search(r"(?:%s)[_ ]*(\d{1,2})" % "|".join(WEEKDAYS), low)
    day = m.group(1) if m else None
    if day is None:
        # also catch "post_15April_..." where the month name follows the day directly
        m = re.search(r"(?:^|[_\- ])(\d{1,2})(?=[_\- ]|[a-z])", low)
        day = m.group(1) if m else None

    cands = []
    for fname in folder_files:
        if not fname.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            continue
        fkey = norm_key(os.path.splitext(fname)[0])
        score = 0
        if fkey.startswith(key[:28]) and len(key) > 12:
            score += 100
        if weekday and weekday in fkey:
            score += 20
        if day and re.search(r"%s0?%s" % (weekday or "", day), fkey):
            score += 30
        elif day and day in fkey:
            score += 12
        if score < 20:
            continue
        if "withlogo" in fkey:
            score += 15
        elif "raw" in fkey:
            score -= 5
        cands.append((score, fname))

    if not cands:
        return None
    cands.sort(reverse=True)
    return cands[0][1]


def make_cover(slug, topic):
    """Draw a branded cover for a post that has no illustration.

    The layout is seeded from the slug, so every post gets a stable, distinct
    network motif instead of a flat placeholder — and the grid stays even.
    """
    import random
    from PIL import ImageDraw, ImageFont

    S = 2                                                  # supersample, then downscale
    W, H = 1200 * S, 675 * S
    img = Image.new("RGB", (W, H), (42, 14, 95))           # --v-950
    d = ImageDraw.Draw(img)

    # deep violet wash: --v-950 top-left to --v-800 bottom-right, so the cover
    # reads as a filled tile against the white card rather than as empty space.
    top, bottom = (36, 12, 82), (86, 34, 168)
    for y in range(H):
        t = y / H
        d.line([(0, y), (W, y)],
               fill=tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3)))

    def font(size):
        for p in (r"C:\Windows\Fonts\segoeuib.ttf", r"C:\Windows\Fonts\arialbd.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
        return ImageFont.load_default()

    label_font, mark_font = font(34 * S), font(24 * S)
    label = topic.upper()
    label_w = d.textlength(label, font=label_font)
    # keep the motif clear of the caption block so nodes never sit under the text
    reserved = (44 * S, 40 * S, 64 * S + max(label_w, d.textlength("SANKARASHIELD", font=mark_font)), 120 * S)

    rnd = random.Random(slug)
    nodes = []
    cols, rows = 6, 4
    for cx in range(cols):
        for ry in range(rows):
            if rnd.random() < 0.34:
                continue
            x = int((cx + 0.5 + rnd.uniform(-0.3, 0.3)) * W / cols)
            y = int((ry + 0.5 + rnd.uniform(-0.3, 0.3)) * H / rows)
            if reserved[0] - 30 * S < x < reserved[2] + 30 * S and \
               reserved[1] - 30 * S < y < reserved[3] + 30 * S:
                continue
            nodes.append((x, y))

    for i, a in enumerate(nodes):                          # link the two nearest peers
        peers = sorted(((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2, j)
                       for j, b in enumerate(nodes) if j != i)[:2]
        for _, j in peers:
            b = nodes[j]
            d.line([a, b], fill=(129, 92, 214), width=3 * S)

    for i, (x, y) in enumerate(nodes):
        r = (13 if i % 5 else 21) * S
        col = (196, 181, 253) if i % 5 == 0 else (139, 92, 246)
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)
        if i % 5 == 0:
            hr = r + 11 * S
            d.ellipse([x - hr, y - hr, x + hr, y + hr], outline=(167, 139, 250), width=3 * S)

    d.rectangle([0, 0, 12 * S, H], fill=(24, 180, 108))    # brand rule, logo green
    d.text((44 * S, 40 * S), label, font=label_font, fill=(237, 233, 254))
    d.text((44 * S, 86 * S), "SANKARASHIELD", font=mark_font, fill=(167, 139, 250))

    img = img.resize((1200, 675), Image.LANCZOS)

    mark_path = os.path.join(ROOT, "assets", "img", "brand-mark.png")
    if os.path.isfile(mark_path):
        from PIL import ImageEnhance
        mark = Image.open(mark_path).convert("RGBA")
        mark.thumbnail((84, 84), Image.LANCZOS)
        rgb, alpha = mark.convert("RGB"), mark.getchannel("A")
        rgb = ImageEnhance.Brightness(rgb).enhance(1.85)    # readable on the violet ground
        rgb = ImageEnhance.Color(rgb).enhance(1.25)
        mark = Image.merge("RGBA", rgb.split() + (alpha,))
        img.paste(mark, (1200 - mark.width - 44, 675 - mark.height - 40), mark)

    hero_name, thumb_name = "%s.jpg" % slug, "%s-thumb.jpg" % slug
    img.save(os.path.join(IMG_DIR, hero_name), "JPEG",
             quality=84, optimize=True, progressive=True)
    thumb = img.copy()
    thumb.thumbnail((640, 640), Image.LANCZOS)
    thumb.save(os.path.join(IMG_DIR, thumb_name), "JPEG",
               quality=80, optimize=True, progressive=True)
    return hero_name, thumb_name


def process_image(src_path, slug):
    """Emit a 1200px hero and a 640px thumb as progressive JPEG."""
    try:
        im = Image.open(src_path)
        im = im.convert("RGB")
    except Exception as exc:                                   # noqa: BLE001
        print("   ! image skipped (%s): %s" % (os.path.basename(src_path), exc))
        return None, None

    w, h = im.size
    target_ratio = 16 / 9
    if w / h > target_ratio * 1.25:                            # very wide -> centre crop
        new_w = int(h * target_ratio)
        im = im.crop(((w - new_w) // 2, 0, (w - new_w) // 2 + new_w, h))
    elif h / w > 1.15:                                         # portrait -> crop to 4:3
        new_h = int(w / (4 / 3))
        top = int((h - new_h) * 0.32)
        im = im.crop((0, top, w, top + new_h))

    hero_name = "%s.jpg" % slug
    thumb_name = "%s-thumb.jpg" % slug

    hero = im.copy()
    hero.thumbnail((1200, 1200), Image.LANCZOS)
    hero.save(os.path.join(IMG_DIR, hero_name), "JPEG",
              quality=82, optimize=True, progressive=True)

    thumb = im.copy()
    thumb.thumbnail((640, 640), Image.LANCZOS)
    thumb.save(os.path.join(IMG_DIR, thumb_name), "JPEG",
               quality=78, optimize=True, progressive=True)

    return hero_name, thumb_name


# --------------------------------------------------------------------------
# text parsing
# --------------------------------------------------------------------------
def to_blocks(raw):
    raw = EMOJI_RE.sub("", raw)
    lines = [ln.rstrip() for ln in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    lines = [ln.strip() for ln in lines]

    blocks, cur = [], []
    for ln in lines:
        if ln:
            cur.append(ln)
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)

    # drop drafting notes the writing tool left behind
    return [b for b in blocks if not JUNK_RE.search(" ".join(b)[:120])]


def split_title(first_block_text):
    """Return (title, leftover). Long opening hooks are cut at the first sentence."""
    text = first_block_text.strip()
    if len(text) <= 118:
        return text, ""
    m = re.search(r"^(.{40,118}?[\.\?\!\u2014:])\s+(.+)$", text, re.S)
    if m:
        return m.group(1).rstrip(" .:\u2014"), m.group(2).strip()
    cut = text[:112].rsplit(" ", 1)[0]
    return cut, text[len(cut):].strip()


_KEY_CACHE = {}


def _key_re(key):
    if key not in _KEY_CACHE:
        # word-boundary match so "ai" does not fire inside "email" or "chain"
        _KEY_CACHE[key] = re.compile(r"(?<![a-z])" + re.escape(key) + r"(?![a-z])")
    return _KEY_CACHE[key]


def classify(title, body_text):
    """Title carries three times the weight of the body; CVE density decides ties."""
    t = title.lower()
    b = body_text[:3000].lower()
    scores = {}
    for name, keys in TOPICS:
        score = 0
        for key in keys:
            rx = _key_re(key)
            score += 3 * len(rx.findall(t)) + len(rx.findall(b))
        scores[name] = score

    cve_hits = len(CVE_RE.findall(body_text)) + len(CVE_RE.findall(title))
    if cve_hits:
        scores["Vulnerabilities"] = scores.get("Vulnerabilities", 0) + min(cve_hits, 6) * 2

    best = max(scores.items(), key=lambda kv: kv[1])
    return best[0] if best[1] > 0 else "Security Brief"


def render_body(blocks):
    """Turn parsed blocks into article HTML."""
    out = []
    pending_list = []
    first_para_done = False

    def flush_list():
        if pending_list:
            items = "".join(
                "<li><b>%s</b>%s</li>" % (enrich(lab), enrich(txt))
                for lab, txt in pending_list
            )
            out.append("<ul>%s</ul>" % items)
            pending_list.clear()

    n = len(blocks)
    for idx, block in enumerate(blocks):
        # section delimiter blocks:  ─────  /  HEADING  /  ─────
        inner = [ln for ln in block if not DELIM_RE.match(ln)]
        if len(inner) < len(block):
            flush_list()
            if inner:
                out.append("<h2>%s</h2>" % esc(" ".join(inner).strip(" :")))
            continue

        # "LABEL IN CAPS" on its own line, body on the lines below -> definition item
        if len(block) >= 2:
            head_line = block[0].strip()
            head_letters = [c for c in head_line if c.isalpha()]
            if (head_letters and len(head_line) <= 62
                    and sum(c.isupper() for c in head_letters) / len(head_letters) > 0.85
                    and not head_line.endswith((".", "?", "!"))):
                body_line = " ".join(block[1:]).strip()
                if len(body_line) > 12:
                    pending_list.append((head_line.strip(" :"), " " + body_line))
                    continue

        text = " ".join(block).strip()
        if not text:
            continue

        if HASHTAG_RE.match(text):
            continue
        if DELIM_RE.match(text) or set(text) <= set("-–—_= "):
            flush_list()
            out.append("<hr>")
            continue

        letters = [c for c in text if c.isalpha()]
        upper_ratio = (sum(c.isupper() for c in letters) / len(letters)) if letters else 0

        m = LEAD_RE.match(text)
        if m and upper_ratio > 0.45:
            pending_list.append((m.group(1).strip(), " " + m.group(2).strip()))
            continue

        flush_list()

        if upper_ratio > 0.82 and len(text) < 95 and len(block) == 1:
            out.append("<h2>%s</h2>" % esc(text.strip(" :")))
            continue

        # short standalone line acting as a sub-heading
        if (len(block) == 1 and len(text) < 78 and not text.endswith((".", "?", "!", ",")) and
                idx + 1 < n and text[0:1].isupper() and upper_ratio < 0.82):
            out.append("<h3>%s</h3>" % esc(text.strip(" :")))
            continue

        # closing question -> pull quote
        if text.endswith("?") and idx >= n - 3 and len(text) < 320:
            out.append("<blockquote>%s</blockquote>" % enrich(text))
            continue

        cls = ""
        if not first_para_done:
            cls = ' class="first-para"'
            first_para_done = True
        out.append("<p%s>%s</p>" % (cls, enrich(text)))

    flush_list()
    return "\n".join(out)


def parse_post(path, month_folder, folder_files):
    raw = read_text(path)
    blocks = to_blocks(raw)
    if not blocks:
        return None

    tags = []
    for block in blocks:
        line = " ".join(block)
        if HASHTAG_RE.match(line.strip()):
            tags = [t for t in re.findall(r"#([A-Za-z0-9_]+)", line)]
    tags = [t for t in tags if t.lower() not in ("sankarashield",)][:8]

    # a file may open on a rule, a separator or a dateline; the title is the first real line
    date_line = re.compile(
        r"^(mon|tues|wednes|thurs|fri|satur|sun)day[, ].{0,24}\d{4}\.?$|^\d{1,2}\s+\w+\s+\d{4}$", re.I)
    while blocks:
        head_text = " ".join(blocks[0]).strip()
        if (all(DELIM_RE.match(ln) or set(ln) <= set("-–—_=* ") for ln in blocks[0])
                or date_line.match(head_text)):
            blocks.pop(0)
            continue
        break
    if not blocks:
        return None

    first_text = strip_md(" ".join(blocks[0]).strip())
    first_text = re.sub(r"^[-–—*_=•·●\s]{2,}", "", first_text).strip()
    first_text = first_text.strip('"“”«» ').strip()
    title, leftover = split_title(first_text)

    body_blocks = blocks[1:]
    if leftover:
        body_blocks = [[leftover]] + body_blocks

    body_html = render_body(body_blocks)
    plain = re.sub(r"<[^>]+>", " ", body_html)
    plain = re.sub(r"\s+", " ", plain).strip()

    excerpt = plain[:180].rsplit(" ", 1)[0] + "\u2026" if len(plain) > 180 else plain
    words = len(plain.split()) + len(title.split())
    minutes = max(2, round(words / 215))

    published, approximate = resolve_date(path, month_folder)
    slug = slugify(title)
    topic = classify(title, plain)

    img_name = find_image(path, folder_files)
    return {
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "body_html": body_html,
        "tags": tags,
        "topic": topic,
        "date": published,
        "date_approx": approximate,
        "minutes": minutes,
        "words": words,
        "source": path,
        "image_src": os.path.join(os.path.dirname(path), img_name) if img_name else None,
    }


# --------------------------------------------------------------------------
# page shell
# --------------------------------------------------------------------------
def head(title, description, base, canonical, og_image=None, extra=""):
    og = og_image or (SITE + "/assets/img/og-default.jpg")
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{brand}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#6D28D9">
<link rel="icon" href="{base}favicon.ico" sizes="any">
<link rel="icon" type="image/png" href="{base}assets/img/icon-192.png" sizes="192x192">
<link rel="apple-touch-icon" href="{base}assets/img/icon-192.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:opsz,wght@6..72,380;6..72,420;6..72,600&display=swap">
<link rel="stylesheet" href="{base}assets/css/site.css">
{extra}</head>
<body>
<a class="skip" href="#main">Skip to content</a>
""".format(title=esc(title), desc=esc(description), canonical=canonical, brand=BRAND,
           og=og, base=base, extra=extra)


def header(base, active=""):
    def cls(name):
        return ' class="active"' if name == active else ""
    return """<header class="site-header">
  <div class="wrap">
    <nav class="nav site-nav" aria-label="Main">
      <a class="brand" href="{base}index.html" aria-label="{brand} home">
        <img class="brand-mark" src="{base}assets/img/brand-mark.png" alt="" width="126" height="132" decoding="async">
        <span class="brand-name">Sankara<span>Shield</span></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-label="Open menu">
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round">
          <path d="M2 5h14M2 9h14M2 13h14"/></svg>
      </button>
      <ul class="nav-links">
        <li><a href="{base}solutions.html"{s}>Solutions</a></li>
        <li><a href="{base}blog/index.html"{b}>Insights</a></li>
        <li><a href="{base}about.html"{a}>About</a></li>
        <li><a href="{base}contact.html"{c}>Contact</a></li>
      </ul>
      <div class="nav-cta">
        <a class="btn btn-primary btn-sm" href="{base}contact.html">Request a quote</a>
      </div>
    </nav>
  </div>
</header>
""".format(base=base, brand=BRAND, s=cls("solutions"), b=cls("blog"),
           a=cls("about"), c=cls("contact"))


def footer(base):
    return """<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div class="footer-col footer-about">
        <a class="brand" href="{base}index.html">
          <img class="brand-mark" src="{base}assets/img/brand-mark.png" alt="" width="126" height="132" decoding="async">
          <span class="brand-name">Sankara<span>Shield</span></span>
        </a>
        <p>Network and security infrastructure &mdash; specified, sourced, deployed and supported.
           Certified engineering, vendor-neutral advice.</p>
        <div class="social mt-16">
          <a href="https://www.linkedin.com/in/kodjo-apedoh-03030990/" aria-label="LinkedIn" rel="noopener" target="_blank">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M4.98 3.5A2.5 2.5 0 1 0 5 8.5a2.5 2.5 0 0 0-.02-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.83-2.05 3.77-2.05 4.03 0 4.78 2.65 4.78 6.1V21h-4v-5.35c0-1.28-.02-2.92-1.78-2.92-1.78 0-2.05 1.39-2.05 2.83V21H9z"/></svg>
          </a>
          <a href="https://github.com/ktf40858-stack" aria-label="GitHub" rel="noopener" target="_blank">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.16-1.11-1.47-1.11-1.47-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.9 1.53 2.34 1.09 2.91.83.09-.65.35-1.09.63-1.34-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.5 9.5 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.68-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>
          </a>
        </div>
      </div>
      <div class="footer-col">
        <h4>Company</h4>
        <ul>
          <li><a href="{base}about.html">About</a></li>
          <li><a href="{base}solutions.html">Solutions</a></li>
          <li><a href="{base}blog/index.html">Insights</a></li>
          <li><a href="{base}contact.html">Contact</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Capabilities</h4>
        <ul>
          <li><a href="{base}solutions.html#infrastructure">Network infrastructure</a></li>
          <li><a href="{base}solutions.html#security">Security &amp; firewalls</a></li>
          <li><a href="{base}solutions.html#deployment">Design &amp; deployment</a></li>
          <li><a href="{base}solutions.html#support">Support &amp; monitoring</a></li>
        </ul>
      </div>
      <div class="footer-col">
        <h4>Contact</h4>
        <ul>
          <li><a href="mailto:contact@sankarashield.com">contact@sankarashield.com</a></li>
          <li><a href="{base}contact.html">Request a quote</a></li>
          <li><a href="{base}about.html#careers">Careers &amp; recruiters</a></li>
        </ul>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; <span data-year>2026</span> {brand}. Arlington, Virginia, United States.</p>
      <p>Built as a static site. No trackers, no cookies.</p>
    </div>
    <p class="legal-note">Vendor and product names referenced on this site are trademarks of their respective
       owners. Their mention describes the technologies {brand} specifies, deploys and supports, and does
       not imply any partnership, endorsement or authorised-reseller status unless explicitly stated.</p>
  </div>
</footer>
<script src="{base}assets/js/site.js" defer></script>
</body>
</html>
""".format(base=base, brand=BRAND)


# --------------------------------------------------------------------------
# page rendering
# --------------------------------------------------------------------------
def render_article(post, prev_post, next_post):
    base = "../"
    canonical = "%s/blog/%s.html" % (SITE, post["slug"])
    og = "%s/assets/blog/%s" % (SITE, post["hero"]) if post.get("hero") else None
    iso = post["date"].isoformat()
    human = post["date"].strftime("%B %-d, %Y") if os.name != "nt" else post["date"].strftime("%B %#d, %Y")

    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"][:110],
        "datePublished": iso,
        "dateModified": iso,
        "author": {"@type": "Organization", "name": BRAND, "url": SITE},
        "publisher": {"@type": "Organization", "name": BRAND,
                      "logo": {"@type": "ImageObject", "url": SITE + "/assets/img/logo-256.png"}},
        "mainEntityOfPage": canonical,
        "description": post["excerpt"],
        "keywords": ", ".join(post["tags"]),
    }
    if post.get("hero"):
        ld["image"] = og

    extra = '<script type="application/ld+json">%s</script>\n' % json.dumps(ld, ensure_ascii=False)

    hero_html = ""
    if post.get("hero"):
        hero_html = (
            '<figure class="article-hero">'
            '<img src="../assets/blog/{h}" alt="" width="1200" height="675" loading="eager" decoding="async">'
            '</figure>'
        ).format(h=post["hero"])

    tags_html = ""
    if post["tags"]:
        tags_html = '<div class="article-tags">%s</div>' % "".join(
            '<span class="tag">#%s</span>' % esc(t) for t in post["tags"]
        )

    nav_parts = []
    if prev_post:
        nav_parts.append(
            '<a class="prev" href="{s}.html"><span class="dir">&larr; Previous</span>'
            '<span class="t">{t}</span></a>'.format(s=prev_post["slug"], t=esc(prev_post["title"][:78]))
        )
    if next_post:
        nav_parts.append(
            '<a class="next" href="{s}.html"><span class="dir">Next &rarr;</span>'
            '<span class="t">{t}</span></a>'.format(s=next_post["slug"], t=esc(next_post["title"][:78]))
        )
    nav_html = '<nav class="article-nav">%s</nav>' % "".join(nav_parts) if nav_parts else ""

    return (
        head(post["title"][:64] + " | " + BRAND + " Insights", post["excerpt"], base, canonical, og, extra)
        + header(base, "blog")
        + """<main id="main">
<article>
  <div class="wrap wrap-narrow article-head">
    <div class="breadcrumb">
      <a href="../index.html">Home</a><span>&rsaquo;</span>
      <a href="index.html">Insights</a><span>&rsaquo;</span>
      <span>{topic}</span>
    </div>
    <h1>{title}</h1>
    <div class="article-meta">
      <span class="post-topic">{topic}</span>
      <span class="sep" aria-hidden="true">&middot;</span>
      <time datetime="{iso}">{human}</time>
      <span class="sep" aria-hidden="true">&middot;</span>
      <span>{mins} min read</span>
    </div>
  </div>
  <div class="wrap wrap-narrow">
    {hero}
    <div class="prose">
{body}
    </div>
    {tags}
    {nav}
    <div class="mt-48"></div>
  </div>
</article>

<section class="section-tight">
  <div class="wrap">
    <div class="cta-panel">
      <span class="eyebrow eyebrow-plain" style="color:#DDD6FE">Turn the analysis into a plan</span>
      <h2 class="h2 mt-8">The gap between knowing the risk and closing it is a purchase order and a weekend.</h2>
      <p>We specify, source and deploy the equipment that closes it &mdash; firewalls, segmentation,
         secure remote access &mdash; and we support it afterwards.</p>
      <div class="btn-row mt-24">
        <a class="btn btn-primary" href="../contact.html">Talk to an engineer
          <svg class="arrow" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h9m0 0-3.4-3.4M12 8l-3.4 3.4"/></svg></a>
        <a class="btn btn-outline" href="index.html">More insights</a>
      </div>
    </div>
  </div>
</section>
</main>
""".format(topic=esc(post["topic"]), title=esc(post["title"]), iso=iso, human=human,
           mins=post["minutes"], hero=hero_html, body=post["body_html"], tags=tags_html, nav=nav_html)
        + footer(base)
    )


def post_card(post, base="", wide=False, eager=False):
    human = post["date"].strftime("%b %#d, %Y") if os.name == "nt" else post["date"].strftime("%b %-d, %Y")
    thumb = post.get("thumb")
    if thumb:
        img = ('<div class="post-thumb"><img src="{b}assets/blog/{t}" alt="" width="640" height="360" '
               'loading="{l}" decoding="async"></div>').format(b=base, t=thumb, l="eager" if eager else "lazy")
    else:
        img = ('<div class="post-thumb" style="background:'
               'linear-gradient(135deg,#EDE9FE,#F6F4FF 55%,#EEF0FF)"></div>')

    return """<a class="post-card{wide}" href="{b}blog/{slug}.html" data-topic="{topic}" data-search="{search}">
  {img}
  <div class="post-body">
    <div class="post-meta">
      <span class="post-topic">{topic}</span>
      <span class="sep" aria-hidden="true"></span>
      <time datetime="{iso}">{human}</time>
      <span class="sep" aria-hidden="true"></span>
      <span>{mins} min</span>
    </div>
    <h3>{title}</h3>
    <p>{excerpt}</p>
    <span class="more">Read the brief
      <svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h9m0 0-3.4-3.4M12 8l-3.4 3.4"/></svg>
    </span>
  </div>
</a>""".format(
        wide=" post-card-wide" if wide else "", b=base, slug=post["slug"],
        topic=esc(post["topic"]),
        search=esc((post["title"] + " " + " ".join(post["tags"]) + " " + post["excerpt"]).lower())
        .replace('"', ""),
        img=img, iso=post["date"].isoformat(), human=human, mins=post["minutes"],
        title=esc(post["title"]), excerpt=esc(post["excerpt"]))


def render_blog_index(posts):
    base = "../"
    canonical = SITE + "/blog/"
    topics = sorted({p["topic"] for p in posts})

    featured = posts[0]
    rest = posts[1:]

    chips = ['<button class="chip" data-filter="all" aria-pressed="true">All</button>']
    chips += ['<button class="chip" data-filter="%s" aria-pressed="false">%s</button>' % (esc(t), esc(t))
              for t in topics]

    cards = "\n".join(post_card(p, base="../", eager=(i < 3)) for i, p in enumerate(rest))

    extra = '<script type="application/ld+json">%s</script>\n' % json.dumps({
        "@context": "https://schema.org", "@type": "Blog",
        "name": BRAND + " Insights", "url": canonical,
        "description": "Vendor-neutral analysis of network and security incidents, vulnerabilities and architecture.",
        "publisher": {"@type": "Organization", "name": BRAND, "url": SITE},
    }, ensure_ascii=False)

    return (
        head("Insights | " + BRAND,
             "Field analysis on network security, vulnerabilities, cloud and zero trust — "
             "%d briefs written for the engineers who have to act on them." % len(posts),
             base, canonical, None, extra)
        + header(base, "blog")
        + """<main id="main">
<section class="hero">
  <div class="wrap hero-inner" style="padding-block:clamp(48px,6vw,78px) clamp(30px,4vw,44px)">
    <div class="section-head">
      <span class="eyebrow">Insights</span>
      <h1 class="display" style="font-size:clamp(2.1rem,1.3rem + 3vw,3.4rem)">
        What broke this week,<br><span class="grad-text">and what it means for your network.</span>
      </h1>
      <p class="lede">Every incident, CVE and outage below was read the same way: what actually happened,
         why the architecture allowed it, and the change that would have stopped it.
         {n} briefs, written for the people who have to act on them.</p>
    </div>
  </div>
</section>

<section class="section-tight">
  <div class="wrap">
    {featured}
  </div>
</section>

<section class="section-tight" style="padding-top:0">
  <div class="wrap">
    <div class="filter-bar">
      <div class="search-box">
        <svg width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><circle cx="7" cy="7" r="4.6"/><path d="m10.6 10.6 3 3"/></svg>
        <input type="search" id="blog-search" placeholder="Search {n} briefs&hellip;" aria-label="Search insights">
      </div>
      <div class="chips" id="blog-chips">{chips}</div>
      <span class="result-count" id="result-count"></span>
    </div>
    <div class="grid grid-3" id="post-grid">
{cards}
      <p class="empty-state" id="empty-state" hidden>No brief matches that search.</p>
    </div>
    <div class="load-more-wrap">
      <button class="btn btn-outline" id="load-more" type="button">Load more briefs</button>
    </div>
  </div>
</section>
</main>
<script>
(function(){{
  var PAGE = 12;
  var grid = document.getElementById('post-grid');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.post-card'));
  var search = document.getElementById('blog-search');
  var chips = document.getElementById('blog-chips');
  var count = document.getElementById('result-count');
  var empty = document.getElementById('empty-state');
  var more = document.getElementById('load-more');
  var topic = 'all', query = '', shown = PAGE;

  function matches(card){{
    if (topic !== 'all' && card.getAttribute('data-topic') !== topic) return false;
    if (!query) return true;
    return card.getAttribute('data-search').indexOf(query) !== -1;
  }}
  function apply(){{
    var visible = 0, total = 0;
    cards.forEach(function(card){{
      if (!matches(card)) {{ card.hidden = true; return; }}
      total++;
      if (visible < shown) {{ card.hidden = false; visible++; }}
      else card.hidden = true;
    }});
    empty.hidden = total !== 0;
    more.hidden = visible >= total;
    count.textContent = total + (total === 1 ? ' brief' : ' briefs');
  }}
  search.addEventListener('input', function(){{
    query = this.value.trim().toLowerCase(); shown = PAGE; apply();
  }});
  chips.addEventListener('click', function(e){{
    var btn = e.target.closest('.chip'); if (!btn) return;
    chips.querySelectorAll('.chip').forEach(function(c){{ c.setAttribute('aria-pressed','false'); }});
    btn.setAttribute('aria-pressed','true');
    topic = btn.getAttribute('data-filter'); shown = PAGE; apply();
  }});
  more.addEventListener('click', function(){{ shown += PAGE; apply(); }});
  apply();
}})();
</script>
""".format(n=len(posts), featured=post_card(featured, base="../", wide=True, eager=True),
           chips="".join(chips), cards=cards)
        + footer(base)
    )


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    if not os.path.isdir(SRC):
        sys.exit("Source archive not found: %s" % SRC)

    os.makedirs(BLOG_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    for f in os.listdir(BLOG_DIR):
        if f.endswith(".html"):
            os.remove(os.path.join(BLOG_DIR, f))

    posts, seen_slugs = [], {}
    for month in sorted(MONTHS, key=lambda m: MONTHS[m]):
        folder = os.path.join(SRC, month)
        if not os.path.isdir(folder):
            continue
        files = os.listdir(folder)
        for fname in sorted(files):
            if not fname.lower().endswith(".txt"):
                continue
            low = fname.lower()
            if "_prompt" in low or "image" in low:
                continue
            path = os.path.join(folder, fname)
            post = parse_post(path, month, files)
            if not post or len(post["body_html"]) < 200:
                print("   - skipped (too short): %s" % fname)
                continue
            slug = post["slug"]
            if slug in seen_slugs:
                seen_slugs[slug] += 1
                post["slug"] = "%s-%d" % (slug, seen_slugs[slug])
            else:
                seen_slugs[slug] = 1
            posts.append(post)

    posts.sort(key=lambda p: (p["date"], p["title"]), reverse=True)
    print("parsed %d posts" % len(posts))

    with_img = generated = 0
    for post in posts:
        post["hero"] = post["thumb"] = None
        if post["image_src"] and os.path.isfile(post["image_src"]):
            hero, thumb = process_image(post["image_src"], post["slug"])
            post["hero"], post["thumb"] = hero, thumb
            if hero:
                with_img += 1
        if not post["hero"]:                               # no artwork: draw a branded cover
            post["hero"], post["thumb"] = make_cover(post["slug"], post["topic"])
            generated += 1
    print("images: %d from the archive, %d covers generated (total %d)"
          % (with_img, generated, len(posts)))

    for i, post in enumerate(posts):
        prev_post = posts[i + 1] if i + 1 < len(posts) else None
        next_post = posts[i - 1] if i > 0 else None
        out = os.path.join(BLOG_DIR, post["slug"] + ".html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(render_article(post, prev_post, next_post))

    with open(os.path.join(BLOG_DIR, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(render_blog_index(posts))

    index = [{
        "slug": p["slug"], "title": p["title"], "topic": p["topic"],
        "date": p["date"].isoformat(), "minutes": p["minutes"],
        "excerpt": p["excerpt"], "tags": p["tags"], "image": p["thumb"],
        "date_approx": p["date_approx"],
    } for p in posts]
    with open(os.path.join(ROOT, "assets", "posts.json"), "w", encoding="utf-8") as fh:
        json.dump(index, fh, ensure_ascii=False, indent=1)

    # homepage feed fragment (3 latest)
    with open(os.path.join(ROOT, "tools", "_latest_posts.html"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(post_card(p, base="") for p in posts[:3]))

    # sitemap
    urls = ["", "solutions.html", "about.html", "contact.html", "blog/index.html"]
    today = date.today().isoformat()
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        lines.append("  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>" % (SITE, u, today))
    for p in posts:
        lines.append("  <url><loc>%s/blog/%s.html</loc><lastmod>%s</lastmod></url>"
                     % (SITE, p["slug"], p["date"].isoformat()))
    lines.append("</urlset>")
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    approx = sum(1 for p in posts if p["date_approx"])
    topics = {}
    for p in posts:
        topics[p["topic"]] = topics.get(p["topic"], 0) + 1
    print("\ntopics:")
    for t, c in sorted(topics.items(), key=lambda kv: -kv[1]):
        print("  %-24s %d" % (t, c))
    print("\ndates inferred from file mtime (approximate): %d" % approx)
    print("date range: %s -> %s" % (posts[-1]["date"], posts[0]["date"]))
    print("done.")


if __name__ == "__main__":
    main()
