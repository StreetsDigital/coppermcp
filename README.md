# CopperMCP

A Model Context Protocol (MCP) adapter for Copper CRM - transforms and serves Copper data in MCP format.

## Features

- Transform Copper CRM entities to MCP format
- Support for People, Companies, Opportunities, and Activities
- STDIO transport support for MCP compatibility
- FastAPI-based HTTP API
- Comprehensive test coverage

## Environment Variables

The application uses environment variables for configuration. Create a `.env` file in the root directory based on `.env.example`:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your actual values
vim .env
```

### Required Variables

- `COPPER_API_TOKEN` - Your Copper CRM API token (found in Copper CRM settings)
- `COPPER_USER_EMAIL` - Your Copper CRM user email

### Optional Variables

- **API Configuration**
  - `COPPER_API_TIMEOUT` - Request timeout in seconds (default: 30)
  - `COPPER_API_MAX_RETRIES` - Maximum number of retries for failed requests (default: 3)
  - `COPPER_API_RETRY_DELAY` - Delay between retries in seconds (default: 1)

- **Logging Configuration**
  - `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `LOG_FORMAT` - Custom log format string

- **Cache Configuration**
  - `TOKEN_CACHE_TTL` - Time-to-live for cached tokens in seconds (default: 3600)

- **Test Configuration**
  - `TEST_MODE` - Enable mock responses in tests (default: False)

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
5. Copy `.env.example` to `.env` and configure your environment variables
6. Run tests: `pytest -v`

## Security Notes

* Never commit your `.env` file to version control
* Keep your API tokens secure and rotate them regularly
* Use environment variables for all sensitive configuration

## License

MIT
