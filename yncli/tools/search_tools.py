import re
import urllib.parse
import urllib.request
import warnings
from typing import Optional

warnings.filterwarnings("ignore")


def web_search(query: str, max_results: int = 5) -> str:
    """
    Performs a real-time web search using lightweight HTTP endpoints.
    100% pure Python with ZERO heavy Rust/C compilation dependencies.
    """
    try:
        import requests
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        results = []

        # 1. Try DuckDuckGo HTML endpoint
        try:
            url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
            resp = requests.get(url, headers=headers, timeout=10)
            
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                
                result_divs = soup.find_all("div", class_=re.compile(r"result|results_links"))
                for r in result_divs:
                    title_tag = r.find("a", class_="result__a") or r.find("a")
                    snippet_tag = r.find("a", class_="result__snippet") or r.find("div", class_="result__snippet")
                    
                    if title_tag:
                        title = title_tag.get_text().strip()
                        raw_href = title_tag.get("href", "")
                        
                        if "uddg=" in raw_href:
                            parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                            link = parsed.get("uddg", [raw_href])[0]
                        else:
                            link = raw_href
                            
                        snippet = snippet_tag.get_text().strip() if snippet_tag else ""
                        if link and (link.startswith("http://") or link.startswith("https://")):
                            if title and not any(res["link"] == link for res in results):
                                results.append({"title": title, "link": link, "snippet": snippet})
                                if len(results) >= max_results:
                                    break
        except Exception:
            pass

        # 2. Fallback to DuckDuckGo Instant Answer API if needed
        if not results:
            try:
                api_url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1&skip_disambig=1"
                api_resp = requests.get(api_url, headers=headers, timeout=8)
                if api_resp.status_code == 200:
                    data = api_resp.json()
                    if data.get("AbstractText"):
                        results.append({
                            "title": data.get("Heading", query),
                            "link": data.get("AbstractURL", ""),
                            "snippet": data.get("AbstractText", "")
                        })
                    for topic in data.get("RelatedTopics", [])[:max_results]:
                        if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                            results.append({
                                "title": topic.get("Text", "")[:60],
                                "link": topic.get("FirstURL", ""),
                                "snippet": topic.get("Text", "")
                            })
            except Exception:
                pass

        if not results:
            return f"No search results found for: '{query}'"

        formatted = [f"Web Search Results for '{query}':", "=" * 50]
        for i, res in enumerate(results[:max_results], start=1):
            title = res.get("title", "No title")
            link = res.get("link", "")
            body = res.get("snippet", "")
            formatted.append(f"[{i}] {title}\nURL: {link}\nSnippet: {body}\n")

        return "\n".join(formatted)
    except Exception as e:
        return f"Error executing web search: {str(e)}"


def fetch_webpage(url: str, max_chars: int = 6000) -> str:
    """
    Fetches the content of a webpage and extracts clean, readable text/markdown.
    """
    try:
        import requests
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "svg", "noscript"]):
            tag.decompose()

        title = soup.title.string.strip() if soup.title else url
        text = soup.get_text(separator="\n")
        
        clean_lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(clean_lines)

        if len(clean_text) > max_chars:
            clean_text = clean_text[:max_chars] + f"\n... [Content truncated, total {len(text)} chars]"

        return f"Title: {title}\nURL: {url}\n\nContent:\n{clean_text}"
    except Exception as e:
        return f"Error fetching webpage from {url}: {str(e)}"
