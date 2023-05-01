import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_campus_list():
    """Test campus list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get entire campus list
        response = await client.get('/campus')
        assert response.status_code == 200
        assert response.json() == {
            'campus': [
                {
                    'id': 1,
                    'name': '서울',
                },
                {
                    'id': 2,
                    'name': 'ERICA',
                },
            ],
        }
        # Query campus list by name
        response = await client.get('/campus?name=서울')
        assert response.status_code == 200
        assert response.json() == {
            'campus': [
                {
                    'id': 1,
                    'name': '서울',
                },
            ],
        }
        # Query campus list by name
        response = await client.get('/campus?name=ERICA')
        assert response.status_code == 200
        assert response.json() == {
            'campus': [
                {
                    'id': 2,
                    'name': 'ERICA',
                },
            ],
        }
        # Query campus list by name
        response = await client.get('/campus?name=서울대학교')
        assert response.status_code == 200
        assert response.json() == {
            'campus': [],
        }


@pytest.mark.asyncio
async def test_campus_item():
    """Test campus item endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        # Get campus item
        response = await client.get('/campus/1')
        assert response.status_code == 200
        assert response.json() == {
            'id': 1,
            'name': '서울',
        }
        # Get campus item
        response = await client.get('/campus/2')
        assert response.status_code == 200
        assert response.json() == {
            'id': 2,
            'name': 'ERICA',
        }
        # Get campus item
        response = await client.get('/campus/3')
        assert response.status_code == 404
        assert response.json() == {
            'message': 'Campus not found',
        }
