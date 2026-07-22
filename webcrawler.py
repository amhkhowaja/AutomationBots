"""
Recursive Web Link Crawler

Crawls a website starting from a given URL, follows links recursively up to a
configurable depth, and builds a tree of all discovered pages. Supports
JavaScript-rendered pages via Playwright.

Usage:
    python webcrawler.py https://example.com
    python webcrawler.py https://example.com --depth 3 --js
    python webcrawler.py https://example.com --output links.json
"""

import argparse
import json
import sys
import time
from collections import deque
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def is_valid_url(url):
    """Check if a URL is valid and has http/https scheme."""
    try:
        result = urlparse(url)
        return all([result.scheme in ("http", "https"), result.netloc])
    except Exception:
        return False


def is_same_domain(url, base_domain):
    """Check if URL belongs to the same domain."""
    return urlparse(url).netloc == base_domain


def normalize_url(url):
    """Remove fragments and trailing slashes for deduplication."""
    parsed = urlparse(url)
    # Remove fragment, normalize path
    normalized = parsed._replace(fragment="", query=parsed.query)
    result = normalized.geturl().rstrip("/")
    return result


def extract_links_static(url, timeout=10):
    """Extract links from a page using requests + BeautifulSoup (no JS)."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; WebCrawler/1.0; +https://github.com/amhkhowaja/AutomationBots)"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else url

        links = set()
        for tag in soup.find_all("a", href=True):
            href = tag["href"]
            absolute_url = urljoin(url, href)
            if is_valid_url(absolute_url):
                links.add(normalize_url(absolute_url))

        return title, links

    except requests.RequestException as e:
        print(f"  ⚠ Failed to fetch {url}: {e}")
        return None, set()


def extract_links_js(url, timeout=15):
    """Extract links from a JS-rendered page using Playwright."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Error: Playwright not installed. Install with:")
        print("  pip install playwright && playwright install chromium")
        sys.exit(1)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=timeout * 1000, wait_until="networkidle")

            title = page.title() or url
            # Extract all links from the rendered DOM
            links = set()
            elements = page.query_selector_all("a[href]")
            for el in elements:
                href = el.get_attribute("href")
                if href:
                    absolute_url = urljoin(url, href)
                    if is_valid_url(absolute_url):
                        links.add(normalize_url(absolute_url))

            browser.close()
            return title, links

    except Exception as e:
        print(f"  ⚠ JS rendering failed for {url}: {e}")
        return None, set()


def crawl(start_url, max_depth=2, same_domain_only=True, use_js=False, delay=0.5):
    """
    Crawl a website recursively using BFS.

    Args:
        start_url: Starting URL to crawl
        max_depth: Maximum link depth to follow (0 = only start page)
        same_domain_only: Only follow links on the same domain
        use_js: Use Playwright for JS-rendered pages
        delay: Seconds to wait between requests (politeness)

    Returns:
        dict: Tree structure of discovered pages
    """
    start_url = normalize_url(start_url)
    base_domain = urlparse(start_url).netloc

    extract_fn = extract_links_js if use_js else extract_links_static

    # BFS queue: (url, depth, parent_url)
    queue = deque([(start_url, 0, None)])
    visited = set()
    tree = {}  # url -> {title, depth, children: [urls]}
    stats = {"pages_crawled": 0, "links_found": 0, "errors": 0}

    print(f"🕷  Crawling: {start_url}")
    print(f"   Depth: {max_depth} | Domain only: {same_domain_only} | JS: {use_js}")
    print()

    while queue:
        url, depth, parent = queue.popleft()

        if url in visited:
            continue
        if depth > max_depth:
            continue

        visited.add(url)
        stats["pages_crawled"] += 1

        indent = "  " * depth
        print(f"{indent}[{depth}] {url}")

        title, links = extract_fn(url)

        if title is None:
            stats["errors"] += 1
            tree[url] = {"title": "(failed)", "depth": depth, "children": []}
            continue

        # Filter links
        valid_links = []
        for link in links:
            if link in visited:
                continue
            if same_domain_only and not is_same_domain(link, base_domain):
                continue
            valid_links.append(link)

        tree[url] = {"title": title, "depth": depth, "children": valid_links}
        stats["links_found"] += len(valid_links)

        # Add children to queue
        for link in valid_links:
            if link not in visited:
                queue.append((link, depth + 1, url))

        # Polite delay
        if delay > 0:
            time.sleep(delay)

    return tree, stats


def print_tree(tree, start_url, indent=0):
    """Print the crawl tree in a readable format."""
    if start_url not in tree:
        return

    node = tree[start_url]
    prefix = "  " * indent
    title = node["title"][:60]
    print(f"{prefix}├── {title}")
    print(f"{prefix}│   {start_url}")

    for child_url in node.get("children", []):
        if child_url in tree:
            print_tree(tree, child_url, indent + 1)


def main():
    parser = argparse.ArgumentParser(
        description="Recursive web crawler — discovers all links on a website"
    )
    parser.add_argument("url", help="Starting URL to crawl")
    parser.add_argument(
        "--depth", "-d", type=int, default=2, help="Max crawl depth (default: 2)"
    )
    parser.add_argument(
        "--js", action="store_true", help="Render JavaScript pages (requires Playwright)"
    )
    parser.add_argument(
        "--all-domains", action="store_true", help="Follow links to external domains"
    )
    parser.add_argument(
        "--delay", type=float, default=0.5, help="Delay between requests in seconds (default: 0.5)"
    )
    parser.add_argument(
        "--output", "-o", help="Save results to JSON file"
    )

    args = parser.parse_args()

    if not is_valid_url(args.url):
        print(f"Error: Invalid URL: {args.url}")
        sys.exit(1)

    tree, stats = crawl(
        start_url=args.url,
        max_depth=args.depth,
        same_domain_only=not args.all_domains,
        use_js=args.js,
        delay=args.delay,
    )

    # Print summary
    print()
    print("=" * 60)
    print(f"Crawl complete:")
    print(f"  Pages crawled: {stats['pages_crawled']}")
    print(f"  Links found:   {stats['links_found']}")
    print(f"  Errors:        {stats['errors']}")
    print("=" * 60)

    # Print tree
    print()
    print("Site tree:")
    print_tree(tree, normalize_url(args.url))

    # Save to file
    if args.output:
        output = {
            "start_url": args.url,
            "stats": stats,
            "pages": tree,
        }
        with open(args.output, "w") as f:
            json.dump(output, f, indent=2)
        print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
