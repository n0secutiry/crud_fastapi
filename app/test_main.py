import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import TEST_DATABASE_URL
from database import get_async_session, Base
from main import app


@pytest_asyncio.fixture(scope="function")
async def test_db():
    test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    test_session_maker = sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with test_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(test_db: AsyncSession):
    async def override_get_async_session():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_async_session] = override_get_async_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_show_all_task(client: AsyncClient):
    response = await client.get("/all_task")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_show_task_by_id(client: AsyncClient):
    response = await client.get("/task/1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_new_task_in_db(client: AsyncClient):

    test_data = {
        "name": "Test Name",
        "task": "Test Task",
    }

    response = await client.post("/create", json=test_data)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

    response_json = response.json()

    assert response_json["name"] == test_data["name"]
    assert response_json["task"] == test_data["task"]
    assert "id" in response_json
    assert isinstance(response_json["id"], int)


@pytest.mark.asyncio
async def test_update_task_by(client: AsyncClient):

    test_data = {
        "name": "Test Name up",
        "task": "Test Task up",
    }

    response = await client.post("/create", json=test_data)
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    task_id = response.json().get("id")


    update_data = {
        "name": "Test Name up",
        "task": "Test Task up",
    }

    update_response = await client.put(f"/update/{task_id}", json=update_data)
    response_data = update_response.json()
    assert update_response.status_code == 200
    assert response_data["name"] == update_data["name"]
    assert response_data["task"] == update_data["task"]
    assert response_data["id"] == task_id

    get_response = await client.get(f"/task/{task_id}")
    assert get_response.status_code == 200
    assert isinstance(get_response.json(), dict)
    assert get_response.json().get("name") == update_data["name"]


@pytest.mark.asyncio
async def test_delete_task(client: AsyncClient):
    new_data = {
        "name": "Test for delete",
        "task": "Test for delete",
    }

    test_response = await client.post("/create", json=new_data)
    assert test_response.status_code == 200
    assert isinstance(test_response.json(), dict)
    task_id = test_response.json().get("id")

    delete_response = await client.delete(f"/delete/{task_id}")
    assert delete_response.status_code == 200

    test_response_by_id = await client.get(f"/task/{task_id}")
    assert test_response_by_id.status_code == 404
