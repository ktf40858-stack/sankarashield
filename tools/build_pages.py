#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SankaraShield — static page generator.

Builds index / solutions / about / contact / 404 on the same shell as the blog,
so the header, the footer and the latest-posts feed can never drift apart.

    python tools/build_blog.py      # first: articles + posts.json
    python tools/build_pages.py     # then: the static pages
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_blog as B                                          # noqa: E402

ROOT = B.ROOT
SITE = B.SITE

# Web3Forms relays the contact form to the mailbox that owns this key.
# Get one free (no account) at https://web3forms.com — enter contact@sankarashield.com,
# the key arrives by email. Paste it here and rebuild. The key is safe to publish.
WEB3FORMS_KEY = "0100db13-7334-46f6-8faf-9a6615feab33"

ARROW = ('<svg class="arrow" width="15" height="15" viewBox="0 0 16 16" fill="none" stroke="currentColor" '
         'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h9m0 0-3.4-3.4M12 8l-3.4 3.4"/></svg>')

CHECK = ('<svg width="13" height="13" viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" '
         'stroke-linecap="round" stroke-linejoin="round"><path d="m3 8.4 3.2 3.2L13 4.8"/></svg>')


def icon(path_d, size=20):
    return ('<svg width="%d" height="%d" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg>' % (size, size, path_d))


ICONS = {
    "router": '<rect x="2" y="13" width="20" height="8" rx="2"/><path d="M6.5 17h.01M10 17h.01"/><path d="M12 9V3m0 0L9 6m3-3 3 3"/>',
    "shield": '<path d="M12 2.8 20 5.4v6.2c0 4.6-3.2 8-8 9.6-4.8-1.6-8-5-8-9.6V5.4z"/><path d="m9 12 2 2 4-4"/>',
    "blueprint": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/><path d="M13 13h4M13 17h4"/>',
    "pulse": '<path d="M2 12h4l2.5-7 4 14 2.5-7h5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18"/>',
    "lock": '<rect x="4" y="10" width="16" height="11" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/>',
    "mail": '<rect x="2.5" y="4.5" width="19" height="15" rx="2.5"/><path d="m3 7 9 6 9-6"/>',
    "briefcase": '<rect x="2.5" y="7.5" width="19" height="12" rx="2"/><path d="M9 7.5V6a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1.5"/><path d="M2.5 12.5h19"/>',
    "handshake": '<path d="M11 17.5 9 19.5a2 2 0 0 1-3-3l5.5-5.5 2.5 2.5"/><path d="m13 7 3-1.5 6 6-3 3-2.5-2.5"/><path d="M2 11.5 8 5.5 11 7"/>',
    "spark": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
}

HERO_SVG = """
<figure class="hero-visual" aria-labelledby="hero-visual-cap">
  <svg viewBox="0 0 520 428" role="img"
       aria-label="A segmented network: the internet reaches a next-generation firewall, which feeds a core switch splitting users, servers and guest devices into separate zones.">
    <defs>
      <linearGradient id="fwg" x1="0" y1="0" x2="1" y2="1">
        <stop offset="0" stop-color="#7C3AED"/><stop offset="1" stop-color="#5B21B6"/>
      </linearGradient>
      <linearGradient id="swg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#F6F4FF"/>
      </linearGradient>
      <filter id="sft" x="-30%" y="-30%" width="160%" height="160%">
        <feDropShadow dx="0" dy="6" stdDeviation="9" flood-color="#2A0E5F" flood-opacity="0.10"/>
      </filter>
    </defs>

    <!-- links -->
    <g stroke="#C4B5FD" stroke-width="1.6" fill="none" stroke-linecap="round">
      <path d="M260 62 V104" class="flow"/>
      <path d="M260 176 V214" class="flow"/>
      <path d="M260 286 V308 H86 V330" class="flow"/>
      <path d="M260 286 V330" class="flow"/>
      <path d="M260 286 V308 H434 V330" class="flow"/>
    </g>

    <!-- internet -->
    <g filter="url(#sft)">
      <rect x="196" y="22" width="128" height="40" rx="12" fill="#FFFFFF" stroke="#E9E4F4"/>
    </g>
    <text x="260" y="47" text-anchor="middle" class="n-label">Internet</text>

    <!-- firewall -->
    <g filter="url(#sft)">
      <rect x="164" y="104" width="192" height="72" rx="16" fill="url(#fwg)"/>
    </g>
    <text x="260" y="133" text-anchor="middle" class="n-title-w">Next-gen firewall</text>
    <text x="260" y="153" text-anchor="middle" class="n-sub-w">policy &middot; inspection &middot; ZTNA</text>

    <!-- core switch -->
    <g filter="url(#sft)">
      <rect x="176" y="214" width="168" height="72" rx="16" fill="url(#swg)" stroke="#DDD6FE"/>
    </g>
    <text x="260" y="243" text-anchor="middle" class="n-title">Core switch</text>
    <text x="260" y="263" text-anchor="middle" class="n-sub">802.1Q &middot; DHCP snooping</text>

    <!-- zones -->
    <g filter="url(#sft)">
      <rect x="16" y="330" width="140" height="72" rx="14" fill="#FFFFFF" stroke="#E9E4F4"/>
      <rect x="190" y="330" width="140" height="72" rx="14" fill="#FFFFFF" stroke="#E9E4F4"/>
      <rect x="364" y="330" width="140" height="72" rx="14" fill="#FFFFFF" stroke="#E9E4F4"/>
    </g>
    <text x="86"  y="358" text-anchor="middle" class="n-title">Staff</text>
    <text x="86"  y="378" text-anchor="middle" class="n-sub">VLAN 10</text>
    <text x="260" y="358" text-anchor="middle" class="n-title">Servers</text>
    <text x="260" y="378" text-anchor="middle" class="n-sub">VLAN 20</text>
    <text x="434" y="358" text-anchor="middle" class="n-title">Guest &amp; IoT</text>
    <text x="434" y="378" text-anchor="middle" class="n-sub">VLAN 30</text>

    <g class="n-dots">
      <circle cx="86" cy="392" r="2.5"/><circle cx="260" cy="392" r="2.5"/><circle cx="434" cy="392" r="2.5"/>
    </g>
  </svg>
  <figcaption id="hero-visual-cap">Segmented by default &mdash; every deployment ships this way, not flat.</figcaption>
</figure>
"""

HERO_STYLE = """<style>
.hero-visual{margin:0;position:relative}
.hero-visual svg{width:100%;height:auto;overflow:visible}
.hero-visual figcaption{
  margin-top:16px;text-align:center;font-size:.82rem;color:var(--ink-3);
}
.n-label{font:600 13.5px var(--sans);fill:var(--ink-2);letter-spacing:-.01em}
.n-title{font:600 14px var(--sans);fill:var(--ink);letter-spacing:-.015em}
.n-sub{font:500 11px var(--sans);fill:var(--ink-4);letter-spacing:.02em}
.n-title-w{font:600 14.5px var(--sans);fill:#fff;letter-spacing:-.015em}
.n-sub-w{font:500 11px var(--sans);fill:rgba(255,255,255,.78);letter-spacing:.02em}
.n-dots circle{fill:var(--v-300)}
.flow{stroke-dasharray:5 7;animation:dash 2.4s linear infinite}
@keyframes dash{to{stroke-dashoffset:-24}}
@media (prefers-reduced-motion:reduce){.flow{animation:none;stroke-dasharray:none}}
</style>
"""


# --------------------------------------------------------------------------
def latest_posts_html():
    path = os.path.join(ROOT, "tools", "_latest_posts.html")
    if os.path.isfile(path):
        return open(path, encoding="utf-8").read()
    return ""


def post_count():
    path = os.path.join(ROOT, "assets", "posts.json")
    if os.path.isfile(path):
        return len(json.load(open(path, encoding="utf-8")))
    return 0


def card(icon_key, title, text, items):
    lis = "".join("<li>%s</li>" % i for i in items)
    return """<article class="card card-hover reveal">
  <span class="card-icon">%s</span>
  <h3 class="h3">%s</h3>
  <p>%s</p>
  <ul class="card-list">%s</ul>
</article>""" % (icon(ICONS[icon_key]), title, text, lis)


def step(n, title, text):
    return """<article class="step reveal">
  <span class="step-n">%s</span>
  <h3>%s</h3>
  <p>%s</p>
</article>""" % (n, title, text)


CREDENTIALS = """<ul class="cred-list">
  <li class="cred">%s Cisco CCNA</li>
  <li class="cred">%s Fortinet NSE</li>
  <li class="cred">%s Palo Alto SASE</li>
  <li class="cred">%s Palo Alto Cloud Security</li>
  <li class="cred progress">CompTIA Security+ &mdash; in progress</li>
  <li class="cred progress">CEH &mdash; in progress</li>
</ul>""" % (CHECK, CHECK, CHECK, CHECK)


PURPLE_BAND = """<section class="section band-violet">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">Why purple</span>
      <h2 class="h2">The name is the method.</h2>
      <p class="lede">Red teams break things. Blue teams defend them. Purple is what happens when the same
         people do both &mdash; and it is the only way to know whether a control actually works.</p>
    </div>
    <div class="pt-equation mt-48">
      <div class="pt-chip red"><b>Red</b><span>how it gets broken</span></div>
      <span class="pt-op" aria-hidden="true">+</span>
      <div class="pt-chip blue"><b>Blue</b><span>how it gets defended</span></div>
      <span class="pt-op" aria-hidden="true">=</span>
      <div class="pt-chip purple"><b>Purple</b><span>proof that it holds</span></div>
    </div>
    <p class="lede center mt-48" style="max-width:720px;margin-inline:auto">
      In practice it means we do not hand over a firewall with the default policy and call it secure.
      We configure it, then we try to get past it, then we show you what the logs looked like when we did.
    </p>
  </div>
</section>
"""


def cta(title, text, primary=("contact.html", "Request a quote"), secondary=("solutions.html", "See what we deploy")):
    return """<section class="section">
  <div class="wrap">
    <div class="cta-panel reveal">
      <span class="eyebrow eyebrow-plain" style="color:#DDD6FE">Next step</span>
      <h2 class="h2 mt-8">%s</h2>
      <p>%s</p>
      <div class="btn-row mt-24">
        <a class="btn btn-primary" href="%s">%s %s</a>
        <a class="btn btn-outline" href="%s">%s</a>
      </div>
    </div>
  </div>
</section>
""" % (title, text, primary[0], primary[1], ARROW, secondary[0], secondary[1])


# --------------------------------------------------------------------------
def page_index():
    n = post_count()
    body = """<main id="main">

<section class="hero">
  <div class="wrap hero-inner">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="pill"><span class="dot dot-live"></span> Networking &amp; cybersecurity &mdash; supply, deploy, support</span>
        <h1 class="display">Security equipment is easy to buy.<br>
          <span class="grad-text">Hard to configure correctly.</span></h1>
        <p class="lede">SankaraShield specifies, sources and deploys the network and security
           infrastructure small and mid-sized organisations actually need &mdash; routers, switches,
           next-generation firewalls, secure remote access &mdash; and stays on to support it.
           Every design is signed off by a certified engineer, not pulled from a catalogue.</p>
        <div class="btn-row">
          <a class="btn btn-primary btn-lg" href="contact.html">Request a quote %s</a>
          <a class="btn btn-outline btn-lg" href="solutions.html">See what we deploy</a>
        </div>
        <ul class="hero-proof">
          <li>%s Cisco CCNA</li>
          <li>%s Fortinet NSE</li>
          <li>%s Palo Alto SASE &amp; Cloud Security</li>
          <li>%s Vendor-neutral</li>
        </ul>
      </div>
      <div class="reveal">%s</div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">What we do</span>
      <h2 class="h2">Four things, done properly.</h2>
      <p class="lede">One point of contact from the first site survey to the support call two years later.
         No hand-off between the people who sold it and the people who have to make it work.</p>
    </div>
    <div class="grid grid-4 mt-48">
      %s
      %s
      %s
      %s
    </div>
  </div>
</section>

%s

<section class="section band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">How we work</span>
      <h2 class="h2">A quote you can read.</h2>
      <p class="lede">Every proposal states what the equipment does, why that model and not the cheaper one,
         and what it costs to run &mdash; before you commit to anything.</p>
    </div>
    <div class="grid grid-4 mt-48">
      %s
      %s
      %s
      %s
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Technologies</span>
      <h2 class="h2">The platforms we specify and support.</h2>
      <p class="lede">We are not tied to one manufacturer, which means the recommendation can be the right
         box rather than the one we have to move. Certifications on the platforms below are current.</p>
    </div>
    <div class="vendor-wall mt-32">
      <div class="vendor">Cisco<small>ROUTING &middot; SWITCHING</small></div>
      <div class="vendor">Fortinet<small>FORTIGATE &middot; SSL VPN</small></div>
      <div class="vendor">Palo Alto Networks<small>NGFW &middot; PRISMA SASE</small></div>
      <div class="vendor">Juniper<small>ENTERPRISE LAN</small></div>
      <div class="vendor">Ubiquiti<small>WIRELESS &middot; SMB</small></div>
      <div class="vendor">MikroTik<small>EDGE &middot; ROUTING</small></div>
      <div class="vendor">Wazuh<small>DETECTION &middot; SIEM</small></div>
      <div class="vendor">Microsoft Entra<small>IDENTITY &middot; ZERO TRUST</small></div>
    </div>
    <p class="legal-note">Vendor and product names are trademarks of their respective owners. Listing them
       describes the technologies we specify, deploy and support &mdash; it does not imply a partnership,
       an endorsement or authorised-reseller status.</p>
  </div>
</section>

<section class="section band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Insights</span>
      <h2 class="h2">We read the incidents so you do not have to.</h2>
      <p class="lede">%d field briefs on the breaches, CVEs and outages that change how a network should be
         built &mdash; what happened, why the architecture allowed it, and the change that stops it.</p>
    </div>
    <div class="grid grid-3 mt-48">
      %s
    </div>
    <div class="btn-row mt-32">
      <a class="btn btn-outline" href="blog/index.html">Read all %d briefs %s</a>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="founder reveal">
      <div class="founder-mark"><img src="assets/img/icon-192.png" alt="" width="62" height="62"></div>
      <div>
        <span class="eyebrow">Who you deal with</span>
        <h2 class="h3 mt-8">Kodjo Apedoh &mdash; founder, and the engineer on your project.</h2>
        <p class="lede mt-16" style="font-size:1.02rem">
          Network and cloud security engineer based in Arlington, Virginia. Associate degree in Computer
          Systems Networking (NWACC, 3.8 GPA, Phi Theta Kappa, Dean&rsquo;s List), a BBA, and two years
          and seven months running IT for a healthcare practice under HIPAA constraints. Certified on the
          platforms he deploys &mdash; and he publishes his lab work, so you can check it.
        </p>
        %s
        <div class="avail">
          <p><strong>Also open to remote roles.</strong> Alongside SankaraShield, Kodjo is available for
             remote Network &amp; Cloud Security Engineer positions &mdash; US citizen, Eastern time zone.</p>
          <a class="btn btn-outline btn-sm" href="about.html#careers">For recruiters %s</a>
        </div>
      </div>
    </div>
  </div>
</section>

%s
</main>
""" % (ARROW, CHECK, CHECK, CHECK, CHECK, HERO_SVG,
       card("router", "Infrastructure supply",
            "Routers, switches, access points and optics &mdash; specified against the load you actually have.",
            ["Genuine equipment, full manufacturer warranty",
             "Sizing based on a site survey, not a guess",
             "Lead times and end-of-life dates stated up front"]),
       card("shield", "Security &amp; firewalls",
            "Next-generation firewalls, segmentation and secure remote access, configured to least privilege.",
            ["NGFW policy built on applications, not ports",
             "Site-to-site and per-role remote access",
             "Guest and IoT isolated from day one"]),
       card("blueprint", "Design &amp; deployment",
            "Addressing plan, VLANs, routing and failover &mdash; documented before a single cable is run.",
            ["Written low-level design you keep",
             "Staged cutover with a rollback plan",
             "Configuration handed over, not held hostage"]),
       card("pulse", "Support &amp; monitoring",
            "The part most resellers skip: someone who answers when the link drops at 07:00.",
            ["Defined response windows, in writing",
             "Firmware and CVE tracking on your fleet",
             "Quarterly configuration review"]),
       PURPLE_BAND,
       step("01", "Assess", "A site survey and a look at what you already run. Free, and yours to keep even if you buy nothing."),
       step("02", "Specify", "A written design and a line-by-line quote: what each item does, and why that model."),
       step("03", "Deploy", "Staged installation outside working hours where possible, with a tested rollback."),
       step("04", "Support", "Documentation handed over, then monitoring, firmware tracking and a quarterly review."),
       n, latest_posts_html(), n, ARROW, CREDENTIALS, ARROW,
       cta("Tell us what the network has to do. We will tell you what it takes.",
           "A first conversation costs nothing and usually saves a purchase order. "
           "Send the requirement, the site count and the deadline &mdash; you get a written answer, not a sales call."))

    return (B.head(
        "SankaraShield — Network & Cybersecurity Infrastructure",
        "SankaraShield specifies, supplies, deploys and supports network and security infrastructure "
        "for small and mid-sized organisations — firewalls, switching, secure remote access — "
        "engineered by certified staff.",
        "", SITE + "/", None,
        HERO_STYLE + '<script type="application/ld+json">%s</script>\n' % json.dumps({
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": "SankaraShield",
            "url": SITE,
            "logo": SITE + "/assets/img/logo-256.png",
            "description": "Network and cybersecurity infrastructure: supply, design, deployment and support.",
            "address": {"@type": "PostalAddress", "addressLocality": "Arlington",
                        "addressRegion": "VA", "addressCountry": "US"},
            "founder": {"@type": "Person", "name": "Kodjo Apedoh"},
            "sameAs": ["https://www.linkedin.com/in/kodjo-apedoh-03030990/",
                       "https://github.com/ktf40858-stack"],
        }, ensure_ascii=False))
        + B.header("", "home") + body + B.footer(""))


# --------------------------------------------------------------------------
def solution_block(anchor, eyebrow, title, lede, columns, note=None):
    cols = "".join(
        """<div class="card">
             <h3 class="h4">%s</h3>
             <ul class="card-list">%s</ul>
           </div>""" % (name, "".join("<li>%s</li>" % i for i in items))
        for name, items in columns)
    note_html = '<p class="legal-note">%s</p>' % note if note else ""
    return """<section class="section" id="%s">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">%s</span>
      <h2 class="h2">%s</h2>
      <p class="lede">%s</p>
    </div>
    <div class="grid grid-3 mt-48">%s</div>
    %s
  </div>
</section>""" % (anchor, eyebrow, title, lede, cols, note_html)


def page_solutions():
    body = """<main id="main">
<section class="hero">
  <div class="wrap hero-inner" style="padding-block:clamp(48px,6vw,84px) clamp(34px,4vw,52px)">
    <div class="section-head">
      <span class="eyebrow">Solutions</span>
      <h1 class="display" style="font-size:clamp(2.1rem,1.3rem + 3vw,3.5rem)">
        Everything between the internet<br><span class="grad-text">and the last access point.</span></h1>
      <p class="lede">Four capability areas. Buy one of them or all four &mdash; but they are designed to fit
         together, because a firewall that nobody segments behind is an expensive router.</p>
      <div class="btn-row">
        <a class="btn btn-primary" href="contact.html">Request a quote %s</a>
        <a class="btn btn-outline" href="#deployment">How a project runs</a>
      </div>
    </div>
  </div>
</section>

%s
%s
%s
%s

<section class="section band">
  <div class="wrap">
    <div class="section-head">
      <span class="eyebrow">Straight answers</span>
      <h2 class="h2">What we will tell you before you ask.</h2>
    </div>
    <div class="grid grid-2 mt-48">
      <article class="card">
        <h3 class="h4">When the cheaper box is the right box</h3>
        <p>Not every site needs a next-generation firewall with a full subscription bundle. If a smaller
           model and tighter segmentation gets you there, the quote will say so &mdash; and the saving is yours.</p>
      </article>
      <article class="card">
        <h3 class="h4">What the renewal really costs</h3>
        <p>Security appliances carry subscription costs that often exceed the hardware over three years.
           Those figures appear in the first quote, not in year two.</p>
      </article>
      <article class="card">
        <h3 class="h4">Where the equipment comes from</h3>
        <p>Genuine, manufacturer-warranted equipment through legitimate distribution. Grey-market kit is
           cheaper and is not supportable; we will not quote it.</p>
      </article>
      <article class="card">
        <h3 class="h4">Who owns the configuration</h3>
        <p>You do. Credentials, configuration files and documentation are handed over at the end of every
           project. Nothing about the design requires you to keep calling us.</p>
      </article>
    </div>
  </div>
</section>

%s
</main>
""" % (ARROW,
       solution_block(
           "infrastructure", "01 &mdash; Infrastructure", "Network infrastructure supply",
           "Sizing first, catalogue second. We survey the site, count what actually connects, "
           "measure what the uplink really carries, and then specify.",
           [("Routing &amp; switching", ["Branch and campus routers", "Layer 2 / Layer 3 switching",
                                         "PoE budgeting for phones, cameras and APs", "Optics, stacking and uplinks"]),
            ("Wireless", ["Wi-Fi 6 / 6E design and survey", "Controller or cloud-managed",
                          "Separate SSIDs per trust level", "Coverage validated after install"]),
            ("Resilience", ["Dual WAN with tested failover", "UPS sizing for the rack",
                            "Spare-unit strategy", "End-of-life tracking per model"])],
           note="Equipment is sourced through legitimate distribution channels with full manufacturer warranty."),
       solution_block(
           "security", "02 &mdash; Security", "Firewalls, segmentation and secure access",
           "The part that decides whether an incident stays in one VLAN or reaches everything. "
           "Configured to least privilege on day one, because nobody comes back to tighten it later.",
           [("Perimeter", ["Next-generation firewall deployment", "Application-aware policy, not port rules",
                           "Inbound publishing done safely", "Logging that survives an audit"]),
            ("Segmentation", ["VLAN design per trust level", "East-West control between segments",
                              "Guest and IoT fully isolated", "Layer 2 hardening: DAI, DHCP snooping, port security"]),
            ("Remote access", ["SSL VPN and IPsec site-to-site", "Access tied to role, not to a flat tunnel",
                               "MFA enforced on every entry point", "ZTNA / SASE migration path"])]),
       solution_block(
           "deployment", "03 &mdash; Delivery", "Design and deployment",
           "The design exists on paper before anything is racked, and you keep that paper. "
           "A network nobody documented is a network nobody can fix.",
           [("Before", ["Site survey and traffic baseline", "Addressing and VLAN plan",
                        "Low-level design document", "Cutover runbook with rollback"]),
            ("During", ["Staged migration, out of hours where possible", "Configuration under version control",
                        "Validation tests per device", "Nothing goes live untested"]),
            ("After", ["Documentation and diagrams handed over", "Credentials transferred to you",
                       "Handover session with your team", "30-day post-cutover check"])]),
       solution_block(
           "support", "04 &mdash; Support", "Support and monitoring",
           "Most of the value of an install shows up in month seven, when something breaks and "
           "somebody has to know how it was built.",
           [("Monitoring", ["Link, device and tunnel availability", "Alerting to a human, not a dashboard",
                            "Capacity trends reviewed quarterly", "Log retention advice"]),
            ("Maintenance", ["Firmware and CVE tracking for your fleet", "Scheduled patch windows",
                             "Configuration backup and restore tests", "Change log kept per site"]),
            ("Response", ["Defined response windows, in writing", "Remote first, on-site when needed",
                          "Escalation path to the manufacturer", "Quarterly configuration review"])]),
       cta("Send us the requirement. We will send back a design and a number.",
           "Site count, user count, what has to keep running and by when. "
           "That is enough to start &mdash; the survey fills in the rest.",
           ("contact.html", "Start a project"), ("blog/index.html", "Read the insights")))

    return (B.head("Solutions | SankaraShield",
                   "Network infrastructure supply, firewalls and segmentation, design and deployment, "
                   "support and monitoring — the four capability areas SankaraShield delivers.",
                   "", SITE + "/solutions.html")
            + B.header("", "solutions") + body + B.footer(""))


# --------------------------------------------------------------------------
def page_about():
    body = """<main id="main">
<section class="hero">
  <div class="wrap hero-inner" style="padding-block:clamp(48px,6vw,84px) clamp(34px,4vw,52px)">
    <div class="section-head">
      <span class="eyebrow">About</span>
      <h1 class="display" style="font-size:clamp(2.1rem,1.3rem + 3vw,3.5rem)">
        A small firm that would rather<br><span class="grad-text">be right than be big.</span></h1>
      <p class="lede">SankaraShield is a network and cybersecurity practice based in Arlington, Virginia,
         serving small and mid-sized organisations in the United States and West Africa. It exists because
         too much infrastructure is sold by people who will never have to defend it.</p>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="grid grid-2" style="gap:clamp(28px,4vw,56px);align-items:start">
      <div class="stack gap-16">
        <span class="eyebrow">What we believe</span>
        <h2 class="h2">Three positions we do not move on.</h2>
      </div>
      <div class="stack gap-24">
        <article class="card">
          <h3 class="h4">The design comes before the invoice</h3>
          <p>A quote without a design is a guess with a price on it. We survey first, write the design,
             and only then price the equipment that design requires.</p>
        </article>
        <article class="card">
          <h3 class="h4">Vendor-neutral, and it costs us money</h3>
          <p>No manufacturer sets our recommendations. Sometimes that means quoting a smaller box, a
             competitor&rsquo;s platform, or telling a client their existing kit is fine for another two years.</p>
        </article>
        <article class="card">
          <h3 class="h4">We do not claim what we cannot show</h3>
          <p>No invented client counts, no borrowed logos, no partner badges we were never granted.
             The certifications listed are held. The lab work is published and can be read line by line.</p>
        </article>
      </div>
    </div>
  </div>
</section>

%s

<section class="section band">
  <div class="wrap">
    <div class="founder">
      <div class="founder-mark"><img src="assets/img/icon-192.png" alt="" width="62" height="62"></div>
      <div>
        <span class="eyebrow">Founder</span>
        <h2 class="h2 mt-8" style="font-size:clamp(1.5rem,1.1rem + 1.6vw,2.1rem)">Kodjo Apedoh</h2>
        <p class="lede mt-16">Network and cloud security engineer, based in Arlington, Virginia.
           US citizen. Works in English and French.</p>
        <div class="grid grid-2 mt-32" style="gap:22px">
          <article class="card">
            <h3 class="h4">Background</h3>
            <ul class="card-list">
              <li>Associate of Applied Science, Computer Systems Networking &mdash; NorthWest Arkansas
                  Community College, 3.8 GPA, Phi Theta Kappa, Dean&rsquo;s List</li>
              <li>Bachelor of Business Administration &mdash; ESGIS</li>
              <li>IT support for a healthcare practice, 2 years 7 months, under HIPAA constraints</li>
              <li>Founder of SankaraShield, network and security infrastructure</li>
            </ul>
          </article>
          <article class="card">
            <h3 class="h4">Focus</h3>
            <ul class="card-list">
              <li>Firewall policy and network segmentation</li>
              <li>Secure remote access &mdash; IPsec, SSL VPN, ZTNA and SASE</li>
              <li>Routing and switching for multi-site networks</li>
              <li>Detection engineering and configuration compliance</li>
            </ul>
          </article>
        </div>
        <h3 class="h4 mt-32">Certifications</h3>
        %s
        <p class="small muted mt-16">Lab work, configurations and detection rules are published at
           <a href="https://github.com/ktf40858-stack" rel="noopener" target="_blank"
              style="color:var(--v-700);font-weight:560">github.com/ktf40858-stack</a>.</p>
      </div>
    </div>
  </div>
</section>

<section class="section" id="careers">
  <div class="wrap">
    <div class="grid grid-2" style="gap:clamp(28px,4vw,56px);align-items:start">
      <div class="stack gap-16">
        <span class="eyebrow">Careers &amp; recruiters</span>
        <h2 class="h2">Open to remote engineering roles.</h2>
        <p class="lede">SankaraShield is a working practice, not a closed door. Its founder is actively
           available for a remote Network &amp; Cloud Security Engineer position, and is happy to say so
           plainly rather than have a recruiter guess.</p>
      </div>
      <div class="card" style="gap:16px">
        <h3 class="h4">The short version</h3>
        <ul class="card-list">
          <li><strong>Looking for:</strong> Network &amp; Cloud Security Engineer, SASE / Zero Trust focus</li>
          <li><strong>Arrangement:</strong> fully remote, or hybrid in the Washington DC / Northern Virginia area</li>
          <li><strong>Status:</strong> US citizen, Arlington VA, Eastern time zone, no sponsorship required</li>
          <li><strong>Certified on:</strong> Cisco, Fortinet and Palo Alto platforms &mdash; Security+ and CEH in progress</li>
          <li><strong>Evidence:</strong> published labs, detection rules and configuration-compliance tooling</li>
        </ul>
        <div class="btn-row mt-8">
          <a class="btn btn-primary btn-sm" href="https://www.linkedin.com/in/kodjo-apedoh-03030990/"
             rel="noopener" target="_blank">LinkedIn profile %s</a>
          <a class="btn btn-outline btn-sm" href="contact.html">Get in touch</a>
        </div>
      </div>
    </div>
  </div>
</section>

%s
</main>
""" % (PURPLE_BAND, CREDENTIALS, ARROW,
       cta("Two ways to start a conversation.",
           "A network that needs building, or a role that needs filling. Both reach the same inbox.",
           ("contact.html", "Contact"), ("solutions.html", "See the solutions")))

    return (B.head("About | SankaraShield",
                   "SankaraShield is a network and cybersecurity practice in Arlington, Virginia — "
                   "vendor-neutral infrastructure design, deployment and support, founded by Kodjo Apedoh.",
                   "", SITE + "/about.html")
            + B.header("", "about") + body + B.footer(""))


# --------------------------------------------------------------------------
def page_contact():
    body = """<main id="main">
<section class="hero">
  <div class="wrap hero-inner" style="padding-block:clamp(48px,6vw,80px) clamp(28px,3vw,40px)">
    <div class="section-head">
      <span class="eyebrow">Contact</span>
      <h1 class="display" style="font-size:clamp(2.1rem,1.3rem + 3vw,3.4rem)">
        Tell us what has to work.<br><span class="grad-text">We answer in writing.</span></h1>
      <p class="lede">No call centre, no sales sequence. The form below goes straight to the engineer who
         would run your project, and is normally answered within one business day.</p>
    </div>
  </div>
</section>

<section class="section" style="padding-top:clamp(30px,4vw,50px)">
  <div class="wrap">
    <div class="grid" style="grid-template-columns:minmax(0,1.55fr) minmax(0,1fr);gap:clamp(24px,3vw,40px);align-items:start">

      <div class="form-panel">
        <span class="eyebrow">Send a message</span>
        <h2 class="h3 mt-8">A few details get you a real answer instead of a callback.</h2>

        <form id="contact-form" novalidate>
          <input type="hidden" name="access_key" value="__KEY__">
          <input type="hidden" name="subject" value="New enquiry from sankarashield.com">
          <input type="hidden" name="from_name" value="SankaraShield website">
          <div class="honey" aria-hidden="true">
            <label for="botcheck">Leave this field empty</label>
            <input type="text" id="botcheck" name="botcheck" tabindex="-1" autocomplete="off">
          </div>

          <div class="form-grid">
            <div class="field">
              <label for="name">Full name</label>
              <input type="text" id="name" name="name" autocomplete="name" required placeholder="Jane Doe">
            </div>
            <div class="field">
              <label for="email">Work email</label>
              <input type="email" id="email" name="email" autocomplete="email" required placeholder="jane@company.com">
            </div>
            <div class="field">
              <label for="company">Company <span class="opt">&mdash; optional</span></label>
              <input type="text" id="company" name="company" autocomplete="organization" placeholder="Company or organisation">
            </div>
            <div class="field">
              <label for="phone">Phone <span class="opt">&mdash; optional</span></label>
              <input type="tel" id="phone" name="phone" autocomplete="tel" placeholder="+1 555 000 0000">
            </div>
            <div class="field">
              <label for="topic">What do you need?</label>
              <select id="topic" name="topic">
                <option>Quote for equipment</option>
                <option>New site or network build</option>
                <option>Firewall or security review</option>
                <option>Support and monitoring contract</option>
                <option>Vendor or distribution enquiry</option>
                <option>Recruiter &mdash; remote engineering role</option>
                <option>Something else</option>
              </select>
            </div>
            <div class="field">
              <label for="sites">Number of sites <span class="opt">&mdash; optional</span></label>
              <input type="text" id="sites" name="sites" placeholder="1, 3, 12&hellip;">
            </div>
            <div class="field full">
              <label for="message">What are you trying to do?</label>
              <textarea id="message" name="message" required
                placeholder="Useful in a first message: how many users, what has to keep running, what you have today, and your deadline."></textarea>
              <span class="hint">The more concrete this is, the more concrete the answer. Attachments can follow by email once we reply.</span>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary btn-lg" type="submit">Send message</button>
            <p class="form-note">Goes to one inbox. No newsletter, no CRM, no third-party tracking.</p>
          </div>

          <div class="form-status" id="form-status"></div>
        </form>
      </div>

      <div class="stack gap-24">
        <article class="card">
          <span class="card-icon">%s</span>
          <h2 class="h4">Prefer plain email?</h2>
          <p class="small muted">Write to us directly &mdash; the form simply saves you opening a mail client.</p>
          <p><a href="mailto:contact@sankarashield.com">contact@sankarashield.com</a></p>
        </article>

        <article class="card">
          <span class="card-icon">%s</span>
          <h2 class="h4">Recruiters</h2>
          <p class="small muted">Remote Network &amp; Cloud Security Engineer roles. US citizen, Arlington VA,
             Eastern time zone, no sponsorship required.</p>
          <p class="small muted">Background and certifications are on the
             <a href="about.html#careers" style="color:var(--v-700);font-weight:560">careers section</a>.</p>
          <p><a href="https://www.linkedin.com/in/kodjo-apedoh-03030990/" rel="noopener" target="_blank">LinkedIn &mdash; Kodjo Apedoh</a></p>
        </article>

        <article class="card">
          <span class="card-icon">%s</span>
          <h2 class="h4">Where we are</h2>
          <p class="small muted">Arlington, Virginia, United States. Serving the Washington DC metropolitan
             area, remote engagements across the US, and projects in West Africa.</p>
          <h3 class="h4 mt-16">Hours</h3>
          <p class="small muted">Monday to Friday, 09:00&ndash;18:00 Eastern. Support windows for contracted
             clients are set in their agreement, including out-of-hours cover.</p>
        </article>
      </div>

    </div>
  </div>
</section>
</main>
""" % (icon(ICONS["mail"]), icon(ICONS["spark"]), icon(ICONS["globe"]))

    body = body.replace("__KEY__", WEB3FORMS_KEY)

    return (B.head("Contact | SankaraShield",
                   "Contact SankaraShield — quotes and projects, vendor enquiries, and remote engineering "
                   "roles. Arlington, Virginia.",
                   "", SITE + "/contact.html")
            + B.header("", "contact") + body + B.footer(""))


# --------------------------------------------------------------------------
def page_404():
    body = """<main id="main">
<section class="section" style="padding-block:clamp(80px,12vw,150px)">
  <div class="wrap">
    <div class="section-head center">
      <span class="eyebrow">Error 404</span>
      <h1 class="display" style="font-size:clamp(2.4rem,1.6rem + 3vw,3.6rem)">
        This route does not <span class="grad-text">resolve.</span></h1>
      <p class="lede">The page you asked for is not here. It may have moved, or the link may be old.</p>
      <div class="btn-row mt-16">
        <a class="btn btn-primary" href="/index.html">Back to the homepage %s</a>
        <a class="btn btn-outline" href="/blog/index.html">Browse the insights</a>
      </div>
    </div>
  </div>
</section>
</main>
""" % ARROW
    return (B.head("Page not found | SankaraShield", "This page does not exist.",
                   "/", SITE + "/404.html")
            + B.header("/", "") + body + B.footer("/"))


# --------------------------------------------------------------------------
def main():
    pages = {
        "index.html": page_index(),
        "solutions.html": page_solutions(),
        "about.html": page_about(),
        "contact.html": page_contact(),
        "404.html": page_404(),
    }
    for name, content in pages.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8") as fh:
            fh.write(content)
        print("  %-16s %6.1f KB" % (name, len(content.encode("utf-8")) / 1024))
    print("pages written.")


if __name__ == "__main__":
    main()
