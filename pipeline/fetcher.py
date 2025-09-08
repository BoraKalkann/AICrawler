import requests
from bs4 import BeautifulSoup
from .state import PipelineState

class WebFetcher:
    def fetch_node(self, state: PipelineState):
        url = state["url"]
        try:
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            content = response.content if response.ok else ""
        except:
            content = ""

        soup = BeautifulSoup(content, "html.parser")
        title = soup.title.string.strip() if soup.title and soup.title.string else "No Title"
        state["raw_data"] = {"html": str(soup), "title": title}
        return state