import datetime
from typing import List

from sqlalchemy import String, Float, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class Stop(BaseModel):
    __table__ = "commute_shuttle_stop"
    name: Mapped[str] = \
        mapped_column("stop_name", String(50), primary_key=True)
    description: Mapped[str] = mapped_column("description", String(100))
    latitude: Mapped[float] = mapped_column("latitude", Float)
    longitude: Mapped[float] = mapped_column("longitude", Float)
    timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="stop")


class Route(BaseModel):
    __table__ = "commute_shuttle_route"
    name: Mapped[str] = \
        mapped_column("route_name", String(15), primary_key=True)
    korean: Mapped[str] = \
        mapped_column("route_description_korean", String(100))
    english: Mapped[str] = \
        mapped_column("route_description_english", String(100))
    timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="route")


class TimetableItem(BaseModel):
    __table__ = "commute_shuttle_timetable"
    # Route - Timetable: 1 - N
    route_name: Mapped[str] = \
        mapped_column("route_name", String(15), primary_key=True)
    route: Mapped["Route"] = \
        relationship(back_populates="timetable")
    # Stop - Timetable: 1 - N
    stop_name: Mapped[str] = \
        mapped_column("stop_name", String(50), primary_key=True)
    stop: Mapped["Stop"] = relationship(back_populates="timetable")
    # Timetable
    stop_order: Mapped[int] = mapped_column("stop_order", Integer)
    departure_time: Mapped[datetime.time] = \
        mapped_column("departure_time", Time)
