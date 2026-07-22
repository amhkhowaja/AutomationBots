# AutomationBots

Two Python automation tools: a recursive web crawler and a WhatsApp message sender.

## Web Crawler

Recursively crawls a website, discovers all links, and builds a site tree. Supports JavaScript-rendered pages.

```bash
# Basic crawl (depth 2, same domain only)
python webcrawler.py https://example.com

# Deeper crawl
python webcrawler.py https://example.com --depth 4

# JS-rendered pages (SPAs, React sites, etc.)
python webcrawler.py https://example.com --js

# Follow external links too
python webcrawler.py https://example.com --all-domains

# Save results to JSON
python webcrawler.py https://example.com --output results.json

# Slower crawl (polite)
python webcrawler.py https://example.com --delay 2
```

### JS Rendering Setup

For sites that load content via JavaScript:

```bash
pip install playwright
playwright install chromium
python webcrawler.py https://spa-website.com --js
```

## WhatsApp Bot

Sends automated messages to contacts via WhatsApp Web.

```bash
# Edit contacts
nano contacts.json

# Send default message
python whatsapp_bot.py

# Custom message
python whatsapp_bot.py --message "Meeting at 3pm today"

# Custom contacts file
python whatsapp_bot.py --contacts my_list.json
```

Scan the QR code when prompted, then messages send automatically.

## Install

```bash
pip install -r requirements.txt
```

For JS-rendered crawling:
```bash
pip install playwright
playwright install chromium
```

## License

MIT
