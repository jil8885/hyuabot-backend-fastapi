import datetime

from pydantic import BaseModel, Field


class Company(BaseModel):
    company_id: int = Field(..., alias="id")
    company_name: str = Field(..., alias="name")
    company_telephone: str = Field(..., alias="telephone")


class Type(BaseModel):
    type_id: str = Field(..., alias="id")
    type_name: str = Field(..., alias="name")


class Terminal(BaseModel):
    bus_stop_id: int = Field(..., alias="id")
    bus_stop_name: str = Field(..., alias="name")
    mobile_no: str = Field(..., alias="mobile")
    first_bus: datetime.time = Field(..., alias="first")
    last_bus: datetime.time = Field(..., alias="last")


class RouteListItemResponse(BaseModel):
    route_id: int = Field(..., alias="id")
    route_name: str = Field(..., alias="name")


class RouteListResponse(BaseModel):
    route_list: list[RouteListItemResponse] = Field(..., alias="route")


class RouteResponse(BaseModel):
    route_id: int = Field(..., alias="id")
    route_name: str = Field(..., alias="name")
    company: Company = Field(..., alias="company")
    route_type: Type = Field(..., alias="type")
    origin: Terminal = Field(..., alias="origin")
    terminal: Terminal = Field(..., alias="terminal")


class StopListItemResponse(BaseModel):
    stop_id: int = Field(..., alias="id")
    stop_name: str = Field(..., alias="name")
    mobile_no: str = Field(..., alias="mobile")


class StopListResponse(BaseModel):
    stop_list: list[StopListItemResponse] = Field(..., alias="stop")


class RouteStopResponse(BaseModel):
    route_id: int = Field(..., alias="id")
    stop_sequence: int = Field(..., alias="sequence")


class Realtime(BaseModel):
    arrival_sequence: int = Field(..., alias="sequence")
    remaining_stop: int = Field(..., alias="stop")
    remaining_seat: int = Field(..., alias="seat")
    remaining_time: datetime.timedelta = Field(..., alias="time")
    low_plate: bool = Field(..., alias="low_plate")
    updated_at: datetime.datetime = Field(..., alias="updated_at")


class RouteArrivalResponse(RouteStopResponse):
    arrival_list: list[Realtime] = Field(..., alias="arrival")
    timetable_list: list[datetime.time] = Field(..., alias="timetable")


class RouteTimetableResponse(RouteStopResponse):
    weekdays: list[datetime.time] = Field(..., alias="weekdays")
    saturdays: list[datetime.time] = Field(..., alias="saturdays")
    sundays: list[datetime.time] = Field(..., alias="sundays")


class StopResponse(BaseModel):
    stop_id: int = Field(..., alias="id")
    stop_name: str = Field(..., alias="name")
    mobile_no: str = Field(..., alias="mobile")
    route: list[RouteStopResponse] = Field(..., alias="route")
