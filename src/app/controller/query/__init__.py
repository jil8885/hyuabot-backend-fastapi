import datetime
from typing import Optional

import strawberry
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info

from app.controller.query.bus import query_bus, BusRouteStopItem, \
    BusRouteStopQuery
from app.controller.query.cafeteria import CafeteriaItem, query_cafeteria
from app.controller.query.commute_shuttle import query_commute_shuttle, \
    CommuteShuttleRoute
from app.controller.query.library import ReadingRoomItem, query_reading_room
from app.controller.query.shuttle import query_shuttle, ShuttleItem
from app.controller.query.subway import StationItem, query_subway
from app.dependancies.database import get_db_session


@strawberry.type
class Query:
    @strawberry.field
    async def shuttle(
        self,
        info: Info,
        stop: Optional[list[str]] = None,
        route: Optional[list[str]] = None,
        tag: Optional[list[str]] = None,
        period: Optional[list[str]] = None,
        weekday: Optional[list[bool]] = None,
        date: Optional[datetime.datetime] = None,
        start: Optional[datetime.time] = None,
        end: Optional[datetime.time] = None,
    ) -> ShuttleItem:
        if tag is not None and route is not None:
            raise ValueError("tag and route cannot be used together")
        db_session: AsyncSession = info.context['db_session']
        result = await query_shuttle(
            db_session,
            stop_query=stop,
            route_query=route,
            tag_query=tag,
            period_query=period,
            weekday_query=weekday,
            date_query=date,
            timetable_start=start,
            timetable_end=end,
        )
        return result

    @strawberry.field
    async def commute_shuttle(
        self,
        info: Info,
        name: Optional[str] = None,
    ) -> list[CommuteShuttleRoute]:
        db_session: AsyncSession = info.context['db_session']
        result = await query_commute_shuttle(
            db_session,
            name=name,
        )
        return result

    @strawberry.field
    async def bus(
        self,
        info: Info,
        route_stop: list[BusRouteStopQuery],
        weekdays: Optional[list[str]] = None,
        date: datetime.date = datetime.date.today(),
        start: Optional[datetime.time] = None,
        end: Optional[datetime.time] = None,
    ) -> list[BusRouteStopItem]:
        db_session: AsyncSession = info.context['db_session']
        result = await query_bus(
            db_session,
            route_stop=route_stop,
            weekdays=weekdays,
            date=date,
            timetable_start=start,
            timetable_end=end,
        )
        return result

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
