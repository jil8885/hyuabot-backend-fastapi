import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, Float, Date, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel

if TYPE_CHECKING:
    from app.model.campus import Campus


class Restaurant(BaseModel):
    __tablename__ = 'restaurant'
    id: Mapped[int] = mapped_column('restaurant_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('restaurant_name', String(50))
    # Campus - Restaurant: 1 - N
    campus_id: Mapped[int] = mapped_column(ForeignKey('campus.campus_id'))
    campus: Mapped['Campus'] = relationship(back_populates='restaurants')
    # Location
    latitude: Mapped[float] = mapped_column('latitude', Float)
    longitude: Mapped[float] = mapped_column('longitude', Float)
    # Menu
    menus: Mapped[list['Menu']] = relationship(back_populates='restaurant')


class Menu(BaseModel):
    __tablename__ = 'menu'
    # Restaurant - Menu: 1 - N
    restaurant_id: Mapped[int] = \
        mapped_column(ForeignKey('restaurant.restaurant_id'), primary_key=True)
    restaurant: Mapped['Restaurant'] = relationship(back_populates='menus')
    # Menu
    date: Mapped[datetime.date] = \
        mapped_column('feed_date', Date, primary_key=True)
    slot: Mapped[str] = \
        mapped_column('time_type', String(10), primary_key=True)
    food: Mapped[str] = \
        mapped_column('menu_food', String(400), primary_key=True)
    price: Mapped[str] = mapped_column('menu_price', String(30))
