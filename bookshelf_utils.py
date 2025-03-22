import requests
import xml.etree.ElementTree as ET
import os
from dotenv import load_dotenv

# Load environment variables for API key
load_dotenv()
API_KEY = os.getenv('NCBI_API_KEY', '')

def search_bookshelf(query, max_results=10):
    """
    Search NCBI Bookshelf for textbook content
    
    Args:
        query: Search terms
        max_results: Maximum number of results to return
        
    Returns:
        List of book metadata
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_params = f"&api_key={API_KEY}" if API_KEY else ""
    
    # Step 1: Search for book IDs
    search_url = f"{base_url}esearch.fcgi?db=books&term={query}&retmode=json&retmax={max_results}{api_params}"
    
    try:
        response = requests.get(search_url)
        data = response.json()
        
        if 'esearchresult' not in data or 'idlist' not in data['esearchresult']:
            return []
            
        book_ids = data['esearchresult']['idlist']
        
        if not book_ids:
            return []
        
        # Step 2: Fetch book details
        fetch_url = f"{base_url}efetch.fcgi?db=books&id={','.join(book_ids)}&retmode=xml{api_params}"
        fetch_response = requests.get(fetch_url)
        
        # Parse XML response
        root = ET.fromstring(fetch_response.text)
        books = []
        
        for book in root.findall('.//Book'):
            book_id_elem = book.find('.//BookId')
            if book_id_elem is None:
                continue
                
            book_id = book_id_elem.text
            
            title_elem = book.find('.//BookTitle')
            publisher_elem = book.find('.//Publisher/PublisherName')
            
            books.append({
                'id': f"bookshelf-{book_id}",
                'title': title_elem.text if title_elem is not None else "Unknown Title",
                'publisher': publisher_elem.text if publisher_elem is not None else None,
                'source_type': 'bookshelf',
                'source_id': book_id,
                'content_type': 'textbook',
                'url': f"https://www.ncbi.nlm.nih.gov/books/{book_id}/"
            })
        
        return books
    except Exception as e:
        print(f"Error searching Bookshelf: {e}")
        return []

def fetch_bookshelf_content(book_id):
    """
    Fetch complete book details and chapter list
    
    Args:
        book_id: Bookshelf ID
        
    Returns:
        Book details with chapter list
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_params = f"&api_key={API_KEY}" if API_KEY else ""
    
    fetch_url = f"{base_url}efetch.fcgi?db=books&id={book_id}&retmode=xml{api_params}"
    
    try:
        response = requests.get(fetch_url)
        root = ET.fromstring(response.text)
        
        book_elem = root.find('.//Book')
        if book_elem is None:
            return {"error": "Book not found"}
        
        title_elem = book_elem.find('.//BookTitle')
        publisher_elem = book_elem.find('.//Publisher/PublisherName')
        
        # Get chapter information
        chapters = []
        for chapter_elem in book_elem.findall('.//Chapter'):
            chapter_title = chapter_elem.find('.//ChapterTitle')
            chapter_id = chapter_elem.find('.//ChapterId')
            
            if chapter_title is not None and chapter_id is not None:
                chapters.append({
                    'title': chapter_title.text,
                    'id': chapter_id.text
                })
        
        # Get authors
        authors = []
        for author_elem in book_elem.findall('.//AuthorList/Author'):
            last_name = author_elem.find('.//LastName')
            fore_name = author_elem.find('.//ForeName')
            if last_name is not None:
                author_name = last_name.text
                if fore_name is not None:
                    author_name = f"{fore_name.text} {author_name}"
                authors.append(author_name)
        
        # Get publication information
        publication_year = None
        year_elem = book_elem.find('.//PubDate/Year')
        if year_elem is not None:
            publication_year = year_elem.text
        
        return {
            'id': f"bookshelf-{book_id}",
            'title': title_elem.text if title_elem is not None else "Unknown Title",
            'publisher': publisher_elem.text if publisher_elem is not None else "Unknown Publisher",
            'authors': authors,
            'publication_year': publication_year,
            'chapters': chapters,
            'source_type': 'bookshelf',
            'source_id': book_id,
            'content_type': 'textbook',
            'url': f"https://www.ncbi.nlm.nih.gov/books/{book_id}/"
        }
    except Exception as e:
        print(f"Error fetching book details: {e}")
        return {"error": f"Error fetching book: {e}"}

def fetch_chapter_content(book_id, chapter_id):
    """
    Fetch specific chapter content
    
    Args:
        book_id: Bookshelf book ID
        chapter_id: Chapter ID
        
    Returns:
        Chapter content and metadata
    """
    base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    api_params = f"&api_key={API_KEY}" if API_KEY else ""
    
    # Fetch specific chapter
    fetch_url = f"{base_url}efetch.fcgi?db=books&id={book_id}.{chapter_id}&retmode=xml{api_params}"
    
    try:
        response = requests.get(fetch_url)
        root = ET.fromstring(response.text)
        
        chapter_elem = root.find('.//Chapter')
        if chapter_elem is None:
            return {"error": "Chapter not found"}
        
        title_elem = chapter_elem.find('.//ChapterTitle')
        
        # Extract text content (simplified)
        sections = []
        for section_elem in chapter_elem.findall('.//Section'):
            section_title = section_elem.find('.//SectionTitle')
            
            # Get paragraphs
            paragraphs = []
            for para in section_elem.findall('.//Para'):
                if para.text:
                    paragraphs.append(para.text)
            
            sections.append({
                'title': section_title.text if section_title is not None else None,
                'content': '\n\n'.join(paragraphs)
            })
        
        return {
            'id': f"bookshelf-{book_id}-{chapter_id}",
            'book_id': book_id,
            'chapter_id': chapter_id,
            'title': title_elem.text if title_elem is not None else "Unknown Chapter",
            'sections': sections,
            'content_type': 'chapter',
            'source_type': 'bookshelf',
            'url': f"https://www.ncbi.nlm.nih.gov/books/{book_id}/{chapter_id}/"
        }
    except Exception as e:
        print(f"Error fetching chapter: {e}")
        return {"error": f"Error fetching chapter: {e}"} 