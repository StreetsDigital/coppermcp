import asyncio
import os
from app.copper.client.base import CopperClient
from app.copper.client.opportunities import OpportunitiesClient
from app.models.copper import Opportunity

async def test_opportunity():
    # Get auth token from environment variable
    auth_token = os.getenv("COPPER_API_TOKEN")
    if not auth_token:
        print("Error: COPPER_API_TOKEN environment variable not set")
        return
        
    client = CopperClient(auth_token=auth_token)
    client.opportunities = OpportunitiesClient(client)
    
    try:
        # Create test opportunity
        opp = await client.opportunities.create({
            'name': 'Test Opportunity (Delete Me)',
            'pipeline_id': 1,
            'pipeline_stage_id': 1,
            'monetary_value': 1000,
            'status': 'Open'
        })
        print(f'Created opportunity: {opp}')
        
        # Search for the opportunity
        results = await client.opportunities.search({'name': 'Test Opportunity (Delete Me)'})
        print(f'Search results: {results}')
        
        # Update the opportunity
        updated = await client.opportunities.update(opp['id'], {'monetary_value': 2000})
        print(f'Updated opportunity: {updated}')
        
    finally:
        # Always try to delete the opportunity
        if 'opp' in locals() and opp:
            await client.opportunities.delete(opp['id'])
            print('Deleted opportunity')
        # Clean up client session
        await client.close()

if __name__ == '__main__':
    asyncio.run(test_opportunity()) 