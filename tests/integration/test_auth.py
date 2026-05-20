from httpx import AsyncClient

TEST_USER = {
    "email": "testuser@test.com",
    "password": "testsecret123",
    "full_name": "test test",
}


async def test_register_success(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json=TEST_USER)

    assert response.status_code == 201
    assert response.json()["email"] == "testuser@test.com"
    assert "password" not in response.json()
    assert "password_hash" not in response.json()


async def test_register_duplicate(client: AsyncClient):

    # User registered
    _ = await client.post("/api/v1/auth/register", json=TEST_USER)

    # User trying to register with same email credentials
    response = await client.post("/api/v1/auth/register", json=TEST_USER)

    assert response.status_code == 400
    assert "detail" in response.json()


async def test_login_success(client: AsyncClient):

    _ = await client.post("/api/v1/auth/register", json=TEST_USER)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": TEST_USER["password"]},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()
    assert isinstance(response.json()["access_token"], str)
    assert isinstance(response.json()["refresh_token"], str)


async def test_login_wrong_password(client: AsyncClient):

    _ = await client.post("/api/v1/auth/register", json=TEST_USER)

    response = await client.post(
        "/api/v1/auth/login",
        json={"email": TEST_USER["email"], "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert "access_token" not in response.json()
    assert "refresh_token" not in response.json()


async def test_get_me_authenticated(authenticated_client: AsyncClient):

    # From conftest file we can see TEST_USER
    # dict to get authenticated user email address
    response = await authenticated_client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert "email" in response.json()
    assert response.json()["email"] == "test@example.com"


async def test_get_me_unauthenticated(client: AsyncClient):

    response = await client.get("/api/v1/auth/me")

    assert response.status_code == 401
    assert "detail" in response.json()
