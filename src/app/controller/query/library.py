import datetime

import strawberry


@strawberry.type
class ReadingRoomInformation:
    active: bool
    reservable: bool


@strawberry.type
class ReadingRoomSeat:
    total: int
    active: int
    occupied: int
    available: int


@strawberry.type
class ReadingRoomItem:
    campus_id: int
    id: int
    name: str
    status: ReadingRoomInformation
    seats: ReadingRoomSeat
    updated_at: datetime.datetime
