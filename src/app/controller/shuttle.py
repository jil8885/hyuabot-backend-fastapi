from datetime import timedelta, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse

from app.dependancies.database import get_db_session
from app.internal.date_utils import current_period, is_weekends, is_holiday
from app.model.shuttle import ShuttleRoute, ShuttleStop, ShuttleRouteStop, \
    ShuttleTimetableItem
from app.response.shuttle import RouteListResponse, RouteListItemResponse, \
    RouteItemResponse, RouteStopItemResponse, StopListItemResponse, \
    StopListResponse, StopItemResponse, ArrivalResponse, ArrivalQuery, \
    ArrivalResponseItem, TimetableResponse, TimetableResponseItem

shuttle_router = APIRouter()


@shuttle_router.get('/route', response_model=RouteListResponse)
async def get_shuttle_route_list(
        name: str | None = None,
        tag: str | None = None,
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all shuttle routes.
    Args:
        name (str): Name of the shuttle route.
        tag (str): Tag of the shuttle route.
        db_session (AsyncSession): Database session.
    Returns:
        ShuttleRouteList: List of all shuttle routes.
    """
    statement = select(ShuttleRoute)
    filter_conditions: list[ColumnElement] = []
    if name is not None:
        filter_conditions.append(ShuttleRoute.name.like(f'%{name}%'))
    if tag is not None:
        filter_conditions.append(ShuttleRoute.tags == tag)
    if filter_conditions:
        statement = statement.where(and_(*filter_conditions))
    query_result = (await db_session.execute(statement)).scalars().all()
    routes: list[RouteListItemResponse] = []
    for route in query_result:  # type: ShuttleRoute
        routes.append(RouteListItemResponse(
            name=route.name,
            tag=route.tags,
            korean=route.korean,
            english=route.english,
        ))
    return RouteListResponse(route=routes)


@shuttle_router.get('/route/{route_id}', response_model=RouteItemResponse)
async def get_shuttle_route_by_id(
        route_id: str,
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a shuttle route by id.
    Args:
        route_id (str): ID of the shuttle route.
        db_session (AsyncSession): Database session.
    Returns:
        ShuttleRoute: Shuttle route with the given id.
    """
    statement = select(ShuttleRoute).where(
        ShuttleRoute.name == route_id,
    ).options(
        selectinload(ShuttleRoute.stops),
    )
    query_result = (await db_session.execute(statement)) \
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Shuttle route not found.'},
        )
    stop_list = []
    for stop in query_result.stops:  # type: ShuttleRouteStop
        stop_list.append(RouteStopItemResponse(
            name=stop.stop_name,
            sequence=stop.stop_order,
            time=timedelta(minutes=stop.cumulative_time),
        ))
    return RouteItemResponse(
        name=query_result.name,
        tag=query_result.tags,
        korean=query_result.korean,
        english=query_result.english,
        stop=stop_list,
    )


@shuttle_router.get('/stop', response_model=StopListResponse)
async def get_shuttle_stop_list(
        name: str | None = None,
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all shuttle stops.
    Args:
        name (str): Name of the shuttle stop.
        db_session (AsyncSession): Database session.
    Returns:
        StopListResponse: List of all shuttle stops.
    """
    statement = select(ShuttleStop)
    if name is not None:
        statement = statement.where(
            ShuttleStop.name.like(f'%{name}%'),
        )
    query_result = (await db_session.execute(statement)).scalars().all()
    stops: list[StopListItemResponse] = []
    for stop in query_result:  # type: ShuttleStop
        stops.append(StopListItemResponse(
            name=stop.name,
            latitude=stop.latitude,
            longitude=stop.longitude,
        ))
    return StopListResponse(stop=stops)


@shuttle_router.get('/stop/{stop_id}', response_model=StopItemResponse)
async def get_shuttle_stop_by_id(
        stop_id: str,
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a shuttle stop by id.
    Args:
        stop_id (str): ID of the shuttle stop.
        db_session (AsyncSession): Database session.
    Returns:
        ShuttleStop: Shuttle stop with the given id.
    """
    statement = select(ShuttleStop).where(
        ShuttleStop.name == stop_id,
    ).options(
        selectinload(ShuttleStop.routes),
    )
    query_result = (await db_session.execute(statement)) \
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Shuttle stop not found.'},
        )
    return StopItemResponse(
        name=query_result.name,
        latitude=query_result.latitude,
        longitude=query_result.longitude,
        route=[route.route_name for route in query_result.routes],
    )


@shuttle_router.get('/stop/{stop_id}/arrival', response_model=ArrivalResponse)
async def get_shuttle_stop_arrival(
        stop_id: str,
        period: str | None = None,
        weekdays: bool | None = None,
        holiday: str | None = None,
        output: str | None = 'tag',
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get the arrival time of the shuttle stop.
    Args:
        stop_id (str): ID of the shuttle stop.
        period (str): Period of the semester.
        weekdays (str): Weekdays of the week.
        holiday (str): Holiday of the week.
        output (str): Output format.
        db_session (AsyncSession): Database session.
    Returns:
        ArrivalResponse: Arrival time of the shuttle stop.
    """
    now = datetime.now()
    # Complete the query parameters
    if period is None:
        period = await current_period(db_session, now)
    if weekdays is None:
        weekdays = not is_weekends(now)
    if holiday is None:
        holiday = await is_holiday(db_session, now)
    statement = select(ShuttleStop).where(
        ShuttleStop.name == stop_id,
    ).options(
        selectinload(ShuttleStop.routes).options(
            selectinload(ShuttleRouteStop.timetable),
            selectinload(ShuttleRouteStop.route),
        ),
    )
    query_result = (await db_session.execute(statement)) \
        .scalars().first()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Shuttle stop not found.'},
        )
    timetable_list = []
    if output not in ['tag', 'route']:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': 'Invalid output format.'},
        )
    elif output == 'route':
        for route in query_result.routes:  # type: ShuttleRouteStop
            departure_timetable = []
            remaining_timetable = []
            if holiday != 'halt':
                for timetable in list(filter(
                        lambda x: (x.period_type_name == period
                                   and x.weekday == weekdays
                                   and datetime.combine(
                                    now.date(), x.departure_time) >= now),
                        route.timetable,
                )):  # type: ShuttleTimetableItem
                    if timetable.departure_time >= now.time():
                        departure_timetable.append(timetable.departure_time)
                        remaining_timetable.append(
                            datetime.combine(
                                now.date(), timetable.departure_time) - now,
                        )
            timetable_list.append(ArrivalResponseItem(
                name=route.route_name,
                departure_time=departure_timetable,
                remaining_time=remaining_timetable,
            ))
    elif output == 'tag':
        timetable_dict: dict[str, list[datetime.time]] = {
            'DH': [], 'DY': [], 'DJ': [], 'C': [],
        }
        for route in query_result.routes:
            if holiday != 'halt':
                for timetable in filter(
                        lambda x: (x.period_type_name == period
                                   and x.weekday == weekdays
                                   and datetime.combine(
                                    now.date(), x.departure_time) >= now),
                        route.timetable,
                ):  # type: ShuttleTimetableItem
                    timetable_dict[route.route.tags].append(
                        timetable.departure_time,
                    )
        for tag, timetable_items in timetable_dict.items():
            merged_timetable = sorted(timetable_items)
            departure_timetable = []
            remaining_timetable = []
            for timetable_item in merged_timetable:
                departure_timetable.append(timetable_item)
                remaining_timetable.append(
                    datetime.combine(
                        now.date(), timetable_item) - now,
                )
            timetable_list.append(ArrivalResponseItem(
                name=tag,
                departure_time=departure_timetable,
                remaining_time=remaining_timetable,
            ))

    return ArrivalResponse(
        name=query_result.name,
        query=ArrivalQuery(
            period=period,
            weekdays=weekdays,
            holiday=holiday,
        ),
        departure=timetable_list,
    )


@shuttle_router.get(
    '/stop/{stop_id}/timetable', response_model=TimetableResponse)
async def get_shuttle_stop_arrival(
        stop_id: str,
        period: str | None = None,
        output: str | None = 'tag',
        db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get the arrival time of the shuttle stop.
    Args:
        stop_id (str): ID of the shuttle stop.
        period (str): Period of the semester.
        weekdays (str): Weekdays of the week.
        holiday (str): Holiday of the week.
        output (str): Output format.
        db_session (AsyncSession): Database session.
    Returns:
        TimetableResponse: Timetable of the shuttle stop.
    """
    now = datetime.now()
    # Complete the query parameters
    if period is None:
        period = await current_period(db_session, now)
    statement = select(ShuttleStop).where(
        ShuttleStop.name == stop_id,
    ).options(
        selectinload(ShuttleStop.routes).options(
            selectinload(ShuttleRouteStop.timetable),
            selectinload(ShuttleRouteStop.route),
        ),
    )
    query_result = (await db_session.execute(statement)) \
        .scalars().first()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Shuttle stop not found.'},
        )
    timetable_list = []
    if output not in ['tag', 'route']:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={'message': 'Invalid output format.'},
        )
    elif output == 'route':
        for route in query_result.routes:  # type: ShuttleRouteStop
            weekdays_timetable = []
            weekends_timetable = []
            for timetable in list(filter(
                    lambda x: x.period_type_name == period,
                    route.timetable,
            )):  # type: ShuttleTimetableItem
                if timetable.weekday is True:
                    weekdays_timetable.append(timetable.departure_time)
                else:
                    weekends_timetable.append(timetable.departure_time)
            timetable_list.append(TimetableResponseItem(
                name=route.route_name,
                weekdays=weekdays_timetable,
                weekends=weekends_timetable,
            ))
    elif output == 'tag':
        timetable_dict: dict[str, dict[str, list[datetime.time]]] = {
            'DH': {
                'weekdays': [],
                'weekends': [],
            },
            'DY': {
                'weekdays': [],
                'weekends': [],
            },
            'DJ': {
                'weekdays': [],
                'weekends': [],
            },
            'C': {
                'weekdays': [],
                'weekends': [],
            },
        }
        for route in query_result.routes:
            for timetable in filter(
                    lambda x: x.period_type_name == period,
                    route.timetable,
            ):  # type: ShuttleTimetableItem
                if timetable.weekday is True:
                    timetable_dict[route.route.tags]['weekdays'].append(
                        timetable.departure_time,
                    )
                else:
                    timetable_dict[route.route.tags]['weekends'].append(
                        timetable.departure_time,
                    )
        for tag, timetable_for_tag in timetable_dict.items():
            timetable_list.append(TimetableResponseItem(
                name=tag,
                weekdays=sorted(timetable_for_tag['weekdays']),
                weekends=sorted(timetable_for_tag['weekends']),
            ))

    return TimetableResponse(
        name=query_result.name,
        period=period,
        departure=timetable_list,
    )
