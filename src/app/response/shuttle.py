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
