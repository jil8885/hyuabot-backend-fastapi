import datetime

from sqlalchemy import Date, String
from sqlalchemy.orm import mapped_column, Mapped

from app.model import BaseModel


class Holiday(BaseModel):
    __tablename__ = "shuttle_holiday"
    holiday_date: Mapped[datetime.date] = mapped_column(
        "holiday_date", Date, primary_key=True)
    holiday_type: Mapped[str] = mapped_column("holiday_type", String(10))
    calendar_type: Mapped[str] = mapped_column("calendar_type", String(15))
