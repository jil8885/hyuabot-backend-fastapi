import datetime
from typing import Optional

import strawberry
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.internal.date_utils import current_period, is_weekends
from app.model.shuttle import ShuttleRouteStop, ShuttleStop, ShuttleRoute


@strawberry.type
class ShuttleArrivalOtherStopItem:
    stop_name: str = strawberry.field(name="stopName")
    timedelta: int = strawberry.field(name="timedelta")
    time: datetime.time = strawberry.field(name="time")


@strawberry.type
class ShuttleArrivalTimeItem:
    weekdays: bool = strawberry.field(name="weekdays")
    time: datetime.time = strawberry.field(name="time")
    remaining_time: float = strawberry.field(name="remainingTime")
    other_stops: list[ShuttleArrivalOtherStopItem] = \
        strawberry.field(name="otherStops")


@strawberry.type
class ShuttleRouteStopItem:
    route_id: str = strawberry.field(name="routeID")
    description_korean: str = strawberry.field(name="descriptionKorean")
    description_english: str = strawberry.field(name="descriptionEnglish")
    timetable: list[ShuttleArrivalTimeItem] = \
        strawberry.field(name="timetable")


@strawberry.type
class ShuttleTagStopItem:
    tag_id: str = strawberry.field(name="tagID")
    timetable: list[ShuttleArrivalTimeItem] = \
        strawberry.field(name="timetable")


@strawberry.type
class ShuttleStopLocationItem:
    latitude: float = strawberry.field(name="latitude")
    longitude: float = strawberry.field(name="longitude")


@strawberry.type
class ShuttleStopItem:
    name: str = strawberry.field(name="stopName")
    location: ShuttleStopLocationItem = strawberry.field(name="location")
    routes: list[ShuttleRouteStopItem] = strawberry.field(name="route")
    tags: list[ShuttleTagStopItem] = strawberry.field(name="tag")


@strawberry.type
class ShuttleQueryItem:
    period: list[str] = strawberry.field(name="period")
    weekday: list[bool] = strawberry.field(name="weekday")


@strawberry.type
class ShuttleItem:
    stops: list[ShuttleStopItem] = strawberry.field(name="stop")
    params: ShuttleQueryItem = strawberry.field(name="params")


async def query_shuttle(
    db_session: AsyncSession,
    stop_query: Optional[list[str]] = None,
    route_query: Optional[list[str]] = None,
    tag_query: Optional[list[str]] = None,
    period_query: Optional[list[str]] = None,
    weekday_query: Optional[list[bool]] = None,
    date_query: Optional[datetime.datetime] = None,
    timetable_start: Optional[datetime.time] = None,
    timetable_end: Optional[datetime.time] = None,
) -> ShuttleItem:
    filters = []
    if date_query is None:
        date_query = datetime.datetime.now()
    if stop_query:
        filters.append(ShuttleStop.name.in_(stop_query))
    if period_query is None:
        period_query = [(await current_period(db_session, date_query))]
    if weekday_query is None:
        weekday_query = [not is_weekends(date_query.date())]
    statement = select(ShuttleStop).where(*filters).options(
        selectinload(ShuttleStop.routes).options(
            selectinload(ShuttleRouteStop.route).options(
                selectinload(ShuttleRoute.stops),
            ),
            selectinload(ShuttleRouteStop.timetable),
        ),
    )
    query_result = (await db_session.execute(statement)).scalars().all()
    result: list[ShuttleStopItem] = []
    for stop in query_result:  # type: ShuttleStop
        route_dict = {}
        tag_dict = {}
        for route in stop.routes:  # type: ShuttleRouteStop
            route_stop_list: list[dict] = []
            for other in route.route.stops:  # type: ShuttleRouteStop
                route_stop_list.append({
                    "stop_name": other.stop_name,
                    "timedelta": other.cumulative_time - route.cumulative_time,
                })
            if route_query is not None and route.route.name not in route_query:
                continue
            if tag_query is not None and route.route.tags not in tag_query:
                continue
            timetable: list[ShuttleArrivalTimeItem] = []
            for timetable_item in route.timetable:
                if timetable_item.period_type_name not in period_query:
                    continue
                elif timetable_item.weekday not in weekday_query:
                    continue
                elif timetable_start is not None and \
                        timetable_item.departure_time < timetable_start:
                    continue
                elif timetable_end is not None and \
                        timetable_item.departure_time > timetable_end:
                    continue
                remaining_time = (datetime.datetime.combine(
                    date_query.date(),
                    timetable_item.departure_time,
                ) - date_query).total_seconds()
                other_stops: list[ShuttleArrivalOtherStopItem] = []
                for other_stop in route_stop_list:
                    other_stops.append(ShuttleArrivalOtherStopItem(
                        stop_name=other_stop["stop_name"],
                        timedelta=other_stop["timedelta"],
                        time=(datetime.datetime.combine(
                            date_query.date(),
                            timetable_item.departure_time,
                        ) + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        )).time(),
                    ))
                timetable.append(ShuttleArrivalTimeItem(
                    weekdays=timetable_item.weekday,
                    time=timetable_item.departure_time,
                    remaining_time=remaining_time,
                    other_stops=other_stops,
                ))
            if route.route.name not in route_dict:
                route_dict[route.route.name] = ShuttleRouteStopItem(
                    route_id=route.route.name,
                    description_korean=route.route.korean,
                    description_english=route.route.english,
                    timetable=timetable,
                )
            if route.route.tags not in tag_dict:
                tag_dict[route.route.tags] = ShuttleTagStopItem(
                    tag_id=route.route.tags,
                    timetable=[],
                )
            tag_dict[route.route.tags].timetable.extend(timetable)
        for route_item in route_dict.values():
            route_item.timetable.sort(key=lambda x: x.remaining_time)
        for tag_item in tag_dict.values():
            tag_item.timetable.sort(key=lambda x: x.remaining_time)
        result.append(ShuttleStopItem(
            name=stop.name,
            location=ShuttleStopLocationItem(
                latitude=stop.latitude,
                longitude=stop.longitude,
            ),
            routes=list(route_dict.values()),
            tags=list(tag_dict.values()),
        ))
    return ShuttleItem(
        stops=result,
        params=ShuttleQueryItem(
            period=period_query,
            weekday=weekday_query,
        ),
    )
