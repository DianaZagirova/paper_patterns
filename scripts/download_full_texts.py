#!/usr/bin/env python3
"""
Download Full Text Papers from PubMed Central

This script searches PubMed for articles matching a query and downloads their
full text from PubMed Central.
"""
import sys
import time
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.api.ncbi_client import NCBIClient
from src.collectors.pmc_downloader import PMCDownloader
from src.collectors.checkpoint_manager import CheckpointManager
from config.settings import NCBIConfig, DownloadConfig, FULL_TEXTS_DIR


def search_pubmed(client: NCBIClient, query: str, max_results: int) -> list:
    """
    Search PubMed and return list of PMIDs.
    
    Args:
        client: NCBI client instance
        query: Search query
        max_results: Maximum number of results
        
    Returns:
        List of PubMed IDs
    """
    print("Searching PubMed for articles matching query...")
    
    record = client.search(
        db=NCBIConfig.DB_PUBMED,
        term=query,
        retmax=max_results,
        sort="relevance"
    )
    
    if not record:
        raise RuntimeError("PubMed search failed. Please check your connection and try again.")
    
    id_list = record["IdList"]
    print(f"Found {len(id_list)} papers with full text available")
    
    return id_list


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Download full-text papers from PubMed Central')
    parser.add_argument('--query', type=str, help='PubMed search query')
    parser.add_argument('--max-results', type=int, default=DownloadConfig.MAX_RESULTS,
                        help=f'Maximum number of results (default: {DownloadConfig.MAX_RESULTS})')
    parser.add_argument('--batch-size', type=int, default=DownloadConfig.BATCH_SIZE,
                        help=f'Batch size (default: {DownloadConfig.BATCH_SIZE})')
    parser.add_argument('--threads', type=int, default=DownloadConfig.NUM_THREADS,
                        help=f'Number of threads (default: {DownloadConfig.NUM_THREADS})')
    parser.add_argument('--checkpoint-interval', type=int, default=DownloadConfig.CHECKPOINT_INTERVAL,
                        help=f'Checkpoint interval (default: {DownloadConfig.CHECKPOINT_INTERVAL})')
    parser.add_argument('--output-dir', type=str, default=str(FULL_TEXTS_DIR),
                        help='Output directory for downloaded papers')
    
    args = parser.parse_args()
    
    # Default query if none provided
    if not args.query:
        args.query = (
            '(("novel"[Title] OR "new"[Title] OR "promising"[Title] OR "candidate"[Title] OR "emerging"[Title]) AND '
            '("target"[Title] OR "targets"[Title])) NOT "review"[Publication Type] '
            'NOT "editorial"[Publication Type] NOT "case reports"[Publication Type]) '
            'AND (2005:2026[pdat]) AND (ffrft[Filter])'
        )
    
    print("=" * 80)
    print("PMC Full Text Downloader")
    print("=" * 80)
    print(f"Query: {args.query}")
    print(f"Max results: {args.max_results}")
    print(f"Batch size: {args.batch_size}")
    print(f"Threads: {args.threads}")
    print(f"Output directory: {args.output_dir}")
    print("=" * 80)
    
    # Initialize components
    client = NCBIClient()
    downloader = PMCDownloader()
    checkpoint_manager = CheckpointManager(Path(args.output_dir))
    
    # Search PubMed
    try:
        id_list = search_pubmed(client, args.query, args.max_results)
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return 1
    
    if not id_list:
        print("No papers found matching the query.")
        return 0
    
    # Progress callback for checkpointing
    def progress_callback(batch_idx, num_batches, documents, failed, multiple):
        if batch_idx == 0 or (batch_idx + 1) % args.checkpoint_interval == 0 or (batch_idx + 1) == num_batches:
            checkpoint_manager.save_checkpoint(batch_idx, num_batches, documents, failed, multiple)
    
    # Download papers
    print(f"\nStarting download with {args.threads} threads, batch size {args.batch_size}...")
    start_time = time.time()
    
    try:
        documents, failed, multiple = downloader.download_batch_parallel(
            id_list=id_list,
            batch_size=args.batch_size,
            num_threads=args.threads,
            progress_callback=progress_callback
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Saving progress...")
        return 1
    except Exception as e:
        print(f"\nError during download: {str(e)}")
        return 1
    
    # Print summary
    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print("Download Summary")
    print("=" * 80)
    print(f"Completed in {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print(f"Total papers successfully retrieved: {len(documents)}")
    print(f"Total papers that failed: {len(failed)}")
    print(f"Papers with multiple PMC IDs: {len(multiple)}")
    print("=" * 80)
    
    # Save final results
    checkpoint_manager.save_final_results(documents, failed, multiple)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nError in main execution: {str(e)}")
        sys.exit(1)
