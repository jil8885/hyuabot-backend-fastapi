from typing import List, TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.model import BaseModel

from app.model.cafeteria import Restaurant
from app.model.library import ReadingRoom


class Campus(BaseModel):
    __tablename__ = 'campus'
    id: Mapped[int] = mapped_column('campus_id', Integer, primary_key=True)
    name: Mapped[str] = mapped_column('campus_name', String(30))
    restaurants: Mapped[List['Restaurant']] = \
        relationship(back_populates='campus')
    reading_rooms: Mapped[List['ReadingRoom']] = \
        relationship(back_populates='campus')
