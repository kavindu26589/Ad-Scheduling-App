import requests

def perform_web_search(query: str) -> str:
    """
    Perform a web search for future programs using the DuckDuckGo Instant Answer API.

    Args:
        query (str): The search query.
        
    Returns:
        str: Formatted search results or an error message.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        results = []
        # Try to use RelatedTopics if available
        related = data.get("RelatedTopics", [])
        if related:
            # Flatten nested RelatedTopics if necessary
            flat_results = []
            for item in related:
                if isinstance(item, dict) and "Text" in item:
                    flat_results.append(item)
                elif isinstance(item, dict) and "Topics" in item:
                    flat_results.extend(item.get("Topics", []))
            
            for item in flat_results[:3]:
                title = item.get("Text", "No Title")
                results.append(f"- {title}")
        else:
            # Fallback to AbstractText
            abstract = data.get("AbstractText", "No results found.")
            results.append(abstract)
            
        return f"Search results for '{query}':\n" + "\n".join(results)
    except Exception as e:
        return f"Error performing web search: {e}"
