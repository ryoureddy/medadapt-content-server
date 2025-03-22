from mcp.server.fastmcp import FastMCP
import json
from datetime import datetime
import logging
import os
import sys
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("medadapt_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("medadapt_server")

# Load environment variables
load_dotenv()

# Import utility modules
try:
    import database
    from pubmed_utils import search_pubmed, fetch_pubmed_article
    from bookshelf_utils import search_bookshelf, fetch_bookshelf_content, fetch_chapter_content
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    sys.exit(1)

# Initialize MCP server
content_server = FastMCP("MedAdapt Content Server")

@content_server.tool()
def search_medical_content(query: str, specialty: str = None, 
                          difficulty: str = None, content_type: str = None,
                          max_results: int = 10) -> list:
    """
    Search for medical educational content based on query and filters.
    
    Args:
        query: Search term to find relevant medical content
        specialty: Optional medical specialty filter
        difficulty: Optional difficulty level filter
        content_type: Optional content type filter
        max_results: Maximum number of results to return
        
    Returns:
        List of matching resources with metadata
    """
    try:
        logger.info(f"Searching for content with query: '{query}', specialty: {specialty}, difficulty: {difficulty}, content_type: {content_type}")
        
        # First, check local database
        local_results = database.search_resources(
            query=query, 
            specialty=specialty, 
            difficulty=difficulty, 
            content_type=content_type, 
            limit=max_results
        )
        
        logger.info(f"Found {len(local_results)} results in local database")
        
        # If we have enough local results, return them
        if len(local_results) >= max_results:
            return local_results
        
        # Otherwise, search external sources
        remaining_results = max_results - len(local_results)
        
        # Allocate remaining results between sources
        pubmed_count = remaining_results // 2
        bookshelf_count = remaining_results - pubmed_count
        
        # Search PubMed
        pubmed_results = []
        if pubmed_count > 0:
            try:
                logger.info(f"Searching PubMed for '{query}'")
                pubmed_results = search_pubmed(query, pubmed_count)
                logger.info(f"Found {len(pubmed_results)} results from PubMed")
                
                # Store results in database for future use
                for result in pubmed_results:
                    database.add_resource(result)
            except Exception as e:
                logger.error(f"PubMed search failed: {str(e)}")
                pubmed_results = []
        
        # Search Bookshelf
        bookshelf_results = []
        if bookshelf_count > 0:
            try:
                logger.info(f"Searching Bookshelf for '{query}'")
                bookshelf_results = search_bookshelf(query, bookshelf_count)
                logger.info(f"Found {len(bookshelf_results)} results from Bookshelf")
                
                # Store results in database for future use
                for result in bookshelf_results:
                    database.add_resource(result)
            except Exception as e:
                logger.error(f"Bookshelf search failed: {str(e)}")
                bookshelf_results = []
        
        # Combine and return results
        all_results = local_results + pubmed_results + bookshelf_results
        return all_results[:max_results]
    except Exception as e:
        logger.error(f"Error in search_medical_content: {str(e)}")
        logger.error(traceback.format_exc())
        return [{"error": f"Search failed: {str(e)}"}]

@content_server.tool()
def get_resource_content(resource_id: str) -> dict:
    """
    Retrieve complete content for a specific resource.
    
    Args:
        resource_id: Unique identifier for the resource
        
    Returns:
        Resource object with complete content
    """
    try:
        logger.info(f"Retrieving content for resource: {resource_id}")
        
        # Check local database first
        resource = database.get_resource(resource_id)
        
        # If resource exists and has cached content, return it
        if resource and resource.get('cached_content'):
            logger.info(f"Resource {resource_id} found in cache")
            return resource
        
        # If not found or no cached content, fetch from source
        if resource_id.startswith('pubmed-'):
            pmid = resource_id.replace('pubmed-', '')
            logger.info(f"Fetching PubMed article: {pmid}")
            content = fetch_pubmed_article(pmid)
        elif resource_id.startswith('bookshelf-'):
            # Check if it's a chapter or a book
            parts = resource_id.replace('bookshelf-', '').split('-')
            if len(parts) > 1:
                book_id = parts[0]
                chapter_id = parts[1]
                logger.info(f"Fetching Bookshelf chapter: {book_id}/{chapter_id}")
                content = fetch_chapter_content(book_id, chapter_id)
            else:
                book_id = parts[0]
                logger.info(f"Fetching Bookshelf book: {book_id}")
                content = fetch_bookshelf_content(book_id)
        elif resource_id.startswith('user-doc-'):
            # It's a user document, get from database
            logger.info(f"Retrieving user document: {resource_id}")
            doc = database.get_user_document(resource_id)
            if doc:
                content = {
                    'id': doc['id'],
                    'title': doc['title'],
                    'content': doc['content'],
                    'upload_date': doc['upload_date'],
                    'source_type': 'user_provided'
                }
            else:
                return {"error": f"User document not found: {resource_id}"}
        else:
            return {"error": f"Unknown resource ID format: {resource_id}"}
        
        # Store fetched content in database
        if 'error' not in content:
            logger.info(f"Caching content for resource: {resource_id}")
            database.add_resource(content)
        else:
            logger.error(f"Error fetching content for {resource_id}: {content.get('error')}")
        
        return content
    except Exception as e:
        logger.error(f"Error in get_resource_content: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": f"Failed to retrieve resource: {str(e)}"}

@content_server.tool()
def get_topic_overview(topic: str) -> dict:
    """
    Generate a comprehensive overview of a medical topic.
    
    Args:
        topic: Medical topic to provide overview for
        
    Returns:
        Structured overview with definitions, key concepts, and related materials
    """
    try:
        logger.info(f"Generating overview for topic: {topic}")
        
        # Search for relevant resources
        resources = search_medical_content(topic, max_results=5)
        
        # Check for errors in resources
        if resources and len(resources) > 0 and 'error' in resources[0]:
            return {"error": f"Failed to find resources for topic overview: {resources[0]['error']}"}
        
        # Extract definition from resources
        definition = extract_definition(topic, resources)
        
        # Identify key concepts
        key_concepts = extract_key_concepts(topic, resources)
        
        # Find related topics
        try:
            related_topics = database.get_related_topics(topic)
        except Exception as e:
            logger.warning(f"Failed to get related topics: {str(e)}")
            related_topics = []
        
        # If no related topics found, use simplified fallback
        if not related_topics:
            related_topics = [
                f"{topic} pathophysiology", 
                f"{topic} anatomy", 
                f"{topic} clinical aspects"
            ]
        
        # Compile overview
        overview = {
            'topic': topic,
            'definition': definition,
            'key_concepts': key_concepts,
            'related_topics': related_topics,
            'recommended_resources': [
                {
                    'id': r['id'],
                    'title': r['title'],
                    'type': r.get('content_type', 'unknown')
                } for r in resources[:3]  # Top 3 resources
            ]
        }
        
        return overview
    except Exception as e:
        logger.error(f"Error in get_topic_overview: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": f"Failed to generate topic overview: {str(e)}"}

def extract_definition(topic, resources):
    """Extract definition from resources"""
    # Search for definition in resources
    for resource in resources:
        # Check abstract first for PubMed articles
        if resource.get('abstract'):
            sentences = resource['abstract'].split('.')
            for sentence in sentences[:3]:
                if topic.lower() in sentence.lower() and len(sentence) > 30:
                    return sentence.strip() + '.'
        
        # Check cached content
        if resource.get('cached_content'):
            content = resource['cached_content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            # Extract from various content types
            if isinstance(content, dict):
                # Check abstract
                if content.get('abstract'):
                    sentences = content['abstract'].split('.')
                    for sentence in sentences[:3]:
                        if topic.lower() in sentence.lower() and len(sentence) > 30:
                            return sentence.strip() + '.'
                
                # Check sections (for book chapters)
                if content.get('sections'):
                    for section in content['sections']:
                        if section.get('content'):
                            sentences = section['content'].split('.')
                            for sentence in sentences[:3]:
                                if topic.lower() in sentence.lower() and len(sentence) > 30:
                                    return sentence.strip() + '.'
    
    # Fallback if no good definition found
    return f"The topic {topic} requires further exploration to provide a comprehensive definition."

def extract_key_concepts(topic, resources):
    """Extract key concepts from resources"""
    concepts = []
    
    # Check MeSH terms for relevant concepts
    for resource in resources:
        if resource.get('cached_content'):
            content = resource['cached_content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            if isinstance(content, dict) and content.get('mesh_terms'):
                # Find relevant MeSH terms
                for term in content['mesh_terms']:
                    if topic.lower() in term.lower():
                        concepts.append(term)
    
    # Check sections and headings in bookshelf content
    for resource in resources:
        if resource.get('source_type') == 'bookshelf' and resource.get('cached_content'):
            content = resource['cached_content']
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except:
                    pass
            
            if isinstance(content, dict) and content.get('chapters'):
                for chapter in content['chapters']:
                    if topic.lower() in chapter.get('title', '').lower():
                        concepts.append(chapter['title'])
    
    # Add generic concepts if we don't have enough
    if len(concepts) < 3:
        generic_concepts = [
            f"Fundamental principles of {topic}",
            f"Clinical significance of {topic}",
            f"Anatomical considerations in {topic}",
            f"Physiological mechanisms of {topic}",
            f"Pathological changes in {topic}"
        ]
        
        # Add generic concepts until we have at least 3
        for concept in generic_concepts:
            if concept not in concepts:
                concepts.append(concept)
                if len(concepts) >= 5:
                    break
    
    return concepts[:5]  # Return up to 5 key concepts

@content_server.tool()
def suggest_learning_resources(topic: str, student_level: str) -> list:
    """
    Suggest learning resources based on topic and student level.
    
    Args:
        topic: Medical topic of interest
        student_level: Student's academic level (first_year, second_year, clinical_years)
        
    Returns:
        List of recommended resources with rationale
    """
    # Map student level to difficulty
    difficulty_map = {
        "first_year": "basic",
        "second_year": "intermediate",
        "clinical_years": "advanced"
    }
    
    difficulty = difficulty_map.get(student_level, "intermediate")
    
    # Search for resources with appropriate difficulty
    resources = search_medical_content(topic, difficulty=difficulty, max_results=5)
    
    # Add recommendation rationale
    recommendations = []
    for resource in resources:
        recommendation = {
            'id': resource['id'],
            'title': resource['title'],
            'type': resource.get('content_type', 'article'),
            'rationale': generate_recommendation_rationale(resource, topic, student_level)
        }
        recommendations.append(recommendation)
    
    return recommendations

def generate_recommendation_rationale(resource, topic, student_level):
    """Generate explanation for resource recommendation"""
    source_type = resource.get('source_type', '')
    
    if source_type == 'pubmed':
        return f"This peer-reviewed article provides evidence-based information on {topic} appropriate for {student_level} understanding."
    elif source_type == 'bookshelf':
        return f"This textbook chapter offers comprehensive coverage of {topic} fundamentals that align with {student_level} curriculum."
    elif source_type == 'user_provided':
        return f"This resource was previously uploaded and contains relevant information about {topic}."
    else:
        return f"This resource contains key information about {topic} presented at a {student_level} level."

@content_server.tool()
def import_user_document(document_content: str, document_title: str) -> str:
    """
    Import user-provided learning material into the system.
    
    Args:
        document_content: Text content of the document
        document_title: Title of the document
        
    Returns:
        Resource ID for the imported document
    """
    # Store document in database
    doc_id = database.add_user_document(document_title, document_content)
    
    return doc_id

@content_server.tool()
def generate_learning_plan(topic: str, student_level: str) -> dict:
    """
    Generate a structured learning plan for a medical topic.
    
    Args:
        topic: Medical topic to create a learning plan for
        student_level: Student's academic level
        
    Returns:
        Structured learning plan with objectives and resources
    """
    # Get topic overview
    overview = get_topic_overview(topic)
    
    # Get recommended resources
    resources = suggest_learning_resources(topic, student_level)
    
    # Create learning objectives based on level
    if student_level == "first_year":
        objectives = [
            f"Define key terms related to {topic}",
            f"Identify basic structures and components involved in {topic}",
            f"Explain fundamental principles of {topic}",
            f"Recognize the relationship between {topic} and related systems"
        ]
    elif student_level == "second_year":
        objectives = [
            f"Apply principles of {topic} to simplified clinical scenarios",
            f"Analyze mechanisms underlying {topic}",
            f"Compare normal and abnormal functioning related to {topic}",
            f"Integrate knowledge of {topic} with pathophysiological concepts"
        ]
    else:  # clinical_years
        objectives = [
            f"Evaluate clinical presentations related to {topic} abnormalities",
            f"Develop diagnostic approaches for conditions involving {topic}",
            f"Interpret clinical findings related to {topic}",
            f"Apply evidence-based principles to management of {topic} disorders"
        ]
    
    # Create a structured learning plan
    learning_plan = {
        'topic': topic,
        'student_level': student_level,
        'definition': overview['definition'],
        'learning_objectives': objectives,
        'key_concepts': overview['key_concepts'],
        'suggested_resources': resources,
        'related_topics': overview['related_topics']
    }
    
    return learning_plan

@content_server.tool()
def extract_article_key_points(resource_id: str) -> dict:
    """
    Extract key points from a medical article or chapter.
    
    Args:
        resource_id: ID of the resource to analyze
        
    Returns:
        Key points, methodology, and findings extracted from the resource
    """
    # Get resource content
    resource = get_resource_content(resource_id)
    
    if 'error' in resource:
        return resource
    
    # Extract based on resource type
    if resource.get('source_type') == 'pubmed':
        # Extract from PubMed article
        key_points = {
            'title': resource.get('title'),
            'main_findings': extract_main_findings(resource),
            'methodology': extract_methodology(resource),
            'clinical_implications': extract_clinical_implications(resource),
            'key_terms': extract_key_terms(resource)
        }
    elif resource.get('source_type') == 'bookshelf':
        # Extract from bookshelf chapter
        key_points = {
            'title': resource.get('title'),
            'main_concepts': extract_main_concepts(resource),
            'key_definitions': extract_key_definitions(resource),
            'clinical_correlations': extract_clinical_correlations(resource),
            'key_terms': extract_key_terms(resource)
        }
    elif resource.get('source_type') == 'user_provided':
        # Extract from user document
        key_points = {
            'title': resource.get('title'),
            'main_points': extract_main_points_from_document(resource),
            'key_terms': extract_key_terms(resource)
        }
    else:
        key_points = {
            'error': "Unable to extract key points from this resource type"
        }
    
    return key_points

def extract_main_findings(resource):
    """Extract main findings from PubMed article"""
    # Simplified implementation - in a real system, use NLP
    if resource.get('abstract'):
        # Look for sentences that might indicate findings
        findings_indicators = [
            "we found", "results showed", "demonstrated", "revealed", 
            "observed", "concluded", "findings"
        ]
        
        findings = []
        sentences = resource['abstract'].split('.')
        
        for sentence in sentences:
            lower_sent = sentence.lower()
            for indicator in findings_indicators:
                if indicator in lower_sent and len(sentence.strip()) > 20:
                    findings.append(sentence.strip() + '.')
                    break
        
        if findings:
            return findings[:3]  # Return top 3 findings
    
    # Fallback if no findings extracted
    return ["The article's main findings could not be automatically extracted. Please review the full abstract."]

def extract_methodology(resource):
    """Extract methodology from PubMed article"""
    # Simplified implementation - in a real system, use NLP
    if resource.get('abstract'):
        # Look for sentences that might describe methodology
        method_indicators = [
            "method", "study design", "we conducted", "participants", 
            "patients", "subjects", "sample", "procedure", "analysis"
        ]
        
        methods = []
        sentences = resource['abstract'].split('.')
        
        for sentence in sentences:
            lower_sent = sentence.lower()
            for indicator in method_indicators:
                if indicator in lower_sent and len(sentence.strip()) > 20:
                    methods.append(sentence.strip() + '.')
                    break
        
        if methods:
            return methods[:2]  # Return top 2 methodology sentences
    
    # Fallback if no methodology extracted
    return ["The article's methodology could not be automatically extracted. Please review the full abstract."]

def extract_clinical_implications(resource):
    """Extract clinical implications from article"""
    # Simplified implementation - in a real system, use NLP
    if resource.get('abstract'):
        # Look for sentences that might indicate clinical implications
        implication_indicators = [
            "implications", "clinical", "practice", "treatment", 
            "management", "care", "patients", "therapy", "intervention"
        ]
        
        implications = []
        sentences = resource['abstract'].split('.')
        
        for sentence in sentences:
            lower_sent = sentence.lower()
            for indicator in implication_indicators:
                if indicator in lower_sent and len(sentence.strip()) > 20:
                    implications.append(sentence.strip() + '.')
                    break
        
        if implications:
            return implications[:2]  # Return top 2 implications
    
    # Fallback if no implications extracted
    return ["The clinical implications could not be automatically extracted. Please review the full abstract."]

def extract_key_terms(resource):
    """Extract key terms from resource"""
    # For PubMed articles, use MeSH terms if available
    if resource.get('source_type') == 'pubmed' and resource.get('mesh_terms'):
        return resource['mesh_terms'][:5]  # Return up to 5 MeSH terms
    
    # For other resources, use a simplified approach
    terms = []
    
    # Extract from title
    if resource.get('title'):
        title_words = resource['title'].split()
        for word in title_words:
            if len(word) > 5 and word.lower() not in ['about', 'these', 'those', 'their', 'there']:
                terms.append(word)
    
    # Extract from abstract if available
    if resource.get('abstract'):
        # This is a very simplified approach - real implementation would use NLP
        abstract_words = resource['abstract'].split()
        word_freq = {}
        
        for word in abstract_words:
            clean_word = ''.join(c for c in word if c.isalnum())
            if len(clean_word) > 5 and clean_word.lower() not in ['about', 'these', 'those', 'their', 'there']:
                if clean_word in word_freq:
                    word_freq[clean_word] += 1
                else:
                    word_freq[clean_word] = 1
        
        # Get top 5 most frequent words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        for word, freq in sorted_words[:5]:
            if word not in terms:
                terms.append(word)
    
    return terms[:5]  # Return up to 5 terms

def extract_main_concepts(resource):
    """Extract main concepts from bookshelf chapter"""
    concepts = []
    
    # Extract from chapter title
    if resource.get('title'):
        concepts.append(f"Understanding {resource['title']}")
    
    # Extract from chapter sections if available
    if resource.get('cached_content') and isinstance(resource['cached_content'], dict):
        content = resource['cached_content']
        
        if content.get('sections'):
            for section in content['sections'][:3]:  # Get first 3 sections
                if section.get('title'):
                    concepts.append(section['title'])
    
    # Add generic concepts if needed
    if len(concepts) < 3:
        generic_concepts = [
            "Basic Principles",
            "Clinical Applications",
            "Physiological Mechanisms",
            "Anatomical Relationships"
        ]
        
        for concept in generic_concepts:
            if concept not in concepts:
                concepts.append(concept)
                if len(concepts) >= 5:
                    break
    
    return concepts[:5]  # Return up to 5 concepts

def extract_key_definitions(resource):
    """Extract key definitions from bookshelf content"""
    definitions = []
    
    # In a real implementation, this would use NLP to identify definitions
    # This is a simplified version
    
    # Check for sections content
    if resource.get('cached_content') and isinstance(resource['cached_content'], dict):
        content = resource['cached_content']
        
        if content.get('sections'):
            for section in content['sections']:
                if section.get('content'):
                    lines = section['content'].split('\n')
                    for line in lines:
                        # Look for definition patterns
                        if ':' in line and len(line) < 200:
                            definitions.append(line.strip())
                        elif ' - ' in line and len(line) < 200:
                            definitions.append(line.strip())
    
    return definitions[:5]  # Return up to 5 definitions

def extract_clinical_correlations(resource):
    """Extract clinical correlations from bookshelf content"""
    correlations = []
    
    # In a real implementation, this would use NLP
    # This is a simplified version
    
    # Check for sections content
    if resource.get('cached_content') and isinstance(resource['cached_content'], dict):
        content = resource['cached_content']
        
        if content.get('sections'):
            for section in content['sections']:
                if section.get('title') and 'clinical' in section['title'].lower():
                    correlations.append(section['title'])
                
                if section.get('content'):
                    sentences = section['content'].split('.')
                    for sentence in sentences:
                        lower_sent = sentence.lower()
                        if ('clinic' in lower_sent or 'patient' in lower_sent or 'disease' in lower_sent) and len(sentence) > 30:
                            correlations.append(sentence.strip() + '.')
    
    return correlations[:3]  # Return up to 3 clinical correlations

def extract_main_points_from_document(resource):
    """Extract main points from user-provided document"""
    main_points = []
    
    # Get content from the resource
    if resource.get('cached_content') and isinstance(resource['cached_content'], dict):
        content = resource['cached_content']
        
        if content.get('content'):
            # Split into paragraphs
            paragraphs = content['content'].split('\n\n')
            
            # Get first paragraph as introduction
            if paragraphs and len(paragraphs[0]) > 50:
                main_points.append(paragraphs[0])
            
            # Look for key sentences in other paragraphs
            indicators = [
                "important", "significant", "key", "essential", "crucial",
                "demonstrated", "found", "shows", "reveals", "concludes"
            ]
            
            for paragraph in paragraphs[1:]:
                sentences = paragraph.split('.')
                for sentence in sentences:
                    lower_sent = sentence.lower()
                    for indicator in indicators:
                        if indicator in lower_sent and len(sentence) > 30:
                            main_points.append(sentence.strip() + '.')
                            break
    
    # If we didn't find enough points, add the first few sentences
    if len(main_points) < 3 and resource.get('cached_content'):
        content = resource['cached_content']
        if isinstance(content, dict) and content.get('content'):
            sentences = content['content'].split('.')
            for sentence in sentences[:5]:
                if len(sentence) > 30 and sentence.strip() + '.' not in main_points:
                    main_points.append(sentence.strip() + '.')
                    if len(main_points) >= 5:
                        break
    
    return main_points[:5]  # Return up to 5 main points

def initialize_server():
    """Initialize the server and perform startup checks"""
    try:
        # Initialize database
        logger.info("Initializing database...")
        database.initialize_database()
        
        # Check for NCBI API key
        api_key = os.getenv('NCBI_API_KEY')
        if api_key:
            logger.info("NCBI API key found in environment")
        else:
            logger.warning("NCBI API key not found. API rate limits will be restricted.")
            
        # Log server information
        logger.info("MedAdapt Content Server initialized successfully")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Server running from: {os.path.dirname(os.path.abspath(__file__))}")
        
        return True
    except Exception as e:
        logger.error(f"Server initialization failed: {str(e)}")
        logger.error(traceback.format_exc())
        return False

# Start server
if __name__ == "__main__":
    # Initialize the server
    if not initialize_server():
        logger.error("Server initialization failed. Exiting.")
        sys.exit(1)
    
    logger.info("Starting MedAdapt Content Server...")
    try:
        content_server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1) 