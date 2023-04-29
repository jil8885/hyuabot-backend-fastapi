import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse

from app.dependancies.database import get_db_session
from app.internal.date_utils import is_weekends, current_period, is_holiday
from app.model.commute_shuttle import CommuteShuttleRoute
from app.response.commute_shuttle import CommuteShuttleList, \
    CommuteShuttleListItem, CommuteShuttleRouteResponse, \
    CommuteShuttleCurrentLocation, CommuteShuttleTimetableResponse, \
    CommuteShuttleArrivalList, CommuteShuttleArrivalListItem

commute_shuttle_router = APIRouter()


@commute_shuttle_router.get('/route', response_model=CommuteShuttleList)
async def get_commute_shuttle_route(
    name: str | None = None,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all commute shuttle routes.
    Args:
        name (str): Name of the commute shuttle route.
        db_session (AsyncSession): Database session.
    Returns:
        CommuteShuttleList: List of all commute shuttle routes.
    """
    if name:
        statement = select(CommuteShuttleRoute).where(
            or_(
                CommuteShuttleRoute.korean.like(f'%{name}%'),
                CommuteShuttleRoute.english.like(f'%{name}%'),
            ),
        )
    else:
        statement = select(CommuteShuttleRoute)
    query_result = (await db_session.execute(statement)).scalars().all()
    routes = []
    for route in query_result:
        routes.append(CommuteShuttleListItem(
            id=route.name,
            korean=route.korean,
            english=route.english,
        ))
    return CommuteShuttleList(route=routes)


@commute_shuttle_router.get(
    '/route/{route_id}',
    response_model=CommuteShuttleRouteResponse,
)
async def get_commute_shuttle_route_by_id(
    route_id: str,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a commute shuttle route by id.
    Args:
        route_id (str): ID of the commute shuttle route.
        db_session (AsyncSession): Database session.
    Returns:
        CommuteShuttleRoute: Commute shuttle route with the given id.
    """
    statement = select(CommuteShuttleRoute).where(
        CommuteShuttleRoute.name == route_id,
    ).options(
        selectinload(CommuteShuttleRoute.timetable),
    )
    query_result = (await db_session.execute(statement)).\
        scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Commute shuttle route not found.'},
        )

    timetable_list: list[CommuteShuttleTimetableResponse] = []
    for timetable in query_result.timetable:
        timetable_list.append(
            CommuteShuttleTimetableResponse(
                name=timetable.stop_name,
                time=timetable.departure_time,
            ),
        )
    now = datetime.datetime.now()
    passed_stops = list(
        filter(
            lambda x: x.time < now.time(),
            timetable_list,
        ),
    )
    if len(passed_stops) == 0:
        recently_stop = CommuteShuttleTimetableResponse(
            name='',
            time=datetime.time(hour=0, minute=0, second=0),
        )
    else:
        recently_stop = max(
            passed_stops,
            key=lambda x: x.time,
        )

    next_stops = list(
        filter(
            lambda x: x.time > now.time(),
            timetable_list,
        ),
    )
    if len(next_stops) == 0:
        next_stop = CommuteShuttleTimetableResponse(
            name='',
            time=datetime.time(hour=0, minute=0, second=0),
        )
    else:
        next_stop = min(
            next_stops,
            key=lambda x: x.time,
        )

    now = datetime.datetime.now()
    if is_weekends(now):
        status_message = 'ERROR.WEEKENDS'
    elif current_period(db_session, now) != 'semester':
        status_message = 'ERROR.NOT_SEMESTER'
    elif is_holiday(db_session, now) != 'normal':
        status_message = 'ERROR.HOLIDAY'
    else:
        status_message = 'SUCCESS'
    return CommuteShuttleRouteResponse(
        name=query_result.name,
        timetable=timetable_list,
        current=CommuteShuttleCurrentLocation(
            start=CommuteShuttleTimetableResponse(
                name=recently_stop.name,
                time=recently_stop.time,
            ),
            end=CommuteShuttleTimetableResponse(
                name=next_stop.name,
                time=next_stop.time,
            ),
        ),
        status=status_message,
    )


@commute_shuttle_router.get(
    '/arrival',
    response_model=CommuteShuttleArrivalList,
)
async def get_commute_shuttle_arrival(
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all commute shuttle routes.
    Args:
        db_session (AsyncSession): Database session.
    Returns:
        CommuteShuttleArrivalList: List of all commute shuttle routes.
    """
    now = datetime.datetime.now()
    if is_weekends(now):
        status_message = 'ERROR.WEEKENDS'
    elif current_period(db_session, now) != 'semester':
        status_message = 'ERROR.NOT_SEMESTER'
    elif is_holiday(db_session, now) != 'normal':
        status_message = 'ERROR.HOLIDAY'
    else:
        status_message = 'SUCCESS'

    statement = select(CommuteShuttleRoute).options(
        selectinload(CommuteShuttleRoute.timetable),
    )
    query_result = (await db_session.execute(statement)).scalars().all()
    routes = []
    for route in query_result:
        timetable_list: list[CommuteShuttleTimetableResponse] = []
        for timetable in route.timetable:
            timetable_list.append(
                CommuteShuttleTimetableResponse(
                    name=timetable.stop_name,
                    time=timetable.departure_time,
                ),
            )
        passed_stops = list(
            filter(
                lambda x: x.time < now.time(),
                timetable_list,
            ),
        )
        if len(passed_stops) == 0:
            recently_stop = CommuteShuttleTimetableResponse(
                name='',
                time=datetime.time(hour=0, minute=0, second=0),
            )
        else:
            recently_stop = max(
                passed_stops,
                key=lambda x: x.time,
            )

        next_stops = list(
            filter(
                lambda x: x.time > now.time(),
                timetable_list,
            ),
        )
        if len(next_stops) == 0:
            next_stop = CommuteShuttleTimetableResponse(
                name='',
                time=datetime.time(hour=0, minute=0, second=0),
            )
        else:
            next_stop = min(
                next_stops,
                key=lambda x: x.time,
            )
        routes.append(
            CommuteShuttleArrivalListItem(
                name=route.name,
                korean=route.korean,
                english=route.english,
                current=CommuteShuttleCurrentLocation(
                    start=CommuteShuttleTimetableResponse(
                        name=recently_stop.name,
                        time=recently_stop.time,
                    ),
                    end=CommuteShuttleTimetableResponse(
                        name=next_stop.name,
                        time=next_stop.time,
                    ),
                ),
            ),
        )
    return CommuteShuttleArrivalList(
        route=routes,
        status=status_message,
    )
