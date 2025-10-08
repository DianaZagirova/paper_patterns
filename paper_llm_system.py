#!/usr/bin/env python3
"""
Paper LLM System

This script creates an LLM system based on OpenAI's GPT-4.1 model that processes
combined JSON data from academic papers and allows users to query the data.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import openai
from dotenv import load_dotenv

# Import the specialized aging theory prompt
from aging_theory_prompt import AGING_THEORY_SYSTEM_PROMPT, QUERY_TEMPLATES

# Load environment variables from .env file (for API keys)
load_dotenv()

# Configuration
PAPERS_DIR = './paper_data/papers/'
MAX_TOKENS = 128000  # GPT-4.1 context window size
OPENAI_MODEL = "gpt-5"  # OpenAI model to use

class PaperLLMSystem:
    """
    A system that uses OpenAI's GPT-4.1 to analyze and answer questions about academic papers.
    """
    
    def __init__(self, papers_dir: str = PAPERS_DIR, model: str = OPENAI_MODEL, prompt_type: str = 'aging_theory'):
        """
        Initialize the Paper LLM System.
        
        Args:
            papers_dir: Directory containing paper JSON files
            model: OpenAI model to use
            prompt_type: Type of system prompt to use ('default' or 'aging_theory')
        """
        self.papers_dir = papers_dir
        self.model = model
        self.prompt_type = prompt_type
        self.api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            print("Warning: OPENAI_API_KEY not found in environment variables.")
            print("Please set your OpenAI API key using:")
            print("  export OPENAI_API_KEY='your-api-key'")
            print("or create a .env file with OPENAI_API_KEY='your-api-key'")
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # Default system prompt template
        self.default_system_prompt = """
You are an expert academic research assistant with deep knowledge of scientific literature.
You have been provided with data from {paper_count} academic papers related to aging research.
Your task is to analyze this data and provide insightful answers to the user's questions.

The data for each paper includes:
- Title, abstract, and full text (organized by sections)
- MESH terms and keywords
- Citation counts
- Authors and their affiliations
- Publication year and journal information

When responding:
1. Be precise and scientific in your language
2. Cite specific papers when making claims (using DOI or title)
3. Acknowledge limitations in the data when appropriate
4. Provide balanced perspectives when there are conflicting findings
5. Organize complex responses with clear headings and structure

Here is the combined data from all papers:
{paper_data_summary}
"""
        
        # Use the specialized aging theory prompt as the default
        self.system_prompt_template = AGING_THEORY_SYSTEM_PROMPT
        self.query_templates = QUERY_TEMPLATES

    def load_paper_data(self) -> List[Dict[str, Any]]:
        """
        Load all paper data from JSON files in the papers directory.
        
        Returns:
            List of paper data dictionaries
        """
        papers = []
        paper_files = list(Path(self.papers_dir).glob('*.json'))
        
        if not paper_files:
            raise FileNotFoundError(f"No JSON files found in {self.papers_dir}")
        
        for paper_file in paper_files:
            try:
                with open(paper_file, 'r', encoding='utf-8') as f:
                    paper_data = json.load(f)
                    papers.append(paper_data)
            except Exception as e:
                print(f"Error loading {paper_file}: {e}")
        
        print(f"Loaded {len(papers)} papers from {self.papers_dir}")
        return papers

    def create_paper_data_summary(self, papers: List[Dict[str, Any]]) -> str:
        """
        Create a summary of paper data suitable for inclusion in the system prompt.
        This function handles token limits by summarizing papers appropriately.
        
        Args:
            papers: List of paper data dictionaries
            
        Returns:
            String summary of paper data
        """
        # Start with basic metadata for all papers
        summary = []
        
        for i, paper in enumerate(papers, 1):
            paper_summary = {
                "index": i,
                "doi": paper.get("doi", "Unknown DOI"),
                "title": paper.get("title", "Unknown Title"),
                "authors": paper.get("authors", []),
                "year": paper.get("year", "Unknown Year"),
                "journal": paper.get("journal", "Unknown Journal"),
                "citation_count": paper.get("citation_count", "Unknown"),
                "abstract": paper.get("abstract", "No abstract available"),
                "keywords": paper.get("keywords", []),
                "mesh_terms": paper.get("mesh_terms", [])
            }
            
            # Add a truncated version of full text sections
            if "full_text" in paper and isinstance(paper["full_text"], dict):
                full_text_summary = {}
                for section, content in paper["full_text"].items():
                    # Truncate long sections to save tokens
                    if len(content) > 1000:
                        full_text_summary[section] = content[:1000] + "... [truncated]"
                    else:
                        full_text_summary[section] = content
                paper_summary["full_text"] = full_text_summary
            
            summary.append(paper_summary)
        
        # Convert to JSON string
        return json.dumps(summary, indent=2)

    def prepare_system_prompt(self, papers: List[Dict[str, Any]]) -> str:
        """
        Prepare the system prompt with paper data.
        
        Args:
            papers: List of paper data dictionaries
            
        Returns:
            Formatted system prompt
        """
        paper_data_summary = self.create_paper_data_summary(papers)
        
        # Format the system prompt template
        system_prompt = self.system_prompt_template.format(
            paper_count=len(papers),
            paper_data_summary=paper_data_summary
        )
        
        return system_prompt

    def get_template_query(self, template_name: str) -> str:
        """
        Get a predefined query template by name.
        
        Args:
            template_name: Name of the template to retrieve
            
        Returns:
            Template query string or error message if template not found
        """
        if template_name in self.query_templates:
            return self.query_templates[template_name]
        else:
            available_templates = list(self.query_templates.keys())
            return f"Template '{template_name}' not found. Available templates: {', '.join(available_templates)}"
    
    def query(self, user_message: str, template_name: str = None) -> str:
        """
        Query the LLM with user message and paper data.
        
        Args:
            user_message: User's query about the papers
            template_name: Optional name of a template to use
            
        Returns:
            LLM response
        """
        if not self.api_key:
            return "Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
        
        try:
            # Load paper data
            papers = self.load_paper_data()
            
            # Prepare system prompt with paper data
            system_prompt = self.prepare_system_prompt(papers)
            
            # If a template is specified, use it instead of the user message
            if template_name:
                if template_name in self.query_templates:
                    user_message = self.query_templates[template_name]
                else:
                    return f"Template '{template_name}' not found. Available templates: {', '.join(self.query_templates.keys())}"
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,  # Lower temperature for more focused responses
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Error querying OpenAI API: {str(e)}"

    def interactive_mode(self):
        """
        Run the system in interactive mode, allowing users to input queries.
        """
        print("\n===== Paper LLM System =====")
        print(f"Using model: {self.model}")
        print(f"Using prompt type: {self.prompt_type}")
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'templates' to see available query templates.")
        print("Type 'template:NAME' to use a specific template.")
        print("================================\n")
        
        while True:
            user_input = input("\nEnter your query: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting interactive mode.")
                break
                
            if user_input.lower() == 'templates':
                print("\nAvailable templates:")
                for name, template in self.query_templates.items():
                    print(f"\n- {name}:\n  {template.strip()[:100]}...")
                continue
                
            template_name = None
            if user_input.lower().startswith('template:'):
                template_name = user_input[9:].strip()
                print(f"\nUsing template: {template_name}")
                
            print("\nProcessing your query...\n")
            response = self.query(user_input, template_name)
            print("\n--- Response ---\n")
            print(response)
            print("\n----------------")


def main():
    """Main function to run the Paper LLM System."""
    parser = argparse.ArgumentParser(description='Paper LLM System using OpenAI GPT-4.1')
    parser.add_argument('--query', '-q', type=str, help='Query to send to the LLM system')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--papers-dir', type=str, default=PAPERS_DIR, help='Directory containing paper JSON files')
    parser.add_argument('--model', type=str, default=OPENAI_MODEL, help='OpenAI model to use')
    parser.add_argument('--prompt-type', type=str, choices=['default', 'aging_theory'], default='aging_theory',
                        help='Type of system prompt to use')
    parser.add_argument('--template', type=str, help='Name of query template to use')
    parser.add_argument('--list-templates', action='store_true', help='List available query templates')
    
    args = parser.parse_args()
    
    # Create the LLM system
    llm_system = PaperLLMSystem(papers_dir=args.papers_dir, model=args.model, prompt_type=args.prompt_type)
    
    if args.list_templates:
        print("\nAvailable query templates:")
        for name, template in llm_system.query_templates.items():
            print(f"\n{name}:\n{template.strip()}\n")
        return
    
    if args.interactive:
        llm_system.interactive_mode()
    elif args.query:
        response = llm_system.query(args.query, args.template)
        print(response)
    elif args.template:
        # If only template is specified without a query, use the template as the query
        response = llm_system.query("", args.template)
        print(response)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
