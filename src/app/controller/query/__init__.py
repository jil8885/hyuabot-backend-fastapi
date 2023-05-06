import datetime
from typing import Optional

import strawberry
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.controller.query.cafeteria import CafeteriaItem, query_cafeteria
from app.controller.query.library import ReadingRoomItem, query_reading_room
from app.controller.query.subway import StationItem, query_subway
from app.dependancies.database import get_db_session


@strawberry.type
class Query:
    @strawberry.field
    async def subway(
        self,
        info: Info,
        station: Optional[list[str]] = None,
        heading: Optional[str] = None,
        weekday: Optional[str] = None,
        start: Optional[datetime.time] = None,
        end: Optional[datetime.time] = None,
    ) -> list[StationItem]:
        db_session: AsyncSession = info.context['db_session']
        result = await query_subway(
            db_session,
            station=station,
            heading=heading,
            weekday=weekday,
            timetable_start=start,
            timetable_end=end,
        )
        return result

    @strawberry.field
    async def reading_room(
        self,
        info: Info,
        campus: Optional[int] = None,
        room: Optional[list[int]] = None,
        active: Optional[bool] = None,
    ) -> list[ReadingRoomItem]:
        db_session: AsyncSession = info.context['db_session']
        result = await query_reading_room(
            db_session,
            campus=campus,
            room=room,
            active=active,
        )
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
