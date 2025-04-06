# Copper MCP Server - Project Planning

## Project Overview
This project implements a Copper CRM integration for the MCP (Model Context Protocol) system. It provides a FastAPI-based server that translates Copper CRM data into a standardized MCP format, enabling unified access to CRM data through a consistent model context interface.

## Architecture

### Core Components
1. FastAPI Application
   - Main application entry point
   - RESTful API endpoints
   - Request/Response validation using Pydantic models
   - Error handling middleware

2. Copper API Integration
   - Authentication module
   - API client for Copper endpoints
   - Rate limiting and error handling
   - Entity-specific modules (people, opportunities, activities)

3. Data Transformation Layer
   - Pydantic models for data validation
   - Mapping logic between Copper and MCP formats
   - Utility functions for data transformation

### Directory Structure
```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── copper/               # Copper API integration
│   │   ├── __init__.py
│   │   ├── auth.py          # Authentication helpers
│   │   ├── client.py        # Base API client
│   │   ├── people.py        # People-related operations
│   │   ├── opportunities.py # Opportunity-related operations
│   │   └── activities.py    # Activity-related operations
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── copper.py       # Copper data models
│   │   └── mcp.py          # MCP format models
│   └── mapping/            # Data transformation logic
│       ├── __init__.py
│       └── transform.py    # Copper to MCP mapping
├── tests/                  # Test directory mirroring app structure
│   ├── __init__.py
│   ├── conftest.py        # Pytest configuration
│   ├── copper/
│   │   ├── test_auth.py
│   │   ├── test_client.py
│   │   └── test_people.py
│   └── mapping/
│       └── test_transform.py
├── .env                    # Environment variables (gitignored)
├── .gitignore
├── requirements.txt        # Project dependencies
├── README.md              # Project documentation
└── TASK.md               # Task tracking
```

## Style Guide & Conventions

### Python Standards
- Python 3.9+ required
- PEP 8 compliance
- Black code formatting
- Type hints required for all functions
- Google-style docstrings

### Code Organization
- Maximum file length: 500 lines
- Clear module separation by responsibility
- Relative imports within packages

### Testing Requirements
- Pytest for all testing
- Test coverage requirements:
  - 1 test for expected use
  - 1 edge case test
  - 1 failure case test
- Tests must mirror app structure

### Documentation
- Clear docstrings for all functions
- Inline comments for complex logic
- Up-to-date README.md
- Maintained TASK.md

## Copper API Integration

### Authentication
- API Key + Email authentication
- Headers required:
  - X-PW-AccessToken: API Key
  - X-PW-Application: User Email

### Key Endpoints
- People:
  - POST /people/search
  - GET /people/{id}
- Opportunities:
  - POST /opportunities/search
  - GET /opportunities/{id}
- Activities:
  - POST /activities/search
  - GET /activities/{id}

### Rate Limiting
- Implement exponential backoff for 429 responses
- Cache frequently accessed data where appropriate

## Error Handling
- Use FastAPI HTTPException for API errors
- Implement proper error logging
- Return appropriate HTTP status codes
- Handle Copper API errors gracefully

## Security
- No hardcoded credentials
- Environment variables for sensitive data
- Input validation using Pydantic
- Proper error message sanitization 