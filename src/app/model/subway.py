import datetime
from typing import List

from sqlalchemy import String, Integer, Time, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class Station(BaseModel):
    __table__ = "subway_station"
    name: Mapped[str] = mapped_column("station_name", String(30))
    # Station - Line: 1 - N
    lines: Mapped["RouteStation"] = relationship(back_populates="station")


class Line(BaseModel):
    __table__ = "subway_route"
    id: Mapped[int] = mapped_column("route_id", Integer)
    name: Mapped[str] = mapped_column("route_name", String(30))
    # Line - Station: 1 - N
    stations: Mapped["RouteStation"] = relationship(back_populates="line")


class RouteStation(BaseModel):
    __table__ = "subway_route_station"
    id: Mapped[str] = mapped_column("station_id", String(10))
    # Line - Station: 1 - N
    line_id: Mapped[int] = mapped_column("route_id", Integer)
    line: Mapped["Line"] = relationship(back_populates="stations")
    # Station - Line: 1 - N
    station_name: Mapped[str] = mapped_column("station_name", String(30))
    station: Mapped["Station"] = relationship(back_populates="lines")
    # Station Order
    sequence: Mapped[int] = mapped_column("station_sequence", Integer)
    cumulative_time: Mapped[int] = mapped_column("cumulative_time", Integer)
    # Timetable
    timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="station")
    terminal_timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="destination")
    start_timetable: Mapped[List["TimetableItem"]] = \
        relationship(back_populates="start_station")
    # Realtime
    realtime: Mapped[List["RealtimeItem"]] = \
        relationship(back_populates="station")
    terminal_realtime: Mapped[List["RealtimeItem"]] = \
        relationship(back_populates="destination")


class TimetableItem(BaseModel):
    __table__ = "subway_timetable"
    # Current Station
    station_id: Mapped[str] = mapped_column("station_id", String(10))
    station: Mapped["RouteStation"] = relationship(back_populates="timetable")
    # Destination Station
    destination_id: Mapped[str] = \
        mapped_column("terminal_station_id", String(10))
    destination: Mapped["RouteStation"] = \
        relationship(back_populates="terminal_timetable")
    # Start Station
    start_station_id: Mapped[str] = \
        mapped_column("start_station_id", String(10))
    start_station: Mapped["RouteStation"] = \
        relationship(back_populates="start_timetable")
    # Time
    weekday: Mapped[str] = mapped_column("weekday", String(10))
    heading: Mapped[str] = mapped_column("up_down_type", String(10))
    departure_time: Mapped[datetime.time] = \
        mapped_column("departure_time", Time)


class RealtimeItem(BaseModel):
    __table__ = "subway_realtime"
    # Current Station
    station_id: Mapped[str] = mapped_column("station_id", String(10))
    station: Mapped["RouteStation"] = relationship(back_populates="realtime")
    # Destination Station
    destination_id: Mapped[str] = \
        mapped_column("terminal_station_id", String(10))
    destination: Mapped["RouteStation"] = \
        relationship(back_populates="terminal_realtime")
    # Time
    heading: Mapped[str] = mapped_column("up_down_type", String(10))
    sequence: Mapped[int] = mapped_column("arrival_sequence", Integer)
    location: Mapped[str] = mapped_column("current_station_name", String(30))
    stop: Mapped[int] = mapped_column("remaining_stop_count", Integer)
    minute: Mapped[int] = mapped_column("remaining_time", Integer)
    train: Mapped[str] = mapped_column("train_number", String(10))
    express: Mapped[bool] = mapped_column("is_express", Boolean)
    last: Mapped[bool] = mapped_column("is_last_train", Boolean)
    status: Mapped[int] = mapped_column("status_code", Integer)
    last_updated_at: Mapped[datetime.datetime] = \
        mapped_column("last_updated_at", DateTime)
