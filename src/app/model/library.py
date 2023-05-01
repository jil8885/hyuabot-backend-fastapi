import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from app.model import BaseModel

if TYPE_CHECKING:
    from app.model.campus import Campus


class ReadingRoom(BaseModel):
    __tablename__ = 'reading_room'
    id: Mapped[int] = mapped_column('room_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('room_name', String(30))
    # Campus - ReadingRoom: 1 - N
    campus_id: Mapped[int] = mapped_column(ForeignKey('campus.campus_id'))
    campus: Mapped['Campus'] = relationship(back_populates='reading_rooms')
    # Room Information
    active: Mapped[bool] = mapped_column('is_active', Integer)
    reservable: Mapped[bool] = mapped_column('is_reservable', Integer)
    # Seats
    total_seats: Mapped[int] = mapped_column('total', Integer)
    active_seats: Mapped[int] = mapped_column('active_total', Integer)
    occupied_seats: Mapped[int] = mapped_column('occupied', Integer)
    available_seats: Mapped[int] = mapped_column('available', Integer)
    # Last Update Time
    last_updated_time: Mapped[datetime.datetime] = \
        mapped_column('last_updated_time', DateTime)
