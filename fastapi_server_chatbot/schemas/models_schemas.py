from pydantic import BaseModel
from typing import Optional

# Request / Response 모델
## Event
class EventRequest(BaseModel): 
    event_id: Optional[str] = None
    client_role: str
    e_description: str
    claim_summary: str
    event_file: str

class EventResponse(BaseModel):
    result: str