import datetime
from typing import List

from sqlalchemy import Integer, String, Float, Time, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class Stop(BaseModel):
    __tablename__ = "bus_stop"
    id: Mapped[int] = mapped_column("stop_id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("stop_name", String(30))
    # Location
    latitude: Mapped[float] = mapped_column("latitude", Float)
    longitude: Mapped[float] = mapped_column("longitude", Float)
    # Region
    district: Mapped[int] = mapped_column("district_code", Integer)
    region: Mapped[str] = mapped_column("region_name", String(10))
    # Mobile Search Number
    mobile_number: Mapped[str] = mapped_column("mobile_number", String(15))
    # Routes Via This Stop
    routes: Mapped["RouteStop"] = relationship(back_populates="stop")
    # Routes starts from this stop
    start_routes: Mapped["Route"] = relationship(back_populates="start_stop")
    start_route_stops: Mapped["RouteStop"] = \
        relationship(back_populates="start_stop")
    # Routes ends at this stop
    end_routes: Mapped["Route"] = relationship(back_populates="end_stop")
    # Timetable that starts from this stop
    start_timetables: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="start_stop")


class Route(BaseModel):
    __tablename__ = "bus_route"
    id: Mapped[int] = mapped_column("route_id", Integer, primary_key=True)
    name: Mapped[str] = mapped_column("route_name", String(30))
    type_code: Mapped[str] = mapped_column("route_type_code", String(10))
    type_name: Mapped[str] = mapped_column("route_type_name", String(10))
    # Company
    company_id: Mapped[int] = mapped_column("company_id", Integer)
    company_name: Mapped[str] = mapped_column("company_name", String(30))
    company_telephone: Mapped[str] = \
        mapped_column("company_telephone", String(15))
    # Region
    discrict: Mapped[int] = mapped_column("district_code", Integer)
    # First Time
    up_first_time: Mapped[datetime.time] = mapped_column("up_first_time", Time)
    down_first_time: Mapped[datetime.time] = \
        mapped_column("down_first_time", Time)
    # Last Time
    up_last_time: Mapped[datetime.time] = mapped_column("up_last_time", Time)
    down_last_time: Mapped[datetime.time] = \
        mapped_column("down_last_time", Time)
    # Start Stop
    start_stop_id: Mapped[int] = mapped_column("start_stop_id", Integer)
    start_stop: Mapped["Stop"] = relationship(back_populates="start_routes")
    # End Stop
    end_stop_id: Mapped[int] = mapped_column("end_stop_id", Integer)
    end_stop: Mapped["Stop"] = relationship(back_populates="end_routes")
    # Route Stops
    route_stops: Mapped["RouteStop"] = relationship(back_populates="route")
    # Timetable
    timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="route")


class RouteStop(BaseModel):
    __tablename__ = "bus_route_stop"
    # Route - RouteStop: 1 - 1
    route_id: Mapped[int] = mapped_column("route_id", Integer)
    route: Mapped["Route"] = relationship(back_populates="route_stops")
    # Stop - RouteStop: 1 - 1
    stop_id: Mapped[int] = mapped_column("stop_id", Integer)
    stop: Mapped["Stop"] = relationship(back_populates="routes")
    # Route Stop
    order: Mapped[int] = mapped_column("stop_sequence", Integer)
    # Start Stop
    start_stop_id: Mapped[int] = mapped_column("start_stop_id", Integer)
    start_stop: Mapped["Stop"] = \
        relationship(back_populates="start_route_stops")
    # Realtime Arrival Time
    realtime: Mapped[List["RealtimeItem"]] = \
        relationship(back_populates="route_stop")


class TimetableItem(BaseModel):
    __tablename__ = "bus_timetable"
    # Route - Timetable: 1 - N
    route_id: Mapped[int] = mapped_column("route_id", Integer)
    route: Mapped["Route"] = relationship(back_populates="timetable")
    # Start Stop - Timetable: 1 - N
    start_stop_id: Mapped[int] = mapped_column("start_stop_id", Integer)
    start_stop: Mapped["Stop"] = \
        relationship(back_populates="start_timetables")
    # Timetable
    weekday: Mapped[str] = mapped_column("weekday", String(10))
    departure_time: Mapped[datetime.time] = \
        mapped_column("departure_time", Time)


class RealtimeItem(BaseModel):
    __tablename__ = "bus_realtime"
    # RouteStop - Realtime: 1 - N
    route_id: Mapped[int] = mapped_column("route_id", Integer)
    stop_id: Mapped[int] = mapped_column("stop_id", Integer)
    sequence: Mapped[int] = mapped_column("arrival_sequence", Integer)
    # Realtime
    stop: Mapped[int] = mapped_column("remaining_stop_count", Integer)
    seat: Mapped[int] = mapped_column("remaining_seat_count", Integer)
    minutes: Mapped[int] = mapped_column("remaining_time", Integer)
    low_floor: Mapped[bool] = mapped_column("low_plate", Boolean)
    last_updated_time: Mapped[datetime.time] = \
        mapped_column("last_updated_time", DateTime)
