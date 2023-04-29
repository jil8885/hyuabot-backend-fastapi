import datetime
from typing import List

from sqlalchemy import String, Float, Integer, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.model import BaseModel


class CommuteShuttleStop(BaseModel):
    __tablename__ = 'commute_shuttle_stop'
    name: Mapped[str] = \
        mapped_column('stop_name', String(50), primary_key=True)
    description: Mapped[str] = mapped_column('description', String(100))
    latitude: Mapped[float] = mapped_column('latitude', Float)
    longitude: Mapped[float] = mapped_column('longitude', Float)
    timetable: Mapped[List['CommuteShuttleTimetableItem']] = \
        relationship(
            'CommuteShuttleTimetableItem',
            foreign_keys='CommuteShuttleTimetableItem.stop_name',
            primaryjoin='CommuteShuttleStop.name == '
                        'CommuteShuttleTimetableItem.stop_name',
            uselist=True,
            viewonly=True,
        )


class CommuteShuttleRoute(BaseModel):
    __tablename__ = 'commute_shuttle_route'
    name: Mapped[str] = \
        mapped_column('route_name', String(15), primary_key=True)
    korean: Mapped[str] = \
        mapped_column('route_description_korean', String(100))
    english: Mapped[str] = \
        mapped_column('route_description_english', String(100))
    timetable: Mapped[List['CommuteShuttleTimetableItem']] = \
        relationship(
            'CommuteShuttleTimetableItem',
            foreign_keys='CommuteShuttleTimetableItem.route_name',
            primaryjoin='CommuteShuttleRoute.name == '
                        'CommuteShuttleTimetableItem.route_name',
            uselist=True,
            viewonly=True,
            order_by='CommuteShuttleTimetableItem.stop_order',
        )


class CommuteShuttleTimetableItem(BaseModel):
    __tablename__ = 'commute_shuttle_timetable'
    # Route - Timetable: 1 - N
    route_name: Mapped[str] = \
        mapped_column('route_name', String(15), primary_key=True)
    route: Mapped['CommuteShuttleRoute'] = \
        relationship(
            'CommuteShuttleRoute',
            foreign_keys='CommuteShuttleTimetableItem.route_name',
            primaryjoin='CommuteShuttleTimetableItem.route_name == '
                        'CommuteShuttleRoute.name',
        )
    # Stop - Timetable: 1 - N
    stop_name: Mapped[str] = \
        mapped_column('stop_name', String(50), primary_key=True)
    stop: Mapped['CommuteShuttleStop'] = relationship(
        'CommuteShuttleStop',
        foreign_keys='CommuteShuttleTimetableItem.stop_name',
        primaryjoin='CommuteShuttleTimetableItem.stop_name == '
                    'CommuteShuttleStop.name',
    )
    # Timetable
    stop_order: Mapped[int] = mapped_column('stop_order', Integer)
    departure_time: Mapped[datetime.time] = \
        mapped_column('departure_time', Time)
