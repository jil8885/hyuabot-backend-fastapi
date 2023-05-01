import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_restaurant_list():
    """Test restaurant list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        for campus_id in range(1, 3):
            response = await client.get(f'/cafeteria/{campus_id}/restaurant')
            assert response.status_code == 200
            response_body = response.json()
            assert response_body['id'] == campus_id
            assert response_body['name'] in ['서울', 'ERICA']
            assert len(response_body['restaurants']) > 0
            for restaurant in response_body['restaurants']:
                assert restaurant['id'] > 0
                assert restaurant['location']['latitude'] >= 0
                assert restaurant['location']['longitude'] >= 0
                assert len(restaurant['menu']) >= 0
                for menu in restaurant['menu']:
                    assert menu['date'] != ''
                    assert any(slot in menu['slot']
                               for slot in ['조식', '중식', '석식'])
                    assert menu['food'] != ''
                    assert menu['price'] != ''
