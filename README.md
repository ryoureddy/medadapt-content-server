# MedAdapt Content Server

MedAdapt Content Server is a specialized Model Context Protocol (MCP) server for Claude Desktop that provides medical education content tools. It fetches, processes, and serves educational resources from PubMed, NCBI Bookshelf, and user-provided documents to enhance AI-assisted medical learning.

## Overview

This repository contains the implementation of the MedAdapt Content Server, which integrates with Claude Desktop to provide enhanced medical education capabilities.

## Quick Start

See the detailed [README](medadapt/content_server/README.md) in the content_server directory for complete installation and usage instructions.

1. Clone the repository:
```bash
git clone https://github.com/your-username/medadapt-content-server.git
cd medadapt-content-server
```

2. Install dependencies:
```bash
pip install -r medadapt/content_server/requirements.txt
```

3. Run the server:
```bash
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NCBI for providing access to PubMed and Bookshelf APIs
- [Claude](https://claude.ai) for the MCP integration capability 