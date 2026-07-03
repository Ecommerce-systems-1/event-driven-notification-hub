from pydantic import BaseModel, Field


class EventPublish(BaseModel):
    id: str = Field(..., min_length=1)
    event_type: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    payload: dict = Field(default_factory=dict)


class EventPublishResponse(BaseModel):
    event_id: str
    status: str
    published_at: str
