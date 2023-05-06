import datetime
import random

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_cafeteria_query_by_campus():
    campus_list = [1, 2]
    async with AsyncClient(app=app, base_url="http://test") as client:
        for campus_id in campus_list:
            response = await client.post(
                "/query",
                json={
                    "query": f"""
                        query {{
                            cafeteria(campus: {campus_id}) {{
                                campus
                                id
                                name
                                menu {{
                                    date
                                    slot
                                    food
                                    price
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body["data"]["cafeteria"]) == list
            today = datetime.date.today()
            for cafeteria in response_body["data"]["cafeteria"]:
                assert cafeteria["campus"] == campus_id
                assert type(cafeteria["id"]) == int
                assert type(cafeteria["name"]) == str
                assert type(cafeteria["menu"]) == list
                for menu in cafeteria["menu"]:
                    assert type(menu["date"]) == str
                    assert type(menu["slot"]) == str
                    assert type(menu["food"]) == str
                    assert type(menu["price"]) == str
                    assert menu["date"] == today.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_cafeteria_query_by_id():
    restaurant_list = random.sample(
        [1, 2, 4, 5, 7, 8, 11, 12, 13, 14, 15],
        random.randint(1, 5),
    )
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        cafeteria(restaurant: {restaurant_list}) {{
                            campus
                            id
                            name
                            menu {{
                                date
                                slot
                                food
                                price
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["cafeteria"]) == list
        today = datetime.date.today()
        for cafeteria in response_body["data"]["cafeteria"]:
            assert type(cafeteria["campus"]) == int
            assert type(cafeteria["id"]) == int
            assert cafeteria["id"] in restaurant_list
            assert type(cafeteria["name"]) == str
            assert type(cafeteria["menu"]) == list
            for menu in cafeteria["menu"]:
                assert type(menu["date"]) == str
                assert type(menu["slot"]) == str
                assert type(menu["food"]) == str
                assert type(menu["price"]) == str
                assert menu["date"] == today.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_cafeteria_query_by_date():
    date_list = random.sample(
        range(1, 32),
        random.randint(1, 13),
    )
    async with AsyncClient(app=app, base_url="http://test") as client:
        for timedelta in date_list:
            feed_date = datetime.date.today() + \
                        datetime.timedelta(days=timedelta)
            response = await client.post(
                "/query",
                json={
                    "query": f"""
                        query {{
                            cafeteria(date: \"{feed_date}\") {{
                                campus
                                id
                                name
                                menu {{
                                    date
                                    slot
                                    food
                                    price
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body["data"]["cafeteria"]) == list
            for cafeteria in response_body["data"]["cafeteria"]:
                assert type(cafeteria["campus"]) == int
                assert type(cafeteria["id"]) == int
                assert type(cafeteria["name"]) == str
                assert type(cafeteria["menu"]) == list
                for menu in cafeteria["menu"]:
                    assert type(menu["date"]) == str
                    assert type(menu["slot"]) == str
                    assert type(menu["food"]) == str
                    assert type(menu["price"]) == str
                    assert menu["date"] == feed_date.strftime("%Y-%m-%d")


@pytest.mark.asyncio
async def test_cafeteria_query_by_slot():
    slots = ['조식', '중식', '석식']
    async with AsyncClient(app=app, base_url="http://test") as client:
        for slot in slots:
            response = await client.post(
                "/query",
                json={
                    "query": f"""
                        query {{
                            cafeteria(slot: \"{slot}\") {{
                                campus
                                id
                                name
                                menu {{
                                    date
                                    slot
                                    food
                                    price
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body["data"]["cafeteria"]) == list
            for cafeteria in response_body["data"]["cafeteria"]:
                assert type(cafeteria["campus"]) == int
                assert type(cafeteria["id"]) == int
                assert type(cafeteria["name"]) == str
                assert type(cafeteria["menu"]) == list
                for menu in cafeteria["menu"]:
                    assert type(menu["date"]) == str
                    assert type(menu["slot"]) == str
                    assert type(menu["food"]) == str
                    assert type(menu["price"]) == str
                    assert slot in menu["slot"]
