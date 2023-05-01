import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_reading_room_list():
    """Test reading room list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get entire campus list
        for campus_id in range(1, 3):
            response = await client.get(f'/library/{campus_id}/room')
            assert response.status_code == 200
            response_body = response.json()
            assert response_body['id'] == campus_id
            assert response_body['name'] in ['서울', 'ERICA']
            assert len(response_body['rooms']) > 0
            for room in response_body['rooms']:
                assert room['id'] > 0
                assert room['name'] != ''
                assert room['status']['active'] in [True, False]
                assert room['status']['reservable'] in [True, False]
                assert room['seats']['total'] > 0
                assert room['seats']['active'] >= 0
                assert room['seats']['occupied'] >= 0
                assert room['seats']['available'] >= 0
                assert room['updated_at'] != ''


@pytest.mark.asyncio
async def test_reading_room_item():
    """Test reading room item endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get campus item
        response = await client.get('/library/2/room/61')
        assert response.status_code == 200
        response_body = response.json()
        assert response_body['id'] == 61
        assert response_body['name'] != ''
        assert response_body['status']['active'] in [True, False]
        assert response_body['status']['reservable'] in [True, False]
        assert response_body['seats']['total'] > 0
        assert response_body['seats']['active'] >= 0
        assert response_body['seats']['occupied'] >= 0
        assert response_body['seats']['available'] >= 0
        assert response_body['updated_at'] != ''
