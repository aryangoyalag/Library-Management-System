import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def token():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/login",
            data={"email": "john@example.com", "password": "password123"}
        )
    assert response.status_code == 200
    return response.json().get("access_token")

@pytest.mark.asyncio
async def test_create_user(token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/User/create_user",
            params={
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password": "password123",
                "role": "Member"
            }
        )
    assert response.status_code == 200
    assert response.json() == {"Message" : "User created successfully."}

@pytest.mark.asyncio
async def test_get_user_details(token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            "/User",
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    
    assert response.json() == {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        "loans": []
    }

@pytest.mark.asyncio
async def test_update_user(token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            "/User/update_user",
            params={
                "password": "password123",
                "new_password": "newpassword123",
                "first_name": "Jane"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    print(response.json())
    assert response.json() == {"Message": "User updated successfully."}

@pytest.mark.asyncio
async def test_delete_user(token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(
            "/User/delete_user",
            params={"password": "newpassword123"},
            headers={"Authorization": f"Bearer {token}"}
        )
    assert response.status_code == 200
    assert response.json() == {"Message": "User deleted successfully."}
