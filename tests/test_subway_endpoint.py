import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_subway_station_list():
    """Test subway station list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get entire subway station list
        response = await client.get('/subway/station')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stations']) > 0
        for station in response_body['stations']:
            assert station['id'] != ''
            assert station['name'] != ''
            assert station['line'] != ''


@pytest.mark.asyncio
async def test_subway_station_search_by_name():
    """Test subway station search endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get subway station list by name
        response = await client.get('/subway/station?name=한대앞')
        assert response.status_code == 200
        response_body = response.json()
        assert len(response_body['stations']) > 0
        for station in response_body['stations']:
            assert station['id'] != ''
            assert station['name'] != ''
            assert station['line'] != ''
            assert '한대앞' in station['name']
