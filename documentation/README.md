# Academic Paper Data Collector

This system collects comprehensive data on academic papers based on DOIs. It extracts various information including title, abstract, full text (by section), MESH terms, keywords, citation counts, authors, institutions, publication year, and journal details.

## Features

- **Comprehensive Data Collection**: Extracts detailed information from multiple sources
- **Incremental Processing**: Only processes new DOIs when the script is rerun
- **Multithreaded Operation**: Efficiently processes multiple DOIs in parallel
- **Error Handling**: Robust error handling with detailed logging
- **Data Storage**: Stores paper data in structured JSON format

## Setup

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Configure your email in `paper_data_collector.py`:
   ```python
   Entrez.email = "your.email@example.com"  # Replace with your email
   ```

3. (Optional) Add your NCBI API key if you have one:
   ```python
   Entrez.api_key = "your_api_key"  # Uncomment and replace with your API key
   ```

## Usage

1. Add your DOIs to `doi_list.py`. The system accepts DOIs in various formats:
   - With URL prefix: `https://doi.org/10.1038/s41576-018-0004-3`
   - Without URL prefix: `10.1038/s41576-018-0004-3`

2. Run the data collection script:
   ```
   python paper_data_collector.py
   ```

3. The collected data will be stored in the `paper_data/papers/` directory as JSON files.

## Data Structure

Each paper is stored as a JSON file with the following structure:

```json
{
  "doi": "10.1038/s41576-018-0004-3",
  "title": "Paper Title",
  "abstract": "Paper abstract text...",
  "full_text": {
    "Introduction": "Section text...",
    "Methods": "Section text...",
    "Results": "Section text...",
    "Discussion": "Section text..."
  },
  "mesh_terms": ["Term 1", "Term 2"],
  "keywords": ["Keyword 1", "Keyword 2"],
  "citation_count": 42,
  "authors": [
    {
      "name": "John Smith",
      "affiliations": ["University of Example"]
    }
  ],
  "year": 2023,
  "journal": "Journal Name",
  "pmid": "12345678",
  "pmcid": "PMC9876543",
  "collection_date": "2025-10-09"
}
```

## Adding New DOIs

Simply add new DOIs to the `doi_list.py` file and run the script again. The system will automatically detect which DOIs have already been processed and only collect data for the new ones.

## Troubleshooting

- Check the `paper_data/collection_log.txt` file for detailed logs of the collection process
- Ensure you have a stable internet connection
- If you're processing many DOIs, consider increasing the wait time between API calls to avoid rate limiting
