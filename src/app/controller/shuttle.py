from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, and_, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status
from starlette.responses import JSONResponse

from app.dependancies.database import get_db_session
from app.model.shuttle import ShuttleRoute, ShuttleStop
from app.response.shuttle import RouteListResponse, RouteListItemResponse, \
    RouteItemResponse, RouteStopItemResponse, StopListItemResponse, \
    StopListResponse, StopItemResponse

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
