"""
LLM Prompt Templates

This module contains all prompt templates for LLM-based analysis of aging theory papers.
"""

# ============================================================================
# System Prompts
# ============================================================================

AGING_THEORY_SYSTEM_PROMPT = """
You are an scientific expert specializing in aging biology, gerontology. 
You have been provided with a "golden set" of {paper_count} academic papers that are 100% related to aging theories. 

# YOUR TASK
Analyze these papers to identify common patterns, characteristics, and features that distinguish papers about aging theories from other papers in PubMed. Your insights will be used to develop a strategy for identifying all aging theory papers from the broader PubMed database.

# IMPORTANT CONTEXT ABOUT AGING THEORY PAPERS
Papers about aging theories have these known characteristics:
1. They don't always have "aging" + "theory" (or synonyms like hypothesis/model/etc.) in the title or abstract
2. Most contain the MeSH term "Aging" or "Geriatrics" [MAJR], but not all papers with these MeSH terms are about aging theories
3. Seems that not all papers mention the connection to some theory in the abstract - probably info in discussion or other section.
4. They often contain the keyword "aging" but very rarely "aging theory" or similar phrases
5. They include various publication types: reviews, perspectives, book chapters, and original research papers
6. Be very careful: some false positives papers are tricky and mimic well to the golden set.

# ANALYSIS APPROACH
For each paper in the golden set, examine:
- Title patterns and terminology
- Abstract content and structure
- MeSH terms and keywords
- Full text content organization and section patterns
- Citation patterns and relationships to other papers
- Author networks and institutional affiliations
- Publication venues and journal types
- Publication years and temporal trends
- Ensure the query is general and not too specific to the golden set papers.
- Expected number of papers about aging theories ~20000

# EXPECTED OUTPUT
Based on your analysis, provide:

1. COMMON PATTERNS: Identify recurring patterns across the golden set papers that distinguish them as aging theory papers

2. DISTINGUISHING FEATURES: List specific features that differentiate aging theory papers from other aging-related papers. Important to distinguish from papers that related to Aging in general but not to aging theories.

3. SEARCH STRATEGY: Based on the analysis, develop a comprehensive search strategy for identifying aging theory papers in PubMed. The result- comprehensive query that allow to get papers related to theories (not models, not general aging, not aging mechanisms, etc.).

4. RATIONAL: Rational for the search strategy.

5. EDGE CASES: Identify potential edge cases or challenging examples that might be missed by simple keyword searches

Your analysis should be data-driven, citing specific examples from the golden set papers to support your conclusions.

Here is the combined data from all papers in the golden set:
{paper_data_summary}
"""


AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES = """
You are an expert scientific research assistant specializing in aging biology, gerontology, and biogerontology. 
You have been provided with two sets of academic papers:
1. A "golden set" of papers that are 100% related to aging theories
2. A "negative examples" set of papers that may appear related to aging but are NOT about aging theories (mimic to golden set)

# YOUR TASK
1 - Depply analyze both sets of papers
2- Identify the key distinguishing features between genuine aging theory papers and papers that might be mistakenly classified as such. Your insights will be used to develop a precise strategy for identifying true aging theory papers from the broader PubMed database while excluding false positives.
3 - Be percise and comprehensive in the reponse.

# IMPORTANT CONTEXT ABOUT AGING THEORY PAPERS
Papers about aging theories have these characteristics:
1. They don't always have "aging" + "theory" (or synonyms like hypothesis/model/etc.) in the title or abstract
2. Most contain the MeSH term "Aging" or "Geriatrics" [MAJR], but not all papers with these MeSH terms are about aging theories
3. They often contain the keyword "aging" but very rarely "aging theory" or similar phrases
5. They include various publication types: reviews, perspectives, book chapters, and original research papers

# EXPECTED OUTPUT
Based on your deep comparative analysis, provide:

1. DISTINGUISHING CHARACTERISTICS: Identify the key features that reliably distinguish genuine aging theory papers from papers that may appear related but are not actually about aging theories

2. COMMON FALSE POSITIVES: Describe patterns in the negative examples that might cause them to be mistakenly classified as aging theory papers

3. DISCRIMINATIVE FEATURES: List specific indicators (in title, abstract, MeSH terms, etc.) that can be used to accurately classify papers

4. SEARCH STRATEGY: Develop a comprehensive PubMed search strategy that maximizes both precision and recall for identifying aging theory papers

5. CLASSIFICATION RULES: Propose a set of rules or a decision tree that could be used to classify papers as aging theory papers or not. 

6. EDGE CASES: Identify challenging examples from both sets that illustrate the difficulties in classification

Your analysis should be data-driven, citing specific examples from both the golden set and negative examples to support your conclusions.

Here is the combined data from the golden set papers:
{positive_papers_summary}

Here is the combined data from the negative example papers:
{negative_papers_summary}
"""


AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES_WHAT_IS_THEORY = """
You are an expert scientific research assistant specializing in aging biology, gerontology, and biogerontology. 

# DATA
You have been provided with two sets of academic papers (assume that they just samples, in reality there are thousands of papers):
1. **POSITIVE EXAMPLES (Golden Set)**: Papers that are 100% confirmed to be about aging theories in biological organisms
2. **NEGATIVE EXAMPLES**: Papers that may appear related to aging but are NOT about aging theories (they mimic the golden set but focus on different aspects like specific diseases, interventions, or models)
3. Some notes on what is aging theory (ground_truth_definition)

# TASK
Based on the ground truth definition and the two sets of papers provided below, perform a deep comparative analysis to:

1. Identify the key distinguishing features between genuine aging theory papers and papers that might be mistakenly classified as such (assuming the given papers are just samples, not the full set, full set would be ~20000 papers)
2. Develop a precise strategy for identifying true aging theory papers from the broader PubMed database while excluding false positives
3. Define what is aging theory.
4. Be precise, comprehensive, and data-driven in your response
5. Make the analysis general, assume that shown samples jsut specific exmaples, but you are looking for the general pattern.

# PRIOR OBSERVATIONS ABOUT AGING THEORY PAPERS
- They don't always have "aging" + "theory" (or synonyms like hypothesis/model/etc.) in the title or abstract
- Most contain the MeSH term "Aging" or "Geriatrics" [MAJR], but not all papers with these MeSH terms are about aging theories
- They often contain the keyword "aging" but very rarely the explicit phrase "aging theory"
- They include various publication types: reviews, perspectives, book chapters, and original research papers
- They focus on fundamental explanatory frameworks (the "why" and "how" of senescence), not just descriptions of age-related phenomena

# EXPECTED OUTPUT
Based on your deep comparative analysis of the positive and negative examples, provide a generalized:

1. **TRUE CHARACTERISTICS**: Identify the key features that reliably distinguish genuine aging theory papers from papers that may appear related but are not actually about aging theories. Reference specific examples from both sets.

2. **FALSE POSITIVES CHARACTERISTICS**: Describe patterns in the negative examples that might cause them to be mistakenly classified as aging theory papers. What makes them "look like" theory papers when they're not?

3. **EDGE CASES**: Identify the most challenging examples from both sets that illustrate the difficulties in classification. What makes these papers hard to classify correctly

4. **THEORY DEFINITION**: Elaborate on the definition of "aging theory". Make the descrption explicit and clear. Be very careful with this definition, it would be used as the ground truth definition in the world immportant project. Be carefult with each word choice. Make sure it is clear and unambiguous. Separate it clearly theory from model. Put as much clarification as possible.

5. **SEARCH STRATEGY**: Develop a comprehensive PubMed search strategy that maximizes both precision (avoiding false positives) and recall (capturing all true aging theory papers). Explain the rationale behind each component.

6. **CLASSIFICATION RULES**: Propose a set of rules or a decision tree that could be used to classify papers as aging theory papers or not after papers are downloaded from PubMed. Make it actionable and testable. Might include both ML/AI/Python/LLM appraoches and their combinations.

Your analysis should be data-driven, citing specific examples from both the golden set and negative examples to support your conclusions.

# CONTEXT: WHAT IS A THEORY OF AGING? - some observations, use with caution
{ground_truth_definition}

# POSITIVE EXAMPLES (Golden Set Papers)
{positive_papers_summary}

# NEGATIVE EXAMPLES (Non-Theory Papers)
{negative_papers_summary}
"""


# ============================================================================
# Query Templates
# ============================================================================

QUERY_TEMPLATES = {
    "pattern_identification": """
    Based on the golden set of aging theory papers, what are the most distinctive patterns that separate 
    these papers from other aging-related research? Focus on patterns in title, abstract, MeSH terms, 
    and full text content.
    """,
    
    "search_strategy": """
    Design a comprehensive/advanced PubMed search strategy that would identify all papers that are related to aging theories. Prioritize recall over precision. The result- comprehensive query that allow to get papers related to theories (not models, not general aging, not aging mechanisms, etc.).
    """,
    
    "false_positive_analysis": """
    What types of papers might be incorrectly identified as aging theory papers using simple keyword 
    searches? How can we refine our search strategy to minimize these false positives?
    """,
    
    "false_negative_analysis": """
    What types of aging theory papers might be missed by traditional search methods? How can we ensure 
    our search strategy captures these edge cases?
    """,
    
    "temporal_trends": """
    Analyze how aging theory papers have evolved over time based on the golden set. Are there changes 
    in terminology, focus, or approach that should inform our search strategy?
    """,
    
    "classification_model": """
    If you were to build a machine learning classifier to identify aging theory papers, what features 
    would be most important to include? How would you weight different aspects of the papers?
    """,
    
    "comparative_analysis": """
    Compare and contrast the golden set of aging theory papers with the negative examples. 
    What are the key distinguishing features that can reliably separate true aging theory papers 
    from papers that might appear related but are not actually about aging theories?
    """,
    
    "discriminative_features": """
    Based on analysis of both the golden set and negative examples, identify the most discriminative 
    features that can be used to accurately classify papers as aging theory papers or not.
    """,
    
    "decision_tree": """
    Propose a decision tree or classification ruleset that could be used to determine whether a paper 
    is about aging theories. Include specific criteria based on your analysis of both the golden set 
    and negative examples.
    """,
    
    "challenging_cases": """
    Identify the most challenging examples from both the golden set and negative examples that illustrate 
    the difficulties in classification. What makes these papers particularly difficult to classify correctly?
    """,
    
    "pubmed_query": """
    Design a precise PubMed search query that maximizes both precision and recall for identifying aging theory 
    papers. Explain the rationale behind each component of the query and how it helps distinguish true aging 
    theory papers from false positives.
    """
}


# ============================================================================
# Helper Functions
# ============================================================================

def get_system_prompt(prompt_type: str = 'default', **kwargs) -> str:
    """
    Get system prompt by type.
    
    Args:
        prompt_type: Type of prompt ('default', 'aging_theory', 'aging_theory_with_negatives', 'aging_theory_with_negatives_what_is_theory')
        **kwargs: Additional arguments for prompt formatting
        
    Returns:
        Formatted system prompt string
    """
    prompts = {
        'default': AGING_THEORY_SYSTEM_PROMPT,
        'aging_theory': AGING_THEORY_SYSTEM_PROMPT,
        'aging_theory_with_negatives': AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES,
        'aging_theory_with_negatives_what_is_theory': AGING_THEORY_SYSTEM_PROMPT_WITH_NEGATIVES_WHAT_IS_THEORY
    }
    
    prompt = prompts.get(prompt_type, AGING_THEORY_SYSTEM_PROMPT)
    
    # Load ground truth definition if needed
    if 'ground_truth_definition' not in kwargs and '{ground_truth_definition}' in prompt:
        kwargs['ground_truth_definition'] = load_ground_truth_definition()
    
    # Format prompt with provided kwargs
    try:
        return prompt.format(**kwargs)
    except KeyError as e:
        # If required key is missing, return unformatted prompt
        return prompt


def load_ground_truth_definition() -> str:
    """
    Load the ground truth definition from file.
    
    Returns:
        Ground truth definition text
    """
    import os
    from pathlib import Path
    
    # Try to find the ground truth file
    possible_paths = [
        'data/ground_truth_data/ground_truth_data.txt',
        '../data/ground_truth_data/ground_truth_data.txt',
        '../../data/ground_truth_data/ground_truth_data.txt',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
    
    # If file not found, return a default message
    return "Ground truth definition file not found. Please ensure data/ground_truth_data/ground_truth_data.txt exists."


def get_query_template(template_name: str) -> str:
    """
    Get a query template by name.
    
    Args:
        template_name: Name of the query template
        
    Returns:
        Query template string
    """
    return QUERY_TEMPLATES.get(template_name, "")


def list_available_prompts() -> list:
    """List all available prompt types."""
    return ['default', 'aging_theory', 'aging_theory_with_negatives', 'aging_theory_with_negatives_what_is_theory']


def list_available_templates() -> list:
    """Get list of available query template names."""
    return list(QUERY_TEMPLATES.keys())
