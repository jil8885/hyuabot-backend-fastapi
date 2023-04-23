import datetime

from pydantic import BaseModel, Field


class Timetable(BaseModel):
    name: str = Field(..., alias="name")
    time: datetime.time = Field(..., alias="time")


class CurrentLocation(BaseModel):
    start: Timetable = Field(..., alias="from")
    end: Timetable = Field(..., alias="to")


class Route(BaseModel):
    name: str = Field(..., alias="name")
    timetable: list[Timetable] = Field(..., alias="timetable")
    current_location: CurrentLocation = Field(..., alias="current")
