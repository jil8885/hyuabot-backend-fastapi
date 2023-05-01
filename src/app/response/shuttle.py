import datetime

from pydantic import BaseModel, Field


class RouteListItemResponse(BaseModel):
    route_name: str = Field(alias='name')
    route_tag: str = Field(alias='tag')
    description_korean: str = Field(alias='korean')
    description_english: str = Field(alias='english')


class RouteListResponse(BaseModel):
    route_list: list[RouteListItemResponse] = Field(alias='route')


class RouteStopItemResponse(BaseModel):
    stop_name: str = Field(alias='name')
    stop_sequence: int = Field(alias='sequence')
    cumulative_time: datetime.timedelta = Field(alias='time')


class RouteItemResponse(BaseModel):
    route_name: str = Field(alias='name')
    route_tag: str = Field(alias='tag')
    description_korean: str = Field(alias='korean')
    description_english: str = Field(alias='english')
    stop_list: list[RouteStopItemResponse] = Field(alias='stop')


class StopListItemResponse(BaseModel):
    stop_name: str = Field(alias='name')
    latitude: float = Field(alias='latitude')
    longitude: float = Field(alias='longitude')


class StopListResponse(BaseModel):
    stop_list: list[StopListItemResponse] = Field(alias='stop')


class StopItemResponse(BaseModel):
    stop_name: str = Field(alias='name')
    latitude: float = Field(alias='latitude')
    longitude: float = Field(alias='longitude')
    route_list: list[str] = Field(alias='route')


class ArrivalQuery(BaseModel):
    period: str = Field(alias='period')
    weekdays: bool = Field(alias='weekdays')
    holiday: str = Field(alias='holiday')


class ArrivalResponseItem(BaseModel):
    route_name: str = Field(alias='name')
    departure_time: list[datetime.time] = Field(alias='departure_time')
    remaining_time: list[datetime.timedelta] = Field(alias='remaining_time')


class ArrivalResponse(BaseModel):
    stop_name: str = Field(alias='name')
    query: ArrivalQuery = Field(alias='query')
    departure_list: list[ArrivalResponseItem] = Field(alias='departure')


class TimetableResponseItem(BaseModel):
    route_name: str = Field(alias='name')
    weekdays: list[datetime.time] = Field(alias='weekdays')
    weekends: list[datetime.time] = Field(alias='weekends')


class TimetableResponse(BaseModel):
    stop_name: str = Field(alias='name')
    period: str = Field(alias='period')
    departure_list: list[TimetableResponseItem] = Field(alias='departure')
