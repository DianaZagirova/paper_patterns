#!/usr/bin/env python3
"""
Paper Data Analyzer

This script provides advanced analysis capabilities for the paper data collected
by the paper_data_collector.py script. It can be used standalone or integrated
with the paper_llm_system.py.
"""
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from collections import Counter, defaultdict
import re
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from wordcloud import WordCloud
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

# Configuration
PAPERS_DIR = './paper_data/papers/'
OUTPUT_DIR = './paper_data/analysis/'

class PaperDataAnalyzer:
    """
    A class for analyzing academic paper data and generating insights.
    """
    
    def __init__(self, papers_dir: str = PAPERS_DIR, output_dir: str = OUTPUT_DIR):
        """
        Initialize the Paper Data Analyzer.
        
        Args:
            papers_dir: Directory containing paper JSON files
            output_dir: Directory to save analysis outputs
        """
        self.papers_dir = papers_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Load paper data
        self.papers = self.load_paper_data()
        
        # Convert to DataFrame for easier analysis
        self.papers_df = self.create_papers_dataframe()
    
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
    
    def create_papers_dataframe(self) -> pd.DataFrame:
        """
        Convert paper data to a pandas DataFrame for easier analysis.
        
        Returns:
            DataFrame containing paper data
        """
        # Extract basic metadata
        paper_records = []
        
        for paper in self.papers:
            record = {
                'doi': paper.get('doi', ''),
                'title': paper.get('title', ''),
                'abstract': paper.get('abstract', ''),
                'year': paper.get('year', None),
                'journal': paper.get('journal', ''),
                'citation_count': paper.get('citation_count', 0),
                'keywords': ', '.join(paper.get('keywords', [])),
                'mesh_terms': ', '.join(paper.get('mesh_terms', [])),
                'author_count': len(paper.get('authors', [])),
                'has_full_text': bool(paper.get('full_text', {})),
                'section_count': len(paper.get('full_text', {})),
            }
            
            # Extract first author
            authors = paper.get('authors', [])
            if authors:
                record['first_author'] = authors[0].get('name', '')
            else:
                record['first_author'] = ''
                
            # Calculate full text length
            full_text_length = 0
            for section, content in paper.get('full_text', {}).items():
                if isinstance(content, str):
                    full_text_length += len(content)
            record['full_text_length'] = full_text_length
            
            paper_records.append(record)
        
        return pd.DataFrame(paper_records)
    
    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics for the paper collection.
        
        Returns:
            Dictionary of summary statistics
        """
        stats = {
            'total_papers': len(self.papers),
            'year_range': (
                int(self.papers_df['year'].min()) if not pd.isna(self.papers_df['year'].min()) else None,
                int(self.papers_df['year'].max()) if not pd.isna(self.papers_df['year'].max()) else None
            ),
            'total_citations': int(self.papers_df['citation_count'].sum()),
            'avg_citations_per_paper': float(self.papers_df['citation_count'].mean()),
            'papers_with_full_text': int(self.papers_df['has_full_text'].sum()),
            'unique_journals': len(self.papers_df['journal'].unique()),
            'top_journals': self.papers_df['journal'].value_counts().head(5).to_dict(),
            'avg_abstract_length': float(self.papers_df['abstract'].str.len().mean()),
            'avg_full_text_length': float(self.papers_df['full_text_length'].mean()),
        }
        
        return stats
    
    def extract_common_terms(self, field: str = 'mesh_terms', top_n: int = 20) -> Dict[str, int]:
        """
        Extract the most common terms from a specified field.
        
        Args:
            field: Field to extract terms from ('mesh_terms', 'keywords')
            top_n: Number of top terms to return
            
        Returns:
            Dictionary of term frequencies
        """
        all_terms = []
        
        for paper in self.papers:
            terms = paper.get(field, [])
            if isinstance(terms, list):
                all_terms.extend(terms)
            elif isinstance(terms, str):
                all_terms.extend([t.strip() for t in terms.split(',')])
        
        term_counter = Counter(all_terms)
        return dict(term_counter.most_common(top_n))
    
    def analyze_citation_trends(self) -> Dict[str, List]:
        """
        Analyze citation trends by year.
        
        Returns:
            Dictionary with years and average citations
        """
        if self.papers_df.empty:
            return {'years': [], 'avg_citations': []}
            
        # Group by year and calculate average citations
        yearly_citations = self.papers_df.groupby('year')['citation_count'].mean().reset_index()
        
        return {
            'years': yearly_citations['year'].tolist(),
            'avg_citations': yearly_citations['citation_count'].tolist()
        }
    
    def generate_topic_clusters(self, n_clusters: int = 5) -> Dict[str, List]:
        """
        Generate topic clusters based on paper abstracts.
        
        Args:
            n_clusters: Number of clusters to generate
            
        Returns:
            Dictionary with cluster information
        """
        # Prepare text data
        abstracts = self.papers_df['abstract'].fillna('').tolist()
        
        if not abstracts or all(not abstract for abstract in abstracts):
            return {'error': 'No abstract data available for clustering'}
        
        # Create TF-IDF matrix
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            min_df=2
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(abstracts)
            
            # Apply K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(tfidf_matrix)
            
            # Get top terms for each cluster
            order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]
            terms = vectorizer.get_feature_names_out()
            
            cluster_terms = {}
            for i in range(n_clusters):
                cluster_terms[f'Cluster {i+1}'] = [terms[ind] for ind in order_centroids[i, :10]]
            
            # Assign papers to clusters
            self.papers_df['cluster'] = clusters
            
            # Get paper titles by cluster
            papers_by_cluster = {}
            for i in range(n_clusters):
                cluster_papers = self.papers_df[self.papers_df['cluster'] == i]['title'].tolist()
                papers_by_cluster[f'Cluster {i+1}'] = cluster_papers
            
            return {
                'cluster_terms': cluster_terms,
                'papers_by_cluster': papers_by_cluster
            }
            
        except Exception as e:
            return {'error': f'Clustering failed: {str(e)}'}
    
    def generate_wordcloud(self, field: str = 'abstract') -> str:
        """
        Generate a word cloud from paper abstracts or full text.
        
        Args:
            field: Field to generate word cloud from ('abstract' or 'full_text')
            
        Returns:
            Path to the saved word cloud image
        """
        if field == 'abstract':
            text = ' '.join(self.papers_df['abstract'].fillna('').tolist())
        elif field == 'full_text':
            text = ''
            for paper in self.papers:
                for section, content in paper.get('full_text', {}).items():
                    if isinstance(content, str):
                        text += ' ' + content
        else:
            raise ValueError(f"Invalid field: {field}. Must be 'abstract' or 'full_text'")
        
        if not text.strip():
            return f"No {field} data available for word cloud generation"
        
        # Generate word cloud
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            max_words=200,
            contour_width=3,
            contour_color='steelblue'
        ).generate(text)
        
        # Save word cloud
        output_path = os.path.join(self.output_dir, f'wordcloud_{field}.png')
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        return output_path
    
    def extract_author_networks(self) -> Dict[str, Any]:
        """
        Extract author collaboration networks.
        
        Returns:
            Dictionary with author network information
        """
        author_papers = defaultdict(list)
        collaborations = defaultdict(int)
        
        for paper in self.papers:
            authors = [author.get('name', '') for author in paper.get('authors', [])]
            title = paper.get('title', '')
            
            # Record papers by author
            for author in authors:
                if author:
                    author_papers[author].append(title)
            
            # Record collaborations
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    if author1 and author2:
                        # Sort author names to ensure consistent key
                        collab_key = tuple(sorted([author1, author2]))
                        collaborations[collab_key] += 1
        
        # Convert to list format for easier JSON serialization
        collab_list = [
            {'authors': list(authors), 'count': count}
            for authors, count in collaborations.items()
        ]
        
        # Sort by collaboration count
        collab_list.sort(key=lambda x: x['count'], reverse=True)
        
        return {
            'author_paper_counts': {author: len(papers) for author, papers in author_papers.items()},
            'top_authors': dict(Counter({author: len(papers) for author, papers in author_papers.items()}).most_common(10)),
            'collaborations': collab_list[:20]  # Top 20 collaborations
        }
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive analysis report.
        
        Returns:
            Dictionary with all analysis results
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary_statistics': self.generate_summary_statistics(),
            'common_mesh_terms': self.extract_common_terms(field='mesh_terms'),
            'common_keywords': self.extract_common_terms(field='keywords'),
            'citation_trends': self.analyze_citation_trends(),
            'topic_clusters': self.generate_topic_clusters(),
            'author_networks': self.extract_author_networks()
        }
        
        # Generate and save word clouds
        abstract_wordcloud = self.generate_wordcloud(field='abstract')
        report['abstract_wordcloud_path'] = abstract_wordcloud
        
        full_text_wordcloud = self.generate_wordcloud(field='full_text')
        report['full_text_wordcloud_path'] = full_text_wordcloud
        
        # Save report to JSON
        report_path = os.path.join(self.output_dir, 'analysis_report.json')
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"Comprehensive report saved to {report_path}")
        return report
    
    def generate_llm_context(self) -> str:
        """
        Generate a context string for the LLM system.
        
        Returns:
            Formatted context string with analysis insights
        """
        stats = self.generate_summary_statistics()
        mesh_terms = self.extract_common_terms(field='mesh_terms', top_n=10)
        keywords = self.extract_common_terms(field='keywords', top_n=10)
        
        context = f"""
PAPER COLLECTION ANALYSIS:

Summary Statistics:
- Total Papers: {stats['total_papers']}
- Year Range: {stats['year_range'][0]} to {stats['year_range'][1]}
- Total Citations: {stats['total_citations']}
- Average Citations Per Paper: {stats['avg_citations_per_paper']:.2f}
- Papers with Full Text: {stats['papers_with_full_text']}
- Unique Journals: {stats['unique_journals']}

Top Journals:
{self._format_dict(stats['top_journals'])}

Top MeSH Terms:
{self._format_dict(mesh_terms)}

Top Keywords:
{self._format_dict(keywords)}

Author Analysis:
{self._format_author_analysis()}
"""
        return context
    
    def _format_dict(self, data: Dict, indent: int = 2) -> str:
        """Helper method to format dictionary for display"""
        result = ""
        for key, value in data.items():
            result += " " * indent + f"- {key}: {value}\n"
        return result
    
    def _format_author_analysis(self) -> str:
        """Helper method to format author analysis for display"""
        author_networks = self.extract_author_networks()
        top_authors = author_networks['top_authors']
        
        result = "Top Authors:\n"
        for author, count in top_authors.items():
            result += f"  - {author}: {count} papers\n"
        
        return result


def main():
    """Main function to run the Paper Data Analyzer."""
    parser = argparse.ArgumentParser(description='Paper Data Analyzer')
    parser.add_argument('--papers-dir', type=str, default=PAPERS_DIR, help='Directory containing paper JSON files')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR, help='Directory to save analysis outputs')
    parser.add_argument('--report', action='store_true', help='Generate comprehensive report')
    parser.add_argument('--wordcloud', choices=['abstract', 'full_text', 'both'], help='Generate word cloud')
    parser.add_argument('--clusters', type=int, help='Generate topic clusters with specified number of clusters')
    parser.add_argument('--llm-context', action='store_true', help='Generate context for LLM system')
    
    args = parser.parse_args()
    
    # Create analyzer
    analyzer = PaperDataAnalyzer(papers_dir=args.papers_dir, output_dir=args.output_dir)
    
    if args.report:
        analyzer.generate_comprehensive_report()
    
    if args.wordcloud:
        if args.wordcloud in ['abstract', 'both']:
            path = analyzer.generate_wordcloud(field='abstract')
            print(f"Abstract word cloud saved to: {path}")
        
        if args.wordcloud in ['full_text', 'both']:
            path = analyzer.generate_wordcloud(field='full_text')
            print(f"Full text word cloud saved to: {path}")
    
    if args.clusters:
        clusters = analyzer.generate_topic_clusters(n_clusters=args.clusters)
        print("Topic Clusters:")
        for cluster, terms in clusters['cluster_terms'].items():
            print(f"\n{cluster}:")
            print(f"  Terms: {', '.join(terms)}")
            print(f"  Papers: {len(clusters['papers_by_cluster'][cluster])}")
    
    if args.llm_context:
        context = analyzer.generate_llm_context()
        print("\nLLM Context:")
        print(context)


if __name__ == "__main__":
    main()
