import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_commute_shuttle_by_name():
    """Test commute shuttle query by name."""
    search_name = ["화정", "공항", "시흥", "천호", "정자"]
    async with AsyncClient(app=app, base_url="http://test") as client:
        for name in search_name:
            response = await client.post(
                "/query",
                json={
                    "query": f"""
                        query {{
                            commuteShuttle(name: \"{name}\") {{
                                routeName
                                descriptionKorean
                                descriptionEnglish
                                timetable {{
                                    stopName
                                    time
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body["data"]["commuteShuttle"]) == list
            for shuttle in response_body["data"]["commuteShuttle"]:
                assert type(shuttle["routeName"]) == str
                assert type(shuttle["descriptionKorean"]) == str
                assert type(shuttle["descriptionEnglish"]) == str
                assert name in shuttle["routeName"] \
                       or name in shuttle["descriptionKorean"] \
                       or name in shuttle["descriptionEnglish"]
                assert type(shuttle["timetable"]) == list
                for timetable in shuttle["timetable"]:
                    assert type(timetable["stopName"]) == str
                    assert type(timetable["time"]) == str
