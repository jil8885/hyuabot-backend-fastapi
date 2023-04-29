import datetime
from typing import List

from sqlalchemy import String, Float, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class ShuttleStop(BaseModel):
    __tablename__ = 'shuttle_stop'
    name: Mapped[str] = \
        mapped_column('stop_name', String(15), primary_key=True)
    # Location
    latitude: Mapped[float] = mapped_column('latitude', Float)
    longitude: Mapped[float] = mapped_column('longitude', Float)
    # Routes that this stop is a part of
    routes: Mapped[list['ShuttleRouteStop']] = relationship(
        'ShuttleRouteStop',
        foreign_keys='ShuttleStop.name',
        primaryjoin='ShuttleStop.name == ShuttleRouteStop.stop_name',
        uselist=True,
        viewonly=True,
    )


class ShuttleRoute(BaseModel):
    __tablename__ = 'shuttle_route'
    name: Mapped[str] = \
        mapped_column('route_name', String(15), primary_key=True)
    # Description
    korean: Mapped[str] = \
        mapped_column('route_description_korean', String(100))
    english: Mapped[str] = \
        mapped_column('route_description_english', String(100))
    # Route
    tags: Mapped[str] = mapped_column('route_tag', String(10))
    # Start Stop
    start_stop_id: Mapped[str] = mapped_column('start_stop', String(15))
    start_stop: Mapped['ShuttleStop'] = relationship(
        'ShuttleStop',
        foreign_keys='ShuttleRoute.start_stop_id',
        primaryjoin='ShuttleRoute.start_stop_id == ShuttleStop.name',
        uselist=False,
        viewonly=True,
    )
    # End Stop
    end_stop_id: Mapped[str] = mapped_column('end_stop', String(15))
    end_stop: Mapped['ShuttleStop'] = relationship(
        'ShuttleStop',
        foreign_keys='ShuttleRoute.end_stop_id',
        primaryjoin='ShuttleRoute.end_stop_id == ShuttleStop.name',
        uselist=False,
        viewonly=True,
    )
    # Stops that this route passes through
    stops: Mapped[list['ShuttleRouteStop']] = relationship(
        'ShuttleRouteStop',
        foreign_keys='ShuttleRoute.name',
        primaryjoin='ShuttleRoute.name == ShuttleRouteStop.route_name',
        uselist=True,
        viewonly=True,
    )


class ShuttleRouteStop(BaseModel):
    __tablename__ = 'shuttle_route_stop'
    # Route - RouteStop: 1 - N
    route_name: Mapped[str] = \
        mapped_column('route_name', String(15), primary_key=True)
    route: Mapped['ShuttleRoute'] = relationship(
        'ShuttleRoute',
        foreign_keys='ShuttleRouteStop.route_name',
        primaryjoin='ShuttleRouteStop.route_name == ShuttleRoute.name',
        uselist=False,
        viewonly=True,
    )
    # Stop - RouteStop: 1 - N
    stop_name: Mapped[str] = \
        mapped_column('stop_name', String(15), primary_key=True)
    stop: Mapped['ShuttleStop'] = relationship(
        'ShuttleStop',
        foreign_keys='ShuttleRouteStop.stop_name',
        primaryjoin='ShuttleRouteStop.stop_name == ShuttleStop.name',
        uselist=False,
        viewonly=True,
    )
    # RouteStop
    stop_order: Mapped[int] = mapped_column('stop_order', Integer)
    cumulative_time: Mapped[int] = mapped_column('cumulative_time', Integer)
    # Timetable
    timetable: Mapped[List['ShuttleTimetableItem']] = relationship(
        'ShuttleTimetableItem',
        foreign_keys=[route_name, stop_name],
        primaryjoin='and_('
                    'ShuttleTimetableItem.route_name == '
                    'ShuttleRouteStop.route_name,'
                    'ShuttleTimetableItem.stop_name == '
                    'ShuttleRouteStop.stop_name)',
        uselist=True,
        viewonly=True,
    )


class ShuttlePeriodType(BaseModel):
    __tablename__ = 'shuttle_period_type'
    name: Mapped[str] = \
        mapped_column('period_type_name', String(20), primary_key=True)
    # Periods that this type is a part of
    periods: Mapped['ShuttlePeriod'] = relationship(
        'ShuttlePeriod',
        foreign_keys='ShuttlePeriodType.name',
        primaryjoin='ShuttlePeriodType.name == ShuttlePeriod.period_type_name',
        uselist=False,
        viewonly=True,
    )


class ShuttlePeriod(BaseModel):
    __tablename__ = 'shuttle_period'
    period_type_name: Mapped[str] = \
        mapped_column('period_type', String(20), primary_key=True)
    period_type: Mapped['ShuttlePeriodType'] = relationship(
        'ShuttlePeriodType',
        foreign_keys='ShuttlePeriod.period_type_name',
        primaryjoin='ShuttlePeriod.period_type_name == '
                    'ShuttlePeriodType.name',
        uselist=False,
        viewonly=True,
    )
    # Period
    start: Mapped[datetime.datetime] = \
        mapped_column('period_start', DateTime, primary_key=True)
    end: Mapped[datetime.datetime] = \
        mapped_column('period_end', DateTime, primary_key=True)


class ShuttleTimetableItem(BaseModel):
    __tablename__ = 'shuttle_timetable'
    # Period - TimetableItem: 1 - N
    period_type_name: Mapped[str] = \
        mapped_column('period_type', String(20), primary_key=True)
    period_type: Mapped['ShuttlePeriodType'] = relationship(
        'ShuttlePeriodType',
        foreign_keys='ShuttleTimetableItem.period_type_name',
        primaryjoin='ShuttleTimetableItem.period_type_name == '
                    'ShuttlePeriodType.name',
        uselist=False,
        viewonly=True,
    )
    # Weekday
    weekday: Mapped[bool] = mapped_column('weekday', Boolean, primary_key=True)
    # RouteStop - TimetableItem: 1 - N
    route_name: Mapped[str] = \
        mapped_column('route_name', String(15), primary_key=True)
    stop_name: Mapped[str] = \
        mapped_column('stop_name', String(15), primary_key=True)
    route_stop: Mapped['ShuttleRouteStop'] = relationship(
        'ShuttleRouteStop',
        foreign_keys=[route_name, stop_name],
        primaryjoin='and_('
                    'ShuttleTimetableItem.route_name == '
                    'ShuttleRouteStop.route_name,'
                    'ShuttleTimetableItem.stop_name == '
                    'ShuttleRouteStop.stop_name)',
        uselist=False,
        viewonly=True,
    )
    departure_time: Mapped[datetime.datetime] = \
        mapped_column('departure_time', DateTime, primary_key=True)
