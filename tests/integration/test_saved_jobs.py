from httpx import AsyncClient

from surfaced.jobs.models import Job


async def test_saved_jobs_lifecycle_correct(
    authenticated_client: AsyncClient, seed_jobs: list[Job]
):
    target_job_id = seed_jobs[0].id

    response = await authenticated_client.post(
        "/api/v1/jobs/me/saved", json={"job_id": target_job_id}
    )

    assert response.status_code == 200

    response = await authenticated_client.get("/api/v1/jobs/me/saved")

    response_data = response.json()
    assert len(response_data["items"]) == 1

    response = await authenticated_client.delete(f"/api/v1/jobs/me/saved/{target_job_id}")

    assert response.status_code == 204

    response = await authenticated_client.get("/api/v1/jobs/me/saved")

    response_data = response.json()
    assert len(response_data["items"]) == 0


async def test_saved_job_security_boundary(
    client: AsyncClient, authenticated_client: AsyncClient, seed_jobs: list[Job]
):
    target_job_id = seed_jobs[0].id

    response_save = await authenticated_client.post(
        "/api/v1/jobs/me/saved", json={"job_id": target_job_id}
    )
    assert response_save.status_code == 200

    token_user_a = authenticated_client.headers["Authorization"]

    user_b_credentials = {
        "email": "user_b@example.com",
        "password": "password123",
        "full_name": "User B",
    }
    await client.post("/api/v1/auth/register", json=user_b_credentials)

    response_login = await client.post(
        "/api/v1/auth/login",
        json={
            "email": user_b_credentials["email"],
            "password": user_b_credentials["password"],
        },
    )
    token_user_b = response_login.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token_user_b}"
    delete_malicious = await client.delete(f"/api/v1/jobs/me/saved/{target_job_id}")
    assert delete_malicious.status_code == 404

    authenticated_client.headers["Authorization"] = token_user_a

    response_user_a_saved = await authenticated_client.get("/api/v1/jobs/me/saved")
    user_a_saved_data = response_user_a_saved.json()

    assert len(user_a_saved_data["items"]) == 1


async def test_saved_job_idempotency(
    authenticated_client: AsyncClient, seed_jobs: list[Job]
):

    target_job_id = seed_jobs[0].id

    response_save = await authenticated_client.post(
        "/api/v1/jobs/me/saved", json={"job_id": target_job_id}
    )

    assert response_save.status_code == 200

    response_save_duplicate = await authenticated_client.post(
        "/api/v1/jobs/me/saved", json={"job_id": target_job_id}
    )

    assert response_save_duplicate.status_code == 400
    assert response_save_duplicate.json()["detail"] == "you have already saved this job"
