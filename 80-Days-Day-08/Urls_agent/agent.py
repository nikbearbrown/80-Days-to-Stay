from langgraph.graph import StateGraph, START, END 
from pydantic import BaseModel, AnyUrl
from typing import TypedDict, Optional, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd 
from dotenv import load_dotenv
import os 
from google import genai
import threading
import time 
from prompt import WEBSITE_EXTRACTION_PROMPT
from rate_limiting import RateLimiter
from config import MODEL, THREAD_WORKERS
from utils import search, normalize_url

load_dotenv()
start = time.time()
rate_limiter = RateLimiter()

class WebsiteFinder(TypedDict):
    company_name: str 
    searched_results: List[Dict[str, str]] 
    results: Dict[str, str]
    tried_enhanced: bool = False

class Content(BaseModel):
    official_website: Optional[str] = None
    reasoning: str 
    alternative_url: Optional[str] = None
    error: bool = False

def enhanced_search(state: WebsiteFinder) -> WebsiteFinder:
    company = state['company_name']
    cleaned = company.replace(" INC", "").replace(" LLC", "").replace(" CORP", "").strip()
    query = f'{cleaned} company'
    print(f'Enhanced search for {company} → Query: {query}')
    state['searched_results'] = search(query)
    state['tried_enhanced'] = True
    return state

def search_web(state: WebsiteFinder) -> WebsiteFinder:
    state['searched_results'] = search(state['company_name'] + ' company')
    return state 

def llm_extraction(state: WebsiteFinder) -> WebsiteFinder:
    rate_limiter.wait()
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    if not state['searched_results']:
        return state
    max_retries = 2
    for attempt in range(max_retries):
        try:
            prompt = WEBSITE_EXTRACTION_PROMPT.format(
            company_name = state['company_name'], search_results = state['searched_results'])

            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": Content,
                }
            )

            result: Content = response.parsed
            state['results'] = result.model_dump()
            return state
        
        except genai.errors.ServerError as e:
            # 503 Service Unavailable
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt 
                print(f"503 error from Gemini for {state['company_name']}, retry {attempt+1} in {wait_time}s")
                time.sleep(wait_time)
                continue
            else:
                print(f"Failed from Gemini after {max_retries} retries: {state['company_name']}")

        except Exception as e:
            # Unexpected errors
            print(f"Unexpected error from Gemini for {state['company_name']}: {e}")
            break

    # All retries exhausted
    state['results'] = {
        'official_website': None,
        'reasoning': f'API failed after {max_retries} retries',
        'alternative_url': None,
        'error': True
    }
    return state

def router(state: WebsiteFinder) -> str:
    results = state['results']
    if results.get('official_website') or results.get('alternative_url'):
        return 'validate_url'
    elif not state.get('tried_enhanced', False):
        return 'enhanced_search'
    else:
        return 'END'

def validation(state: WebsiteFinder) -> WebsiteFinder:    
    url1 = normalize_url(state['results'].get('official_website'))
    url2 = normalize_url(state['results'].get('alternative_url'))
    
    if url1:
        state['results']['official_website'] = url1
    if url2:
        state['results']['alternative_url'] = url2
    
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}

    if url1:
        try:
            r = requests.get(url1, headers=headers, allow_redirects=True, timeout=10, stream=True)
            r.close()
        except requests.exceptions.RequestException:
            print(f"{url1} unreachable")
            state['results']['official_website'] = None
            
            if url2:
                try:
                    r = requests.get(url2, headers=headers, allow_redirects=True, timeout=10, stream=True)
                    r.close()
                except requests.exceptions.RequestException:
                    print(f"{url2} also unreachable")
                    state['results']['alternative_url'] = None

    return state

def process_one(company_name):
    initial_state = {
        "company_name": company_name, 
        "results": {},
        "searched_results": [],
        "tried_enhanced": False
    }
    output_state = workflow.invoke(initial_state)
    return output_state

graph = StateGraph(WebsiteFinder)

# Nodes
graph.add_node("Search_Web", search_web)
graph.add_node("LLM_Extraction", llm_extraction)
graph.add_node("enhanced_search", enhanced_search)
graph.add_node("Validate_Url", validation)

# Edges
graph.add_edge(START, "Search_Web")
graph.add_edge("Search_Web", "LLM_Extraction")
graph.add_conditional_edges("LLM_Extraction", router, {"enhanced_search": "enhanced_search",
                                                       "validate_url": "Validate_Url" ,
                                                       "END": END})
graph.add_edge("enhanced_search", "LLM_Extraction")
graph.add_edge("Validate_Url", END)

workflow = graph.compile()

# Main processing
successful = []
failed = []

company_names = []

write_lock = threading.Lock()

print(f"Processing {len(company_names)} companies...")

with ThreadPoolExecutor(max_workers=THREAD_WORKERS) as executor:
    futures = {executor.submit(process_one, c): c for c in company_names}
    
    for i, future in enumerate(as_completed(futures), 1):
        output_state = future.result()
        
        with write_lock:
            if output_state.get('error'):
                failed.append({
                    'company': output_state['company_name'],
                    'error': output_state['results']['error']
                })
            else:
                row = {
                    "company_name": output_state['company_name'],
                    "website": output_state['results']['official_website'],
                    "reasoning": output_state['results']['reasoning'],
                    "alternative_url": output_state['results']['alternative_url']
                }
                successful.append(row)
                
                pd.DataFrame([row]).to_csv(
                    'Websites_data.csv',
                    mode='a',
                    header=not os.path.exists('Websites_data.csv'),
                    index=False
                )
            
            # Progress every 100
            if i % 100 == 0:
                print(f"Progress: {i}/{len(company_names)} | "
                      f"Success: {len(successful)} | Failed: {len(failed)}")
end = time.time()
print(f"\n Done! Success: {len(successful)}, Failed: {len(failed)}, time taken: {end - start}")

    








