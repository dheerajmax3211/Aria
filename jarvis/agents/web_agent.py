import requests
from playwright.sync_api import sync_playwright
from loguru import logger


class WebAgent:
    name = "web_agent"
    description = "Web search, page scraping, deep research, fact-checking, and content summarization"

    def search(self, query: str, num_results: int = 5) -> str:
        try:
            from ddgs import DDGS
            results = DDGS().text(query, max_results=num_results)
            output = []
            for r in results:
                title = r.get("title", "")
                link = r.get("href", "")
                snippet = r.get("body", "")
                if title and link:
                    output.append(f"{title}: {link}\n  Snippet: {snippet}")
            return "\n\n".join(output) if output else "No results found"
        except Exception as e:
            return f"Web search failed: {e}"

    def scrape_page(self, url: str) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                text = page.inner_text("body")
                browser.close()
                return text[:3000]
        except Exception as e:
            return f"Page scrape failed: {e}"

    def summarize_url(self, url: str) -> str:
        text = self.scrape_page(url)
        return f"Content from {url}:\n{text[:1500]}..."

    def deep_research(self, query: str, num_pages: int = 5) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(f"https://www.google.com/search?q={query}", wait_until="networkidle")
                results = page.query_selector_all("div.g")
                links = []
                for r in results[:num_pages]:
                    title_el = r.query_selector("h3")
                    link_el = r.query_selector("a")
                    if title_el and link_el:
                        links.append({"title": title_el.inner_text(), "url": link_el.get_attribute("href")})

                research = [f"Research Report: {query}\n{'='*50}\n"]
                for link in links:
                    try:
                        page.goto(link["url"], wait_until="domcontentloaded", timeout=15000)
                        text = page.inner_text("body")
                        summary = text[:2000].replace("\n", " ")
                        research.append(f"\n## {link['title']}\nSource: {link['url']}\n{summary}\n")
                    except Exception as e:
                        logger.warning(f"Failed to scrape {link['url']}: {e}")

                browser.close()
                report = "\n".join(research)
                logger.info(f"Deep research completed: {len(links)} sources analyzed")
                return report
        except Exception as e:
            return f"Deep research failed: {e}"

    def fact_check(self, claim: str) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                page.goto(f"https://www.google.com/search?q={claim}+fact+check", wait_until="networkidle")
                results = page.query_selector_all("div.g")
                sources = []
                for r in results[:5]:
                    title_el = r.query_selector("h3")
                    link_el = r.query_selector("a")
                    if title_el and link_el:
                        sources.append({"title": title_el.inner_text(), "url": link_el.get_attribute("href")})

                report = [f"Fact Check: {claim}\n{'='*50}\n"]
                report.append(f"\nSources found: {len(sources)}\n")
                for i, src in enumerate(sources, 1):
                    report.append(f"{i}. {src['title']}")
                    report.append(f"   URL: {src['url']}")

                report.append(f"\nReview these sources to verify the claim. Cross-reference multiple sources for accuracy.")
                browser.close()
                logger.info(f"Fact check completed for: {claim[:50]}...")
                return "\n".join(report)
        except Exception as e:
            return f"Fact check failed: {e}"

    def competitor_research(self, company: str, industry: str = "") -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                queries = [
                    f"{company} competitors",
                    f"{company} vs alternatives {industry}",
                    f"{industry} market leaders comparison",
                ]

                report = [f"Competitor Research: {company}", f"Industry: {industry}" if industry else "", "="*50, ""]

                for query in queries:
                    page.goto(f"https://www.google.com/search?q={query}", wait_until="networkidle")
                    results = page.query_selector_all("div.g")
                    for r in results[:5]:
                        title_el = r.query_selector("h3")
                        link_el = r.query_selector("a")
                        if title_el and link_el:
                            report.append(f"- {title_el.inner_text()}")
                            report.append(f"  URL: {link_el.get_attribute('href')}")

                    page.goto(f"https://www.google.com/search?q={query}+site:crunchbase.com+OR+site:SimilarWeb.com", wait_until="networkidle", timeout=15000)
                    results = page.query_selector_all("div.g")
                    for r in results[:3]:
                        title_el = r.query_selector("h3")
                        link_el = r.query_selector("a")
                        if title_el and link_el:
                            report.append(f"- {title_el.inner_text()}")
                            report.append(f"  URL: {link_el.get_attribute('href')}")
                    report.append("")

                browser.close()
                logger.info(f"Competitor research completed for {company}")
                return "\n".join(report)
        except Exception as e:
            return f"Competitor research failed: {e}"

    def market_research(self, topic: str) -> str:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                queries = [
                    f"{topic} market size 2025 2026",
                    f"{topic} industry trends growth",
                    f"{topic} market analysis report",
                ]

                report = [f"Market Research: {topic}", "="*50, ""]

                for query in queries:
                    page.goto(f"https://www.google.com/search?q={query}", wait_until="networkidle")
                    results = page.query_selector_all("div.g")
                    for r in results[:5]:
                        title_el = r.query_selector("h3")
                        link_el = r.query_selector("a")
                        if title_el and link_el:
                            report.append(f"- {title_el.inner_text()}")
                            report.append(f"  URL: {link_el.get_attribute('href')}")
                    report.append("")

                browser.close()
                logger.info(f"Market research completed for {topic}")
                return "\n".join(report)
        except Exception as e:
            return f"Market research failed: {e}"
