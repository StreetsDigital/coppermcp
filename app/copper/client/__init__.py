"""Copper CRM API Client.

This module provides a client for interacting with the Copper CRM API.

AI Usage Guide:
---------------
When processing natural language requests related to Copper CRM, consider these patterns:

1. List/Search Requests:
   - "Show me outstanding tasks"
   -> Use tasks.search({"is_complete": false, "assignee_id": current_user_id})
   
   - "Find all deals with ACME Corp"
   -> First search for company by name
   -> Then search opportunities with company_id
   
   - "Show me contacts at TechCorp"
   -> Search company first
   -> Then search people with company_id

2. Creation Requests:
   - "Create a task to follow up with Jane Doe next Tuesday"
   -> Search for person "Jane Doe" to get ID
   -> Parse date to timestamp
   -> Create task with person_id and due_date
   
   - "Add new company Innovate Solutions"
   -> Check if company exists first
   -> Create if not found
   
   - "Start an opportunity with TechCorp for $50,000"
   -> Search for company
   -> Create opportunity with monetary_value

3. Update Requests:
   - "Mark task 123 as complete"
   -> Update task with is_complete=True
   
   - "Change John Smith's email to john@newdomain.com"
   -> Search person first
   -> Update with new email

4. Common Patterns:
   - Always search before creating to avoid duplicates
   - Resolve references (names -> IDs) before operations
   - Convert dates to timestamps
   - Handle amounts/currencies appropriately
   - Consider related entities (e.g., task for person at company)

Example Workflow:
----------------
```python
# Natural language: "Create a task to follow up with Jane at ACME Corp next week"

# 1. Find the company
companies = await client.companies.search({"name": "ACME Corp"})
company_id = companies[0].id if companies else None

# 2. Find the person
people = await client.people.search({
    "name": "Jane",
    "company_id": company_id
})
person_id = people[0].id if people else None

# 3. Calculate the due date
next_week = datetime.now() + timedelta(days=7)
due_date = int(next_week.timestamp())

# 4. Create the task
task = await client.tasks.create(TaskCreate(
    name="Follow up with Jane",
    due_date=due_date,
    related_resource={
        "id": person_id,
        "type": "person"
    }
))
```

For more examples and patterns, see the documentation in each client module.
"""

from .base import CopperClient
from .tasks import TasksClient
from .people import PeopleClient
from .companies import CompaniesClient
from .opportunities import OpportunitiesClient
from .activities import ActivitiesClient

__all__ = [
    'CopperClient',
    'TasksClient',
    'PeopleClient',
    'CompaniesClient',
    'OpportunitiesClient',
    'ActivitiesClient',
] 