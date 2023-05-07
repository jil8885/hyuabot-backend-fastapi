import datetime

import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_subway_query_by_station():
    station_list = ['K449', 'K251']
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f"""
                    query {{
                        subway(station: \"{station_list}\") {{
                            id
                            name
                            lineID
                            lineName
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['subway']) == list
        for station in response_body['data']['subway']:
            assert type(station['id']) == str
            assert type(station['name']) == str
            assert type(station['lineID']) == str
            assert type(station['lineName']) == str
            assert station['id'] in station_list
            assert station['name'] == '한대앞'


@pytest.mark.asyncio
async def test_subway_timetable_query():
    station_list = ['K449', 'K251']
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f"""
                    query {{
                        subway(station: \"{station_list}\") {{
                            timetable {{
                                up {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                                down {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        print(response_body)
        assert type(response_body['data']['subway']) == list
        for station in response_body['data']['subway']:
            assert type(station['timetable']) == dict
            assert type(station['timetable']['up']) == list
            assert type(station['timetable']['down']) == list
            for timetable in station['timetable']['up']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
            for timetable in station['timetable']['down']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str


@pytest.mark.asyncio
async def test_subway_timetable_weekday_query():
    weekday_list = ['weekdays', 'weekends', 'holidays']
    async with AsyncClient(app=app, base_url='http://test') as client:
        for weekday in weekday_list:
            response = await client.post(
                '/query',
                json={
                    'query': f"""
                        query {{
                            subway(weekday: \"{weekday}\") {{
                                timetable {{
                                    up {{
                                        destinationID
                                        destinationName
                                        weekday
                                        time
                                    }}
                                    down {{
                                        destinationID
                                        destinationName
                                        weekday
                                        time
                                    }}
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body['data']['subway']) == list
            for station in response_body['data']['subway']:
                assert type(station['timetable']) == dict
                assert type(station['timetable']['up']) == list
                assert type(station['timetable']['down']) == list
                for timetable in station['timetable']['up']:
                    assert type(timetable['destinationID']) == str
                    assert type(timetable['destinationName']) == str
                    assert type(timetable['weekday']) == str
                    assert type(timetable['time']) == str
                    assert timetable['weekday'] == weekday
                for timetable in station['timetable']['down']:
                    assert type(timetable['destinationID']) == str
                    assert type(timetable['destinationName']) == str
                    assert type(timetable['weekday']) == str
                    assert type(timetable['time']) == str
                    assert timetable['weekday'] == weekday


@pytest.mark.asyncio
async def test_subway_timetable_start_time_query():
    start_time = datetime.datetime.now().strftime('%H:%M:%S')
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f"""
                    query {{
                        subway(start: \"{start_time}\") {{
                            timetable {{
                                up {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                                down {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['subway']) == list
        for station in response_body['data']['subway']:
            assert type(station['timetable']) == dict
            assert type(station['timetable']['up']) == list
            assert type(station['timetable']['down']) == list
            for timetable in station['timetable']['up']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] >= start_time or \
                       timetable['time'] <= '04:00:00'
            for timetable in station['timetable']['down']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] >= start_time or \
                       timetable['time'] <= '04:00:00'


@pytest.mark.asyncio
async def test_subway_timetable_end_time_query():
    end_time = datetime.datetime.now().strftime('%H:%M:%S')
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f"""
                    query {{
                        subway(end: \"{end_time}\") {{
                            timetable {{
                                up {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                                down {{
                                    destinationID
                                    destinationName
                                    weekday
                                    time
                                }}
                            }}
                        }}
                    }}
                """,
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['subway']) == list
        for station in response_body['data']['subway']:
            assert type(station['timetable']) == dict
            assert type(station['timetable']['up']) == list
            assert type(station['timetable']['down']) == list
            for timetable in station['timetable']['up']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] <= end_time
            for timetable in station['timetable']['down']:
                assert type(timetable['destinationID']) == str
                assert type(timetable['destinationName']) == str
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] <= end_time


@pytest.mark.asyncio
async def test_subway_timetable_heading_query():
    heading_list = ['up', 'down']
    async with AsyncClient(app=app, base_url='http://test') as client:
        for heading in heading_list:
            response = await client.post(
                '/query',
                json={
                    'query': f"""
                        query {{
                            subway(heading: \"{heading}\") {{
                                timetable {{
                                    up {{
                                        destinationID
                                        destinationName
                                        weekday
                                        time
                                    }}
                                    down {{
                                        destinationID
                                        destinationName
                                        weekday
                                        time
                                    }}
                                }}
                            }}
                        }}
                    """,
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body['data']['subway']) == list
            for station in response_body['data']['subway']:
                assert type(station['timetable']) == dict
                assert type(station['timetable'][heading]) == list
                for timetable in station['timetable'][heading]:
                    assert type(timetable['destinationID']) == str
                    assert type(timetable['destinationName']) == str
                    assert type(timetable['weekday']) == str
                    assert type(timetable['time']) == str
