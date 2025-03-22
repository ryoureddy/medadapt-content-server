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
pip install -r requirements.txt

# Run the server
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

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone https://github.com/ryoureddy/medadapt-content-server.git
cd medadapt-content-server
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure (optional):
   - Get an NCBI API key for improved rate limits: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
   - Create a `.env` file based on `.env.example`

## Usage

### Running the Server

```bash
python content_server.py
```

### Integration with Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Model Context Protocol → Add Server
3. Configure with the following JSON in your `claude_desktop_config.json` file located in:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "medadapt": {
      "command": "/path/to/python",
      "args": [
        "/path/to/medadapt-content-server/content_server.py"
      ],
      "env": {
        "DB_PATH": "/path/to/medadapt-content-server/medadapt_content.db"
      }
    }
  }
}
```

Replace `/path/to/python` with your actual Python path (e.g., `/opt/anaconda3/bin/python` or `C:\Python311\python.exe`).
Replace `/path/to/medadapt-content-server/` with the absolute path to your cloned repository.

> **Important**: The `DB_PATH` environment variable ensures the database file is created and accessed with an absolute path, preventing common file access errors.

### Populating Initial Topic Mappings

```bash
python populate_topics.py
```

### Testing

Run tests to verify everything is working:
```bash
python test_server.py
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

## Troubleshooting

### Common Issues and Solutions

1. **Database Connection Error**
   - **Symptom**: `sqlite3.OperationalError: unable to open database file`
   - **Solution**: Make sure the `DB_PATH` environment variable is set correctly in your Claude Desktop configuration, pointing to an absolute path where the application has write permissions.

2. **File Path Error**
   - **Symptom**: `No such file or directory` errors
   - **Solution**: Ensure all paths in the Claude Desktop configuration are absolute paths without extra quotes or escape characters.

3. **API Rate Limiting**
   - **Symptom**: Slow or failed responses from PubMed or NCBI Bookshelf
   - **Solution**: Get an NCBI API key and add it to your `.env` file

4. **Claude Desktop Connection**
   - **Symptom**: Claude cannot connect to the MCP server
   - **Solution**: Verify the server is running in a terminal window and properly configured in Claude Desktop

## Project Structure

```
medadapt-content-server/
│
├── content_server.py     # Main MCP server implementation
├── database.py          # SQLite database interface
├── pubmed_utils.py      # PubMed API utilities
├── bookshelf_utils.py   # NCBI Bookshelf utilities
├── populate_topics.py   # Script to populate initial topic data
├── test_server.py       # Test script
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment variables
└── README.md            # Documentation
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCBI for providing access to PubMed and Bookshelf APIs
- Anthropic for Claude and the MCP integration capability 