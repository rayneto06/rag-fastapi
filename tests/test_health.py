from __future__ import annotations

import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_healthcheck() -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/v1/health")
    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data.get("status") == "ok"
