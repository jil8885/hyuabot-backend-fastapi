from pydantic import BaseModel, Field


class CampusListItemResponse(BaseModel):
    id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")


class CampusListResponse(BaseModel):
    campus: list[CampusListItemResponse] = Field(..., alias="campus")
