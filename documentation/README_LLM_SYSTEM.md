# Paper LLM System

A system that uses OpenAI's GPT-4.1 model to analyze and answer questions about academic papers. This system combines data from multiple academic papers and allows users to query the combined knowledge base.

## Features

- **Data Integration**: Automatically combines all paper JSON files from the papers directory
- **Interactive Mode**: Engage in a conversation with the LLM about the papers
- **Query Mode**: Send one-off queries to the LLM
- **Customizable System Prompt**: Tailor the system prompt to your specific needs
- **Token Management**: Intelligently handles token limits for large datasets

## Setup

### Prerequisites

- Python 3.7+
- OpenAI API key

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Set up your OpenAI API key:

   - Copy the `.env.template` file to `.env`:
     ```bash
     cp .env.template .env
     ```
   - Edit the `.env` file and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     ```

## Usage

### Interactive Mode

Run the system in interactive mode to have a conversation with the LLM about the papers:

```bash
python paper_llm_system.py --interactive
```

This will start an interactive session where you can ask questions about the papers and receive responses from the LLM.

### Query Mode

Send a one-off query to the LLM:

```bash
python paper_llm_system.py --query "What are the main findings about physiological dysregulation in aging?"
```

### Additional Options

- Specify a different papers directory:
  ```bash
  python paper_llm_system.py --interactive --papers-dir /path/to/papers
  ```

- Use a different OpenAI model:
  ```bash
  python paper_llm_system.py --interactive --model gpt-4.1-turbo
  ```

## Example Queries

Here are some example queries you can try:

1. **Literature Review**:
   ```
   Provide a comprehensive literature review on the role of complex systems dynamics in aging based on the papers.
   ```

2. **Compare and Contrast**:
   ```
   Compare and contrast the findings on physiological dysregulation across the different papers.
   ```

3. **Identify Gaps**:
   ```
   What are the major gaps in the research on aging based on these papers?
   ```

4. **Methodological Analysis**:
   ```
   What methodologies are commonly used to study aging in these papers, and what are their strengths and limitations?
   ```

5. **Citation Analysis**:
   ```
   Which papers are most cited, and what might explain their impact?
   ```

## Customizing the System

### Modifying the System Prompt

You can modify the system prompt template in the `paper_llm_system.py` file to better suit your needs. The template is defined in the `__init__` method of the `PaperLLMSystem` class.

### Advanced Query Capabilities

For more advanced query capabilities, you can extend the `PaperLLMSystem` class with additional methods. For example, you could add methods to:

- Filter papers by specific criteria
- Generate visualizations of the data
- Perform more sophisticated analyses

## Troubleshooting

### API Key Issues

If you encounter issues with the OpenAI API key:

1. Ensure your API key is correctly set in the `.env` file
2. Check that you have sufficient credits in your OpenAI account
3. Verify that the API key has the necessary permissions

### Token Limit Exceeded

If you encounter token limit issues:

1. The system automatically truncates long sections of text to fit within token limits
2. If you still encounter issues, you can modify the `create_paper_data_summary` method to further reduce the amount of data included in the system prompt

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
