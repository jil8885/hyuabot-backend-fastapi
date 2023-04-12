import datetime
from typing import List

from sqlalchemy import String, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class Stop(BaseModel):
    __table__ = "shuttle_stop"
    name: Mapped[str] = mapped_column("stop_name", String(15), primary_key=True)
    # Location
    latitude: Mapped[float] = mapped_column("latitude", Float)
    longitude: Mapped[float] = mapped_column("longitude", Float)
    # Routes that start from this stop
    start_routes: Mapped["Route"] = relationship(back_populates="start_stop")
    # Routes that end at this stop
    end_routes: Mapped["Route"] = relationship(back_populates="end_stop")
    # Routes that this stop is a part of
    routes: Mapped["RouteStop"] = relationship(back_populates="stop")


class Route(BaseModel):
    __table__ = "shuttle_route"
    name: Mapped[str] = mapped_column("route_name", String(15), primary_key=True)
    # Description
    korean: Mapped[str] = mapped_column("route_description_korean", String(100))
    english: Mapped[str] = mapped_column("route_description_english", String(100))
    # Route
    tags: Mapped[str] = mapped_column("route_tag", String(10))
    # Start Stop
    start_stop_id: Mapped[str] = mapped_column("start_stop", String(15))
    start_stop: Mapped["Stop"] = relationship(back_populates="start_routes")
    # End Stop
    end_stop_id: Mapped[str] = mapped_column("end_stop", String(15))
    end_stop: Mapped["Stop"] = relationship(back_populates="end_routes")
    # Stops that this route passes through
    stops: Mapped["RouteStop"] = relationship(back_populates="route")


class RouteStop(BaseModel):
    __table__ = "shuttle_route_stop"
    # Route - RouteStop: 1 - N
    route_name: Mapped[str] = \
        mapped_column("route_name", String(15), primary_key=True)
    route: Mapped["Route"] = relationship(back_populates="stops")
    # Stop - RouteStop: 1 - N
    stop_name: Mapped[str] = \
        mapped_column("stop_name", String(15), primary_key=True)
    stop: Mapped["Stop"] = relationship(back_populates="routes")
    # RouteStop
    stop_order: Mapped[int] = mapped_column("stop_order", Integer)
    cumulative_time: Mapped[int] = mapped_column("cumulative_time", Integer)
    # Timetable
    timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="route_stop")


class PeriodType(BaseModel):
    __table__ = "shuttle_period_type"
    name: Mapped[str] = \
        mapped_column("period_type_name", String(20), primary_key=True)
    # Periods that this type is a part of
    periods: Mapped["Period"] = relationship(back_populates="type")


class Period(BaseModel):
    period_type_name: Mapped[str] = \
        mapped_column("period_type", String(20), primary_key=True)
    period_type: Mapped["PeriodType"] = relationship(back_populates="periods")
    # Period
    start: Mapped[datetime.datetime] = \
        mapped_column("period_start", DateTime, primary_key=True)
    end: Mapped[datetime.datetime] = \
        mapped_column("period_end", DateTime, primary_key=True)


class TimetableItem(BaseModel):
    # Period - TimetableItem: 1 - N
    period_type_name: Mapped[str] = \
        mapped_column("period_type", String(20), primary_key=True)
    period_type: Mapped["PeriodType"] = \
        relationship(back_populates="timetable")
    # Weekday
    weekday: Mapped[bool] = mapped_column("weekday", Boolean, primary_key=True)
    # RouteStop - TimetableItem: 1 - N
    route_name: Mapped[str] = \
        mapped_column("route_name", String(15), primary_key=True)
    stop_name: Mapped[str] = \
        mapped_column("stop_name", String(15), primary_key=True)
    route_stop: Mapped["RouteStop"] = relationship(back_populates="timetable")
    departure_time: Mapped[datetime.datetime] = \
        mapped_column("departure_time", DateTime, primary_key=True)
