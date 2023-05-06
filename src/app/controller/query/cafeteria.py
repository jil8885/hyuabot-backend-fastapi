import datetime
from typing import Optional

import strawberry
from sqlalchemy import select, and_, true
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.cafeteria import Restaurant, Menu


@strawberry.type
class MenuItem:
    date: datetime.date = strawberry.field(name="date")
    slot: str = strawberry.field(name="slot")
    food: str = strawberry.field(name="food")
    price: str = strawberry.field(name="price")


@strawberry.type
class CafeteriaItem:
    campus_id: int = strawberry.field(name="campus")
    id: int = strawberry.field(name="id")
    name: str = strawberry.field(name="name")
    menus: list[MenuItem] = strawberry.field(name="menu")


async def query_cafeteria(
    db_session: AsyncSession,
    campus: Optional[int] = None,
    restaurant: Optional[list[int]] = None,
    date: Optional[datetime.date] = None,
    slot: Optional[str] = None,
) -> list[CafeteriaItem]:
    restaurant_filters = []
    menu_filters = []
    if campus is not None:
        restaurant_filters.append(Restaurant.campus_id == campus)
    if restaurant is not None:
        restaurant_filters.append(Restaurant.id.in_(restaurant))
    if date is not None:
        menu_filters.append(Menu.date == date)
    else:
        menu_filters.append(Menu.date == datetime.date.today())
    if slot is not None:
        menu_filters.append(Menu.slot == slot)

    restaurant_statement = select(Restaurant).where(and_(
        true(), *restaurant_filters,
    ))
    restaurants = (await db_session.execute(restaurant_statement)).\
        scalars().all()

    menu_statement = select(Menu).options(
        selectinload(Menu.restaurant),
    ).where(and_(true(), *menu_filters))
    menus = (await db_session.execute(menu_statement)).scalars().all()
    menu_dict: dict[int, list[Menu]] = {}
    for menu in menus:
        if menu.restaurant_id not in menu_dict:
            menu_dict[menu.restaurant_id] = []
        menu_dict[menu.restaurant_id].append(menu)

    result: list[CafeteriaItem] = []
    for row in restaurants:
        menu_list = []
        if row.id in menu_dict:
            for menu in menu_dict[row.id]:
                menu_list.append(MenuItem(
                    date=menu.date,
                    slot=menu.slot,
                    food=menu.food,
                    price=menu.price,
                ))
        result.append(CafeteriaItem(
            campus_id=row.campus_id,
            id=row.id,
            name=row.name,
            menus=menu_list,
        ))
    return result
