import pytest
from httpx import AsyncClient

from app import AppContext
from app.main import app


@pytest.mark.asyncio
async def test_get_app_context():
    """Test bus stop list endpoint."""
    async with AsyncClient(app=app, base_url='http://test') as client:
        with pytest.raises(Exception):
            AppContext.from_app(app)
