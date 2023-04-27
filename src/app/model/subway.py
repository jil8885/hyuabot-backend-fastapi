import datetime
from typing import List

from sqlalchemy import String, Integer, Time, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, backref

from app.model import BaseModel


class Station(BaseModel):
    __tablename__ = 'subway_station'
    name: Mapped[str] = \
        mapped_column('station_name', String(30), primary_key=True)
    # Station - Line: 1 - N
    lines: Mapped[List['RouteStation']] = \
        relationship(back_populates='station')


class Line(BaseModel):
    __tablename__ = 'subway_route'
    id: Mapped[int] = mapped_column('route_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('route_name', String(30))
    # Line - Station: 1 - N
    stations: Mapped[List['RouteStation']] = \
        relationship(back_populates='line')


class RouteStation(BaseModel):
    __tablename__ = 'subway_route_station'
    id: Mapped[str] = mapped_column('station_id', String(10), primary_key=True)
    # Line - Station: 1 - N
    line_id: Mapped[int] = mapped_column(
        'route_id', ForeignKey('subway_route.route_id'))
    line: Mapped['Line'] = relationship(back_populates='stations')
    # Station - Line: 1 - N
    station_name: Mapped[str] = \
        mapped_column(
            'station_name', ForeignKey('subway_station.station_name'))
    station: Mapped['Station'] = relationship(
        back_populates='lines',
        uselist=False,
    )
    # Station Order
    sequence: Mapped[int] = mapped_column('station_sequence', Integer)
    cumulative_time: Mapped[int] = mapped_column('cumulative_time', Integer)
    # Timetable
    timetable: Mapped[List['TimetableItem']] = \
        relationship(
            'TimetableItem',
            primaryjoin='RouteStation.id == TimetableItem.station_id',
            back_populates='station',
        )
    # Realtime
    realtime: Mapped[List['RealtimeItem']] = \
        relationship(
            'RealtimeItem',
            primaryjoin='RouteStation.id == RealtimeItem.station_id',
            back_populates='station',
            order_by='RealtimeItem.minute',
        )


class TimetableItem(BaseModel):
    __tablename__ = 'subway_timetable'
    # Current Station
    station_id: Mapped[str] = \
        mapped_column(
            'station_id',
            ForeignKey('subway_route_station.station_id'),
            primary_key=True,
        )
    station: Mapped['RouteStation'] = relationship(
        'RouteStation',
        foreign_keys='TimetableItem.station_id',
        uselist=False,
    )
    # Destination Station
    destination_id: Mapped[str] = \
        mapped_column(
            'terminal_station_id',
            ForeignKey('subway_route_station.station_id'),
        )
    destination: Mapped['RouteStation'] = \
        relationship(
            'RouteStation',
            foreign_keys='TimetableItem.destination_id',
        )
    # Start Station
    start_station_id: Mapped[str] = \
        mapped_column(
            'start_station_id',
            ForeignKey('subway_route_station.station_id'),
        )
    start_station: Mapped['RouteStation'] = \
        relationship(
            'RouteStation',
            foreign_keys='TimetableItem.start_station_id',
        )
    # Time
    weekday: Mapped[str] = mapped_column(
        'weekday', String(10), primary_key=True)
    heading: Mapped[str] = mapped_column(
        'up_down_type', String(10), primary_key=True)
    departure_time: Mapped[datetime.time] = \
        mapped_column('departure_time', Time, primary_key=True)


class RealtimeItem(BaseModel):
    __tablename__ = 'subway_realtime'
    # Current Station
    station_id: Mapped[str] = \
        mapped_column(
            'station_id',
            ForeignKey('subway_route_station.station_id'),
            primary_key=True,
        )
    station: Mapped['RouteStation'] = relationship(
        'RouteStation',
        foreign_keys='RealtimeItem.station_id',
        primaryjoin='RealtimeItem.station_id == RouteStation.id',
        uselist=False,
    )
    # Destination Station
    destination_id: Mapped[str] = \
        mapped_column('terminal_station_id', String(10))
    destination: Mapped['RouteStation'] = \
        relationship(
            'RouteStation',
            foreign_keys='RealtimeItem.destination_id',
            primaryjoin='RealtimeItem.destination_id == RouteStation.id',
            backref=backref('destination', uselist=False),
        )
    # Time
    heading: Mapped[str] = mapped_column(
        'up_down_type', String(10), primary_key=True)
    sequence: Mapped[int] = mapped_column(
        'arrival_sequence', Integer, primary_key=True)
    location: Mapped[str] = mapped_column('current_station_name', String(30))
    stop: Mapped[int] = mapped_column('remaining_stop_count', Integer)
    minute: Mapped[int] = mapped_column('remaining_time', Integer)
    train: Mapped[str] = mapped_column('train_number', String(10))
    express: Mapped[bool] = mapped_column('is_express_train', Boolean)
    last: Mapped[bool] = mapped_column('is_last_train', Boolean)
    status: Mapped[int] = mapped_column('status_code', Integer)
    last_updated_at: Mapped[datetime.datetime] = \
        mapped_column('last_updated_time', DateTime)
