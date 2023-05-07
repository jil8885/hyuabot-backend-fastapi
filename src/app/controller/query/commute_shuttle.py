from typing import Optional

import strawberry
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.model.commute_shuttle import CommuteShuttleRoute as RouteModel
from app.model.commute_shuttle import CommuteShuttleTimetableItem


@strawberry.type
class CommuteShuttleTimetable:
    stop: str = strawberry.field(name='stopName')
    time: str = strawberry.field(name='time')


@strawberry.type
class CommuteShuttleRoute:
    name: str = strawberry.field(name='routeName')
    description_korean: str = strawberry.field(name='descriptionKorean')
    description_english: str = strawberry.field(name='descriptionEnglish')
    timetable: list[CommuteShuttleTimetable] = strawberry.field(
        name='timetable')


async def query_commute_shuttle(
    db_session: AsyncSession,
    name: Optional[str] = None,
) -> list[CommuteShuttleRoute]:
    filters = []
    if name:
        filters.append(or_(
            RouteModel.name.like(f'%{name}%'),
            RouteModel.korean.like(f'%{name}%'),
            RouteModel.english.like(f'%{name}%'),
        ))
    statement = select(RouteModel).where(*filters).options(
        selectinload(RouteModel.timetable).selectinload(
            CommuteShuttleTimetableItem.stop,
        ),
    )
    query_result = (await db_session.execute(statement)).scalars().all()
    result = []
    for route in query_result:  # type: RouteModel
        result.append(CommuteShuttleRoute(
            name=route.name,
            description_korean=route.korean,
            description_english=route.english,
            timetable=[CommuteShuttleTimetable(
                stop=timetable.stop.name,
                time=timetable.departure_time.strftime('%H:%M'),
            ) for timetable in route.timetable],
        ))
    return result
