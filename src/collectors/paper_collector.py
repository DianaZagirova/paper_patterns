#!/usr/bin/env python3
"""
Academic Paper Data Collector

This script collects comprehensive data on academic papers based on DOIs, including:
- Title, abstract
- Full text (by section)
- MESH terms, keywords
- Number of citations
- Authors and their institutions
- Publication year
- Journal information

The system processes DOIs incrementally, only handling new entries when the script is rerun.
"""
import os
import time
import json
import pickle
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union, Any

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from Bio import Entrez
import xml.etree.ElementTree as ET

# Configuration constants
DATA_DIR = './data/paper_data'
CACHE_FILE = os.path.join(DATA_DIR, 'processed_dois.json')
PAPERS_DIR = os.path.join(DATA_DIR, 'papers')
LOG_FILE = os.path.join(DATA_DIR, 'collection_log.txt')

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PAPERS_DIR, exist_ok=True)

# NCBI API rate limiting (max 10 requests/sec with API key, we use 2 to be very safe)
MAX_REQUESTS_PER_SEC = 2
semaphore = threading.BoundedSemaphore(value=MAX_REQUESTS_PER_SEC)
last_req_time = [0]  # List to allow modification in nested scopes

# Initialize logging
def log_message(message: str) -> None:
    """Write a timestamped message to the log file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")
    print(message)

def normalize_doi(doi: str) -> str:
    """
    Normalize a DOI by removing the URL prefix if present.
    
    Args:
        doi: DOI string, possibly with URL prefix
        
    Returns:
        Normalized DOI string
    """
    if doi.startswith('https://doi.org/'):
        return doi[16:]
    elif doi.startswith('http://doi.org/'):
        return doi[15:]
    elif doi.startswith('doi.org/'):
        return doi[8:]
    return doi

def safe_api_call(func, *args, **kwargs):
    """
    Wrapper for API calls with timeout handling, retries, and rate-limiting.
    
    Args:
        func: The function to call
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function
        
    Returns:
        The result of the function call or None if all attempts failed
    """
    tries = 3
    for attempt in range(tries):
        try:
            with semaphore:
                # Respect API rate limit: ensure minimum time between requests
                elapsed = time.time() - last_req_time[0]
                wait = max(0, 1.0/MAX_REQUESTS_PER_SEC - elapsed)
                if wait:
                    time.sleep(wait)
                last_req_time[0] = time.time()
                return func(*args, **kwargs)
        except Exception as e:
            if attempt < tries-1:
                # Exponential backoff for rate limit errors
                if '429' in str(e) or 'Too Many Requests' in str(e):
                    wait_time = 5 * (attempt + 1)  # 5, 10 seconds
                    log_message(f"Rate limit hit, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                else:
                    log_message(f"Retrying {func.__name__} (Error: {str(e)})")
                    time.sleep(2)
            else:
                log_message(f"Failed {func.__name__} after {tries} attempts (Error: {str(e)})")
                return None

def get_paper_data_from_doi(doi: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve comprehensive data about a paper using its DOI.
    
    Args:
        doi: Digital Object Identifier for the paper
        
    Returns:
        Dictionary containing all available paper data or None if retrieval failed
    """
    normalized_doi = normalize_doi(doi)
    
    # Initialize paper data structure
    paper_data = {
        'doi': normalized_doi,
        'title': None,
        'abstract': None,
        'full_text': {},  # Will contain sections
        'mesh_terms': [],
        'keywords': [],
        'citation_count': None,
        'authors': [],
        'year': None,
        'journal': None,
        'pmid': None,
        'pmcid': None,
        'collection_date': datetime.now().strftime("%Y-%m-%d"),
    }
    
    # Step 1: Get basic metadata from CrossRef
    crossref_data = get_crossref_metadata(normalized_doi)
    if crossref_data:
        paper_data.update(crossref_data)
    
    # Step 2: Get PubMed/PMC data if available
    pubmed_data = get_pubmed_data(normalized_doi)
    if pubmed_data:
        paper_data.update(pubmed_data)
        
        # If we have a PMCID, try to get full text
        if paper_data.get('pmcid'):
            full_text_data = get_pmc_full_text(paper_data['pmcid'])
            if full_text_data:
                paper_data.update(full_text_data)
    
    # Step 3: Try to get citation count from various sources
    if not paper_data.get('citation_count'):
        paper_data['citation_count'] = get_citation_count(normalized_doi)
    
    # Return None if we couldn't get any meaningful data
    if paper_data['title'] is None:
        log_message(f"Failed to retrieve any meaningful data for DOI: {doi}")
        return None
        
    return paper_data

def get_crossref_metadata(doi: str) -> Dict[str, Any]:
    """
    Retrieve metadata from CrossRef API.
    
    Args:
        doi: Normalized DOI string
        
    Returns:
        Dictionary with paper metadata
    """
    result = {}
    url = f"https://api.crossref.org/works/{doi}"
    
    response = safe_api_call(requests.get, url, headers={'User-Agent': 'PaperDataCollector/1.0 (mailto:your.email@example.com)'})
    if not response or response.status_code != 200:
        return result
        
    try:
        data = response.json()['message']
        
        # Extract basic metadata
        result['title'] = data.get('title', [None])[0]
        result['journal'] = data.get('container-title', [None])[0]
        
        # Extract publication date
        if 'published' in data and 'date-parts' in data['published']:
            date_parts = data['published']['date-parts'][0]
            if len(date_parts) > 0:
                result['year'] = date_parts[0]
        
        # Extract authors
        if 'author' in data:
            authors = []
            for author in data['author']:
                author_info = {
                    'name': f"{author.get('given', '')} {author.get('family', '')}".strip(),
                    'affiliations': []
                }
                
                if 'affiliation' in author:
                    for affiliation in author['affiliation']:
                        if 'name' in affiliation:
                            author_info['affiliations'].append(affiliation['name'])
                
                authors.append(author_info)
            result['authors'] = authors
            
        # Extract citation count if available
        if 'is-referenced-by-count' in data:
            result['citation_count'] = data['is-referenced-by-count']
            
    except Exception as e:
        log_message(f"Error parsing CrossRef data for DOI {doi}: {str(e)}")
    
    return result

def get_pubmed_data(doi: str) -> Dict[str, Any]:
    """
    Retrieve data from PubMed using the DOI.
    
    Args:
        doi: Normalized DOI string
        
    Returns:
        Dictionary with PubMed data including PMID, PMCID, MeSH terms, etc.
    """
    result = {}
    
    # Search for the article by DOI
    handle = safe_api_call(
        Entrez.esearch,
        db="pubmed",
        term=f"{doi}[DOI]",
        retmax=1
    )
    
    if not handle:
        return result
        
    try:
        record = Entrez.read(handle)
        handle.close()
        
        if not record['IdList']:
            return result
            
        pmid = record['IdList'][0]
        result['pmid'] = pmid
        
        # Fetch detailed article data
        fetch_handle = safe_api_call(
            Entrez.efetch,
            db="pubmed",
            id=pmid,
            retmode="xml"
        )
        
        if not fetch_handle:
            return result
            
        articles = Entrez.read(fetch_handle)
        fetch_handle.close()
        
        if not articles['PubmedArticle']:
            return result
            
        article = articles['PubmedArticle'][0]
        
        # Extract MeSH terms
        mesh_terms = []
        if 'MeshHeadingList' in article['MedlineCitation']:
            for mesh in article['MedlineCitation']['MeshHeadingList']:
                term = mesh['DescriptorName']
                mesh_terms.append(term)
        result['mesh_terms'] = mesh_terms
        
        # Extract keywords
        keywords = []
        if 'KeywordList' in article['MedlineCitation']:
            for keyword_list in article['MedlineCitation']['KeywordList']:
                for keyword in keyword_list:
                    keywords.append(str(keyword))
        result['keywords'] = keywords
        
        # Extract abstract
        if 'Abstract' in article['MedlineCitation']['Article']:
            abstract_parts = article['MedlineCitation']['Article']['Abstract']['AbstractText']
            abstract = ""
            for part in abstract_parts:
                if hasattr(part, 'attributes') and 'Label' in part.attributes:
                    abstract += f"{part.attributes['Label']}: {part}\n"
                else:
                    abstract += f"{part}\n"
            result['abstract'] = abstract.strip()
        
        # Check for PMCID
        if 'ArticleIdList' in article['PubmedData']:
            for id_item in article['PubmedData']['ArticleIdList']:
                if str(id_item).startswith('PMC'):
                    result['pmcid'] = str(id_item)
                    break
                    
    except Exception as e:
        log_message(f"Error retrieving PubMed data for DOI {doi}: {str(e)}")
    
    return result

def get_pmc_full_text(pmcid: str) -> Dict[str, Any]:
    """
    Retrieve full text content from PubMed Central.
    
    Args:
        pmcid: PubMed Central ID (with or without 'PMC' prefix)
        
    Returns:
        Dictionary with full text content organized by sections
    """
    result = {'full_text': {}}
    
    # Normalize PMCID format (strip 'PMC' prefix if present)
    pmcid_stripped = pmcid.replace("PMC", "") if pmcid.startswith("PMC") else pmcid
    
    # Fetch the document from PMC
    handle = safe_api_call(
        Entrez.efetch,
        db="pmc",
        id=pmcid_stripped,
        rettype="full",
        retmode="xml"
    )
    
    if not handle:
        return result
        
    # Parse the XML content
    try:
        records = handle.read()
        handle.close()
        if isinstance(records, bytes):
            records = records.decode("utf-8")
        root = ET.fromstring(records)
    except Exception as e:
        log_message(f"Failed to parse XML for PMCID {pmcid}: {str(e)}")
        return result

    # Prefer <article> as root
    article_tag = root.find('.//article') or (root if root.tag == 'article' else None)
    if not article_tag and root.find('.//pmc-articleset') is not None:
        article_tag = root.find('.//pmc-articleset/article')
    if not article_tag:
        log_message(f"No <article> tag found in XML for PMCID {pmcid}")
        return result

    # Extract full text by sections
    def extract_section(parent, section_name=None):
        text = ''
        sect_title = parent.find('./title')
        if sect_title is not None:
            section_name = ''.join(sect_title.itertext()).strip()
            
        for p in parent.findall('./p'):
            text += ''.join(p.itertext()).strip() + '\n\n'
            
        return section_name, text

    # Process main body sections
    body = article_tag.find('.//body')
    if body is not None:
        for top_sec in body.findall('./sec'):
            section_name, section_text = extract_section(top_sec)
            if section_name and section_text:
                result['full_text'][section_name] = section_text
                
            # Process subsections
            for subsec in top_sec.findall('./sec'):
                subsection_name, subsection_text = extract_section(subsec)
                if subsection_name and subsection_text:
                    result['full_text'][f"{section_name} - {subsection_name}"] = subsection_text
    
    # If no structured sections were found, try to get all paragraphs
    if not result['full_text'] and body is not None:
        all_paragraphs = ""
        for p in body.findall('.//p'):
            all_paragraphs += ''.join(p.itertext()).strip() + '\n\n'
        if all_paragraphs:
            result['full_text']['Main Text'] = all_paragraphs
    
    return result

def get_citation_count(doi: str) -> Optional[int]:
    """
    Try to get citation count from various sources.
    
    Args:
        doi: Normalized DOI string
        
    Returns:
        Citation count if available, otherwise None
    """
    # Try Semantic Scholar API
    url = f"https://api.semanticscholar.org/v1/paper/{doi}"
    response = safe_api_call(requests.get, url)
    
    if response and response.status_code == 200:
        try:
            data = response.json()
            if 'citationCount' in data:
                return data['citationCount']
        except Exception:
            pass
    
    return None

def load_processed_dois() -> Set[str]:
    """
    Load the set of already processed DOIs from cache file.
    
    Returns:
        Set of normalized DOIs that have already been processed
    """
    if not os.path.exists(CACHE_FILE):
        return set()
        
    try:
        with open(CACHE_FILE, 'r') as f:
            return set(json.load(f))
    except Exception as e:
        log_message(f"Error loading processed DOIs cache: {str(e)}")
        return set()

def save_processed_dois(processed_dois: Set[str]) -> None:
    """
    Save the set of processed DOIs to cache file.
    
    Args:
        processed_dois: Set of normalized DOIs that have been processed
    """
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump(list(processed_dois), f)
    except Exception as e:
        log_message(f"Error saving processed DOIs cache: {str(e)}")

def save_paper_data(paper_data: Dict[str, Any]) -> str:
    """
    Save paper data to a JSON file.
    
    Args:
        paper_data: Dictionary containing paper data
        
    Returns:
        Path to the saved file
    """
    # Create a filename based on DOI (replacing invalid characters)
    safe_filename = paper_data['doi'].replace('/', '_').replace('\\', '_')
    file_path = os.path.join(PAPERS_DIR, f"{safe_filename}.json")
    
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(paper_data, f, ensure_ascii=False, indent=2)
        return file_path
    except Exception as e:
        log_message(f"Error saving paper data for DOI {paper_data['doi']}: {str(e)}")
        return ""

def process_doi(doi: str, processed_dois: Set[str]) -> Tuple[bool, Optional[str]]:
    """
    Process a single DOI to collect paper data.
    
    Args:
        doi: DOI string to process
        processed_dois: Set of already processed DOIs
        
    Returns:
        Tuple of (success_flag, file_path_if_saved)
    """
    normalized_doi = normalize_doi(doi)
    
    # Skip if already processed
    if normalized_doi in processed_dois:
        return False, None
        
    log_message(f"Processing DOI: {doi}")
    
    # Get paper data
    paper_data = get_paper_data_from_doi(normalized_doi)
    if not paper_data:
        log_message(f"Failed to retrieve data for DOI: {doi}")
        return False, None
        
    # Save paper data
    file_path = save_paper_data(paper_data)
    if file_path:
        log_message(f"Successfully saved data for DOI: {doi}")
        return True, file_path
    else:
        return False, None

def main():
    """Main function to process DOIs from the list."""
    # Set up Entrez email and API key (if available)
    Entrez.email = "your.email@example.com"  # Replace with your email
    # Entrez.api_key = "your_api_key"  # Uncomment and replace with your API key if you have one
    
    # Import DOI list (if not already set by wrapper script)
    global dois
    if 'dois' not in globals() or dois is None:
        try:
            # Try to import from root directory
            import sys
            from pathlib import Path
            root_dir = Path(__file__).parent.parent.parent
            sys.path.insert(0, str(root_dir))
            from doi_list import dois
        except ImportError:
            log_message("Error: Could not import DOI list. Make sure doi_list.py exists or use the wrapper script.")
            return
    
    # Load already processed DOIs
    processed_dois = load_processed_dois()
    log_message(f"Loaded {len(processed_dois)} previously processed DOIs")
    
    # Filter out already processed DOIs
    dois_to_process = [doi for doi in dois if normalize_doi(doi) not in processed_dois]
    log_message(f"Found {len(dois_to_process)} new DOIs to process")
    
    if not dois_to_process:
        log_message("No new DOIs to process. Exiting.")
        return
    
    # Process DOIs with multithreading
    num_threads = min(5, len(dois_to_process))  # Use at most 5 threads
    successful_dois = []
    
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = {executor.submit(process_doi, doi, processed_dois): doi for doi in dois_to_process}
        
        for future in tqdm(as_completed(futures), total=len(futures), desc="Processing DOIs"):
            doi = futures[future]
            try:
                success, file_path = future.result()
                if success:
                    normalized_doi = normalize_doi(doi)
                    processed_dois.add(normalized_doi)
                    successful_dois.append((normalized_doi, file_path))
            except Exception as e:
                log_message(f"Error processing DOI {doi}: {str(e)}")
    
    # Save updated processed DOIs
    save_processed_dois(processed_dois)
    
    # Print summary
    log_message(f"Processing complete. Successfully processed {len(successful_dois)} out of {len(dois_to_process)} DOIs.")
    for doi, file_path in successful_dois:
        log_message(f"  - {doi} -> {os.path.basename(file_path)}")

if __name__ == "__main__":
    try:
        start_time = time.time()
        log_message("Starting paper data collection process")
        main()
        elapsed = time.time() - start_time
        log_message(f"Process completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    except KeyboardInterrupt:
        log_message("Process interrupted by user. Exiting...")
    except Exception as e:
        log_message(f"Error in main execution: {str(e)}")
