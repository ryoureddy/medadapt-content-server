import database
from pubmed_utils import search_pubmed, fetch_pubmed_article
from bookshelf_utils import search_bookshelf, fetch_bookshelf_content

def test_database():
    """Test database functionality"""
    print("Testing database functionality...")
    
    # Initialize database
    database.initialize_database()
    
    # Add a test resource
    test_resource = {
        'id': 'test-resource-001',
        'title': 'Test Resource',
        'source_type': 'test',
        'content_type': 'article',
        'cached_content': {'content': 'This is a test resource.'}
    }
    
    database.add_resource(test_resource)
    
    # Retrieve the resource
    retrieved = database.get_resource('test-resource-001')
    
    if retrieved and retrieved['title'] == 'Test Resource':
        print("✓ Database add/retrieve working correctly")
    else:
        print("✗ Database add/retrieve failed")
    
    # Test search
    search_results = database.search_resources(query='test')
    
    if search_results and len(search_results) > 0:
        print("✓ Database search working correctly")
    else:
        print("✗ Database search failed")

def test_pubmed():
    """Test PubMed API functionality"""
    print("\nTesting PubMed API functionality...")
    
    # Test search
    results = search_pubmed('cardiac cycle', 2)
    
    if results and len(results) > 0:
        print(f"✓ PubMed search returned {len(results)} results")
        print(f"  First result: {results[0]['title']}")
    else:
        print("✗ PubMed search failed")
    
    # Test article fetch
    if results and len(results) > 0:
        pmid = results[0]['source_id']
        article = fetch_pubmed_article(pmid)
        
        if article and 'error' not in article:
            print(f"✓ PubMed article fetch successful")
        else:
            print(f"✗ PubMed article fetch failed: {article.get('error', 'Unknown error')}")

def test_bookshelf():
    """Test Bookshelf API functionality"""
    print("\nTesting Bookshelf API functionality...")
    
    # Test search
    results = search_bookshelf('cardiovascular system', 2)
    
    if results and len(results) > 0:
        print(f"✓ Bookshelf search returned {len(results)} results")
        print(f"  First result: {results[0]['title']}")
    else:
        print("✗ Bookshelf search failed")
    
    # Test book fetch
    if results and len(results) > 0:
        book_id = results[0]['source_id']
        book = fetch_bookshelf_content(book_id)
        
        if book and 'error' not in book:
            print(f"✓ Bookshelf content fetch successful")
            if book.get('chapters') and len(book['chapters']) > 0:
                print(f"  Book has {len(book['chapters'])} chapters")
        else:
            print(f"✗ Bookshelf content fetch failed: {book.get('error', 'Unknown error')}")

if __name__ == "__main__":
    print("Running MedAdapt Content Server tests...")
    
    # Run tests
    test_database()
    test_pubmed()
    test_bookshelf()
    
    print("\nAll tests completed.") 