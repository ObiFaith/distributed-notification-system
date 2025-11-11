# app/models.py
"""Why do we need this file:
In fastapi, models(which are usually built with pydantic, 
which helps us describe what kind of data the API receives, what kind of data it sends,
 and how to validate, document and serialize/deserialize those data structures)

"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field ,HttpUrl
from enum import Enum
from uuid import UUID


"""
since this api gateway is the entry point , so it needs to
1. recieve requests from the clients
2.validate the body of those requests are correctly formatted
3. package valid requests into message to send to rabitMQ
"""


"""
I was wondering why we needed the pagination, since its  just a push/email notification system ,
ie a user send a request for an email or a push notification , this is the case most the time but in some end points , especially when listing
or fetching many items , the response contains a list(array) of objects instead of a single one.

Eg.
1. getting all the notifications a users has sent
2. getting all templates in the system
3. getting all failed notifications from the dead-letter queue
4. getting all registered users 

Pagination helps us handle things like this .
"""
class PaginationMeta(BaseModel):
    total: int = 0
    limit: int = 10
    page: int = 1
    total_pages: int = 0
    has_next: bool = False
    has_previous: bool = False


""" This is the standard API response format for every API response whether it is success or error"""
class ResponseEnvelope(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    message: str
    meta: Optional[PaginationMeta] = None



"""
Before sending out the messages to rabbitMQ , fastapi needs to know what a valid notification requests looks like:
this is what this class does , defines the expected shape of the incoming data"
"""
# class NotificationPayload(BaseModel):
#     request_id: str = Field(..., description="Unique id for idempotency")
#     user_id: int
#     notification_type: str = Field(..., pattern="^(email|push)$")
#     template: str
#     variables: Dict[str, Any] = Field(default_factory=dict)
#     priority: Optional[int] = 0




class NotificationType(str, Enum):
    email = "email"
    push = "push"

class UserData(BaseModel):
    name: str
    link: HttpUrl
    meta: Optional[dict]

class NotificationPayload(BaseModel):
    notification_type: NotificationType = Field(..., description="Either 'email' or 'push'")
    user_id: UUID = Field(..., description="Unique identifier for the user")
    template_code: str = Field(..., description="Template name or code to use for the notification")
    variables: UserData = Field(..., description="Dynamic variables for rendering the message")
    request_id: str = Field(..., description="Unique id for idempotency")
    priority: int = Field(0, description="Notification priority level (default: 0)")
    metadata: Optional[dict] = Field(None, description="Additional metadata if needed")
