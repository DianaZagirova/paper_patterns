#!/usr/bin/env python3
"""
Paper LLM System

This script creates an LLM system based on OpenAI's GPT-4.1 model that processes
combined JSON data from academic papers and allows users to query the data.
"""
import os
import json
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

import openai
from dotenv import load_dotenv

# Import the specialized aging theory prompts
from aging_theory_prompt import AGING_THEORY_SYSTEM_PROMPT, AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES, QUERY_TEMPLATES

# Load environment variables from .env file (for API keys)
load_dotenv()

# Configuration
PAPERS_DIR = './paper_data/papers/'
NEGATIVES_PAPERS_DIR = './negative_examples/papers/'
RESULTS_DIR = './llm_analysis_results/'  # Directory to save results
MAX_TOKENS = 128000  # GPT-4.1 context window size
OPENAI_MODEL = "gpt-5"  # OpenAI model to use
TEMPERATURE = 0.6  # Default temperature for API calls

# Create results directory if it doesn't exist
os.makedirs(RESULTS_DIR, exist_ok=True)

class PaperLLMSystem:
    """
    A system that uses OpenAI's GPT-4.1 to analyze and answer questions about academic papers.
    """
    
    def __init__(self, papers_dir: str = PAPERS_DIR, model: str = OPENAI_MODEL, prompt_type: str = 'aging_theory_with_negatives', negatives_dir: str = NEGATIVES_PAPERS_DIR):
        """
        Initialize the Paper LLM System.
        
        Args:
            papers_dir: Directory containing positive paper JSON files
            model: OpenAI model to use
            prompt_type: Type of system prompt to use ('default', 'aging_theory', or 'aging_theory_with_negatives')
            negatives_dir: Directory containing negative example paper JSON files
        """
        self.papers_dir = papers_dir
        self.negatives_dir = negatives_dir
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
        
        # Select the appropriate system prompt template based on prompt_type
        if prompt_type == 'aging_theory':
            self.system_prompt_template = AGING_THEORY_SYSTEM_PROMPT
        elif prompt_type == 'aging_theory_with_negatives':
            self.system_prompt_template = AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES
        else:
            self.system_prompt_template = self.default_system_prompt
        
        # Store query templates for easy access
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
                    # Mark as positive example (golden set)
                    paper_data['is_positive_example'] = True
                    papers.append(paper_data)
            except Exception as e:
                print(f"Error loading {paper_file}: {e}")
        
        print(f"Loaded {len(papers)} positive papers from {self.papers_dir}")
        return papers

    def load_negative_examples(self) -> List[Dict[str, Any]]:
        """
        Load all negative example paper data from JSON files in the negatives directory.
        
        Returns:
            List of negative example paper data dictionaries
        """
        papers = []
        paper_files = list(Path(self.negatives_dir).glob('*.json'))
        
        if not paper_files:
            print(f"Warning: No negative example JSON files found in {self.negatives_dir}")
            return papers
        
        for paper_file in paper_files:
            try:
                with open(paper_file, 'r', encoding='utf-8') as f:
                    paper_data = json.load(f)
                    # Ensure it's marked as negative example
                    paper_data['is_negative_example'] = True
                    papers.append(paper_data)
            except Exception as e:
                print(f"Error loading negative example {paper_file}: {e}")
        
        print(f"Loaded {len(papers)} negative example papers from {self.negatives_dir}")
        return papers

    def save_results(self, response: str, query: str, template_name: Optional[str] = None, output_file: Optional[str] = None) -> str:
        """
        Save the LLM response to a file with timestamp, model name, and temperature information.
        
        Args:
            response: The response from the LLM
            query: The query that was sent to the LLM
            template_name: Optional name of the template that was used
            output_file: Optional specific output file path
            
        Returns:
            Path to the saved file
        """
        # Generate timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Determine temperature used
        temperature = TEMPERATURE if "5" not in self.model and "o" not in self.model else 1.0
        
        # Create filename if not provided
        if not output_file:
            # Create a safe filename
            if template_name:
                filename = f"results_{self.model}_{template_name}_{timestamp}_temp{temperature}.txt"
            else:
                # Use the first few words of the query to create a filename
                query_words = query.split()[:3]
                query_part = "_".join(query_words) if query_words else "custom_query"
                filename = f"results_{self.model}_{query_part}_{timestamp}_temp{temperature}.txt"
            
            output_file = os.path.join(RESULTS_DIR, filename)
        
        # Create the content with metadata
        content = f"""# LLM Analysis Results

## Metadata
- Timestamp: {timestamp}
- Model: {self.model}
- Temperature: {temperature}
- Prompt Type: {self.prompt_type}

## Query
{query}

## Template Used
{template_name if template_name else 'None'}

## Response
{response}
"""
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\nResults saved to: {output_file}")
        return output_file

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

    def prepare_system_prompt(self, papers: List[Dict[str, Any]], negative_papers: List[Dict[str, Any]] = None) -> str:
        """
        Prepare the system prompt with paper data.
        
        Args:
            papers: List of positive paper data dictionaries
            negative_papers: Optional list of negative example paper data dictionaries
            
        Returns:
            Formatted system prompt
        """
        paper_data_summary = self.create_paper_data_summary(papers)
        
        # If using the prompt with negatives and negative papers are provided
        if self.prompt_type == 'aging_theory_with_negatives' and negative_papers:
            negative_papers_summary = self.create_paper_data_summary(negative_papers)
            
            # Format the system prompt template with both positive and negative examples
            system_prompt = self.system_prompt_template.format(
                paper_count=len(papers),
                positive_papers_summary=paper_data_summary,
                negative_papers_summary=negative_papers_summary
            )
        else:
            # Format the standard system prompt template
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
    
    def query(self, user_message: str, template_name: str = None, save_output: bool = True, output_file: str = None) -> str:
        """
        Query the LLM with user message and paper data.
        
        Args:
            user_message: User's query about the papers
            template_name: Optional name of a template to use
            save_output: Whether to save the output to a file
            output_file: Optional specific output file path
            
        Returns:
            LLM response
        """
        if not self.api_key:
            return "Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
        
        try:
            # Load positive paper data (golden set)
            papers = self.load_paper_data()
            
            # If using the prompt with negatives, also load negative examples
            negative_papers = None
            if self.prompt_type == 'aging_theory_with_negatives':
                negative_papers = self.load_negative_examples()
            
            # Prepare system prompt with paper data
            system_prompt = self.prepare_system_prompt(papers, negative_papers)
            
            # Store the original query for saving
            original_query = user_message
            
            # If a template is specified, use it instead of the user message
            if template_name:
                if template_name in self.query_templates:
                    user_message = self.query_templates[template_name]
                else:
                    return f"Template '{template_name}' not found. Available templates: {', '.join(self.query_templates.keys())}"
            
            # Call OpenAI API
            temperature = TEMPERATURE if "5" not in self.model and "o" not in self.model else 1
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=temperature, 
            )
            
            response_text = response.choices[0].message.content
            
            # Save results to file if requested
            if save_output:
                self.save_results(response_text, user_message, template_name, output_file)
            
            return response_text
            
        except Exception as e:
            return f"Error querying OpenAI API: {str(e)}"

    def interactive_mode(self, save_output: bool = True):
        """
        Run the system in interactive mode, allowing users to input queries.
        
        Args:
            save_output: Whether to save responses to files
        """
        print("\n===== Paper LLM System =====")
        print(f"Using model: {self.model}")
        print(f"Using prompt type: {self.prompt_type}")
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'templates' to see available query templates.")
        print("Type 'template:NAME' to use a specific template.")
        print("Type 'save:on' or 'save:off' to toggle saving results.")
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
                
            if user_input.lower() == 'save:on':
                save_output = True
                print("Saving results is now ON")
                continue
                
            if user_input.lower() == 'save:off':
                save_output = False
                print("Saving results is now OFF")
                continue
                
            template_name = None
            output_file = None
            
            if user_input.lower().startswith('template:'):
                template_name = user_input[9:].strip()
                print(f"\nUsing template: {template_name}")
                
            print("\nProcessing your query...\n")
            response = self.query(user_input, template_name, save_output, output_file)
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
    parser.add_argument('--prompt-type', type=str, choices=['default', 'aging_theory', 'aging_theory_with_negatives'], 
                        default='aging_theory_with_negatives', help='Type of system prompt to use')
    parser.add_argument('--template', type=str, help='Name of query template to use')
    parser.add_argument('--list-templates', action='store_true', help='List available query templates')
    parser.add_argument('--output-file', '-o', type=str, help='Specify output file path for saving results')
    parser.add_argument('--no-save', action='store_true', help='Do not save results to a file')
    
    args = parser.parse_args()
    
    # Create the LLM system
    llm_system = PaperLLMSystem(papers_dir=args.papers_dir, model=args.model, prompt_type=args.prompt_type)
    
    if args.list_templates:
        print("\nAvailable query templates:")
        for name, template in llm_system.query_templates.items():
            print(f"\n{name}:\n{template.strip()}\n")
        return
    
    if args.interactive:
        llm_system.interactive_mode(not args.no_save)
    elif args.query:
        response = llm_system.query(args.query, args.template, not args.no_save, args.output_file)
        print(response)
    elif args.template:
        # If only template is specified without a query, use the template as the query
        response = llm_system.query("", args.template, not args.no_save, args.output_file)
        print(response)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
