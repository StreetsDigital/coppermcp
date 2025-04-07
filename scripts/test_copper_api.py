"""Test script for Copper API client."""
import os
from datetime import datetime
from dotenv import load_dotenv

from app.copper import create_copper_client
from app.copper.models import (
    PersonCreate,
    Email,
    ActivityCreate,
    ActivityType,
    Parent
)

# Load environment variables
load_dotenv()

def main():
    """Main test function."""
    print("\nCreating Copper client...")
    client = create_copper_client()
    
    # Generate unique email using timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_email = f"test_{timestamp}@example.com"
    
    print("\nTesting person creation...")
    try:
        # Create a new person using Pydantic model
        person_data = PersonCreate(
            name="Test Contact",
            emails=[Email(email=test_email, category="work")]
        )
        new_person = client.people.create(person_data)
        print(f"Created person: {new_person.model_dump()}")
        
        person_id = new_person.id
        
        print("\nTesting person retrieval...")
        # Get the person we just created
        person = client.people.get(person_id)
        print(f"Retrieved person: {person.model_dump()}")
        
        print("\nTesting activity addition...")
        # Add an activity using Pydantic model
        activity_data = ActivityCreate(
            type=ActivityType(category="user", id=0),
            details="Test note added via API",
            parent=Parent(id=person_id, type="person")
        )
        activity = client.people.add_activity(person_id, activity_data)
        print(f"Added activity: {activity.model_dump()}")
        
        print("\nTesting activity retrieval...")
        # Get activities for the person
        activities = client.people.get_activities(person_id)
        print(f"Retrieved activities: [")
        for act in activities:
            print(f"  {act.model_dump()}")
        print("]")
        
        print("\nTesting person deletion...")
        # Delete the test person
        result = client.people.delete(person_id)
        print(f"Deletion result: {result}")
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    main() 