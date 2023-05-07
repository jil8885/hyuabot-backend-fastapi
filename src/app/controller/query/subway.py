import datetime
from typing import Optional

import strawberry
from sqlalchemy import select, true, and_, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.subway import RouteStation


@strawberry.type
class TimetableItemResponse:
    terminal_id: str = strawberry.field(name="destinationID")
    terminal_name: str = strawberry.field(name="destinationName")
    weekday: str = strawberry.field(name="weekday")
    time: datetime.time = strawberry.field(name="time")


@strawberry.type
class TimetableListResponse:
    up: list[TimetableItemResponse] = strawberry.field(name="up")
    down: list[TimetableItemResponse] = strawberry.field(name="down")


@strawberry.type
class RealtimeItemResponse:
    terminal_id: str = strawberry.field(name="destinationID")
    terminal_name: str = strawberry.field(name="destinationName")
    sequence: int = strawberry.field(name="sequence")
    location: str = strawberry.field(name="location")
    remaining_station: int = strawberry.field(name="remainingStation")
    remaining_time: int = strawberry.field(name="remainingTime")
    train_no: str = strawberry.field(name="trainNo")
    is_express: bool = strawberry.field(name="isExpress")
    is_last: bool = strawberry.field(name="isLast")


@strawberry.type
class RealtimeListResponse:
    up: list[RealtimeItemResponse] = strawberry.field(name="up")
    down: list[RealtimeItemResponse] = strawberry.field(name="down")


@strawberry.type
class StationItem:
    station_id: str = strawberry.field(name="id")
    station_name: str = strawberry.field(name="name")
    line_id: int = strawberry.field(name="lineID")
    line_name: str = strawberry.field(name="lineName")
    sequence: int = strawberry.field(name="sequence")
    timetable: TimetableListResponse = strawberry.field(name="timetable")
    realtime: RealtimeListResponse = strawberry.field(name="realtime")


async def query_subway(
    db_session: AsyncSession,
    station: Optional[list[str]] = None,
    heading: Optional[str] = None,
    weekday: Optional[str] = None,
    timetable_start: Optional[datetime.time] = None,
    timetable_end: Optional[datetime.time] = None,
):
    filters: list[ColumnElement] = []

    if station is not None:
        filters.append(RouteStation.id.in_(station))

    station_statement = select(RouteStation).where(and_(
        true(), *filters,
    )).options(
        selectinload(RouteStation.line),
        selectinload(RouteStation.timetable),
        selectinload(RouteStation.realtime),
    )
    stations = (await db_session.execute(station_statement)).scalars().all()

    result: list[StationItem] = []
    for station_item in stations:  # type: RouteStation
        station_timetable_dict: dict[str, list[TimetableItemResponse]] = \
            {'up': [], 'down': []}
        station_realtime_dict: dict[str, list[RealtimeItemResponse]] = \
            {'up': [], 'down': []}
        for timetable_item in station_item.timetable:
            if heading is not None and timetable_item.heading != heading:
                continue
            if weekday is not None and timetable_item.weekday != weekday:
                continue
            if timetable_start is not None and \
                    (timetable_start >
                     timetable_item.departure_time > datetime.time(4, 0)):
                continue
            if timetable_end is not None and \
                    timetable_end < timetable_item.departure_time:
                continue
            station_timetable_dict[timetable_item.heading].append(
                TimetableItemResponse(
                    terminal_id=timetable_item.destination.id,
                    terminal_name=timetable_item.destination.station_name,
                    weekday=timetable_item.weekday,
                    time=timetable_item.departure_time,
                ),
            )
        for realtime_item in station_item.realtime:
            heading = 'up' if realtime_item.heading == 'true' else 'down'
            station_realtime_dict[heading].append(
                RealtimeItemResponse(
                    terminal_id=realtime_item.destination.id,
                    terminal_name=realtime_item.destination.station_name,
                    sequence=realtime_item.sequence,
                    location=realtime_item.location,
                    remaining_station=realtime_item.stop,
                    remaining_time=realtime_item.minute,
                    train_no=realtime_item.train,
                    is_express=realtime_item.express,
                    is_last=realtime_item.last,
                ),
            )
        result.append(StationItem(
            station_id=station_item.id,
            station_name=station_item.station_name,
            line_id=station_item.line.id,
            line_name=station_item.line.name,
            sequence=station_item.sequence,
            timetable=TimetableListResponse(
                up=station_timetable_dict['up'],
                down=station_timetable_dict['down'],
            ),
            realtime=RealtimeListResponse(
                up=station_realtime_dict['up'],
                down=station_realtime_dict['down'],
            ),
        ))
    return result
