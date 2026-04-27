"""Seed curated cybersecurity intelligence feed sources."""


from db.models.intel_feed_source import IntelFeedSource

_SOURCES = [
    # Threat / APT
    ("Krebs on Security", "https://krebsonsecurity.com/feed/", "rss", "news",
     "Brian Krebs — investigative cybersecurity journalism"),
    ("Schneier on Security", "https://www.schneier.com/feed/atom/", "atom", "news",
     "Bruce Schneier's security blog"),
    ("SANS Internet Storm Center", "https://isc.sans.edu/rssfeed_full.xml", "rss", "threat",
     "SANS ISC daily threat briefings and diaries"),
    ("CISA Alerts", "https://www.cisa.gov/uscert/ncas/alerts.xml", "rss", "threat",
     "US CISA official security alerts"),
    ("CISA Advisories", "https://www.cisa.gov/uscert/ncas/advisories.xml", "rss", "threat",
     "US CISA ICS and cybersecurity advisories"),
    ("BleepingComputer", "https://www.bleepingcomputer.com/feed/", "rss", "news",
     "Breaking cybersecurity and tech news"),
    ("The Hacker News", "https://feeds.feedburner.com/TheHackersNews", "rss", "news",
     "Cybersecurity news and analysis"),
    ("Dark Reading", "https://www.darkreading.com/rss.xml", "rss", "news",
     "Enterprise security news"),
    ("Wired Security", "https://www.wired.com/feed/category/security/latest/rss", "rss", "news",
     "Wired magazine security section"),
    ("Ars Technica Security", "https://feeds.arstechnica.com/arstechnica/security", "rss", "news",
     "Ars Technica security reporting"),
    # Vulnerability
    ("NVD CVE Recent", "https://nvd.nist.gov/feeds/xml/cve/misc/nvd-rss.xml", "rss", "vuln",
     "NIST National Vulnerability Database — recent CVEs"),
    ("Exploit-DB", "https://www.exploit-db.com/rss.xml", "rss", "vuln",
     "Exploit Database — public exploits and PoCs"),
    ("Vulhub PoC Feed", "https://github.com/vulhub/vulhub/commits/master.atom", "atom", "vuln",
     "Vulhub vulnerable environment commit feed"),
    # APT / Threat Intel
    ("Mandiant Threat Intelligence", "https://www.mandiant.com/resources/blog/rss.xml", "rss", "apt",
     "Mandiant (Google) threat research blog"),
    ("Recorded Future Blog", "https://www.recordedfuture.com/feed", "rss", "apt",
     "Recorded Future threat intelligence research"),
    ("SecureList (Kaspersky)", "https://securelist.com/feed/", "rss", "apt",
     "Kaspersky Lab global research and analysis team"),
    ("Trend Micro Research", "https://feeds.trendmicro.com/TrendMicroSimplySecurity", "rss", "apt",
     "Trend Micro threat research and analysis"),
    ("Palo Alto Unit 42", "https://unit42.paloaltonetworks.com/feed/", "rss", "apt",
     "Palo Alto Networks Unit 42 threat intelligence"),
    ("Cisco Talos", "https://blog.talosintelligence.com/feeds/posts/default", "atom", "apt",
     "Cisco Talos intelligence and research blog"),
    ("AlienVault OTX Pulses", "https://otx.alienvault.com/api/v1/pulses/subscribed?modified_since=2024-01-01", "json", "threat",
     "AlienVault OTX threat pulse feed (requires API key in URL)"),
]


async def seed_intel_feed_sources() -> int:
    """Seed intelligence feed sources. Returns count of created records."""
    created = 0
    for name, url, feed_type, category, description in _SOURCES:
        _, was_created = await IntelFeedSource.get_or_create(
            url=url,
            defaults={
                "name": name,
                "feed_type": feed_type,
                "category": category,
                "description": description,
                "is_active": True,
            },
        )
        if was_created:
            created += 1
    return created
