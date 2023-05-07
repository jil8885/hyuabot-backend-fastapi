import datetime
from typing import Optional

import holidays
import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.bus import BusRouteStop


@strawberry.input
class BusRouteStopQuery:
    stop: int
    route: int


@strawberry.type
class BusRealtime:
    stop: int = strawberry.field(name='remainingStop')
    time: int = strawberry.field(name='remainingTime')
    seat: int = strawberry.field(name='remainingSeat')
    low_floor: bool = strawberry.field(name='lowFloor')
    updated_at: datetime.datetime = strawberry.field(name='updatedAt')


@strawberry.type
class BusTimetable:
    weekday: str = strawberry.field(name='weekday')
    time: datetime.time = strawberry.field(name='time')


@strawberry.type
class BusRouteStopItem:
    stop_id: int = strawberry.field(name='stopID')
    stop_name: str = strawberry.field(name='stopName')
    route_id: int = strawberry.field(name='routeID')
    route_name: str = strawberry.field(name='routeName')
    sequence: int = strawberry.field(name='sequence')
    start_stop_id: int = strawberry.field(name='startStopID')
    start_stop_name: str = strawberry.field(name='startStopName')
    realtime: list[BusRealtime] = strawberry.field(name='realtime')
    timetable: list[BusTimetable] = strawberry.field(name='timetable')


async def query_bus(
    db_session: AsyncSession,
    route_stop: list[BusRouteStopQuery],
    weekdays: Optional[list[str]] = None,
    date: datetime.date = datetime.date.today(),
    timetable_start: Optional[datetime.time] = None,
    timetable_end: Optional[datetime.time] = None,
) -> list[BusRouteStopItem]:
    result: list[BusRouteStopItem] = []
    korean_holidays = holidays.KR()
    for query in route_stop:
        statement = select(BusRouteStop).where(
            BusRouteStop.stop_id == query.stop,
            BusRouteStop.route_id == query.route,
        ).options(
            selectinload(BusRouteStop.stop),
            selectinload(BusRouteStop.route),
            selectinload(BusRouteStop.realtime),
            selectinload(BusRouteStop.timetable),
            selectinload(BusRouteStop.start_stop),
        )
        query_result: Optional[BusRouteStop] = (
            await db_session.execute(statement)
        ).scalars().first()
        if query_result is None:
            continue

        realtime_list: list[BusRealtime] = []
        for realtime in query_result.realtime:
            realtime_list.append(BusRealtime(
                stop=realtime.stop,
                time=realtime.minutes,
                seat=realtime.seat,
                low_floor=realtime.low_floor,
                updated_at=realtime.last_updated_time,
            ))

        timetable_list: list[BusTimetable] = []

        for timetable in query_result.timetable:
            if weekdays is None:
                if date in korean_holidays or date.weekday() == 6:
                    if timetable.weekday != 'sunday':
                        continue
                elif date.weekday() == 5:
                    if timetable.weekday != 'saturday':
                        continue
                elif timetable.weekday != 'weekdays':
                    continue
            else:
                if timetable.weekday not in weekdays:
                    continue

            if timetable_start is not None and timetable_start > \
                    timetable.departure_time > datetime.time(4, 0, 0):
                continue
            if timetable_end is not None and \
                    timetable_end < timetable.departure_time:
                continue
            timetable_list.append(BusTimetable(
                weekday=timetable.weekday,
                time=timetable.departure_time,
            ))
        result.append(BusRouteStopItem(
            stop_id=query_result.stop_id,
            stop_name=query_result.stop.name,
            route_id=query_result.route_id,
            route_name=query_result.route.name,
            sequence=query_result.order,
            start_stop_id=query_result.start_stop.id,
            start_stop_name=query_result.start_stop.name,
            realtime=realtime_list,
            timetable=timetable_list,
        ))
    return result
