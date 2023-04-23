import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CurrentStatus(BaseModel):
    location: str = Field(..., alias="location")
    time: datetime.timedelta = Field(..., alias="time")
    status: str = Field(..., alias="status")


class Origin(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")


class Destination(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")


class Realtime(BaseModel):
    heading: str = Field(..., alias="heading")
    sequence: int = Field(..., alias="sequence")
    train_no: str = Field(..., alias="no")
    destination: Destination = Field(..., alias="destination")
    current_status: CurrentStatus = Field(..., alias="current")
    express_train: bool = Field(..., alias="express")
    last_train: bool = Field(..., alias="last")
    updated_at: datetime.datetime = Field(..., alias="updated_at")


class Timetable(BaseModel):
    weekday: Optional[str] = Field(None, alias="weekday")
    heading: str = Field(..., alias="heading")
    sequence: int = Field(..., alias="sequence")
    origin: Origin = Field(..., alias="origin")
    destination: Destination = Field(..., alias="destination")
    time: datetime.time = Field(..., alias="time")


class RealtimeResponse(BaseModel):
    up: list[Realtime] = Field(..., alias="up")
    down: list[Realtime] = Field(..., alias="down")


class TimetableResponse(BaseModel):
    up: list[Timetable] = Field(..., alias="up")
    down: list[Timetable] = Field(..., alias="down")


class StationListResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    line_list: list[int] = Field(..., alias="lines")


class LineListResponse(BaseModel):
    id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")
    station_list: list[str] = Field(..., alias="stations")


class StationCurrentStatusResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    realtime: RealtimeResponse = Field(..., alias="realtime")
    timetable: TimetableResponse = Field(..., alias="timetable")


class StationTimetableResponse(BaseModel):
    id: str = Field(..., alias="id")
    name: str = Field(..., alias="name")
    weekdays: TimetableResponse = Field(..., alias="weekdays")
    weekends: TimetableResponse = Field(..., alias="weekends")
