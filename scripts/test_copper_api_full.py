"""Test script for the Copper API client.

This script tests the functionality of People, Companies, and Opportunities clients.
Uses VCR to record and replay HTTP interactions.
"""

import os
import sys
import vcr
from datetime import datetime, timedelta
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.copper.client import CopperClient
from app.copper.models import (
    PersonCreate,
    CompanyCreate,
    OpportunityCreate,
    ActivityCreate,
    Parent,
    Email,
    Phone,
    Address,
    SocialProfile,
    ActivityType,
    TaskCreate,
    RelatedResource,
)

# Configure VCR
vcr_config = vcr.VCR(
    cassette_library_dir="tests/vcr_cassettes",
    record_mode="all",  # Record all requests
    match_on=["method", "scheme", "host", "port", "path", "query", "body"],
    filter_headers=["authorization"],  # Don't record auth headers
    filter_post_data_parameters=["token", "email"],  # Don't record sensitive data
)

# TODO: Remove hardcoded user ID and implement proper user lookup
CURRENT_USER_ID = 1139515

def print_separator(title: str = "") -> None:
    """Print a separator line with optional title."""
    print("\n" + "="*80)
    if title:
        print(f"Testing: {title}")
        print("-"*80)

def print_response(title: str, data: Dict[str, Any]) -> None:
    """Print formatted response data."""
    print(f"\n{title}:")
    print(f"ID: {data.get('id')}")
    print(f"Name: {data.get('name')}")
    print(f"Created: {data.get('date_created')}")
    print(f"Modified: {data.get('date_modified')}")

def main():
    """Run tests for Copper API client."""
    
    # Initialize client
    print_separator("Initializing Copper Client")
    client = CopperClient(
        api_key=os.environ["COPPER_API_KEY"],
        email=os.environ["COPPER_USER_EMAIL"],
    )
    print("Copper client created successfully")
    
    # Generate unique timestamp for email addresses
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Use VCR to record/replay HTTP interactions
    with vcr_config.use_cassette("test_copper_api_full.yaml"):
        try:
            # Test People Client
            print_separator("People Client")
            
            # Create a person
            person_data = PersonCreate(
                name="Test Contact",
                emails=[Email(email=f"test.contact.{timestamp}@example.com", category="work")],
                title="Software Engineer",
                company_name="Test Company",
                phones=[Phone(number="+1-555-123-4567", category="work")],
                address=Address(
                    street="123 Main St",
                    city="San Francisco",
                    state="CA",
                    postal_code="94105",
                    country="US"
                ),
                social_profiles=[
                    SocialProfile(url="https://linkedin.com/in/testcontact", category="linkedin")
                ],
                tags=["test", "api"]
            )
            person = client.people.create(person_data)
            print_response("Created Person", person.model_dump())
            
            # Get the person
            retrieved_person = client.people.get(person.id)
            print_response("Retrieved Person", retrieved_person.model_dump())
            
            # Test Companies Client
            print_separator("Companies Client")
            
            # Create a company
            company_data = CompanyCreate(
                name="Test Company",
                emails=[Email(email=f"info.{timestamp}@testcompany.com", category="work")],
                phones=[Phone(number="+1-555-987-6543", category="work")],
                address=Address(
                    street="456 Market St",
                    city="San Francisco",
                    state="CA",
                    postal_code="94105",
                    country="US"
                ),
                social_profiles=[
                    SocialProfile(url="https://linkedin.com/company/testcompany", category="linkedin")
                ],
                tags=["test", "api"]
            )
            company = client.companies.create(company_data)
            print_response("Created Company", company.model_dump())
            
            # Get the company
            retrieved_company = client.companies.get(company.id)
            print_response("Retrieved Company", retrieved_company.model_dump())
            
            # Test Opportunities Client
            print_separator("Opportunities Client")
            
            # Get available pipelines
            pipelines = client.opportunities.get_pipelines()
            if not pipelines:
                print("No pipelines found")
                return
                
            pipeline = pipelines[0]
            pipeline_id = pipeline['id']
            pipeline_stage_id = pipeline['stages'][0]['id']
            
            # Get customer sources
            customer_sources = client.opportunities.get_customer_sources()
            customer_source_id = customer_sources[0]['id'] if customer_sources else None
            
            # Create an opportunity
            opportunity_data = OpportunityCreate(
                name="Test Opportunity",
                pipeline_id=pipeline_id,
                pipeline_stage_id=pipeline_stage_id,
                primary_contact_id=person.id,
                company_id=company.id
            )
            opportunity = client.opportunities.create(opportunity_data)
            print_response("Created Opportunity", opportunity.model_dump())
            
            # Get the opportunity
            retrieved_opportunity = client.opportunities.get(opportunity.id)
            print_response("Retrieved Opportunity", retrieved_opportunity.model_dump())
            
            # Add an activity to the opportunity
            activity_data = ActivityCreate(
                type=ActivityType(category="user"),
                details="Test activity for opportunity",
                parent=Parent(
                    id=opportunity.id,
                    type="opportunity"
                )
            )
            activity = client.opportunities.add_activity(opportunity.id, activity_data)
            print("\nCreated Activity:", activity.model_dump())
            
            # Test Tasks Client
            print_separator("Tasks Client")
            
            # Create a task
            task_data = TaskCreate(
                name="Test Task",
                related_resource=RelatedResource(
                    id=opportunity.id,
                    type="opportunity"
                ),
                assignee_id=CURRENT_USER_ID,  # Use the current user's ID
                due_date=datetime.now() + timedelta(days=7),
                reminder_date=datetime.now() + timedelta(days=6),
                priority="High",
                status="Open",
                details="Test task details",
                tags=["test", "api"],
            )
            task = client.tasks.create(task_data)
            print_response("Created Task", task.model_dump())
            
            # Get the task
            retrieved_task = client.tasks.get(task.id)
            print_response("Retrieved Task", retrieved_task.model_dump())
            
            # Clean up
            print("\nCleaning up...")
            client.tasks.delete(task.id)
            print(f"Deleted task: {task.id}")
            
            client.opportunities.delete(opportunity.id)
            print(f"Deleted opportunity: {opportunity.id}")
            
            client.companies.delete(company.id)
            print(f"Deleted company: {company.id}")
            
            client.people.delete(person.id)
            print(f"Deleted person: {person.id}")
            
            print("\nAll tests completed successfully!")
            
        except Exception as e:
            print(f"\nError during testing: {str(e)}")
            raise

if __name__ == "__main__":
    main()