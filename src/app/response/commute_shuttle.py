import datetime

from pydantic import BaseModel, Field


class CommuteShuttleTimetableResponse(BaseModel):
    name: str = Field(alias='name')
    time: datetime.time = Field(alias='time')


class CommuteShuttleCurrentLocation(BaseModel):
    start: CommuteShuttleTimetableResponse = Field(alias='start')
    end: CommuteShuttleTimetableResponse = Field(alias='end')


class CommuteShuttleRouteResponse(BaseModel):
    name: str = Field(alias='name')
    timetable: list[CommuteShuttleTimetableResponse] = Field(alias='timetable')
    current_location: CommuteShuttleCurrentLocation = Field(alias='current')
    status: str = Field(alias='status')


class CommuteShuttleListItem(BaseModel):
    route_id: str = Field(alias='id')
    route_description_korean: str = Field(alias='korean')
    route_description_english: str = Field(alias='english')


class CommuteShuttleList(BaseModel):
    route_list: list[CommuteShuttleListItem] = Field(alias='route')


class CommuteShuttleArrivalListItem(BaseModel):
    name: str = Field(alias='name')
    korean: str = Field(alias='korean')
    english: str = Field(alias='english')
    current_location: CommuteShuttleCurrentLocation = Field(alias='current')


class CommuteShuttleArrivalList(BaseModel):
    route_list: list[CommuteShuttleArrivalListItem] = Field(alias='route')
    status: str = Field(alias='status')
