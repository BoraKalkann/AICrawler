from bs4 import BeautifulSoup
from urllib.parse import urljoin
from langgraph.graph import StateGraph, START, END
from pipeline.state import PipelineState 
from pipeline.fetcher import WebFetcher
from pipeline.cleaner import ContentCleaner

class WebCrawler:
    def __init__(self):
        self.fetcher = WebFetcher()
        self.cleaner = ContentCleaner()
        self.compiled_graph = self.setup_graph()
    
    def setup_graph(self):
        graph = StateGraph(state_schema=PipelineState)
        graph.add_node("fetch", self.fetcher.fetch_node)
        graph.add_node("clean", self.cleaner.clean_node)
        graph.add_edge(START, "fetch")
        graph.add_edge("fetch", "clean")
        graph.add_edge("clean", END)
        return graph.compile()

    def crawl(self, url, depth, max_depth, max_links, format_choice="JSON", visited=None, all_results=None):
        if visited is None:
            visited = set()
        if all_results is None:
            all_results = []

        if depth > max_depth or url in visited:
            return all_results
        
        visited.add(url)

        state = {
            "url": url,
            "raw_data": {},
            "cleaned_data": "",
            "depth": depth,
            "max_depth": max_depth,
            "max_links": max_links,
            "format_choice": format_choice
        }

        result = self.compiled_graph.invoke(state)
        all_results.append(result)
        
        soup = BeautifulSoup(result["raw_data"].get("html", ""), "html.parser")
        content_div = soup.find("div", id="mw-content-text")
        if content_div:
            result["cleaned_data"] = content_div.get_text(separator="\n", strip=True)
            links = [a["href"] for a in content_div.find_all("a", href=True)]
        else:
            links = [a["href"] for a in soup.find_all("a", href=True)]
        abs_links = [urljoin(url, link) for link in links if link.startswith(("/", "http"))]
        if depth < max_depth:
            for link in abs_links[:max_links]:
                if link not in visited:  
                    self.crawl(link, depth + 1, max_depth, max_links, format_choice, visited, all_results)
        return all_results