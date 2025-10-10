"""
Centralized Configuration Settings

This module contains all configuration settings for the paper patterns project.
"""
import os
from pathlib import Path
from typing import Optional


# ============================================================================
# Project Paths
# ============================================================================

# Root directory of the project
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / 'data'
PAPER_DATA_DIR = DATA_DIR / 'paper_data'
PAPERS_DIR = PAPER_DATA_DIR / 'papers'
NEGATIVE_EXAMPLES_DIR = DATA_DIR / 'negative_examples'
NEGATIVE_PAPERS_DIR = NEGATIVE_EXAMPLES_DIR / 'papers'
FULL_TEXTS_DIR = DATA_DIR / 'paper_full_texts'
ANALYSIS_RESULTS_DIR = DATA_DIR / 'paper_data' / 'analysis'
LLM_RESULTS_DIR = DATA_DIR / 'llm_analysis_results'
FINAL_QUERY_RESULTS_DIR = DATA_DIR / 'final_query_results'

# Cache and log files
CACHE_FILE = PAPER_DATA_DIR / 'processed_dois.json'
COLLECTION_LOG_FILE = PAPER_DATA_DIR / 'collection_log.txt'
NEGATIVE_CACHE_FILE = NEGATIVE_EXAMPLES_DIR / 'processed_dois.json'
NEGATIVE_LOG_FILE = NEGATIVE_EXAMPLES_DIR / 'collection_log.txt'


# ============================================================================
# NCBI/Entrez API Configuration
# ============================================================================

class NCBIConfig:
    """NCBI API configuration settings."""
    
    # API credentials (should be set via environment variables or .env file)
    EMAIL: Optional[str] = os.getenv('NCBI_EMAIL', 'diana.z@insilicomedicine.com')
    API_KEY: Optional[str] = os.getenv('NCBI_API_KEY', '9f5d0d5238d7eb65e0526c84d79a5b945d08')
    
    # Rate limiting
    MAX_REQUESTS_PER_SEC = 9  # NCBI allows 10/sec with API key, use 9 to be safe
    MAX_REQUESTS_PER_SEC_NO_KEY = 3  # Without API key, use 3/sec
    
    # Retry settings
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 2  # seconds
    
    # Database names
    DB_PUBMED = "pubmed"
    DB_PMC = "pmc"
    
    @classmethod
    def get_rate_limit(cls) -> int:
        """Get appropriate rate limit based on whether API key is set."""
        return cls.MAX_REQUESTS_PER_SEC if cls.API_KEY else cls.MAX_REQUESTS_PER_SEC_NO_KEY


# ============================================================================
# Download/Collection Configuration
# ============================================================================

class DownloadConfig:
    """Configuration for downloading and collecting papers."""
    
    # Parallel processing
    BATCH_SIZE = 20
    NUM_THREADS = 2
    
    # Checkpointing
    CHECKPOINT_INTERVAL = 32  # Save progress every N batches
    
    # Search limits
    MAX_RESULTS = 50000
    
    # Timeouts
    REQUEST_TIMEOUT = 30  # seconds


# ============================================================================
# LLM Configuration
# ============================================================================

class LLMConfig:
    """Configuration for LLM system."""
    
    # OpenAI settings
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    MODEL = "gpt-5"
    MAX_TOKENS = 128000  # Context window size
    TEMPERATURE = 0.6
    
    # Prompt types
    PROMPT_TYPE_DEFAULT = 'default'
    PROMPT_TYPE_AGING_THEORY = 'aging_theory'
    PROMPT_TYPE_AGING_WITH_NEGATIVES = 'aging_theory_with_negatives'


# ============================================================================
# Analysis Configuration
# ============================================================================

class AnalysisConfig:
    """Configuration for paper analysis."""
    
    # Clustering
    N_CLUSTERS = 5
    
    # Visualization
    FIGURE_DPI = 300
    FIGURE_SIZE = (12, 8)


# ============================================================================
# Logging Configuration
# ============================================================================

class LogConfig:
    """Logging configuration."""
    
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'


# ============================================================================
# Directory Initialization
# ============================================================================

def initialize_directories():
    """Create all necessary directories if they don't exist."""
    directories = [
        DATA_DIR,
        PAPER_DATA_DIR,
        PAPERS_DIR,
        NEGATIVE_EXAMPLES_DIR,
        NEGATIVE_PAPERS_DIR,
        FULL_TEXTS_DIR,
        ANALYSIS_RESULTS_DIR,
        LLM_RESULTS_DIR,
        FINAL_QUERY_RESULTS_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# Initialize directories when module is imported
initialize_directories()
