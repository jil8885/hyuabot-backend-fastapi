""" Module that can query the campus database.

Attributes:
    campus_router (APIRouter): FastAPI router for the campus module.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only
from starlette import status

from app.dependancies.database import get_db_session
from app.model.campus import Campus
from app.response.campus import CampusListResponse, CampusListItemResponse

campus_router = APIRouter()


@campus_router.get('', response_model=CampusListResponse)
async def get_campus_list(
    name: str | None = None,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a list of all campuses.
    Returns:
        List[Campus]: List of all campuses.
    """
    if name:
        statement = select(Campus).where(Campus.name.like(f'%{name}%'))
    else:
        statement = select(Campus)
    query_result = (await db_session.execute(
        statement.options(load_only(Campus.id, Campus.name)),
    )).scalars().all()

    search_result = []
    for campus in query_result:
        search_result.append(
            CampusListItemResponse(id=campus.id, name=campus.name),
        )
    return CampusListResponse(campus=search_result)


@campus_router.get('/{campus_id}', response_model=CampusListItemResponse)
async def get_campus(
    campus_id: int,
    db_session: AsyncSession = Depends(get_db_session),
):
    """Function to get a campus by id.
    Args:
        campus_id (int): ID of the campus.
        db_session (AsyncSession): Database session.
    Returns:
        Campus: Campus with the given id.
    """
    statement = select(Campus).where(Campus.id == campus_id)
    query_result = (await db_session.execute(
        statement,
    )).scalars().one_or_none()
    if query_result is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Campus not found'},
        )
    return CampusListItemResponse(id=query_result.id, name=query_result.name)
