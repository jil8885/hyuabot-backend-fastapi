import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_bus_stop_list():
    """Test bus stop list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get entire bus stop list
        response = await client.get('/bus/stop')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stop']) > 0
        for stop in response_body['stop']:
            print(stop)
            assert stop['id'] != 0
            assert stop['name'] != ''
            assert len(str(stop['mobile']).lstrip()) == 5


@pytest.mark.asyncio
async def test_bus_stop_search_by_name():
    """Test bus stop search endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus stop list by name
        response = await client.get('/bus/stop?name=한양대')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stop']) > 0
        for stop in response_body['stop']:
            assert stop['id'] != 0
            assert stop['name'] != ''
            assert len(str(stop['mobile']).lstrip()) == 5
            assert '한양대' in stop['name']


@pytest.mark.asyncio
async def test_bus_stop_item():
    """Test bus stop item endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus stop item
        response = await client.get('/bus/stop/216000379')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['id'] == 216000379
        assert response_body['name'] != ''
        assert len(response_body['mobile']) == 5
        assert response_body['location']['latitude'] != ''
        assert response_body['location']['longitude'] != ''
        assert response_body['location']['district'] != 0
        assert response_body['location']['region'] != ''


@pytest.mark.asyncio
async def test_bus_route_list():
    """Test bus route list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get entire bus route list
        response = await client.get('/bus/route')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['id'] != ''
            assert route['name'] != ''


@pytest.mark.asyncio
async def test_bus_route_search_by_name():
    """Test bus route search endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus route list by name
        response = await client.get('/bus/route?name=3102')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['id'] != ''
            assert route['name'] != ''
            assert '3102' in route['name']


@pytest.mark.asyncio
async def test_bus_route_item():
    """Test bus route item endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus route item
        response = await client.get('/bus/route/216000061')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['id'] == 216000061
        assert response_body['name'] != ''
        assert response_body['company']['id'] != 0
        assert response_body['company']['name'] != ''
        assert response_body['company']['telephone'] != ''
        assert response_body['type']['id'] != 0
        assert response_body['type']['name'] != ''
        assert response_body['origin']['id'] != 0
        assert response_body['origin']['name'] != ''
        assert response_body['origin']['mobile'] != ''
        assert response_body['origin']['first'] != ''
        assert response_body['origin']['last'] != ''
        assert response_body['terminal']['id'] != 0
        assert response_body['terminal']['name'] != ''
        assert response_body['terminal']['mobile'] != ''
        assert response_body['terminal']['first'] != ''
        assert response_body['terminal']['last'] != ''


@pytest.mark.asyncio
async def test_bus_stop_arrival_list():
    """Test bus stop arrival list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus stop arrival list
        response = await client.get('/bus/stop/216000379/arrival')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['id'] == 216000379
        assert response_body['name'] != ''
        assert len(response_body['mobile']) == 5
        assert response_body['location']['latitude'] != 0
        assert response_body['location']['longitude'] != 0
        assert response_body['location']['district'] != 0
        assert response_body['location']['region'] != ''
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['id'] != ''
            assert route['name'] != ''
            assert route['sequence'] != 0
            assert len(route['arrival']) >= 0
            for arrival in route['arrival']:
                assert arrival['sequence'] >= 0
                assert arrival['stop'] >= 0
                assert arrival['time'] >= 0
                assert arrival['seat'] >= -1
                assert arrival['low_plate'] in [True, False]
                assert arrival['updated_at'] != ''
            assert len(route['timetable']) >= 0


@pytest.mark.asyncio
async def test_bus_stop_route_timeatble():
    """Test bus stop route timetable endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get bus stop route timetable
        response = await client.get(
            '/bus/stop/216000379/route/216000061/timetable')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['weekdays']) >= 0
        assert len(response_body['saturdays']) >= 0
        assert len(response_body['sundays']) >= 0
