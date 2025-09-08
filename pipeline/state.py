from typing import TypedDict, List, Dict, Any

class PipelineState(TypedDict):
    url: str
    raw_data: dict
    cleaned_data: str
    depth: int
    max_depth: int
    max_links: int
    
class ChatState(TypedDict):
    question: str
    answer: str
    context_data: List[Dict[str, Any]]