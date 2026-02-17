import time
from youdotcom import You
from youdotcom.errors import YouDefaultError
from typing import List, Dict
import os 

def search(query: str) -> List[Dict[str, str]]:
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            with You(os.getenv('you')) as you:
                result = you.search.unified(query=query)
            
            search_results = []
            for web_item in result.results.web[:10]:
                search_results.append({
                    "Title": web_item.title,
                    "URL": web_item.url,
                    "Description": web_item.description,
                })
            
            return search_results
        
        except YouDefaultError as e:
            error_msg = str(e).lower()
            status = getattr(e, 'status_code', 0)
            
            # 429 Rate Limit
            if status == 429 or "rate limit" in error_msg:
                if attempt < max_retries - 1:
                    wait = 10
                    print(f"Search rate limit, waiting {wait}s...")
                    time.sleep(wait)
                    continue
                else:
                    print(f"Search rate limit exhausted for: {query}")
                    return []
            
            # 503 Service Unavailable
            elif status in [503, 504] or "network error" in error_msg or "timeout" in error_msg:
                if attempt < max_retries - 1:
                    wait = 3 ** attempt  
                    print(f"Search {status} error, retry {attempt+1} in {wait}s: {query[:50]}")
                    time.sleep(wait)
                    continue
                else:
                    print(f"Search failed after {max_retries} retries: {query[:50]}")
                    return []
            
            # Other errors
            else:
                print(f"Search error for '{query[:50]}': {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return []
        
        except Exception as e:
            print(f"Unexpected search error for '{query[:50]}': {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return []
    
    return []  

def normalize_url(url):
    if not url:
        return None
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        return f'https://{url}'
    return url