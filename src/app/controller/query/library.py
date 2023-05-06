import datetime
from typing import Optional

import strawberry
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.library import ReadingRoom


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


async def query_reading_room(
    db_session: AsyncSession,
    campus: Optional[int] = None,
    room: Optional[list[int]] = None,
    active: Optional[bool] = None,
) -> list[ReadingRoomItem]:
    filters = []
    if campus is not None:
        filters.append(ReadingRoom.campus_id == campus)
    if room is not None:
        filters.append(ReadingRoom.id.in_(room))
    if active is not None:
        filters.append(ReadingRoom.active == active)

    if len(filters) == 0:
        statement = select(ReadingRoom)
    else:
        statement = select(ReadingRoom).where(and_(*filters))

    query_result = (await db_session.execute(statement)).scalars().all()
    result: list[ReadingRoomItem] = []
    for row in query_result:
        result.append(ReadingRoomItem(
            campus_id=row.campus_id,
            id=row.id,
            name=row.name,
            status=ReadingRoomInformation(
                active=row.active,
                reservable=row.reservable,
            ),
            seats=ReadingRoomSeat(
                total=row.total_seats,
                active=row.active_seats,
                occupied=row.occupied_seats,
                available=row.available_seats,
            ),
            updated_at=row.last_updated_time,
        ))
    return result
