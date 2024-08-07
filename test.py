import pytest
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

@pytest.fixture
async def access_token():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/login",
            data={"username": "test@mail.com", "password": "pass@123"}
        )
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
        response_json = response.json()
        return response_json.get("access_token")
    
@pytest.fixture
async def librarian_access_token():
     async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            "/login",
            data={"username": "lib@mail.com", "password": "pass@123"}
        )
        assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
        response_json = response.json()
        return response_json.get("access_token")
     
@pytest.mark.asyncio
async def test_create_author(librarian_access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            '/Author/create_author',
            json={"pen_name": "Rosette","email": "rosette@mail.com",
  "author_books": [
  ]},
            headers={"Authorization": f"Bearer {await librarian_access_token}"}
        )
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
@pytest.mark.asyncio
async def test_get_user_details(access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            "/User/details",
            headers={"Authorization": f"Bearer {await access_token}"}
        )
    
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
    response_json = response.json()
    assert "first_name" in response_json, "No 'first_name' in response."
    assert "last_name" in response_json, "No 'last_name' in response."
    assert "email" in response_json, "No 'email' in response."
    assert "loans" in response_json, "No 'loans' in response."

@pytest.mark.asyncio
async def test_update_user_details(access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.put(
            '/User/update_user',
            params={
                'password': "pass@123",
                'first_name': 'New',
                'last_name': None,
                'new_password': None
            },
            headers={"Authorization": f"Bearer {await access_token}"}
        )
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_delete_user_details(access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.delete(
            '/User/delete_user',
            params={
                'password': "pass@123",
            },
            headers={"Authorization": f"Bearer {await access_token}"}
        )
    assert response.status_code == 400, f"Expected 400 but got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_search_by_pen_name():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            '/Author/search_by_pen_name',
            params={
                'pen_name': "Guido"
            }
        )
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
    

@pytest.mark.asyncio
async def test_search_books():
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.get(
            '/book/search_books',
            params={
                'title': None,
                'author': "G",
                'genre': None
            }
        )
    assert response.status_code == 200, f"Expected 200 but got {response.status_code}. Response: {response.text}"
    

@pytest.mark.asyncio
async def test_create_loan(access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            '/loan/User/create_loan',
            params={
                'rent_title': "Python"
            },
            headers={"Authorization": f"Bearer {await access_token}"}
        )
    assert response.status_code == 200, f"Expected 400 but got {response.status_code}. Response: {response.text}"

@pytest.mark.asyncio
async def test_approve_loan(librarian_access_token):
    async with AsyncClient(base_url=BASE_URL) as client:
        response = await client.post(
            '/loan/librarian/approve_loan',
            json={'loan_id': 4, 'due_date': None},
            headers={"Authorization": f"Bearer {await librarian_access_token}"}
        )
    assert response.status_code == 404, f"Expected 200 but got {response.status_code}. Response: {response.text}"

