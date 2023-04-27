from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, selectinload
from starlette import status
from starlette.responses import JSONResponse

from app.dependancies.database import get_db_session
from app.internal.date_utils import is_weekends, current_time
from app.model.subway import RouteStation, RealtimeItem, TimetableItem
from app.response.subway import StationListItemResponse, StationListResponse, \
    StationItemResponse, StationCurrentStatusResponse, RealtimeResponse, \
    Realtime, Destination, CurrentStatus, TimetableResponse, Timetable, \
    Origin, StationTimetableResponse

subway_router = APIRouter()


@subway_router.get('/station', response_model=StationListResponse)
async def get_station_list(
        name: str | None = None,
        db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a list of subway stations.
    Args:
        name (str, optional): Name of the subway station.
        db_session (AsyncSession): Database session.
    Returns:
        SubwayStationResponse: Response contains of subway stations.
    """
    statement = select(RouteStation). \
        where(RouteStation.station_name.like(f'%{name}%') if name else True). \
        options(load_only(
            RouteStation.station_name,
            RouteStation.line_id,
            RouteStation.id,
        )
    )

    query_result = (
        await db_session.execute(statement)
    ).scalars().all()
    stations: list[StationListItemResponse] = []
    for station in query_result:
        stations.append(StationListItemResponse(
            id=station.id,
            name=station.station_name,
            line=station.line_id,
        ))
    return StationListResponse(stations=stations)


@subway_router.get(
    '/station/{station_id}', response_model=StationItemResponse)
async def get_station(
        station_id: str,
        db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a subway station.
    Args:
        station_id (str): ID of the subway station.
        db_session (AsyncSession): Database session.
    Returns:
        SubwayStationResponse: Response contains of subway station.
    """
    statement = select(RouteStation).where(RouteStation.id == station_id)

    query_result: RouteStation = (
        await db_session.execute(statement)
    ).scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Station not found'},
        )
    return StationItemResponse(
        id=query_result.id,
        name=query_result.station_name,
        line=query_result.line_id,
        sequence=query_result.sequence,
        cumulative_time=timedelta(minutes=query_result.cumulative_time),
    )


@subway_router.get(
    '/station/{station_id}/arrival',
    response_model=StationCurrentStatusResponse,
)
async def get_station_arrival(
        station_id: str,
        db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a subway station.
    Args:
        station_id (str): ID of the subway station.
        db_session (AsyncSession): Database session.
    Returns:
        SubwayStationResponse: Response contains of subway station.
    """
    statement = select(RouteStation). \
        where(RouteStation.id == station_id). \
        options(
        selectinload(RouteStation.realtime).selectinload(
            RealtimeItem.destination
        ),
        selectinload(RouteStation.timetable).selectinload(
            TimetableItem.start_station,
        ),
        selectinload(RouteStation.timetable).selectinload(
            TimetableItem.destination,
        ),
    )

    query_result: RouteStation = (
        await db_session.execute(statement)
    ).scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Station not found'},
        )
    up_timetable_filter = list(filter(
        lambda x: (x.heading == 'up'
                   and (x.weekday == 'weekends') == is_weekends()
                   and current_time() < x.departure_time),
        query_result.timetable,
    ))
    down_timetable_filter = list(filter(
        lambda x: (x.heading == 'down'
                   and (x.weekday == 'weekends') == is_weekends()
                   and current_time() < x.departure_time),
        query_result.timetable,
    ))

    up_timetable = []
    for index, item in enumerate(up_timetable_filter):
        up_timetable.append(Timetable(
            weekday=item.weekday,
            heading='up',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))

    down_timetable = []
    for index, item in enumerate(down_timetable_filter):
        down_timetable.append(Timetable(
            weekday=item.weekday,
            heading='down',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))
    return StationCurrentStatusResponse(
        id=query_result.id,
        name=query_result.station_name,
        line=query_result.line_id,
        realtime=RealtimeResponse(
            up=list(map(
                lambda x: Realtime(
                    heading='up',
                    sequence=x.sequence,
                    no=x.train,
                    destination=Destination(
                        id=x.destination_id,
                        name=x.destination.station_name,
                    ),
                    current=CurrentStatus(
                        location=x.location,
                        time=x.minute,
                        status=x.status,
                    ),
                    express=x.express,
                    last=x.last,
                    updated_at=x.last_updated_at,
                ),
                filter(
                    lambda x: x.heading == 'true',
                    query_result.realtime,
                ),
            )),
            down=list(map(
                lambda x: Realtime(
                    heading='down',
                    sequence=x.sequence,
                    no=x.train,
                    destination=Destination(
                        id=x.destination_id,
                        name=x.destination.station_name,
                    ),
                    current=CurrentStatus(
                        location=x.location,
                        time=x.minute,
                        status=x.status,
                    ),
                    express=x.express,
                    last=x.last,
                    updated_at=x.last_updated_at,
                ),
                filter(
                    lambda x: x.heading == 'false',
                    query_result.realtime,
                ),
            )),
        ),
        timetable=TimetableResponse(
            up=up_timetable,
            down=down_timetable,
        )
    )


@subway_router.get(
    '/station/{station_id}/timetable',
    response_model=StationTimetableResponse,
)
async def get_station_timetable(
        station_id: str,
        db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a subway station.
    Args:
        station_id (str): ID of the subway station.
        db_session (AsyncSession): Database session.
    Returns:
        SubwayStationResponse: Response contains of subway station.
    """
    statement = select(RouteStation). \
        where(RouteStation.id == station_id). \
        options(
        selectinload(RouteStation.timetable).selectinload(
            TimetableItem.start_station,
        ),
        selectinload(RouteStation.timetable).selectinload(
            TimetableItem.destination,
        ),
    )
    query_result: RouteStation = (
        await db_session.execute(statement)
    ).scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Station not found'},
        )
    up_weekends_timetable_filter = list(filter(
        lambda x: (x.heading == 'up'
                   and x.weekday == 'weekends'),
        query_result.timetable,
    ))
    down_weekends_timetable_filter = list(filter(
        lambda x: (x.heading == 'down'
                   and x.weekday == 'weekends'),
        query_result.timetable,
    ))
    up_weekdays_timetable_filter = list(filter(
        lambda x: (x.heading == 'up'
                   and x.weekday == 'weekdays'),
        query_result.timetable,
    ))
    down_weekdays_timetable_filter = list(filter(
        lambda x: (x.heading == 'down'
                   and x.weekday == 'weekdays'),
        query_result.timetable,
    ))
    up_weekdays_timetable = []
    for index, item in enumerate(up_weekdays_timetable_filter):
        up_weekdays_timetable.append(Timetable(
            weekday=item.weekday,
            heading='up',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))
    down_weekdays_timetable = []
    for index, item in enumerate(down_weekdays_timetable_filter):
        down_weekdays_timetable.append(Timetable(
            weekday=item.weekday,
            heading='down',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))
    up_weekends_timetable = []
    for index, item in enumerate(up_weekends_timetable_filter):
        up_weekends_timetable.append(Timetable(
            weekday=item.weekday,
            heading='up',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))
    down_weekends_timetable = []
    for index, item in enumerate(down_weekends_timetable_filter):
        down_weekends_timetable.append(Timetable(
            weekday=item.weekday,
            heading='down',
            sequence=index,
            origin=Origin(
                id=item.start_station.id,
                name=item.start_station.station_name,
            ),
            destination=Destination(
                id=item.destination_id,
                name=item.destination.station_name,
            ),
            time=item.departure_time,
        ))
    return StationTimetableResponse(
        id=query_result.id,
        name=query_result.station_name,
        weekdays=TimetableResponse(
            up=up_weekdays_timetable,
            down=down_weekdays_timetable,
        ),
        weekends=TimetableResponse(
            up=up_weekends_timetable,
            down=down_weekends_timetable,
        ),
    )
