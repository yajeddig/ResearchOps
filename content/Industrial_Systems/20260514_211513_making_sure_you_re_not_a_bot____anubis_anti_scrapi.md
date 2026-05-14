---
title: "Making sure you're not a bot! - Anubis Anti-Scraping System"
date: 2026-05-14
category: Industrial_Systems
confidence: 0.90
tags: ['anti-scraping', 'proof-of-work', 'web security', 'IT infrastructure', 'cybersecurity', 'bot protection', 'Hashcash', 'headless browser detection']
source: "https://hal.science/hal-04976856v2"
type: Article
source_type: Article
hash: 211513
---

## 🎯 Relevance
This content is useful for understanding IT security measures for protecting digital assets and data sources from automated abuse. In an industrial context, where data availability and integrity from various IT systems (including web-based interfaces) are critical for data science and operational intelligence, understanding such anti-scraping mechanisms is relevant for ensuring reliable data pipelines and system uptime. It highlights a practical application of cybersecurity principles to maintain system availability.

## 📖 Content
Loading...

You are seeing this because the administrator of this website has set up Anubis to protect the server against the scourge of AI companies aggressively scraping websites. This can and does cause downtime for the websites, which makes their resources inaccessible for everyone.

Anubis is a compromise. Anubis uses a Proof-of-Work scheme in the vein of Hashcash, a proposed proof-of-work scheme for reducing email spam. The idea is that at individual scales the additional load is ignorable, but at mass scraper levels it adds up and makes scraping much more expensive.

Ultimately, this is a placeholder solution so that more time can be spent on fingerprinting and identifying headless browsers (EG: via how they do font rendering) so that the challenge proof of work page doesn't need to be presented to users that are much more likely to be legitimate.

Please note that Anubis requires the use of modern JavaScript features that plugins like JShelter will disable. Please disable JShelter or other such plugins for this domain.

## 💡 Key Insights
- Anubis is a Proof-of-Work (PoW) system implemented to protect websites from aggressive scraping by AI companies.
- It operates similarly to Hashcash, imposing a small, ignorable load on individual users but making mass scraping economically unfeasible due to cumulative computational cost.
- Anubis is a temporary solution, with future development aimed at more sophisticated headless browser fingerprinting to reduce the need for PoW challenges for legitimate users.
- The system requires modern JavaScript features, potentially conflicting with privacy-enhancing browser plugins like JShelter.

## 📚 References
- hal.science, 'Making sure you're not a bot!', URL: https://hal.science/hal-04976856v2 *(source)*

## 🏷️ Classification
The content describes an IT security mechanism (Anubis) designed to protect web servers from aggressive scraping, which falls under the 'IT/OT, automatismes, edge, cybersécurité industrielle' aspects of the Industrial_Systems category, focusing on the protection of digital infrastructure.
