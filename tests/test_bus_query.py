import datetime

import pytest
from httpx import AsyncClient

from app.main import app

route_stop_list = [
    {"route": 216000026, "stop": 216000719},
    {"route": 216000096, "stop": 216000719},
    {"route": 216000043, "stop": 216000719},
    {"route": 216000070, "stop": 216000719},
    {"route": 216000061, "stop": 216000378},
    {"route": 216000068, "stop": 216000378},
    {"route": 216000061, "stop": 216000379},
    {"route": 216000068, "stop": 216000379},
    {"route": 216000068, "stop": 216000138},
    {"route": 216000016, "stop": 216000152},
    {"route": 217000014, "stop": 216000070},
    {"route": 216000001, "stop": 216000070},
    {"route": 200000015, "stop": 216000070},
    {"route": 216000075, "stop": 216000759},
    {"route": 216000075, "stop": 216000117},
]


@pytest.mark.asyncio
async def test_bus_query_by_route_stop():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f'''
                    query {{
                        bus(routeStop: {route_stop_list}) {{
                            stopID
                            stopName
                            routeID
                            routeName
                            sequence
                            startStopID
                            startStopName
                            realtime {{
                                remainingStop
                                remainingTime
                                remainingSeat
                                lowFloor
                                updatedAt
                            }}
                            timetable {{
                                weekday
                                time
                            }}
                        }}
                    }}
                '''.replace("'", ''),
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['bus']) == list
        for bus in response_body['data']['bus']:
            assert type(bus['stopID']) == int
            assert type(bus['stopName']) == str
            assert type(bus['routeID']) == int
            assert type(bus['routeName']) == str
            assert type(bus['sequence']) == int
            assert type(bus['startStopID']) == int
            assert type(bus['startStopName']) == str
            assert type(bus['realtime']) == list
            assert {
                'stop': bus['stopID'], 'route': bus['routeID'],
            } in route_stop_list
            for realtime in bus['realtime']:
                assert type(realtime['remainingStop']) == int
                assert type(realtime['remainingTime']) == int
                assert type(realtime['remainingSeat']) == int
                assert type(realtime['lowFloor']) == bool
                assert type(realtime['updatedAt']) == str
            assert type(bus['timetable']) == list
            for timetable in bus['timetable']:
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str


@pytest.mark.asyncio
async def test_bus_query_by_weekday():
    weekday_list = ['weekdays']
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.post(
            '/query',
            json={
                'query': f'''
                    query {{
                        bus(
                            routeStop: {str(route_stop_list).replace("'", '')},
                            weekdays: {str(weekday_list).replace("'", '"')}
                        ) {{
                            stopID
                            routeID
                            timetable {{
                                weekday
                                time
                            }}
                        }}
                    }}
                ''',
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['bus']) == list
        for bus in response_body['data']['bus']:
            assert type(bus['stopID']) == int
            assert type(bus['routeID']) == int
            assert {
                'stop': bus['stopID'], 'route': bus['routeID'],
            } in route_stop_list
            assert type(bus['timetable']) == list
            for timetable in bus['timetable']:
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['weekday'] in weekday_list


@pytest.mark.asyncio
async def test_bus_query_by_date():
    date_dict = {
        'saturday': datetime.date(2023, 5, 6),
        'sunday': datetime.date(2023, 5, 7),
        'weekdays': datetime.date(2023, 5, 8),
    }
    async with AsyncClient(app=app, base_url='http://test') as client:
        route_stop_str = str(route_stop_list).replace("'", '')
        for value, date in date_dict.items():
            response = await client.post(
                '/query',
                json={
                    'query': f'''
                        query {{
                            bus(
                                routeStop: {route_stop_str},
                                date: \"{date}\"
                            ) {{
                                stopID
                                routeID
                                timetable {{
                                    weekday
                                    time
                                }}
                            }}
                        }}
                    ''',
                },
            )
            assert response.status_code == 200
            response_body = response.json()
            assert type(response_body['data']['bus']) == list
            for bus in response_body['data']['bus']:
                assert type(bus['stopID']) == int
                assert type(bus['routeID']) == int
                assert {
                    'stop': bus['stopID'], 'route': bus['routeID'],
                } in route_stop_list
                assert type(bus['timetable']) == list
                for timetable in bus['timetable']:
                    assert type(timetable['weekday']) == str
                    assert type(timetable['time']) == str
                    assert timetable['weekday'] == value


@pytest.mark.asyncio
async def test_bus_query_by_start_time():
    current_time = datetime.datetime.now().time()
    async with AsyncClient(app=app, base_url='http://test') as client:
        route_stop_str = str(route_stop_list).replace("'", '')
        response = await client.post(
            '/query',
            json={
                'query': f'''
                    query {{
                        bus(
                            routeStop: {route_stop_str},
                            start: \"{current_time}\"
                        ) {{
                            stopID
                            routeID
                            timetable {{
                                weekday
                                time
                            }}
                        }}
                    }}
                ''',
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['bus']) == list
        for bus in response_body['data']['bus']:
            assert type(bus['stopID']) == int
            assert type(bus['routeID']) == int
            assert {
                'stop': bus['stopID'], 'route': bus['routeID'],
            } in route_stop_list
            assert type(bus['timetable']) == list
            for timetable in bus['timetable']:
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] >= str(current_time) or \
                    timetable['time'] < '04:00:00'


@pytest.mark.asyncio
async def test_bus_query_by_end_time():
    current_time = datetime.datetime.now().time()
    async with AsyncClient(app=app, base_url='http://test') as client:
        route_stop_str = str(route_stop_list).replace("'", '')
        response = await client.post(
            '/query',
            json={
                'query': f'''
                    query {{
                        bus(
                            routeStop: {route_stop_str},
                            end: \"{current_time}\"
                        ) {{
                            stopID
                            routeID
                            timetable {{
                                weekday
                                time
                            }}
                        }}
                    }}
                ''',
            },
        )
        assert response.status_code == 200
        response_body = response.json()
        assert type(response_body['data']['bus']) == list
        for bus in response_body['data']['bus']:
            assert type(bus['stopID']) == int
            assert type(bus['routeID']) == int
            assert {
                'stop': bus['stopID'], 'route': bus['routeID'],
            } in route_stop_list
            assert type(bus['timetable']) == list
            for timetable in bus['timetable']:
                assert type(timetable['weekday']) == str
                assert type(timetable['time']) == str
                assert timetable['time'] < str(current_time)
