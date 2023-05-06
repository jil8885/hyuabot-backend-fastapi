import random

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_reading_room_query_by_campus():
    campus_list = [1, 2]
    async with AsyncClient(app=app, base_url="http://test") as client:
        for campus_id in campus_list:
            response = await client.post(
                "/query",
                json={
                    "query": f"""
                        query {{
                            readingRoom(campus: {campus_id}) {{
                                campusId
                                id
                                name
                                status {{
                                    active
                                    reservable
                                }}
                                seats {{
                                    total
                                    active
                                    occupied
                                    available
                                }}
                                updatedAt
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body["data"]["readingRoom"]) == list
            for reading_room in response_body["data"]["readingRoom"]:
                assert reading_room["campusId"] == campus_id
                assert type(reading_room["id"]) == int
                assert type(reading_room["name"]) == str
                assert type(reading_room["status"]["active"]) == bool
                assert type(reading_room["status"]["reservable"]) == bool
                assert type(reading_room["seats"]["total"]) == int
                assert type(reading_room["seats"]["active"]) == int
                assert type(reading_room["seats"]["occupied"]) == int
                assert type(reading_room["seats"]["available"]) == int
                assert type(reading_room["updatedAt"]) == str
                assert reading_room["seats"]["active"] == \
                       reading_room["seats"]["occupied"] + \
                       reading_room["seats"]["available"]


@pytest.mark.asyncio
async def test_reading_room_query_by_room_list():
    room_list = random.sample(
        [1, 53, 54, 55, 56, 57, 58, 59, 61, 63, 68, 131, 132],
        random.randint(1, 13),
    )
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        readingRoom(room: {room_list}) {{
                            id
                            name
                            status {{
                                active
                                reservable
                            }}
                            seats {{
                                total
                                active
                                occupied
                                available
                            }}
                            updatedAt
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["readingRoom"]) == list
        for reading_room in response_body["data"]["readingRoom"]:
            assert reading_room["id"] in room_list
            assert type(reading_room["name"]) == str
            assert type(reading_room["status"]["active"]) == bool
            assert type(reading_room["status"]["reservable"]) == bool
            assert type(reading_room["seats"]["total"]) == int
            assert type(reading_room["seats"]["active"]) == int
            assert type(reading_room["seats"]["occupied"]) == int
            assert type(reading_room["seats"]["available"]) == int
            assert type(reading_room["updatedAt"]) == str
            assert reading_room["seats"]["active"] == \
                   reading_room["seats"]["occupied"] + \
                   reading_room["seats"]["available"]
