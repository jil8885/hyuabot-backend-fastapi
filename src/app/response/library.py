import datetime

from pydantic import BaseModel, Field

from app.response.campus import CampusListItemResponse


class ReadingRoomInformation(BaseModel):
    active: bool = Field(..., alias="active")
    reservable: bool = Field(..., alias="reservable")


class ReadingRoomSeat(BaseModel):
    total: int = Field(..., alias="total")
    active: int = Field(..., alias="active")
    occupied: int = Field(..., alias="occupied")
    available: int = Field(..., alias="available")


class ReadingRoom(BaseModel):
    id: int = Field(..., alias="id")
    name: str = Field(..., alias="name")
    status: ReadingRoomInformation = Field(..., alias="status")
    seats: ReadingRoomSeat = Field(..., alias="seats")
    updated_at: datetime.datetime = Field(..., alias="updated_at")


class CampusReadingRoomResponse(CampusListItemResponse):
    reading_rooms: list[ReadingRoom] = Field(..., alias="rooms")
