import datetime
from typing import Optional

import strawberry
from fastapi import Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.controller.query.cafeteria import CafeteriaItem, query_cafeteria
from app.controller.query.library import ReadingRoomItem, \
    ReadingRoomInformation, ReadingRoomSeat
from app.dependancies.database import get_db_session
from app.model.library import ReadingRoom


@strawberry.type
class Query:
    @strawberry.field
    async def reading_room(
        self,
        info: Info,
        campus: Optional[int] = None,
        room: Optional[list[int]] = None,
        active: Optional[bool] = None,
    ) -> list[ReadingRoomItem]:
        db_session: AsyncSession = info.context['db_session']

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

    @strawberry.field
    async def cafeteria(
        self,
        info: Info,
        campus: Optional[int] = None,
        restaurant: Optional[list[int]] = None,
        date: Optional[datetime.date] = None,
        slot: Optional[str] = None,
    ) -> list[CafeteriaItem]:
        result: list[CafeteriaItem] = await query_cafeteria(
            info.context['db_session'],
            campus=campus,
            restaurant=restaurant,
            date=date,
            slot=slot,
        )
        return result


async def graphql_context(
    db_session: AsyncSession = Depends(get_db_session),
) -> dict[str, AsyncSession]:
    """Function to get the GraphQL context.
    Args:
        db_session (AsyncSession): Database session.
    Returns:
        dict[str, AsyncSession]: GraphQL context.
    """
    return {'db_session': db_session}


schema = strawberry.Schema(query=Query)
graphql_router: GraphQLRouter = GraphQLRouter(
    schema, context_getter=graphql_context)
