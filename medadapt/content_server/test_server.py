import database
from pubmed_utils import search_pubmed, fetch_pubmed_article
from bookshelf_utils import search_bookshelf, fetch_bookshelf_content
import os
import logging
import time
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_results.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("medadapt_tests")

def test_database():
    """Test database functionality with comprehensive checks"""
    logger.info("Testing database functionality...")
    
    # Initialize database
    try:
        database.initialize_database()
        logger.info("✓ Database initialization successful")
    except Exception as e:
        logger.error(f"✗ Database initialization failed: {str(e)}")
        return False
    
    # Test resource operations
    test_resource = {
        'id': 'test-resource-001',
        'title': 'Test Resource for Database Operations',
        'source_type': 'test',
        'specialty': 'cardiology',
        'difficulty': 'intermediate',
        'content_type': 'article',
        'cached_content': {'content': 'This is a test resource for database operations.'}
    }
    
    try:
        # Add resource
        database.add_resource(test_resource)
        logger.info("✓ Database add resource successful")
        
        # Retrieve resource
        retrieved = database.get_resource('test-resource-001')
        
        if retrieved and retrieved['title'] == 'Test Resource for Database Operations':
            logger.info("✓ Database retrieve resource successful")
        else:
            logger.error("✗ Database retrieve resource failed")
            return False
        
        # Test search
        search_results = database.search_resources(query='test')
        
        if search_results and len(search_results) > 0:
            logger.info(f"✓ Database search successful, found {len(search_results)} results")
        else:
            logger.error("✗ Database search failed")
            return False
        
        # Test filtering
        filter_results = database.search_resources(
            specialty='cardiology', 
            difficulty='intermediate'
        )
        
        if filter_results and any(r['id'] == 'test-resource-001' for r in filter_results):
            logger.info("✓ Database filtering successful")
        else:
            logger.error("✗ Database filtering failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Database operation failed: {str(e)}")
        return False
    
    # Test topic mappings
    try:
        # Add topic mapping
        database.add_topic_mapping(
            "test_topic", 
            "test_parent_topic", 
            "test_specialty", 
            "This is a test topic description"
        )
        
        # Get related topics
        related = database.get_related_topics("test_topic")
        
        if related and "test_parent_topic" in related:
            logger.info("✓ Topic mapping operations successful")
        else:
            logger.error("✗ Topic mapping operations failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ Topic mapping operation failed: {str(e)}")
        return False
    
    # Test user documents
    try:
        # Add user document
        doc_id = database.add_user_document(
            "Test User Document",
            "This is content for a test user document."
        )
        
        # Retrieve user document
        doc = database.get_user_document(doc_id)
        
        if doc and doc['title'] == "Test User Document":
            logger.info("✓ User document operations successful")
        else:
            logger.error("✗ User document operations failed")
            return False
            
    except Exception as e:
        logger.error(f"✗ User document operation failed: {str(e)}")
        return False
    
    return True

def test_pubmed(retry_count=2, delay=1.0):
    """Test PubMed API functionality with retries"""
    logger.info("Testing PubMed API functionality...")
    
    # Test search with retries
    results = None
    for attempt in range(retry_count + 1):
        try:
            results = search_pubmed('cardiac cycle', 2)
            break
        except Exception as e:
            if attempt < retry_count:
                logger.warning(f"PubMed search attempt {attempt+1} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"PubMed search failed after {retry_count+1} attempts: {str(e)}")
                return False
    
    if results and len(results) > 0:
        logger.info(f"✓ PubMed search returned {len(results)} results")
        logger.info(f"  First result: {results[0]['title']}")
        
        # Store the search results for later analysis
        with open("pubmed_search_results.json", "w") as f:
            json.dump(results, f, indent=4)
    else:
        logger.error("✗ PubMed search returned no results")
        return False
    
    # Test article fetch with retries
    if results and len(results) > 0:
        pmid = results[0]['source_id']
        article = None
        
        for attempt in range(retry_count + 1):
            try:
                article = fetch_pubmed_article(pmid)
                break
            except Exception as e:
                if attempt < retry_count:
                    logger.warning(f"PubMed article fetch attempt {attempt+1} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"PubMed article fetch failed after {retry_count+1} attempts: {str(e)}")
                    return False
        
        if article and 'error' not in article:
            logger.info(f"✓ PubMed article fetch successful")
            
            # Store the article for later analysis
            with open("pubmed_article_sample.json", "w") as f:
                json.dump(article, f, indent=4)
        else:
            logger.error(f"✗ PubMed article fetch failed: {article.get('error', 'Unknown error')}")
            return False
    
    return True

def test_bookshelf(retry_count=2, delay=1.0):
    """Test Bookshelf API functionality with retries"""
    logger.info("Testing Bookshelf API functionality...")
    
    # Test search with retries
    results = None
    for attempt in range(retry_count + 1):
        try:
            results = search_bookshelf('cardiovascular system', 2)
            break
        except Exception as e:
            if attempt < retry_count:
                logger.warning(f"Bookshelf search attempt {attempt+1} failed: {str(e)}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                logger.error(f"Bookshelf search failed after {retry_count+1} attempts: {str(e)}")
                return False
    
    if results and len(results) > 0:
        logger.info(f"✓ Bookshelf search returned {len(results)} results")
        logger.info(f"  First result: {results[0]['title']}")
        
        # Store the search results for later analysis
        with open("bookshelf_search_results.json", "w") as f:
            json.dump(results, f, indent=4)
    else:
        logger.error("✗ Bookshelf search returned no results")
        return False
    
    # Test book fetch with retries
    if results and len(results) > 0:
        book_id = results[0]['source_id']
        book = None
        
        for attempt in range(retry_count + 1):
            try:
                book = fetch_bookshelf_content(book_id)
                break
            except Exception as e:
                if attempt < retry_count:
                    logger.warning(f"Bookshelf content fetch attempt {attempt+1} failed: {str(e)}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"Bookshelf content fetch failed after {retry_count+1} attempts: {str(e)}")
                    return False
        
        if book and 'error' not in book:
            logger.info(f"✓ Bookshelf content fetch successful")
            if book.get('chapters') and len(book['chapters']) > 0:
                logger.info(f"  Book has {len(book['chapters'])} chapters")
                
                # Store the book for later analysis
                with open("bookshelf_book_sample.json", "w") as f:
                    json.dump(book, f, indent=4)
        else:
            logger.error(f"✗ Bookshelf content fetch failed: {book.get('error', 'Unknown error')}")
            return False
    
    return True

def test_environment():
    """Verify environmental setup and configuration"""
    logger.info("Testing environment configuration...")
    
    # Check for NCBI API key
    api_key = os.getenv('NCBI_API_KEY')
    if api_key:
        logger.info("✓ NCBI API key found in environment")
    else:
        logger.warning("⚠ NCBI API key not found. API rate limits will be restricted.")
    
    # Check for database file or ability to create it
    db_dir = os.path.dirname(os.path.abspath('medadapt_content.db'))
    if os.access(db_dir, os.W_OK):
        logger.info(f"✓ Write access available for database directory: {db_dir}")
    else:
        logger.error(f"✗ No write access for database directory: {db_dir}")
        return False
    
    # Check required modules
    try:
        import sqlite3
        import requests
        import dotenv
        import mcp
        logger.info("✓ All required modules are available")
    except ImportError as e:
        logger.error(f"✗ Required module missing: {str(e)}")
        return False
    
    return True

def run_all_tests():
    """Run all tests and return overall status"""
    logger.info("Starting MedAdapt Content Server tests...")
    
    # Track test results
    results = {
        "environment": False,
        "database": False,
        "pubmed": False,
        "bookshelf": False
    }
    
    # Run tests
    results["environment"] = test_environment()
    results["database"] = test_database()
    results["pubmed"] = test_pubmed()
    results["bookshelf"] = test_bookshelf()
    
    # Summarize results
    logger.info("\n=== Test Results Summary ===")
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test_name.capitalize()}: {status}")
    
    all_passed = all(results.values())
    logger.info(f"\nOverall Status: {'SUCCESS' if all_passed else 'FAILURE'}")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests() 