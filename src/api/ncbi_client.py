"""
NCBI API Client

This module provides a wrapper for NCBI Entrez API calls with rate limiting,
retry logic, and error handling.
"""
import time
from typing import Optional, Any
from Bio import Entrez

from config.settings import NCBIConfig
from src.api.rate_limiter import RateLimiter


class NCBIClient:
    """Client for interacting with NCBI Entrez API."""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the NCBI client.
        
        Args:
            email: Email address for NCBI (required by NCBI)
            api_key: Optional API key for higher rate limits
        """
        # Set Entrez credentials
        Entrez.email = email or NCBIConfig.EMAIL
        if api_key or NCBIConfig.API_KEY:
            Entrez.api_key = api_key or NCBIConfig.API_KEY
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(NCBIConfig.get_rate_limit())
        self.retry_attempts = NCBIConfig.RETRY_ATTEMPTS
        self.retry_delay = NCBIConfig.RETRY_DELAY
    
    def safe_call(self, func, *args, **kwargs) -> Optional[Any]:
        """
        Execute an Entrez API call with rate limiting and retry logic.
        
        Args:
            func: The Entrez function to call
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            The result of the function call or None if all attempts failed
        """
        for attempt in range(self.retry_attempts):
            try:
                return self.rate_limiter(func, *args, **kwargs)
            except Exception as e:
                if attempt < self.retry_attempts - 1:
                    print(f"Retrying {func.__name__} (attempt {attempt + 1}/{self.retry_attempts}): {str(e)}")
                    time.sleep(self.retry_delay)
                else:
                    print(f"Failed {func.__name__} after {self.retry_attempts} attempts: {str(e)}")
                    return None
    
    def search(self, db: str, term: str, retmax: int = 100, sort: str = "relevance") -> Optional[Any]:
        """
        Search NCBI database.
        
        Args:
            db: Database name (e.g., 'pubmed', 'pmc')
            term: Search query
            retmax: Maximum number of results
            sort: Sort order
            
        Returns:
            Search results or None if failed
        """
        handle = self.safe_call(Entrez.esearch, db=db, term=term, retmax=retmax, sort=sort)
        if handle:
            try:
                record = Entrez.read(handle)
                handle.close()
                return record
            except Exception as e:
                print(f"Failed to parse search results: {str(e)}")
                return None
        return None
    
    def fetch(self, db: str, id: str, rettype: str = "xml", retmode: str = "xml") -> Optional[Any]:
        """
        Fetch records from NCBI database.
        
        Args:
            db: Database name
            id: Record ID(s) (can be comma-separated)
            rettype: Return type
            retmode: Return mode
            
        Returns:
            Fetched record(s) or None if failed
        """
        return self.safe_call(Entrez.efetch, db=db, id=id, rettype=rettype, retmode=retmode)
    
    def fetch_and_parse(self, db: str, id: str, retmode: str = "xml") -> Optional[Any]:
        """
        Fetch and parse records from NCBI database.
        
        Args:
            db: Database name
            id: Record ID(s)
            retmode: Return mode
            
        Returns:
            Parsed record(s) or None if failed
        """
        handle = self.fetch(db=db, id=id, retmode=retmode)
        if handle:
            try:
                record = Entrez.read(handle)
                handle.close()
                return record
            except Exception as e:
                print(f"Failed to parse fetched records: {str(e)}")
                return None
        return None
