import datetime
from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload
from starlette import status
from starlette.responses import JSONResponse

from app.dependancies.database import get_db_session
from app.internal.date_utils import is_weekends
from app.model.bus import BusRoute, BusStop, BusRouteStop
from app.response.bus import RouteListResponse, RouteListItemResponse, \
    RouteResponse, Company, Type, Terminal, StopListResponse, \
    StopListItemResponse, StopResponse, Location, \
    StopArrivalResponse, RouteArrivalResponse, Realtime, RouteTimetableResponse

bus_router = APIRouter()


@bus_router.get('/route', response_model=RouteListResponse)
async def get_bus_route(
    name: str | None = None,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all bus routes.
    Args:
        name (str): Name of the bus route.
        db_session (AsyncSession): Database session.
    Returns:
        RouteListResponse: List of all bus routes.
    """
    if name is not None:
        statement = select(BusRoute).where(BusRoute.name.like(f'%{name}%'))
    else:
        statement = select(BusRoute)
    query_result = (await db_session.execute(statement)).scalars().all()
    routes: list[RouteListItemResponse] = []
    for route in query_result:
        routes.append(RouteListItemResponse(id=route.id, name=route.name))
    return RouteListResponse(route=routes)


@bus_router.get('/route/{route_id}', response_model=RouteResponse)
async def get_bus_route_by_id(
    route_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a bus route by id.
    Args:
        route_id (int): ID of the bus route.
        db_session (AsyncSession): Database session.
    Returns:
        RouteResponse: Bus route with the given id.
    """
    statement = select(BusRoute).where(BusRoute.id == route_id).options(
        joinedload(BusRoute.start_stop),
        joinedload(BusRoute.end_stop),
    )
    query_result: BusRoute | None = (await db_session.execute(statement))\
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Bus route not found.'},
        )
    return RouteResponse(
        id=query_result.id,
        name=query_result.name,
        company=Company(
            id=query_result.company_id,
            name=query_result.company_name,
            telephone=query_result.company_telephone,
        ),
        type=Type(
            id=query_result.type_code,
            name=query_result.type_name,
        ),
        origin=Terminal(
            id=query_result.start_stop_id,
            name=query_result.start_stop.name,
            mobile=query_result.start_stop.mobile_number,
            first=query_result.up_first_time,
            last=query_result.up_last_time,
        ),
        terminal=Terminal(
            id=query_result.end_stop_id,
            name=query_result.end_stop.name,
            mobile=query_result.end_stop.mobile_number,
            first=query_result.down_first_time,
            last=query_result.down_last_time,
        ),
    )


@bus_router.get('/stop', response_model=StopListResponse)
async def get_bus_stop(
    name: str | None = None,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all bus stops.
    Args:
        name (str): Name of the bus stop.
        db_session (AsyncSession): Database session.
    Returns:
        StopListResponse: List of all bus stops.
    """
    if name is not None:
        statement = select(BusStop).where(BusStop.name.like(f'%{name}%'))
    else:
        statement = select(BusStop)
    query_result = (await db_session.execute(statement)).scalars().all()
    stops: list[StopListItemResponse] = []
    for route in query_result:
        stops.append(StopListItemResponse(
            id=route.id,
            name=route.name,
            mobile=route.mobile_number,
        ))
    return StopListResponse(stop=stops)


@bus_router.get('/stop/{stop_id}', response_model=StopResponse)
async def get_bus_stop_by_id(
    stop_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a bus stop by id.
    Args:
        stop_id (int): ID of the bus stop.
        db_session (AsyncSession): Database session.
    Returns:
        StopResponse: Bus stop with the given id.
    """
    statement = select(BusStop).where(BusStop.id == stop_id).options(
        selectinload(BusStop.routes),
    )
    query_result: BusStop | None = (await db_session.execute(statement))\
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Bus stop not found.'},
        )
    return StopResponse(
        id=query_result.id,
        name=query_result.name,
        mobile=query_result.mobile_number,
        location=Location(
            latitude=query_result.latitude,
            longitude=query_result.longitude,
            district=query_result.district,
            region=query_result.region,
        ),
    )


@bus_router.get('/stop/{stop_id}/arrival', response_model=StopArrivalResponse)
async def get_bus_stop_arrival(
    stop_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a bus stop arrival by id.
    Args:
        stop_id (int): ID of the bus stop.
        db_session (AsyncSession): Database session.
    Returns:
        StopArrivalResponse: Bus stop arrival with the given id.
    """
    statement = select(BusStop).where(BusStop.id == stop_id).options(
        selectinload(BusStop.routes).options(
            selectinload(BusRouteStop.route),
            selectinload(BusRouteStop.realtime),
            selectinload(BusRouteStop.timetable),
        ),
    )
    query_result: BusStop | None = (await db_session.execute(statement))\
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Bus stop not found.'},
        )
    routes: list[RouteArrivalResponse] = []
    now = datetime.datetime.now()
    weekdays = 'weekdays'
    if now.weekday() == 5:
        weekdays = 'saturday'
    elif now.weekday() == 6 or is_weekends(now.today()):
        weekdays = 'sunday'
    for route in query_result.routes:
        realtime_list: list[Realtime] = []
        for index, realtime in enumerate(route.realtime):
            realtime_list.append(Realtime(
                sequence=index + 1,
                stop=realtime.stop,
                seat=realtime.seat,
                time=timedelta(minutes=realtime.minutes),
                low_plate=realtime.low_floor,
                updated_at=realtime.last_updated_time,
            ))
        timetable_list: list[datetime.time] = []
        for timetable in filter(
            lambda x: (x.weekday == weekdays
                       and x.departure_time > now.time()),
            route.timetable,
        ):
            timetable_list.append(timetable.departure_time)
        routes.append(RouteArrivalResponse(
            id=route.route_id,
            name=route.route.name,
            sequence=route.order,
            arrival=realtime_list,
            timetable=timetable_list,
        ))
    return StopArrivalResponse(
        id=query_result.id,
        name=query_result.name,
        mobile=query_result.mobile_number,
        location=Location(
            latitude=query_result.latitude,
            longitude=query_result.longitude,
            district=query_result.district,
            region=query_result.region,
        ),
        route=routes,
    )


@bus_router.get(
    '/stop/{stop_id}/route/{route_id}/timetable',
    response_model=RouteTimetableResponse,
)
async def get_bus_stop_timetable(
    stop_id: int,
    route_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a bus stop timetable by id.
    Args:
        stop_id (int): ID of the bus stop.
        route_id (int): ID of the bus route.
        db_session (AsyncSession): Database session.
    Returns:
        RouteTimetableResponse: Bus stop timetable with the given id.
    """
    statement = select(BusRouteStop).where(
        and_(
            BusRouteStop.stop_id == stop_id,
            BusRouteStop.route_id == route_id,
        ),
    ).options(
        selectinload(BusRouteStop.timetable),
    )
    query_result: BusRouteStop | None = (await db_session.execute(statement))\
        .scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Bus route - stop not found.'},
        )
    return RouteTimetableResponse(
        weekdays=list(map(
            lambda x: x.departure_time,
            filter(
                lambda x: x.weekday == 'weekdays',
                query_result.timetable,
            ),
        )),
        saturdays=list(map(
            lambda x: x.departure_time,
            filter(
                lambda x: x.weekday == 'saturday',
                query_result.timetable,
            ),
        )),
        sundays=list(map(
            lambda x: x.departure_time,
            filter(
                lambda x: x.weekday == 'sunday',
                query_result.timetable,
            ),
        )),
    )
