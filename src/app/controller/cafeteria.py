""" Module that can query the cafeteria database

Attributes:
    cafeteria_router (APIRouter): FastAPI router for the cafeteria module.
"""
import datetime

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from starlette import status

from app.dependancies.database import get_db_session
from app.model.cafeteria import Restaurant
from app.model.campus import Campus
from app.response.cafeteria import Restaurant as RestaurantResponse, Menu
from app.response.cafeteria import RestaurantList, RestaurantLocation

cafeteria_router = APIRouter()


def get_time_slot(current_time: datetime.time) -> str:
    if current_time.hour < 10:
        return '조식'
    elif current_time.hour < 15:
        return '중식'
    else:
        return '석식'


@cafeteria_router.get(
    '/{campus_id}/restaurant',
    response_model=RestaurantList,
)
async def get_restaurant_list(
    campus_id: int,
    feed_date: datetime.date = datetime.date.today(),
    time_slot: str = get_time_slot(datetime.datetime.now().time()),
    all: bool = False,
    db_session: AsyncSession = Depends(get_db_session),
):
    """ Function to get a list of restaurants of a campus.
    Args:
        campus_id (int): ID of the campus.
        feed_date (datetime.date): Date of the menu.
        time_slot (str): Time slot of the menu.
        all (bool): Whether to get all menus.
        db_session (AsyncSession): Database session.
    Returns:
        RestaurantList: Response contains of restaurants in a campus.
    """
    statement = select(Campus).\
        where(Campus.id == campus_id).\
        options(
            selectinload(Campus.restaurants).selectinload(Restaurant.menus),
        )
    query_result = (
        await db_session.execute(statement)
    ).scalars().all()

    if len(query_result) == 0:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={'message': 'Campus not found'},
        )
    result = query_result[0]
    restaurants = []
    for restaurant in result.restaurants:
        menus: list[Menu] = []
        for menu in filter(lambda x: (
            (x.date == feed_date
             and (time_slot in x.slot if not all else True))
        ), restaurant.menus):
            menus.append(
                Menu(
                    date=menu.date,
                    slot=menu.slot,
                    food=menu.food,
                    price=menu.price,
                ),
            )
        restaurants.append(
            RestaurantResponse(
                id=restaurant.id,
                location=RestaurantLocation(
                    latitude=restaurant.latitude,
                    longitude=restaurant.longitude,
                ),
                menu=menus,
            ),
        )
    return RestaurantList(
        id=result.id,
        name=result.name,
        restaurants=restaurants,
    )
