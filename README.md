# MedAdapt Content Server

A specialized Model Context Protocol (MCP) server for Claude Desktop that enhances AI-assisted medical learning by fetching and processing educational resources from PubMed, NCBI Bookshelf, and user-provided documents.

## Overview

The MedAdapt Content Server integrates with Claude Desktop to provide tools for searching, retrieving, and analyzing medical education content. It serves as a bridge between Claude and medical knowledge sources, allowing for enhanced AI-assisted learning experiences.

## Quick Start

```bash
# Clone the repository
git clone https://github.com/ryoureddy/medadapt-content-server.git
cd medadapt-content-server

# Install dependencies
pip install -r medadapt/content_server/requirements.txt

# Run the server
cd medadapt/content_server
python content_server.py
```

## Features

- **Content Search**: Search for medical educational content across multiple sources
- **Resource Retrieval**: Fetch complete articles, book chapters, and user documents
- **Topic Overviews**: Generate comprehensive overviews of medical topics
- **Learning Resources**: Suggest appropriate learning resources based on topic and student level
- **Learning Plans**: Create structured learning plans with objectives and resources
- **Content Analysis**: Extract key points, methodologies, and findings from medical resources
- **User Content**: Import and analyze user-provided documents
- **Database Backup**: Automated backup and restore functionality
- **Docker Support**: Easy containerized deployment

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/ryoureddy/medadapt-content-server.git
cd medadapt-content-server
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r medadapt/content_server/requirements.txt
```

4. Configure (optional):
   - Get an NCBI API key for improved rate limits: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
   - Create a `.env` file based on `.env.example`

### Docker Installation

1. Clone the repository:
```bash
git clone https://github.com/ryoureddy/medadapt-content-server.git
cd medadapt-content-server/medadapt/content_server
```

2. Run with Docker Compose:
```bash
docker-compose up -d
```

This will build the Docker image and start the server in the background.

## Usage

### Running the Server

```bash
cd medadapt/content_server
python content_server.py
```

### Integration with Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Model Context Protocol → Add Server
3. Configure with the following details:
   - Name: MedAdapt Content Server
   - Transport Type: Command
   - Command: `/path/to/python /path/to/medadapt-content-server/medadapt/content_server/content_server.py`

### Populating Initial Topic Mappings

```bash
cd medadapt/content_server
python populate_topics.py
```

### Testing

Run comprehensive tests:
```bash
cd medadapt/content_server
python run_tests.py
```

Run specific test types:
```bash
python run_tests.py --unit        # Unit tests only
python run_tests.py --integration # Integration tests only
python run_tests.py --performance # Performance tests only
python run_tests.py --api         # External API tests only
```

## Example Usage with Claude

### Scenario 1: Learning About a Medical Topic

User prompt to Claude:
```
I'd like to learn about the cardiac cycle. Can you provide a big picture overview and help me understand the key concepts?
```

### Scenario 2: Finding Specific Resources

User prompt to Claude:
```
I need to find recent research articles about COVID-19 treatment options. Can you help me find relevant resources?
```

### Scenario 3: Creating a Learning Plan

User prompt to Claude:
```
I'm a second-year medical student studying neurology. Can you create a learning plan for understanding stroke pathophysiology?
```

## Available Tools

The server provides the following tools to Claude:

- `search_medical_content`: Search for medical content with filters
- `get_resource_content`: Retrieve complete content for a specific resource
- `get_topic_overview`: Generate comprehensive overview of a medical topic
- `suggest_learning_resources`: Get personalized resource recommendations
- `import_user_document`: Upload user-provided learning materials
- `generate_learning_plan`: Create structured learning plan with objectives
- `extract_article_key_points`: Extract key findings from medical articles

## Database Management

### Backups

Create a database backup:
```bash
cd medadapt/content_server
python backup_utils.py
```

Schedule regular backups (runs in foreground):
```bash
python -c "import backup_utils; backup_utils.schedule_backup(24)"
```

List available backups:
```bash
python -c "import backup_utils; print(backup_utils.list_backups())"
```

Restore from backup:
```bash
python -c "import backup_utils; backup_utils.restore_backup('backups/your_backup_file.db')"
```

## Troubleshooting

- **API Rate Limiting**: If you encounter rate limits from NCBI, add an API key to your `.env` file
- **Database File Permission Issues**: Ensure the directory where the server runs has write permissions
- **Claude Desktop Connection**: Verify the server is running and properly configured in Claude Desktop
- **Docker Issues**: Check logs with `docker-compose logs` if you're running in Docker

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCBI for providing access to PubMed and Bookshelf APIs
- Claude for the MCP integration capability 