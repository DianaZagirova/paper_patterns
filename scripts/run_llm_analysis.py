#!/usr/bin/env python3
"""
Run LLM Analysis on Papers

This script provides a command-line interface for analyzing academic papers using LLM.
"""
import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.llm.system import PaperLLMSystem
from config.settings import LLMConfig, PAPERS_DIR, NEGATIVE_PAPERS_DIR


def main():
    """Main function to run the Paper LLM System."""
    parser = argparse.ArgumentParser(
        description='Paper LLM System - Analyze academic papers using OpenAI LLM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python scripts/run_llm_analysis.py --interactive
  
  # Run a specific query
  python scripts/run_llm_analysis.py --query "What are the main aging theories?"
  
  # Use a predefined template
  python scripts/run_llm_analysis.py --template search_strategy
  
  # List available templates
  python scripts/run_llm_analysis.py --list-templates
        """
    )
    
    parser.add_argument(
        '--query', '-q',
        default='Perform a task on papers analysis and formulation of aging theory. Be very careful on word choice and do not make any assumptions.',
        type=str,
        help='Query to send to the LLM system'
    )
    
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Run in interactive mode'
    )
    
    parser.add_argument(
        '--papers-dir',
        type=str,
        default=str(PAPERS_DIR),
        help=f'Directory containing paper JSON files (default: {PAPERS_DIR})'
    )
    
    parser.add_argument(
        '--negatives-dir',
        type=str,
        default=str(NEGATIVE_PAPERS_DIR),
        help=f'Directory containing negative example papers (default: {NEGATIVE_PAPERS_DIR})'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        default=LLMConfig.MODEL,
        help=f'OpenAI model to use (default: {LLMConfig.MODEL})'
    )
    
    parser.add_argument(
        '--prompt-type',
        type=str,
        choices=['default', 'aging_theory', 'aging_theory_with_negatives', 'aging_theory_with_negatives_what_is_theory'],
        default='aging_theory_with_negatives_what_is_theory',
        help='Type of system prompt to use (default: aging_theory_with_negatives_what_is_theory)'
    )
    
    parser.add_argument(
        '--template',
        type=str,
        help='Name of query template to use'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available query templates'
    )
    
    parser.add_argument(
        '--output-file', '-o',
        type=str,
        help='Specify output file path for saving results'
    )
    
    parser.add_argument(
        '--no-save',
        action='store_true',
        help='Do not save results to a file'
    )
    
    args = parser.parse_args()
    
    # Create the LLM system
    try:
        llm_system = PaperLLMSystem(
            papers_dir=Path(args.papers_dir),
            negatives_dir=Path(args.negatives_dir),
            model=args.model,
            prompt_type=args.prompt_type
        )
    except Exception as e:
        print(f"Error initializing LLM system: {e}")
        return 1
    
    # List templates if requested
    if args.list_templates:
        print("\n" + "="*80)
        print("Available Query Templates")
        print("="*80)
        for name, template in llm_system.query_templates.items():
            print(f"\n📋 {name}:")
            print("-" * 80)
            print(template.strip())
            print()
        return 0
    
    # Run interactive mode
    if args.interactive:
        llm_system.interactive_mode(save_output=not args.no_save)
        return 0
    
    # Run single query
    if args.query or args.template:
        query = args.query or ""
        response = llm_system.query(
            user_message=query,
            template_name=args.template,
            save_output=not args.no_save,
            output_file=args.output_file
        )
        print("\n" + "="*80)
        print("LLM Response")
        print("="*80)
        print(response)
        print("="*80)
        return 0
    
    # No action specified, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
