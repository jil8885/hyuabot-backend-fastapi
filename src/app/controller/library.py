""" Module that can query the reading room database

Attributes:
    library_router (APIRouter): FastAPI router for the library module.
"""

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.dependancies.database import get_db_session
from app.model.library import ReadingRoom
from app.response.library import ReadingRoom as ReadingRoomResponse
from app.response.library import CampusReadingRoomResponse
from app.response.library import ReadingRoomSeat, ReadingRoomInformation


library_router = APIRouter()


@library_router.get(
    '/{campus_id}/room',
    response_model=CampusReadingRoomResponse,
)
async def get_reading_room_list(
    campus_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a list of reading rooms of a campus.
    Args:
        campus_id (int): ID of the campus.
        db_session (AsyncSession): Database session.
    Returns:
        CampusReadingRoomResponse: Response contains of reading rooms in a
            campus.
    """
    statement = select(ReadingRoom).where(ReadingRoom.campus_id == campus_id)
    query_result = (
        await db_session.execute(statement.options(
            selectinload(ReadingRoom.campus),
        ))
    ).scalars().all()
    reading_rooms = []
    for reading_room in query_result:
        reading_rooms.append(
            ReadingRoomResponse(
                id=reading_room.id,
                name=reading_room.name,
                status=ReadingRoomInformation(
                    active=reading_room.active,
                    reservable=reading_room.reservable,
                ),
                seats=ReadingRoomSeat(
                    total=reading_room.total_seats,
                    active=reading_room.active_seats,
                    occupied=reading_room.occupied_seats,
                    available=reading_room.available_seats,
                ),
                updated_at=reading_room.last_updated_time,
            ),
        )
    return CampusReadingRoomResponse(
        id=campus_id,
        name=query_result[0].campus.name,
        rooms=reading_rooms,
    )


@library_router.get(
    '/{campus_id}/room/{room_id}',
    response_model=ReadingRoomResponse,
)
async def get_reading_room(
    campus_id: int,
    room_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a reading room by id.
    Args:
        campus_id (int): ID of the campus.
        room_id (int): ID of the reading room.
        db_session (AsyncSession): Database session.
    Returns:
        ReadomgRoomResponse: Response contains a reading room
    """
    statement = select(ReadingRoom).where(
        and_(ReadingRoom.campus_id == campus_id, ReadingRoom.id == room_id)
    )
    reading_room = (await db_session.execute(statement))\
        .scalars().one_or_none()
    if reading_room is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Reading room not found'},
        )

    return ReadingRoomResponse(
        id=reading_room.id,
        name=reading_room.name,
        status=ReadingRoomInformation(
            active=reading_room.active,
            reservable=reading_room.reservable,
        ),
        seats=ReadingRoomSeat(
            total=reading_room.total_seats,
            active=reading_room.active_seats,
            occupied=reading_room.occupied_seats,
            available=reading_room.available_seats,
        ),
        updated_at=reading_room.last_updated_time,
    )
