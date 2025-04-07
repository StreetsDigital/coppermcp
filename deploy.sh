#!/bin/bash

# Initialize git if not already initialized
if [ ! -d .git ]; then
    git init
fi

# Create .gitignore
cat > .gitignore << EOL
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# Environment variables
.env

# Logs
*.log

# Coverage
.coverage
htmlcov/

# pytest
.pytest_cache/
EOL

# Create README.md
cat > README.md << EOL
# Copper MCP Server

A server implementation for transforming Copper CRM data to MCP (Model Context Protocol) format.

## Features

- Transform Copper CRM entities to MCP format
- Support for People, Companies, Opportunities, and Activities
- STDIO transport support for MCP compatibility
- FastAPI-based HTTP API
- Comprehensive test coverage

## Environment Variables

\`\`\`
COPPER_API_TOKEN=your_api_token
COPPER_USER_EMAIL=your_email
COPPER_USER_ID=your_user_id
\`\`\`

## Installation

\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Running the Server

### HTTP Mode
\`\`\`bash
uvicorn app.main:app --reload
\`\`\`

### STDIO Mode
\`\`\`bash
python app/run_stdio.py
\`\`\`

## Testing

\`\`\`bash
pytest -v
\`\`\`

## API Endpoints

- \`GET /health\` - Health check endpoint
- \`GET /search\` - Search across multiple entity types
- \`GET /person/{id}\` - Get person by ID
- \`GET /company/{id}\` - Get company by ID
- \`GET /opportunity/{id}\` - Get opportunity by ID
- \`GET /activity/{id}\` - Get activity by ID

## Development

1. Clone the repository
2. Create a virtual environment: \`python -m venv venv\`
3. Activate the virtual environment: \`source venv/bin/activate\`
4. Install dependencies: \`pip install -r requirements.txt\`
5. Set up environment variables
6. Run tests: \`pytest -v\`

## License

MIT
EOL

# Create requirements.txt
cat > requirements.txt << EOL
fastapi>=0.109.0
uvicorn>=0.27.0
pydantic>=2.6.0
httpx>=0.27.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
python-dotenv>=1.0.0
aiohttp>=3.9.0
typing-extensions>=4.9.0
EOL

# Add all files
git add .

# Initial commit
git commit -m "Initial commit: Copper MCP Server implementation"

# Add GitHub remote (you'll need to create the repository on GitHub first)
echo "Next steps:"
echo "1. Create a new repository on GitHub named 'copper-mcp-server'"
echo "2. Run the following commands:"
echo "   git remote add origin git@github.com:YOUR_USERNAME/copper-mcp-server.git"
echo "   git branch -M main"
echo "   git push -u origin main" 