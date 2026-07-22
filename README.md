# WebCrawler

A recursive web crawler that discovers all links on a website and builds a site tree. Supports JavaScript-rendered pages.

## Usage

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

## Install

```bash
pip install -r requirements.txt
```

For JS-rendered pages:
```bash
pip install playwright
playwright install chromium
```

## JS Rendering

Regular websites work out of the box. For single-page apps (React, Vue, Angular) that load content via JavaScript, use the `--js` flag:

```bash
python webcrawler.py https://spa-website.com --js
```

This uses Playwright to render the page in a headless browser before extracting links.

## Output

The crawler prints a tree to the terminal and optionally saves full results as JSON:

```json
{
  "start_url": "https://example.com",
  "stats": {"pages_crawled": 149, "links_found": 788, "errors": 0},
  "pages": {
    "https://example.com": {
      "title": "Example",
      "depth": 0,
      "children": ["https://example.com/about", "https://example.com/contact"]
    }
  }
}
```

## License

MIT
