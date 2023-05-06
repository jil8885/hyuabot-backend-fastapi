import datetime
from typing import Optional

import strawberry
from sqlalchemy import select, true, or_, and_, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.subway import RouteStation, TimetableItem, RealtimeItem


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
    station_filters: list[ColumnElement] = []
    realtime_filters: list[ColumnElement] = []
    timetable_filters: list[ColumnElement] = []

    if station is not None:
        station_filters.append(RouteStation.id.in_(station))
        realtime_filters.append(RealtimeItem.station_id.in_(station))
        timetable_filters.append(TimetableItem.station_id.in_(station))
    if heading is not None:
        realtime_heading = 'true' if heading == 'up' else 'false'
        timetable_filters.append(TimetableItem.heading == heading)
        realtime_filters.append(RealtimeItem.heading == realtime_heading)
    if timetable_start is not None:
        timetable_filters.append(or_(
            TimetableItem.departure_time >= timetable_start,
            TimetableItem.departure_time <= datetime.time(4, 59, 59),
        ))
    if timetable_end is not None:
        timetable_filters.append(
            TimetableItem.departure_time <= timetable_end)
    if weekday is not None:
        timetable_filters.append(TimetableItem.weekday == weekday)

    station_statement = select(RouteStation).where(and_(
        true(), *station_filters,
    )).options(
        selectinload(RouteStation.line),
    )
    stations = (await db_session.execute(station_statement)).scalars().all()

    realtime_statement = select(RealtimeItem).where(and_(
        true(), *realtime_filters,
    )).options(
        selectinload(RealtimeItem.destination),
    )
    realtime_dict: dict[str, list[RealtimeItem]] = {}
    realtime_items = (
        await db_session.execute(realtime_statement)
    ).scalars().all()
    for realtime_item in realtime_items:  # type: RealtimeItem
        if realtime_item.station_id not in realtime_dict:
            realtime_dict[realtime_item.station_id] = []
        realtime_dict[realtime_item.station_id].append(realtime_item)

    timetable_statement = select(TimetableItem).where(and_(
        true(), *timetable_filters,
    )).options(
        selectinload(TimetableItem.destination),
    )
    timetable_dict: dict[str, list[TimetableItem]] = {}
    timetable_items = (
        await db_session.execute(timetable_statement)
    ).scalars().all()
    for timetable_item in timetable_items:  # type: TimetableItem
        if timetable_item.station_id not in timetable_dict:
            timetable_dict[timetable_item.station_id] = []
        timetable_dict[timetable_item.station_id].append(timetable_item)
    result: list[StationItem] = []
    for station_item in stations:  # type: RouteStation
        station_timetable_dict: dict[str, list[TimetableItemResponse]] = \
            {'up': [], 'down': []}
        station_realtime_dict: dict[str, list[RealtimeItemResponse]] = \
            {'up': [], 'down': []}
        if station_item.id in timetable_dict:
            for timetable_item in timetable_dict[station_item.id]:
                station_timetable_dict[timetable_item.heading].append(
                    TimetableItemResponse(
                        terminal_id=timetable_item.destination.id,
                        terminal_name=timetable_item.destination.station_name,
                        weekday=timetable_item.weekday,
                        time=timetable_item.departure_time,
                    ),
                )
        if station_item.id in realtime_dict:
            for realtime_item in realtime_dict[station_item.id]:
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
