import sqlite3
import os
import json
from datetime import datetime

def get_db_connection():
    """Create connection to SQLite database with row factory"""
    conn = sqlite3.connect('medadapt_content.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    """Initialize the database schema if it doesn't exist"""
    conn = sqlite3.connect('medadapt_content.db')
    c = conn.cursor()
    
    # Resources table for storing content metadata and cached content
    c.execute('''
    CREATE TABLE IF NOT EXISTS resources (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        source_type TEXT NOT NULL,
        specialty TEXT,
        difficulty TEXT,
        content_type TEXT,
        source_id TEXT,
        cached_content TEXT,
        last_updated TEXT,
        access_count INTEGER DEFAULT 0
    )
    ''')
    
    # Topic mappings for relationships between medical topics
    c.execute('''
    CREATE TABLE IF NOT EXISTS topic_mappings (
        topic TEXT NOT NULL,
        parent_topic TEXT,
        specialty TEXT,
        description TEXT,
        PRIMARY KEY (topic, parent_topic)
    )
    ''')
    
    # User documents table for tracking user-provided content
    c.execute('''
    CREATE TABLE IF NOT EXISTS user_documents (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        upload_date TEXT NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_resource(resource_data):
    """Add or update a resource in the database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if resource already exists
    c.execute("SELECT id FROM resources WHERE id = ?", (resource_data['id'],))
    existing = c.fetchone()
    
    if existing:
        # Update existing resource
        c.execute('''
        UPDATE resources 
        SET title = ?, source_type = ?, specialty = ?, 
            difficulty = ?, content_type = ?, source_id = ?,
            cached_content = ?, last_updated = ?
        WHERE id = ?
        ''', (
            resource_data['title'],
            resource_data['source_type'],
            resource_data.get('specialty'),
            resource_data.get('difficulty'),
            resource_data.get('content_type'),
            resource_data.get('source_id'),
            json.dumps(resource_data.get('cached_content', {})),
            datetime.now().isoformat(),
            resource_data['id']
        ))
    else:
        # Insert new resource
        c.execute('''
        INSERT INTO resources 
        (id, title, source_type, specialty, difficulty, content_type, 
         source_id, cached_content, last_updated, access_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
        ''', (
            resource_data['id'],
            resource_data['title'],
            resource_data['source_type'],
            resource_data.get('specialty'),
            resource_data.get('difficulty'),
            resource_data.get('content_type'),
            resource_data.get('source_id'),
            json.dumps(resource_data.get('cached_content', {})),
            datetime.now().isoformat()
        ))
    
    conn.commit()
    conn.close()

def get_resource(resource_id):
    """Retrieve a resource from the database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM resources WHERE id = ?", (resource_id,))
    resource = c.fetchone()
    
    if resource:
        # Update access count
        c.execute("UPDATE resources SET access_count = access_count + 1 WHERE id = ?", 
                 (resource_id,))
        conn.commit()
        
        # Convert to dict
        result = dict(resource)
        
        # Parse cached_content if it's a JSON string
        if result.get('cached_content'):
            try:
                result['cached_content'] = json.loads(result['cached_content'])
            except:
                pass
    else:
        result = None
    
    conn.close()
    return result

def search_resources(query=None, specialty=None, difficulty=None, content_type=None, limit=10):
    """Search resources based on criteria"""
    conn = get_db_connection()
    c = conn.cursor()
    
    sql = "SELECT * FROM resources WHERE 1=1"
    params = []
    
    if query:
        sql += " AND (title LIKE ? OR cached_content LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%"])
    
    if specialty:
        sql += " AND specialty = ?"
        params.append(specialty)
    
    if difficulty:
        sql += " AND difficulty = ?"
        params.append(difficulty)
    
    if content_type:
        sql += " AND content_type = ?"
        params.append(content_type)
    
    sql += " ORDER BY access_count DESC LIMIT ?"
    params.append(limit)
    
    c.execute(sql, params)
    resources = [dict(row) for row in c.fetchall()]
    
    # Parse cached_content if it's a JSON string
    for resource in resources:
        if resource.get('cached_content'):
            try:
                resource['cached_content'] = json.loads(resource['cached_content'])
            except:
                pass
    
    conn.close()
    return resources

def add_user_document(title, content):
    """Add user-provided document to the database"""
    doc_id = f"user-doc-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
    INSERT INTO user_documents (id, title, content, upload_date)
    VALUES (?, ?, ?, ?)
    ''', (doc_id, title, content, datetime.now().isoformat()))
    
    # Also add to resources table for unified search
    resource_data = {
        'id': doc_id,
        'title': title,
        'source_type': 'user_provided',
        'content_type': 'document',
        'cached_content': {'content': content},
        'last_updated': datetime.now().isoformat()
    }
    
    add_resource(resource_data)
    
    conn.commit()
    conn.close()
    
    return doc_id

def get_user_document(doc_id):
    """Retrieve user document by ID"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT * FROM user_documents WHERE id = ?", (doc_id,))
    document = c.fetchone()
    
    conn.close()
    
    return dict(document) if document else None

def add_topic_mapping(topic, parent_topic, specialty=None, description=None):
    """Add topic mapping to the database"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
    INSERT OR REPLACE INTO topic_mappings (topic, parent_topic, specialty, description)
    VALUES (?, ?, ?, ?)
    ''', (topic, parent_topic, specialty, description))
    
    conn.commit()
    conn.close()

def get_related_topics(topic, limit=5):
    """Get related topics based on mappings"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get parent topics
    c.execute("SELECT parent_topic FROM topic_mappings WHERE topic = ?", (topic,))
    parents = [row['parent_topic'] for row in c.fetchall() if row['parent_topic']]
    
    # Get child topics
    c.execute("SELECT topic FROM topic_mappings WHERE parent_topic = ?", (topic,))
    children = [row['topic'] for row in c.fetchall() if row['topic'] != topic]
    
    # Get sibling topics (same parent)
    sibling_query = '''
    SELECT tm2.topic 
    FROM topic_mappings tm1 
    JOIN topic_mappings tm2 ON tm1.parent_topic = tm2.parent_topic 
    WHERE tm1.topic = ? AND tm2.topic != ?
    LIMIT ?
    '''
    c.execute(sibling_query, (topic, topic, limit))
    siblings = [row['topic'] for row in c.fetchall()]
    
    conn.close()
    
    # Combine and limit results
    related = []
    related.extend(parents)
    related.extend(children)
    related.extend(siblings)
    
    # Remove duplicates and limit
    return list(dict.fromkeys(related))[:limit]

if __name__ == "__main__":
    # Initialize database when script is run directly
    initialize_database() 