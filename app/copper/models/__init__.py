"""Models for the Copper API.

This module provides Pydantic models for data validation and serialization.
"""

from .base import (
    BaseEntity,
    BaseModel,
    Parent,
    Email,
    Phone,
    Address,
    SocialProfile,
    CustomField,
    ActivityType
)
from .people import Person, PersonCreate, PersonUpdate
from .activities import Activity, ActivityCreate, ActivityUpdate
from .companies import Company, CompanyCreate, CompanyUpdate
from .opportunities import (
    Pipeline, 
    Opportunity, 
    OpportunityCreate, 
    OpportunityUpdate
)
from .tasks import Task, TaskCreate, TaskUpdate, RelatedResource

__all__ = [
    # Base models
    'BaseEntity',
    'BaseModel',
    'Parent',
    'Email',
    'Phone',
    'Address',
    'SocialProfile',
    'CustomField',
    'ActivityType',
    
    # People models
    'Person',
    'PersonCreate',
    'PersonUpdate',
    
    # Activity models
    'Activity',
    'ActivityCreate',
    'ActivityUpdate',
    
    # Company models
    'Company',
    'CompanyCreate',
    'CompanyUpdate',
    
    # Opportunity models
    'Pipeline',
    'Opportunity',
    'OpportunityCreate',
    'OpportunityUpdate',
    
    # Task models
    'Task',
    'TaskCreate',
    'TaskUpdate',
    'RelatedResource',
] 