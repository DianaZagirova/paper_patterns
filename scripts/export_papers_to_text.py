#!/usr/bin/env python3
"""
Export Papers to Text Files

This script exports paper data from JSON files to consolidated text files
for easier analysis and LLM processing.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def format_paper_for_text(paper: Dict[str, Any]) -> str:
    """
    Format a single paper's data as readable text.
    
    Args:
        paper: Paper data dictionary
        
    Returns:
        Formatted text string
    """
    lines = []
    lines.append("=" * 80)
    lines.append(f"DOI: {paper.get('doi', 'N/A')}")
    lines.append("=" * 80)
    lines.append("")
    
    # Title
    lines.append(f"TITLE: {paper.get('title', 'N/A')}")
    lines.append("")
    
    # Abstract
    abstract = paper.get('abstract', 'N/A')
    lines.append(f"ABSTRACT: {abstract}")
    lines.append("")
    
    # Full text
    full_text = paper.get('full_text', {})
    if full_text and isinstance(full_text, dict):
        lines.append("FULL TEXT:")
        for section, content in full_text.items():
            if content:
                lines.append(f"\n[{section}]")
                lines.append(content)
        lines.append("")
    
    # MeSH terms
    mesh_terms = paper.get('mesh_terms', [])
    if mesh_terms:
        lines.append(f"MESH TERMS: {', '.join(mesh_terms)}")
        lines.append("")
    
    # Keywords
    keywords = paper.get('keywords', [])
    if keywords:
        lines.append(f"KEYWORDS: {', '.join(keywords)}")
        lines.append("")
    
    # Authors
    authors = paper.get('authors', [])
    if authors:
        author_names = [a.get('name', 'Unknown') for a in authors if isinstance(a, dict)]
        lines.append(f"AUTHORS: {', '.join(author_names)}")
        lines.append("")
    
    # Year and Journal
    year = paper.get('year', 'N/A')
    journal = paper.get('journal', 'N/A')
    lines.append(f"YEAR: {year}")
    lines.append(f"JOURNAL: {journal}")
    lines.append("")
    
    return "\n".join(lines)


def export_papers_to_text(
    papers_dir: Path,
    output_file: Path,
    description: str = "papers"
) -> int:
    """
    Export all papers from a directory to a single text file.
    
    Args:
        papers_dir: Directory containing paper JSON files
        output_file: Output text file path
        description: Description for logging
        
    Returns:
        Number of papers exported
    """
    if not papers_dir.exists():
        print(f"Warning: Directory {papers_dir} does not exist")
        return 0
    
    json_files = list(papers_dir.glob("*.json"))
    if not json_files:
        print(f"Warning: No JSON files found in {papers_dir}")
        return 0
    
    print(f"Processing {len(json_files)} {description}...")
    
    papers_text = []
    papers_text.append(f"# {description.upper()}")
    papers_text.append(f"# Total papers: {len(json_files)}")
    papers_text.append(f"# Exported: {Path.cwd()}")
    papers_text.append("")
    
    for json_file in sorted(json_files):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                paper = json.load(f)
                papers_text.append(format_paper_for_text(paper))
        except Exception as e:
            print(f"Error processing {json_file.name}: {e}")
            continue
    
    # Write to output file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(papers_text))
    
    print(f"✅ Exported {len(json_files)} {description} to {output_file}")
    return len(json_files)


def main():
    """Main function to export papers."""
    print("=" * 80)
    print("Paper Data Export to Text Files")
    print("=" * 80)
    print()
    
    # Define paths
    positive_papers_dir = Path("data/paper_data/papers")
    negative_papers_dir = Path("data/negative_examples/papers")
    
    positive_output = Path("data/paper_data/papers_export.txt")
    negative_output = Path("data/negative_examples/papers_export.txt")
    
    # Export positive examples
    positive_count = export_papers_to_text(
        positive_papers_dir,
        positive_output,
        "positive examples (aging theory papers)"
    )
    
    print()
    
    # Export negative examples
    negative_count = export_papers_to_text(
        negative_papers_dir,
        negative_output,
        "negative examples (non-theory papers)"
    )
    
    print()
    print("=" * 80)
    print("Export Summary")
    print("=" * 80)
    print(f"Positive examples: {positive_count} papers → {positive_output}")
    print(f"Negative examples: {negative_count} papers → {negative_output}")
    print()
    print("✅ Export complete!")


if __name__ == "__main__":
    main()
