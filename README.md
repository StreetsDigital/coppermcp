# Copper MCP Server

A server implementation for transforming Copper CRM data to MCP (Model Context Protocol) format.

## Features

- Transform Copper CRM entities to MCP format
- Support for People, Companies, Opportunities, and Activities
- STDIO transport support for MCP compatibility
- FastAPI-based HTTP API
- Comprehensive test coverage

## Environment Variables

```
COPPER_API_TOKEN=your_api_token
COPPER_USER_EMAIL=your_email
COPPER_USER_ID=your_user_id
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

### HTTP Mode
```bash
uvicorn app.main:app --reload
```

### STDIO Mode
```bash
python app/run_stdio.py
```

## Testing

```bash
pytest -v
```

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /search` - Search across multiple entity types
- `GET /person/{id}` - Get person by ID
- `GET /company/{id}` - Get company by ID
- `GET /opportunity/{id}` - Get opportunity by ID
- `GET /activity/{id}` - Get activity by ID

## Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up environment variables
6. Run tests: `pytest -v`

## License

MIT
