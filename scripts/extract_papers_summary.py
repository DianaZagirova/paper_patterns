#!/usr/bin/env python3
"""
Extract Papers Summary

This script reads paper JSON files from a directory and creates a summary JSON
with the format: {"doi": {"abstract": "...", "title": "..."}}
"""
import json
import argparse
from pathlib import Path


def load_dois_from_txt(txt_file: str) -> set:
    """
    Load DOIs from text file (one DOI per line).
    
    Args:
        txt_file: Path to text file containing DOIs
        
    Returns:
        Set of normalized DOI strings
    """
    dois = set()
    try:
        with open(txt_file, 'r', encoding='utf-8') as f:
            for line in f:
                doi = line.strip()
                # Skip empty lines and comments
                if doi and not doi.startswith('#'):
                    # Normalize DOI (remove URL prefix if present)
                    if doi.startswith('https://doi.org/'):
                        doi = doi[16:]
                    elif doi.startswith('http://doi.org/'):
                        doi = doi[15:]
                    elif doi.startswith('doi.org/'):
                        doi = doi[8:]
                    dois.add(doi)
        print(f"Loaded {len(dois)} DOIs from {txt_file}")
    except Exception as e:
        print(f"Error reading DOI file: {e}")
    return dois


def extract_papers_summary(input_dir: str, output_file: str = None, doi_filter: set = None) -> dict:
    """
    Extract DOI, title, and abstract from all JSON files in a directory.
    
    Args:
        input_dir: Directory containing paper JSON files
        output_file: Optional output file path. If None, returns dict without saving.
        doi_filter: Optional set of DOIs to filter by. If provided, only these DOIs are included.
        
    Returns:
        Dictionary with format {"doi": {"abstract": "...", "title": "..."}}
    """
    input_path = Path(input_dir)
    
    if not input_path.exists():
        print(f"Error: Directory '{input_dir}' does not exist")
        return {}
    
    if not input_path.is_dir():
        print(f"Error: '{input_dir}' is not a directory")
        return {}
    
    # Find all JSON files
    json_files = list(input_path.glob("*.json"))
    
    if not json_files:
        print(f"Warning: No JSON files found in '{input_dir}'")
        return {}
    
    print(f"Found {len(json_files)} JSON files in '{input_dir}'")
    
    # Extract data from each file
    summary = {}
    skipped = 0
    filtered_out = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            doi = data.get('doi')
            title = data.get('title')
            abstract = data.get('abstract')
            
            if doi:
                # If DOI filter is provided, check if this DOI is in the filter
                if doi_filter is not None and doi not in doi_filter:
                    filtered_out += 1
                    continue
                
                summary[doi] = {
                    "title": title if title else "",
                    "abstract": abstract if abstract else ""
                }
            else:
                print(f"Warning: No DOI found in {json_file.name}")
                skipped += 1
                
        except Exception as e:
            print(f"Error reading {json_file.name}: {e}")
            skipped += 1
    
    print(f"Successfully extracted {len(summary)} papers")
    if doi_filter is not None:
        print(f"Filtered out {filtered_out} papers not in DOI list")
    if skipped > 0:
        print(f"Skipped {skipped} files due to errors")
    
    # Save to file if output path provided
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"Summary saved to: {output_file}")
    
    return summary


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Extract DOI, title, and abstract from paper JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract from default directory and save to default output
  python scripts/extract_papers_summary.py
  
  # Specify custom input directory
  python scripts/extract_papers_summary.py --input-dir data/dois_fp/papers
  
  # Filter by DOIs from text file
  python scripts/extract_papers_summary.py --input-dir data/paper_data/papers --doi-file data/aging_theories_papers/dois_tp.txt --output data/dois_tp_summary.json
  
  # Specify custom output file
  python scripts/extract_papers_summary.py --input-dir data/dois_fp/papers --output papers_summary.json
        """
    )
    
    parser.add_argument(
        '--input-dir',
        type=str,
        default='data/paper_data/papers',
        help='Directory containing paper JSON files (default: data/paper_data/papers)'
    )
    
    parser.add_argument(
        '--doi-file',
        type=str,
        default=None,
        help='Text file containing DOI list to filter by (one per line, optional)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='data/papers_summary.json',
        help='Output JSON file path (default: data/papers_summary.json)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("Paper Summary Extractor")
    print("="*80)
    print(f"Input directory: {args.input_dir}")
    if args.doi_file:
        print(f"DOI filter file: {args.doi_file}")
    print(f"Output file: {args.output}")
    print("="*80)
    print()
    
    # Load DOI filter if provided
    doi_filter = None
    if args.doi_file:
        doi_filter = load_dois_from_txt(args.doi_file)
        if not doi_filter:
            print("Error: No DOIs loaded from filter file")
            return
    
    extract_papers_summary(args.input_dir, args.output, doi_filter)
    
    print()
    print("Done!")


if __name__ == "__main__":
    main()
