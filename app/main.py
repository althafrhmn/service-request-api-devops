from datetime import datetime, timezone
from enum import Enum
from itertools import count

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(
title="Service Request Management API",
description="An API for creating and managing service requests.",
version="1.0.0",
)

class Priority(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"

class RequestStatus(str, Enum):
    open = "Open"
    in_progress = "In Progress"
    resolved = "Resolved"
    closed = "Closed"

class ServiceRequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=5, max_length=1000)
    priority: Priority = Priority.medium

class ServiceRequest(ServiceRequestCreate):
    id: int
    status: RequestStatus
    created_at: datetime

requests: dict[int, ServiceRequest] = {}
request_ids = count(1)

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post(
     "/requests",
     response_model=ServiceRequest,
     status_code=status.HTTP_201_CREATED,
)
def create_request(request: ServiceRequestCreate):
    request_id = next(request_ids)

    new_request = ServiceRequest(
        id=request_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        status=RequestStatus.open,
        created_at=datetime.now(timezone.utc),
    )

    requests[request_id] = new_request
    return new_request

@app.get("/requests", response_model=list[ServiceRequest])
def list_requests():
    return list(requests.values())

@app.get("/requests/{request_id}", response_model=ServiceRequest)
def get_request(request_id: int):
    request = requests.get(request_id)

    if request is None:
       raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Service request not found",
    )

    return request

@app.patch("/requests/{request_id}/status", response_model=ServiceRequest)
def update_request_status(
request_id: int,
new_status: RequestStatus,
):
    request = requests.get(request_id)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
        )

    updated_request = request.model_copy(update={"status": new_status})
    requests[request_id] = updated_request

    return updated_request

@app.delete("/requests/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_request(request_id: int):
    request = requests.pop(request_id, None)

    if request is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Service request not found",
    )

    return None