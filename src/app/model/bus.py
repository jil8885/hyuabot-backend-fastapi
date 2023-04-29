import datetime
from typing import List

from sqlalchemy import Integer, String, Float, Time, Boolean, DateTime, \
    ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class BusStop(BaseModel):
    __tablename__ = 'bus_stop'
    id: Mapped[int] = mapped_column('stop_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('stop_name', String(30))
    # Location
    latitude: Mapped[float] = mapped_column('latitude', Float)
    longitude: Mapped[float] = mapped_column('longitude', Float)
    # Region
    district: Mapped[int] = mapped_column('district_code', Integer)
    region: Mapped[str] = mapped_column('region_name', String(10))
    # Mobile Search Number
    mobile_number: Mapped[str] = mapped_column('mobile_number', String(15))
    # Routes Via This Stop
    routes: Mapped[List['BusRouteStop']] = relationship(
        foreign_keys='BusStop.id',
        primaryjoin='BusStop.id == BusRouteStop.stop_id',
        uselist=True,
    )


class BusRoute(BaseModel):
    __tablename__ = 'bus_route'
    id: Mapped[int] = mapped_column('route_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('route_name', String(30))
    type_code: Mapped[str] = mapped_column('route_type_code', String(10))
    type_name: Mapped[str] = mapped_column('route_type_name', String(10))
    # Company
    company_id: Mapped[int] = mapped_column('company_id', Integer)
    company_name: Mapped[str] = mapped_column('company_name', String(30))
    company_telephone: Mapped[str] = \
        mapped_column('company_telephone', String(15))
    # Region
    discrict: Mapped[int] = mapped_column('district_code', Integer)
    # First Time
    up_first_time: Mapped[datetime.time] = mapped_column('up_first_time', Time)
    down_first_time: Mapped[datetime.time] = \
        mapped_column('down_first_time', Time)
    # Last Time
    up_last_time: Mapped[datetime.time] = mapped_column('up_last_time', Time)
    down_last_time: Mapped[datetime.time] = \
        mapped_column('down_last_time', Time)
    # Start Stop
    start_stop_id: Mapped[int] = mapped_column('start_stop_id', Integer)
    start_stop: Mapped['BusStop'] = relationship(
        'BusStop',
        foreign_keys='BusRoute.start_stop_id',
        primaryjoin='BusRoute.start_stop_id == BusStop.id',
    )
    # End Stop
    end_stop_id: Mapped[int] = mapped_column('end_stop_id', Integer)
    end_stop: Mapped['BusStop'] = relationship(
        'BusStop',
        foreign_keys='BusRoute.end_stop_id',
        primaryjoin='BusRoute.end_stop_id == BusStop.id',
    )
    # Route Stops
    route_stops: Mapped['BusRouteStop'] = relationship(
        back_populates='route', viewonly=True)


class BusRouteStop(BaseModel):
    __tablename__ = 'bus_route_stop'
    # Route - RouteStop: 1 - 1
    route_id: Mapped[int] = mapped_column(
        'route_id', ForeignKey('bus_route.route_id'), primary_key=True)
    route: Mapped['BusRoute'] = relationship(back_populates='route_stops')
    # Stop - RouteStop: 1 - 1
    stop_id: Mapped[int] = mapped_column(
        'stop_id', ForeignKey('bus_stop.stop_id'), primary_key=True)
    stop: Mapped['BusStop'] = relationship(
        primaryjoin='BusRouteStop.stop_id == BusStop.id',
        viewonly=True,
    )
    # Route Stop
    order: Mapped[int] = mapped_column('stop_sequence', Integer)
    # Start Stop
    start_stop_id: Mapped[int] = mapped_column(
        'start_stop_id', ForeignKey('bus_stop.stop_id'))
    start_stop: Mapped['BusStop'] = \
        relationship(
            'BusStop',
            foreign_keys='BusRouteStop.start_stop_id',
            primaryjoin='BusRouteStop.start_stop_id == BusStop.id',
        )
    # Realtime Arrival Time
    realtime: Mapped[List['BusRealtimeItem']] = \
        relationship(
            'BusRealtimeItem',
            foreign_keys=[route_id, stop_id],
            primaryjoin='and_('
                        'BusRouteStop.route_id == BusRealtimeItem.route_id, '
                        'BusRouteStop.stop_id == BusRealtimeItem.stop_id)',
            uselist=True,
            viewonly=True,
        )
    # Timetable Arrival Time
    timetable: Mapped[List['BusTimetableItem']] = \
        relationship(
            'BusTimetableItem',
            foreign_keys=[route_id, start_stop_id],
            primaryjoin='and_('
                        'BusRouteStop.route_id == BusTimetableItem.route_id, '
                        'BusRouteStop.start_stop_id == '
                        'BusTimetableItem.start_stop_id)',
            uselist=True,
            viewonly=True,
        )


class BusTimetableItem(BaseModel):
    __tablename__ = 'bus_timetable'
    # Route - Timetable: 1 - N
    route_id: Mapped[int] = mapped_column(
        'route_id', Integer, primary_key=True)
    route: Mapped['BusRoute'] = relationship(
        'BusRoute',
        foreign_keys='BusTimetableItem.route_id',
        primaryjoin='BusTimetableItem.route_id == BusRoute.id',
    )
    # Start Stop - Timetable: 1 - N
    start_stop_id: Mapped[int] = mapped_column('start_stop_id', Integer)
    start_stop: Mapped['BusStop'] = \
        relationship(
            'BusStop',
            foreign_keys='BusTimetableItem.start_stop_id',
            primaryjoin='BusTimetableItem.start_stop_id == BusStop.id',
        )
    # Timetable
    weekday: Mapped[str] = mapped_column(
        'weekday', String(10), primary_key=True)
    departure_time: Mapped[datetime.time] = \
        mapped_column('departure_time', Time, primary_key=True)


class BusRealtimeItem(BaseModel):
    __tablename__ = 'bus_realtime'
    # RouteStop - Realtime: 1 - N
    route_id: Mapped[int] = mapped_column(
        'route_id', Integer, primary_key=True)
    stop_id: Mapped[int] = mapped_column(
        'stop_id', Integer, primary_key=True)
    sequence: Mapped[int] = mapped_column(
        'arrival_sequence', Integer, primary_key=True)
    # Realtime
    stop: Mapped[int] = mapped_column('remaining_stop_count', Integer)
    seat: Mapped[int] = mapped_column('remaining_seat_count', Integer)
    minutes: Mapped[int] = mapped_column('remaining_time', Integer)
    low_floor: Mapped[bool] = mapped_column('low_plate', Boolean)
    last_updated_time: Mapped[datetime.datetime] = \
        mapped_column('last_updated_time', DateTime)
