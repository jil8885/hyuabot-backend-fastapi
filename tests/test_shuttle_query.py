import datetime
import random

import pytest
from httpx import AsyncClient

from app.main import app


stop_list = [
    "dormitory_o", "shuttlecock_o", "station",
    "terminal", "dormitory_i", "shuttlecock_i",
    "jungang_stn",
]
route_type_list = ["DH", "DY", "DJ", "C"]
period_list = ["vacation", "semester", "vacation_session"]


@pytest.mark.asyncio
async def test_shuttle_query():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": """
                    query {
                        shuttle {
                            stop {
                                stopName
                                location {
                                    latitude
                                    longitude
                                }
                                route {
                                    routeID
                                    descriptionKorean
                                    descriptionEnglish
                                    timetable {
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {
                                            stopName
                                            timedelta
                                            time
                                        }
                                    }
                                }
                                tag {
                                    tagID
                                    timetable {
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {
                                            stopName
                                            timedelta
                                            time
                                        }
                                    }
                                }
                            }
                            params {
                                period
                                weekday
                            }
                        }
                    }
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["stopName"]) == str
            assert stop["stopName"] in stop_list

            assert type(stop["location"]["latitude"]) == float
            assert type(stop["location"]["longitude"]) == float

            assert type(stop["route"]) == list
            for route in stop["route"]:
                assert type(route["routeID"]) == str
                assert any(route["routeID"].startswith(route_type)
                           for route_type in route_type_list)

                assert type(route["descriptionKorean"]) == str
                assert type(route["descriptionEnglish"]) == str

                assert type(route["timetable"]) == list
                assert route["timetable"] == sorted(
                    route["timetable"], key=lambda x: x["time"],
                )
                for timetable in route["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time

            assert type(stop["tag"]) == list
            for tag in stop["tag"]:
                assert type(tag["tagID"]) == str
                assert type(tag["timetable"]) == list
                assert tag["timetable"] == sorted(
                    tag["timetable"], key=lambda x: x["time"],
                )
                for timetable in tag["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time
            assert type(response_body["data"]["shuttle"]["params"]) == dict
            params = response_body["data"]["shuttle"]["params"]
            assert type(params["period"]) == list
            assert type(params["weekday"]) == list
            assert all(period in period_list for period in params["period"])
            assert all(type(weekday) == bool for weekday in params["weekday"])


@pytest.mark.asyncio
async def test_shuttle_query_by_stop():
    sampled_stop_list = random.sample(stop_list, 3)
    sampled_stop_list_str = str(sampled_stop_list).replace("'", '"')
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (stop: {sampled_stop_list_str}) {{
                            stop {{
                                stopName
                                location {{
                                    latitude
                                    longitude
                                }}
                                route {{
                                    routeID
                                    descriptionKorean
                                    descriptionEnglish
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                                tag {{
                                    tagID
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                            }}
                            params {{
                                period
                                weekday
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["stopName"]) == str
            assert stop["stopName"] in sampled_stop_list

            assert type(stop["location"]["latitude"]) == float
            assert type(stop["location"]["longitude"]) == float

            assert type(stop["route"]) == list
            for route in stop["route"]:
                assert type(route["routeID"]) == str
                assert any(route["routeID"].startswith(route_type)
                           for route_type in route_type_list)

                assert type(route["descriptionKorean"]) == str
                assert type(route["descriptionEnglish"]) == str

                assert type(route["timetable"]) == list
                assert route["timetable"] == sorted(
                    route["timetable"], key=lambda x: x["time"],
                )
                for timetable in route["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time

            assert type(stop["tag"]) == list
            for tag in stop["tag"]:
                assert type(tag["tagID"]) == str
                assert type(tag["timetable"]) == list
                assert tag["timetable"] == sorted(
                    tag["timetable"], key=lambda x: x["time"],
                )
                for timetable in tag["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time
            assert type(response_body["data"]["shuttle"]["params"]) == dict
            params = response_body["data"]["shuttle"]["params"]
            assert type(params["period"]) == list
            assert type(params["weekday"]) == list
            assert all(period in period_list for period in params["period"])
            assert all(type(weekday) == bool for weekday in params["weekday"])


@pytest.mark.asyncio
async def test_shuttle_query_by_tag():
    sampled_tag_list = random.sample(route_type_list, 3)
    sampled_tag_list_str = str(sampled_tag_list).replace("'", '"')
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (tag: {sampled_tag_list_str}) {{
                            stop {{
                                stopName
                                tag {{
                                    tagID
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["stopName"]) == str
            assert stop["stopName"] in stop_list

            assert type(stop["tag"]) == list
            for tag in stop["tag"]:
                assert type(tag["tagID"]) == str
                assert tag["tagID"] in sampled_tag_list
                assert type(tag["timetable"]) == list
                assert tag["timetable"] == sorted(
                    tag["timetable"], key=lambda x: x["time"],
                )
                for timetable in tag["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time


@pytest.mark.asyncio
async def test_shuttle_query_by_route():
    route_list = ["DHDD", "CDD", "DYDD"]
    route_list_str = str(route_list).replace("'", '"')
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (route: {route_list_str}) {{
                            stop {{
                                route {{
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["route"]) == list
            for route in stop["route"]:
                assert type(route["timetable"]) == list
                assert route["timetable"] == sorted(
                    route["timetable"], key=lambda x: x["time"],
                )
                for timetable in route["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time


@pytest.mark.asyncio
async def test_shuttle_query_by_start_time():
    start_time = datetime.time(12, 0, 0)
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (start: \"{start_time}\") {{
                            stop {{
                                route {{
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["route"]) == list
            for route in stop["route"]:
                assert type(route["timetable"]) == list
                assert route["timetable"] == sorted(
                    route["timetable"], key=lambda x: x["time"],
                )
                for timetable in route["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    ).time() >= start_time
                    assert type(timetable["remainingTime"]) == float
                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time


@pytest.mark.asyncio
async def test_shuttle_query_by_end_time():
    end_time = datetime.time(20, 0, 0)
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (end: \"{end_time}\") {{
                            stop {{
                                route {{
                                    timetable {{
                                        weekdays
                                        time
                                        remainingTime
                                        otherStops {{
                                            stopName
                                            timedelta
                                            time
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body["data"]["shuttle"]["stop"]) == list
        for stop in response_body["data"]["shuttle"]["stop"]:
            assert type(stop["route"]) == list
            for route in stop["route"]:
                assert type(route["timetable"]) == list
                assert route["timetable"] == sorted(
                    route["timetable"], key=lambda x: x["time"],
                )
                for timetable in route["timetable"]:
                    assert type(timetable["weekdays"]) == bool
                    assert type(timetable["time"]) == str
                    assert datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    ).time() <= end_time
                    assert type(timetable["remainingTime"]) == float

                    departure_time = datetime.datetime.strptime(
                        timetable["time"], "%H:%M:%S",
                    )
                    assert type(timetable["otherStops"]) == list
                    for other_stop in timetable["otherStops"]:
                        assert type(other_stop["stopName"]) == str
                        assert other_stop["stopName"] in stop_list
                        assert type(other_stop["timedelta"]) == int
                        assert type(other_stop["time"]) == str
                        arrival_time = datetime.datetime.strptime(
                            other_stop["time"], "%H:%M:%S",
                        )
                        assert departure_time + datetime.timedelta(
                            minutes=other_stop["timedelta"],
                        ) == arrival_time


@pytest.mark.asyncio
async def test_shuttle_query_by_tag_and_stop():
    route_list = ["DHDD", "CDD", "DYDD"]
    route_list_str = str(route_list).replace("'", '"')
    sampled_tag_list = random.sample(route_type_list, 3)
    sampled_tag_list_str = str(sampled_tag_list).replace("'", '"')
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/query",
            json={
                "query": f"""
                    query {{
                        shuttle (
                            tag: {sampled_tag_list_str},
                            route: {route_list_str}
                        ) {{
                            params {{
                                period
                                weekday
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert response_body["errors"][0]["message"] == \
               "tag and route cannot be used together"
