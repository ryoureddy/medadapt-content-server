import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Load environment variables for API key
load_dotenv()
API_KEY = os.getenv('NCBI_API_KEY', '')

def search_pubmed(query, max_results=10):
    """
    Search PubMed for articles matching query
    
    Args:
        query: Search terms
        max_results: Maximum number of results to return
        
    Returns:
        List of article metadata
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_params = f"&api_key={API_KEY}" if API_KEY else ""
    
    # Step 1: Search for article IDs
    search_url = f"{base_url}esearch.fcgi?db=pubmed&term={query}&retmode=json&retmax={max_results}{api_params}"
    
    try:
        response = requests.get(search_url)
        data = response.json()
        
        if 'esearchresult' not in data or 'idlist' not in data['esearchresult']:
            return []
            
        pmids = data['esearchresult']['idlist']
        
        if not pmids:
            return []
        
        # Step 2: Fetch article details
        fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={','.join(pmids)}&retmode=xml{api_params}"
        fetch_response = requests.get(fetch_url)
        
        # Parse XML response
        root = ET.fromstring(fetch_response.text)
        articles = []
        
        for article in root.findall('.//PubmedArticle'):
            # Extract article metadata
            pmid_elem = article.find('.//PMID')
            if pmid_elem is None:
                continue
                
            pmid = pmid_elem.text
            
            # Title
            title_elem = article.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else "Unknown Title"
            
            # Abstract
            abstract_elem = article.find('.//AbstractText')
            abstract = abstract_elem.text if abstract_elem is not None else None
            
            # Journal
            journal_elem = article.find('.//Journal/Title')
            journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
            
            # Year
            year_elem = article.find('.//PubDate/Year')
            year = year_elem.text if year_elem is not None else None
            
            # Authors
            authors = []
            for author_elem in article.findall('.//Author'):
                last_name = author_elem.find('LastName')
                fore_name = author_elem.find('ForeName')
                if last_name is not None:
                    author_name = last_name.text
                    if fore_name is not None:
                        author_name = f"{fore_name.text} {author_name}"
                    authors.append(author_name)
            
            articles.append({
                'id': f"pubmed-{pmid}",
                'title': title,
                'abstract': abstract,
                'journal': journal,
                'year': year,
                'authors': authors,
                'source_type': 'pubmed',
                'source_id': pmid,
                'content_type': 'article',
                'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            })
        
        return articles
    except Exception as e:
        print(f"Error searching PubMed: {e}")
        return []

def fetch_pubmed_article(pmid):
    """
    Fetch complete article details by PubMed ID
    
    Args:
        pmid: PubMed ID
        
    Returns:
        Complete article metadata
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_params = f"&api_key={API_KEY}" if API_KEY else ""
    
    fetch_url = f"{base_url}efetch.fcgi?db=pubmed&id={pmid}&retmode=xml{api_params}"
    
    try:
        response = requests.get(fetch_url)
        root = ET.fromstring(response.text)
        
        article_elem = root.find('.//PubmedArticle')
        if article_elem is None:
            return {"error": "Article not found"}
        
        # Extract article metadata
        title_elem = article_elem.find('.//ArticleTitle')
        abstract_elem = article_elem.find('.//AbstractText')
        journal_elem = article_elem.find('.//Journal/Title')
        year_elem = article_elem.find('.//PubDate/Year')
        
        authors = []
        for author_elem in article_elem.findall('.//Author'):
            last_name = author_elem.find('LastName')
            fore_name = author_elem.find('ForeName')
            if last_name is not None:
                author_name = last_name.text
                if fore_name is not None:
                    author_name = f"{fore_name.text} {author_name}"
                authors.append(author_name)
        
        # Extract mesh terms
        mesh_terms = []
        for mesh_elem in article_elem.findall('.//MeshHeading'):
            descriptor = mesh_elem.find('DescriptorName')
            if descriptor is not None:
                mesh_terms.append(descriptor.text)
        
        return {
            'id': f"pubmed-{pmid}",
            'title': title_elem.text if title_elem is not None else "Unknown Title",
            'abstract': abstract_elem.text if abstract_elem is not None else "No abstract available",
            'authors': authors,
            'journal': journal_elem.text if journal_elem is not None else "Unknown Journal",
            'year': year_elem.text if year_elem is not None else "Unknown Year",
            'mesh_terms': mesh_terms,
            'source_type': 'pubmed',
            'source_id': pmid,
            'content_type': 'article',
            'url': f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        }
    except Exception as e:
        print(f"Error fetching PubMed article: {e}")
        return {"error": f"Error fetching article: {e}"} 