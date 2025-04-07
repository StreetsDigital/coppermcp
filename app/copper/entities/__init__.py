"""Entity clients for the Copper API.

This module provides clients for interacting with different entities in Copper CRM.
"""

from .activities import ActivitiesClient
from .companies import CompaniesClient
from .opportunities import OpportunitiesClient
from .people import PeopleClient
from .tasks import TasksClient

__all__ = [
    "ActivitiesClient",
    "CompaniesClient",
    "OpportunitiesClient",
    "PeopleClient",
    "TasksClient",
] 