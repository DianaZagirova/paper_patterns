#!/usr/bin/env python3
"""
Collect Negative Example Papers

This script collects data on papers that mimic aging theory papers but are not
actually about aging theories. It's the modular replacement for process_negative_examples.py
"""
import sys
import argparse
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the negative collector module
import importlib.util
spec = importlib.util.spec_from_file_location(
    "negative_collector",
    project_root / "src" / "collectors" / "negative_collector.py"
)
negative_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(negative_module)


def load_dois_from_excel(excel_file: str, sheet_name: str = 'negatives', doi_column: str = 'DOI') -> list:
    """
    Load DOIs from Excel file.
    
    Args:
        excel_file: Path to Excel file
        sheet_name: Name of the sheet to read
        doi_column: Name of the DOI column
        
    Returns:
        List of DOI strings
    """
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        if doi_column not in df.columns:
            raise ValueError(f"Column '{doi_column}' not found in sheet '{sheet_name}'")
        
        # Get DOIs and convert to list, removing NaN values
        dois = df[doi_column].dropna().tolist()
        
        # Add https://doi.org/ prefix if not present
        formatted_dois = []
        for doi in dois:
            doi_str = str(doi).strip()
            if not doi_str.startswith('http'):
                doi_str = f'https://doi.org/{doi_str}'
            formatted_dois.append(doi_str)
        
        return formatted_dois
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return []


def main():
    """Main function - wrapper for process_negative_examples."""
    parser = argparse.ArgumentParser(
        description='Collect negative example papers (papers that mimic but are not aging theory papers)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script collects negative examples for training/analysis:
- Papers that appear related to aging but are NOT about aging theories
- Used to improve classification and search strategies
- Helps identify false positives

The system processes DOIs from Excel file or Python file

Examples:
  # Run with default settings (reads from Excel)
  python scripts/collect_negative_examples.py
  
  # Specify custom Excel file
  python scripts/collect_negative_examples.py --excel-file my_papers.xlsx --sheet negatives
  
  # Use old Python DOI list file
  python scripts/collect_negative_examples.py --doi-file dois_minus_list.py
        """
    )
    
    parser.add_argument(
        '--excel-file',
        type=str,
        default='data/aging_theories_papers/aging_theories_papers.xlsx',
        help='Excel file containing DOI list (default: data/aging_theories_papers/aging_theories_papers.xlsx)'
    )
    
    parser.add_argument(
        '--sheet',
        type=str,
        default='negatives',
        help='Sheet name in Excel file (default: negatives)'
    )
    
    parser.add_argument(
        '--doi-file',
        type=str,
        default=None,
        help='Python file containing negative example DOI list (legacy option, overrides Excel file)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./data/negative_examples',
        help='Output directory for negative examples (default: ./negative_examples)'
    )
    
    parser.add_argument(
        '--threads',
        type=int,
        default=1,
        help='Number of parallel threads (default: 1)'
    )
    
    args = parser.parse_args()
    
    print("="*80)
    print("Negative Examples Collector")
    print("="*80)
    
    # Load DOIs from Excel or Python file
    if args.doi_file:
        print(f"DOI source: {args.doi_file} (Python file)")
        # Use the original dois_minus_list.py approach
        dois = None
    else:
        print(f"DOI source: {args.excel_file}")
        print(f"Sheet: {args.sheet}")
        dois = load_dois_from_excel(args.excel_file, args.sheet)
        if not dois:
            print("Error: No DOIs loaded from Excel file")
            return 1
        print(f"Loaded {len(dois)} DOIs from Excel")
        
        # Override the dois in the module
        negative_module.dois = dois
    
    print(f"Output directory: {args.output_dir}")
    print(f"Threads: {args.threads}")
    print("="*80)
    print()
    
    # Update configuration in the module
    negative_module.DATA_DIR = args.output_dir
    negative_module.PAPERS_DIR = f"{args.output_dir}/papers"
    negative_module.CACHE_FILE = f"{args.output_dir}/processed_dois.json"
    negative_module.LOG_FILE = f"{args.output_dir}/collection_log.txt"
    
    # Run the main collection
    try:
        negative_module.main()
        return 0
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress has been saved.")
        return 1
    except Exception as e:
        print(f"\nError: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
