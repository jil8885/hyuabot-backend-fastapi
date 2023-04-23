import datetime

from pydantic import BaseModel, Field


class RouteListItemResponse(BaseModel):
    route_name: str = Field(..., alias="name")
    route_tag: str = Field(..., alias="tag")


class RouteListResponse(BaseModel):
    route_list: list[RouteListItemResponse] = Field(..., alias="route")


class StopListItemResponse(BaseModel):
    stop_name: str = Field(..., alias="name")
    latitude: float = Field(..., alias="latitude")
    longitude: float = Field(..., alias="longitude")


class StopListResponse(BaseModel):
    stop_list: list[StopListItemResponse] = Field(..., alias="stop")


class TagStopResponse(BaseModel):
    route_tag: str = Field(..., alias="tag")


class ArrivalTimeResponse(BaseModel):
    stop_name: str = Field(..., alias="name")
    remaining_time: datetime.timedelta = Field(..., alias="remaining_time")


class TagStopArrivalItemResponse(BaseModel):
    route_name: str = Field(..., alias="name")
    remaining_time: datetime.timedelta = Field(..., alias="remaining_time")
    departure_time: datetime.time = Field(..., alias="departure_time")
    arrival_time: list[ArrivalTimeResponse] = Field(..., alias="arrival_time")


class TagStopArrivalResponse(TagStopResponse):
    arrival_list: list[TagStopArrivalItemResponse] = \
        Field(..., alias="arrival")


class StopResponse(BaseModel):
    stop_name: str = Field(..., alias="name")
    latitude: float = Field(..., alias="latitude")
    longitude: float = Field(..., alias="longitude")


class TagStopTimetableItemResponse(BaseModel):
    route_name: str = Field(..., alias="name")
    departure_time: datetime.time = Field(..., alias="departure_time")


class TagStopTimetableResponse(TagStopResponse):
    weekdays: list[TagStopTimetableItemResponse] = Field(..., alias="weekdays")
    weekends: list[TagStopTimetableItemResponse] = Field(..., alias="weekends")
