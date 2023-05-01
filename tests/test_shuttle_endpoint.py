import pytest
from httpx import AsyncClient

from app.main import app

route_list = ['DHDD', 'DHSD', 'DHDS', 'DHSS', 'DYDD', 'DYSD', 'DYDS', 'DYSS',
              'CDD', 'CDS', 'CSD', 'CSS', 'DJDD']
tag_list = ['DH', 'DY', 'C', 'DJ']


@pytest.mark.asyncio
async def test_shuttle_route_list():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/route')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['name'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''
            assert route['tag'] != ''

        response = await client.get('/shuttle/route?name=DHD')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['name'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''
            assert route['tag'] != ''
            assert 'DHD' in route['name']

        response = await client.get('/shuttle/route?tag=DH')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['name'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''
            assert route['tag'] != ''
            assert 'DH' in route['tag']


@pytest.mark.asyncio
async def test_shuttle_route_item():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/route/DHDD')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'DHDD'
        assert response_body['tag'] == 'DH'
        assert response_body['korean'] != ''
        assert response_body['english'] != ''
        assert len(response_body['stop']) > 0
        for stop in response_body['stop']:
            assert stop['name'] != ''
            assert stop['sequence'] >= 0
            assert stop['time'] >= -300


@pytest.mark.asyncio
async def test_shuttle_stop_list():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stop']) > 0
        for stop in response_body['stop']:
            assert stop['name'] != ''
            assert stop['latitude'] >= 0
            assert stop['longitude'] >= 0

        response = await client.get('/shuttle/stop?name=shuttlecock')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stop']) > 0
        for stop in response_body['stop']:
            assert stop['name'] != ''
            assert stop['latitude'] >= 0
            assert stop['longitude'] >= 0
            assert 'shuttlecock' in stop['name']


@pytest.mark.asyncio
async def test_shuttle_stop_item():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop/shuttlecock_o')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['latitude'] >= 0
        assert response_body['longitude'] >= 0
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route != ''


@pytest.mark.asyncio
async def test_shuttle_arrival_by_route():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/shuttle/stop/shuttlecock_o/arrival?output=route')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert type(response_body['query']['weekdays']) == bool
        assert response_body['query']['holiday'] in \
               ['normal', 'halt', 'weekends']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['departure_time']) >= 0
            assert len(departure['remaining_time']) >= 0
            for departure_time in departure['departure_time']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for remaining_time in departure['remaining_time']:
                assert type(remaining_time) == float
                assert remaining_time >= 0.0


@pytest.mark.asyncio
async def test_shuttle_arrival_by_tag():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/shuttle/stop/shuttlecock_o/arrival?output=tag')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert type(response_body['query']['weekdays']) == bool
        assert response_body['query']['holiday'] in \
               ['normal', 'halt', 'weekends']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in tag_list
            assert len(departure['departure_time']) >= 0
            assert len(departure['remaining_time']) >= 0
            for departure_time in departure['departure_time']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for remaining_time in departure['remaining_time']:
                assert type(remaining_time) == float
                assert remaining_time >= 0.0


@pytest.mark.asyncio
async def test_shuttle_arrival_period_query():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/shuttle/stop/shuttlecock_o/arrival?period=vacation&output=route')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] == 'vacation'
        assert type(response_body['query']['weekdays']) == bool
        assert response_body['query']['holiday'] in \
               ['normal', 'halt', 'weekends']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['departure_time']) >= 0
            assert len(departure['remaining_time']) >= 0
            for departure_time in departure['departure_time']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for remaining_time in departure['remaining_time']:
                assert type(remaining_time) == float
                assert remaining_time >= 0.0


@pytest.mark.asyncio
async def test_shuttle_arrival_weekdays_query():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/shuttle/stop/shuttlecock_o/arrival?weekdays=True&output=route')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert response_body['query']['weekdays'] is True
        assert response_body['query']['holiday'] in \
               ['normal', 'halt', 'weekends']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['departure_time']) >= 0
            assert len(departure['remaining_time']) >= 0
            for departure_time in departure['departure_time']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for remaining_time in departure['remaining_time']:
                assert type(remaining_time) == float
                assert remaining_time >= 0.0


@pytest.mark.asyncio
async def test_shuttle_arrival_holiday_weekends_query():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop/shuttlecock_o/arrival',
                                    params={
                                        'holiday': 'weekends',
                                        'output': 'route',
                                    })
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert response_body['query']['weekdays'] is True
        assert response_body['query']['holiday'] == 'weekends'
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['departure_time']) >= 0
            assert len(departure['remaining_time']) >= 0
            for departure_time in departure['departure_time']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for remaining_time in departure['remaining_time']:
                assert type(remaining_time) == float


@pytest.mark.asyncio
async def test_shuttle_arrival_holiday_halt_query():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get(
            '/shuttle/stop/shuttlecock_o/arrival',
            params={'holiday': 'halt', 'output': 'route'})
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['query']['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert type(response_body['query']['weekdays']) == bool
        assert response_body['query']['holiday'] in \
               ['normal', 'halt', 'weekends']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['departure_time']) == 0
            assert len(departure['remaining_time']) == 0


@pytest.mark.asyncio
async def test_shuttle_timetable_by_route():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop/shuttlecock_o/timetable',
                                    params={'output': 'route'})
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in route_list
            assert len(departure['weekdays']) >= 0
            assert len(departure['weekends']) >= 0
            for departure_time in departure['weekdays']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for departure_time in departure['weekends']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3


@pytest.mark.asyncio
async def test_shuttle_timetable_by_tag():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop/shuttlecock_o/timetable',
                                    params={'output': 'tag'})
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['period'] in \
               ['semester', 'vacation', 'vacation_session']
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in tag_list
            assert len(departure['weekdays']) >= 0
            assert len(departure['weekends']) >= 0
            for departure_time in departure['weekdays']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for departure_time in departure['weekends']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3


@pytest.mark.asyncio
async def test_shuttle_timetable_period_query():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/shuttle/stop/shuttlecock_o/timetable',
                                    params={'period': 'vacation_session'})
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == 'shuttlecock_o'
        assert response_body['period'] == 'vacation_session'
        assert len(response_body['departure']) > 0
        for departure in response_body['departure']:
            assert departure['name'] in tag_list
            assert len(departure['weekdays']) >= 0
            assert len(departure['weekends']) >= 0
            for departure_time in departure['weekdays']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
            for departure_time in departure['weekends']:
                assert type(departure_time) == str
                assert len(str(departure_time).split(':')) == 3
