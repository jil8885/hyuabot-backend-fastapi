from pydantic import BaseModel, Field


class Campus(BaseModel):
    id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")
