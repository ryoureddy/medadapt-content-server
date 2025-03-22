# MedAdapt Content Server

The MedAdapt Content Server is a specialized Model Context Protocol (MCP) server for Claude Desktop that provides medical education content tools. It fetches, processes, and serves educational resources from PubMed, NCBI Bookshelf, and user-provided documents to enhance AI-assisted medical learning.

## Features

- **Content Search**: Search for medical educational content across multiple sources
- **Resource Retrieval**: Fetch complete articles, book chapters, and user documents
- **Topic Overviews**: Generate comprehensive overviews of medical topics
- **Learning Resources**: Suggest appropriate learning resources based on topic and student level
- **Learning Plans**: Create structured learning plans with objectives and resources
- **Content Analysis**: Extract key points, methodologies, and findings from medical resources
- **User Content**: Import and analyze user-provided documents

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-username/medadapt-content-server.git
cd medadapt-content-server
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure (optional):
   - Get an NCBI API key for improved rate limits: https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/
   - Create a `.env` file based on `.env.example`

## Usage

1. Run the server:
```bash
python content_server.py
```

2. Configure Claude Desktop to use this MCP server (Settings → Model Context Protocol → Add Server)

3. Populate initial topic mappings (optional):
```bash
python populate_topics.py
```

4. Test server functionality:
```bash
python test_server.py
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

- **API Rate Limiting**: If you encounter rate limits from NCBI, add an API key to your `.env` file
- **Database File Permission Issues**: Ensure the directory where the server runs has write permissions
- **Claude Desktop Connection**: Verify the server is running and properly configured in Claude Desktop

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCBI for providing access to PubMed and Bookshelf APIs
- Claude for the MCP integration capability
