"""
PMC Full Text Downloader

This module handles downloading full-text articles from PubMed Central.
"""
from typing import Optional, Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from src.api.ncbi_client import NCBIClient
from src.parsers.xml_parser import parse_pmc_xml
from config.settings import NCBIConfig


class PMCDownloader:
    """Handles downloading full-text articles from PubMed Central."""
    
    def __init__(self, email: Optional[str] = None, api_key: Optional[str] = None):
        """
        Initialize the PMC downloader.
        
        Args:
            email: Email address for NCBI
            api_key: Optional API key for higher rate limits
        """
        self.client = NCBIClient(email=email, api_key=api_key)
    
    def download_article(self, pmcid: str) -> Optional[Dict[str, any]]:
        """
        Download and parse a single PMC article.
        
        Args:
            pmcid: PubMed Central ID (with or without 'PMC' prefix)
            
        Returns:
            Dictionary containing metadata and full text, or None if failed
        """
        # Normalize PMCID format
        pmcid_stripped = pmcid.replace("PMC", "") if pmcid.startswith("PMC") else pmcid
        
        # Fetch document from PMC
        handle = self.client.fetch(db=NCBIConfig.DB_PMC, id=pmcid_stripped, rettype="full", retmode="xml")
        if handle is None:
            return None
        
        # Read XML content
        try:
            xml_content = handle.read()
            handle.close()
        except Exception as e:
            print(f"Failed to read XML for PMCID {pmcid}: {str(e)}")
            return None
        
        # Parse XML
        return parse_pmc_xml(xml_content, pmcid_stripped)
    
    def fetch_pmcids_from_pmids(self, pmid_batch: List[str]) -> Tuple[List[str], Dict[str, List[str]], Dict[str, Dict]]:
        """
        Process a batch of PubMed IDs to retrieve their corresponding PMC articles.
        
        Args:
            pmid_batch: List of PubMed IDs to process
            
        Returns:
            Tuple of (failed_pmids, multiple_pmcids_map, retrieved_documents)
            - failed_pmids: List of PMIDs that failed to download
            - multiple_pmcids_map: Dict mapping PMIDs to multiple PMCIDs
            - retrieved_documents: Dict mapping PMIDs to document data
        """
        failed_pmids = []
        multiple_pmcids_map = {}
        retrieved_documents = {}
        
        # Fetch metadata for all PMIDs in batch
        joined_ids = ','.join(map(str, pmid_batch))
        records = self.client.fetch_and_parse(db=NCBIConfig.DB_PUBMED, id=joined_ids)
        
        if records is None:
            failed_pmids.extend(pmid_batch)
            return failed_pmids, multiple_pmcids_map, retrieved_documents
        
        # Process each article
        articles = records.get('PubmedArticle', [])
        for article in articles:
            pmid = None
            try:
                pmid = str(article['MedlineCitation']['PMID'])
                
                # Extract PMC IDs
                article_ids = article['PubmedData']['ArticleIdList']
                pmcids = [str(id_item) for id_item in article_ids if str(id_item).startswith('PMC')]
                
                if not pmcids:
                    failed_pmids.append(pmid)
                    continue
                
                # Track multiple PMCIDs
                if len(pmcids) > 1:
                    multiple_pmcids_map[pmid] = pmcids
                
                # Download full text
                document = self.download_article(pmcids[0])
                if document:
                    document['metadata']['PMCID'] = pmcids[0]
                    retrieved_documents[pmid] = document
                else:
                    failed_pmids.append(pmid)
                    
            except Exception as e:
                if pmid:
                    failed_pmids.append(pmid)
                    print(f"Error processing PMID {pmid}: {str(e)}")
                else:
                    print(f"Error processing article: {str(e)}")
        
        return failed_pmids, multiple_pmcids_map, retrieved_documents
    
    def download_batch_parallel(
        self,
        id_list: List[str],
        batch_size: int,
        num_threads: int,
        progress_callback: Optional[callable] = None
    ) -> Tuple[Dict[str, Dict], List[str], Dict[str, List[str]]]:
        """
        Download multiple articles in parallel batches.
        
        Args:
            id_list: List of PubMed IDs
            batch_size: Number of IDs per batch
            num_threads: Number of parallel threads
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Tuple of (retrieved_documents, failed_pmids, multiple_pmcids)
        """
        failed_pmids = []
        multiple_pmcids = {}
        retrieved_documents = {}
        
        # Create batches
        batches = [id_list[i:i + batch_size] for i in range(0, len(id_list), batch_size)]
        
        # Process batches in parallel
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(self.fetch_pmcids_from_pmids, batch): batch for batch in batches}
            
            for i, future in enumerate(tqdm(as_completed(futures), total=len(futures), desc="Processing batches")):
                try:
                    batch_failed, batch_multiple, batch_documents = future.result()
                    failed_pmids.extend(batch_failed)
                    multiple_pmcids.update(batch_multiple)
                    retrieved_documents.update(batch_documents)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress_callback(i, len(futures), retrieved_documents, failed_pmids, multiple_pmcids)
                        
                except Exception as exc:
                    print(f"Batch failed with exception: {exc}")
        
        return retrieved_documents, failed_pmids, multiple_pmcids
