import pytest
from httpx import AsyncClient

from app.main import app


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
