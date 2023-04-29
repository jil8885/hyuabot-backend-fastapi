import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_commute_shuttle_route():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/commute-shuttle/route')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['id'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''


@pytest.mark.asyncio
async def test_commute_shuttle_route_search_by_name():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/commute-shuttle/route?name=화정')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['id'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''
            assert '화정' in route['korean']


@pytest.mark.asyncio
async def test_commute_shuttle_route_item():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/commute-shuttle/route/1')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['name'] == '1'
        assert len(response_body['timetable']) > 0
        for timetable in response_body['timetable']:
            assert timetable['name'] != ''
            assert timetable['time'] != ''
        assert response_body['current']['start']['time'] != ''
        assert response_body['current']['end']['time'] != ''
        assert response_body['status'] != ''


@pytest.mark.asyncio
async def test_commute_shuttle_arrival():
    async with AsyncClient(app=app, base_url='http://test') as client:
        response = await client.get('/commute-shuttle/arrival')
        assert response.status_code == 200
        response_body = response.json()
        print(response_body)
        assert response_body['status'] != ''
        assert len(response_body['route']) > 0
        for route in response_body['route']:
            assert route['name'] != ''
            assert route['korean'] != ''
            assert route['english'] != ''
            assert route['current']['start']['time'] != ''
            assert route['current']['end']['time'] != ''
