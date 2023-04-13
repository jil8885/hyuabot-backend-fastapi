import datetime

from sqlalchemy import Integer, Float, Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel
from app.model.campus import Campus


class Restaurant(BaseModel):
    __table__ = "restaurant"
    id: Mapped[int] = mapped_column("restaurant_id", Integer, primary_key=True)
    # Campus - Restaurant: 1 - N
    campus_id: Mapped[int] = mapped_column("campus_id", Integer)
    campus: Mapped["Campus"] = relationship(back_populates="restaurants")
    # Location
    latitude: Mapped[float] = mapped_column("latitude", Float)
    longitude: Mapped[float] = mapped_column("longitude", Float)
    # Menu
    menus: Mapped["Menu"] = relationship(back_populates="restaurant")


class Menu(BaseModel):
    __table__ = "menu"
    # Restaurant - Menu: 1 - N
    restaurant_id: Mapped[int] = mapped_column("restaurant_id", Integer)
    restaurant: Mapped["Restaurant"] = relationship(back_populates="menus")
    # Menu
    date: Mapped[datetime.date] = mapped_column("feed_date", Date)
    slot: Mapped[str] = mapped_column("time_type", String(10))
    food: Mapped[str] = mapped_column("menu_food", String(400))
    price: Mapped[str] = mapped_column("menu_price", String(30))
