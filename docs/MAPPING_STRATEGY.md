# Copper to MCP Mapping Strategy

This document outlines the strategy for mapping data between Copper CRM and the Model Context Protocol (MCP) format.

## Core Principles

1. **Consistent Structure**: All MCP entities follow a standard structure:
   ```json
   {
     "id": "string",
     "type": "string",
     "attributes": {},
     "relationships": {},
     "meta": {}
   }
   ```

2. **Data Validation**: All data is validated using Pydantic models at both input and output.

3. **Standardized Timestamps**: All timestamps are converted to ISO8601 format with UTC timezone.

4. **Relationship Handling**: Entity relationships are explicitly defined in a standardized format.

5. **Custom Field Support**: Custom fields are preserved in the meta section with their original IDs.

## Entity Type Mappings

### 1. Person
| Copper Field | MCP Field | Notes |
|--------------|-----------|-------|
| id | id | Converted to string |
| name | attributes.name | Full name |
| first_name | attributes.first_name | |
| last_name | attributes.last_name | |
| emails[0] | attributes.email | Primary email |
| phone_numbers[0] | attributes.phone | Primary phone |
| title | attributes.title | |
| company_name | attributes.company | |
| address | attributes.address | Nested object |
| company_id | relationships.company | |
| assignee_id | relationships.assignee | |
| custom_fields | meta.custom_fields | |

### 2. Company
| Copper Field | MCP Field | Notes |
|--------------|-----------|-------|
| id | id | Converted to string |
| name | attributes.name | |
| phone_numbers[0] | attributes.phone | Primary phone |
| websites[0] | attributes.website | Primary website |
| industry | attributes.industry | |
| email_domain | attributes.email_domain | |
| assignee_id | relationships.assignee | |
| custom_fields | meta.custom_fields | |

### 3. Opportunity
| Copper Field | MCP Field | Notes |
|--------------|-----------|-------|
| id | id | Converted to string |
| name | attributes.name | |
| status | attributes.status | |
| priority | attributes.priority | |
| monetary_value | attributes.monetary_value | |
| win_probability | attributes.win_probability | |
| close_date | attributes.close_date | ISO8601 format |
| assignee_id | relationships.assignee | |
| company_id | relationships.company | |
| pipeline_id | relationships.pipeline | |
| custom_fields | meta.custom_fields | |

### 4. Activity
| Copper Field | MCP Field | Notes |
|--------------|-----------|-------|
| id | id | Converted to string |
| type | attributes.activity_type | Category and ID |
| details | attributes.details | |
| activity_date | attributes.activity_date | ISO8601 format |
| parent | relationships.parent | |
| user_id | relationships.user | |
| assignee_id | relationships.assignee | |
| custom_fields | meta.custom_fields | |

## Special Handling

### 1. Contact Methods
- Primary contact methods (email, phone) are extracted from arrays
- Additional contact methods are stored in meta section
- Work contacts are prioritized as primary when available

### 2. Timestamps
- All timestamps are converted to ISO8601 format with 'Z' timezone
- Unix timestamps are properly converted
- Missing timestamps are represented as null

### 3. Custom Fields
- Custom fields are preserved with their original field definition IDs
- Values are stored without type conversion
- Custom field metadata can be included in the meta section

### 4. Relationships
- All relationships include type and ID
- Optional name field for improved context
- Null relationships are explicitly represented

### 5. Error Handling
- Invalid data types raise validation errors
- Missing required fields raise validation errors
- Relationship integrity is enforced

## Implementation Details

1. **Base Transformer**
   - Handles common fields and validation
   - Provides utility methods for contact and datetime handling
   - Ensures consistent output structure

2. **Entity-Specific Transformers**
   - Extend base transformer
   - Implement entity-specific mapping logic
   - Handle special cases and relationships

3. **Validation Flow**
   1. Input data validated against Copper models
   2. Transformation applied
   3. Output validated against MCP models
   4. Final JSON structure verified

## Testing Strategy

1. **Unit Tests**
   - Test each transformer independently
   - Verify field mappings
   - Check error handling

2. **Integration Tests**
   - Test with real API data
   - Verify end-to-end transformations
   - Validate relationship handling

3. **Edge Cases**
   - Missing optional fields
   - Invalid data types
   - Complex nested structures
   - Custom field variations 