"""
XML Parser for PMC Articles

This module provides functions to parse XML content from PubMed Central articles
and extract structured information.
"""
import xml.etree.ElementTree as ET
from typing import Optional, Dict


def extract_article_root(root: ET.Element) -> Optional[ET.Element]:
    """
    Extract the article element from XML root.
    
    Args:
        root: XML root element
        
    Returns:
        Article element or None if not found
    """
    if root.tag == 'article':
        return root
    
    article = root.find('.//article')
    if article is not None:
        return article
    
    pmc_set = root.find('.//pmc-articleset')
    if pmc_set is not None:
        return pmc_set.find('.//article')
    
    return None


def extract_metadata(article: ET.Element, pmcid: str) -> Dict[str, str]:
    """
    Extract metadata from article XML element.
    
    Args:
        article: Article XML element
        pmcid: PubMed Central ID (without PMC prefix)
        
    Returns:
        Dictionary containing article metadata
    """
    metadata = {}
    
    # Article type
    metadata['Article Type'] = article.attrib.get('article-type', 'Not specified')
    
    # DOI
    doi_elem = article.find('.//article-id[@pub-id-type="doi"]')
    metadata['DOI'] = doi_elem.text if doi_elem is not None else "DOI not available"
    
    # PubMed link
    pmid_elem = article.find('.//article-id[@pub-id-type="pmid"]')
    if pmid_elem is not None:
        metadata['PubMed Link'] = f"https://pubmed.ncbi.nlm.nih.gov/{pmid_elem.text}/"
    else:
        metadata['PubMed Link'] = "Not available"
    
    # PMC link
    metadata['PMC Link'] = f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
    
    # Journal
    journal_elem = article.find('.//journal-title')
    if journal_elem is not None:
        metadata['Journal'] = journal_elem.text
    
    # Title
    title_elem = article.find('.//article-title')
    if title_elem is not None:
        metadata['Title'] = ''.join(title_elem.itertext())
    
    # Publication year
    year_elem = article.find('.//pub-date/year')
    if year_elem is not None:
        metadata['Year Published'] = year_elem.text
    
    return metadata


def extract_abstract(article: ET.Element) -> str:
    """
    Extract abstract text from article.
    
    Args:
        article: Article XML element
        
    Returns:
        Formatted abstract text
    """
    abstract_elem = article.find('.//abstract')
    if abstract_elem is not None:
        abstract_text = ' '.join(abstract_elem.itertext())
        return f"ABSTRACT:\n{abstract_text}\n\n"
    return ""


def extract_sections(parent: ET.Element, level: int = 1) -> str:
    """
    Recursively extract text from article sections.
    
    Args:
        parent: Parent XML element
        level: Section nesting level (for header formatting)
        
    Returns:
        Formatted section text
    """
    text = ''
    
    # Section title
    title_elem = parent.find('./title')
    if title_elem is not None:
        title_text = ''.join(title_elem.itertext()).strip()
        text += f"{' #' * level} {title_text}\n"
    
    # Paragraphs
    for paragraph in parent.findall('./p'):
        text += ''.join(paragraph.itertext()).strip() + '\n\n'
    
    # Nested sections
    for subsection in parent.findall('./sec'):
        text += extract_sections(subsection, level=level + 1)
    
    return text


def extract_body(article: ET.Element) -> str:
    """
    Extract main body text from article.
    
    Args:
        article: Article XML element
        
    Returns:
        Formatted body text
    """
    body_elem = article.find('.//body')
    if body_elem is None:
        return ""
    
    text = ''
    
    # Extract sections
    for section in body_elem.findall('./sec'):
        text += extract_sections(section, level=1)
    
    # Extract top-level paragraphs
    for paragraph in body_elem.findall('./p'):
        text += ''.join(paragraph.itertext()).strip() + '\n\n'
    
    return text


def extract_tables(article: ET.Element) -> str:
    """
    Extract table captions and content from article.
    
    Args:
        article: Article XML element
        
    Returns:
        Formatted table text
    """
    tables = article.findall('.//table-wrap')
    if not tables:
        return ""
    
    text = "TABLES:\n"
    for idx, table in enumerate(tables, 1):
        caption_elem = table.find('.//caption')
        if caption_elem is not None:
            text += f"Table {idx}: {' '.join(caption_elem.itertext())}\n"
        
        table_elem = table.find('.//table')
        if table_elem is not None:
            text += ' '.join(table_elem.itertext()) + "\n\n"
    
    return text


def extract_figures(article: ET.Element) -> str:
    """
    Extract figure captions from article.
    
    Args:
        article: Article XML element
        
    Returns:
        Formatted figure captions
    """
    figures = article.findall('.//fig')
    if not figures:
        return ""
    
    text = "FIGURES:\n"
    for idx, figure in enumerate(figures, 1):
        caption_elem = figure.find('.//caption')
        if caption_elem is not None:
            text += f"Figure {idx}: {' '.join(caption_elem.itertext())}\n\n"
    
    return text


def extract_references(article: ET.Element) -> str:
    """
    Extract references from article.
    
    Args:
        article: Article XML element
        
    Returns:
        Formatted references
    """
    refs = article.findall('.//ref-list//ref')
    if not refs:
        return ""
    
    text = "REFERENCES:\n"
    for idx, ref in enumerate(refs, 1):
        ref_text = ' '.join(ref.itertext())
        text += f"{idx}. {ref_text}\n"
    
    return text


def parse_pmc_xml(xml_content: str, pmcid: str) -> Optional[Dict[str, any]]:
    """
    Parse PMC XML content and extract all information.
    
    Args:
        xml_content: Raw XML content as string
        pmcid: PubMed Central ID (without PMC prefix)
        
    Returns:
        Dictionary containing metadata and full text, or None if parsing failed
    """
    try:
        # Parse XML
        if isinstance(xml_content, bytes):
            xml_content = xml_content.decode("utf-8")
        
        root = ET.fromstring(xml_content)
    except Exception as e:
        print(f"Failed to parse XML for PMCID {pmcid}: {str(e)}")
        return None
    
    # Extract article element
    article = extract_article_root(root)
    if article is None:
        print(f"No <article> tag found in XML for PMCID {pmcid}")
        return None
    
    # Build document structure
    document = {
        'metadata': extract_metadata(article, pmcid),
        'page_content': ''
    }
    
    # Assemble full text content
    document['page_content'] += extract_abstract(article)
    document['page_content'] += extract_body(article)
    document['page_content'] += extract_tables(article)
    document['page_content'] += extract_figures(article)
    document['page_content'] += extract_references(article)
    
    return document
