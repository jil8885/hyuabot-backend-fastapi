import datetime
import holidays
from korean_lunar_calendar import KoreanLunarCalendar
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.calendar import Holiday
from app.model.shuttle import ShuttlePeriod

korean_holidays = holidays.KR()
lunar_calendar = KoreanLunarCalendar()


def is_weekends(value: datetime.date = datetime.date.today()) -> bool:
    return value.weekday() >= 5 or value in korean_holidays


def current_time() -> datetime.time:
    return datetime.datetime.now().time()


async def current_period(
    db_session: AsyncSession,
    value: datetime.datetime = datetime.datetime.now(),
) -> str:
    statement = select(ShuttlePeriod).where(
        and_(
            ShuttlePeriod.start <= value.time(),
            ShuttlePeriod.end >= value.time(),
        ),
    )
    query_result = (await db_session.execute(statement)).scalars().first()
    if query_result is None:
        return 'semester'
    return query_result.period_type_name


async def is_holiday(
    db_session: AsyncSession,
    value: datetime.date = datetime.date.today(),
) -> str:
    lunar_calendar.setSolarDate(value.year, value.month, value.day)
    statement = select(Holiday).where(
        or_(
            and_(
                Holiday.holiday_date == value,
                Holiday.calendar_type == 'solar',
            ),
            and_(
                Holiday.holiday_date == lunar_calendar.LunarIsoFormat(),
                Holiday.calendar_type == 'lunar',
            ),
        ),
    )
    query_result = (await db_session.execute(statement)).scalars()\
        .one_or_none()
    if query_result is None:
        return 'normal'
    return query_result.holiday_type
