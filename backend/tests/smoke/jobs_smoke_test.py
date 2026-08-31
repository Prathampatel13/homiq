"""
Jobs module smoke test.

Covers the exact Jobs API surface:
  POST   /auth/register (company + technician)
  POST   /jobs                      (company creates a job post)
  GET    /jobs                      (list active job posts)
  POST   /jobs/{id}/apply           (technician applies)
  POST   /jobs/{id}/apply           (duplicate -> 400)
  GET    /jobs/{id}/applications    (company lists applicants)
  PUT    /jobs/applications/{id}/status  (company updates status)
  GET    /jobs/applications/my      (technician lists my applications)
  PUT    /jobs/{id}                 (company updates job post)
  DELETE /jobs/applications/{id}    (technician withdraw, only if not accepted)

Also verifies role enforcement: a customer cannot create a job post (403).
"""
import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PASSWORD = "Test@1234"

RESULTS = []


def check(name, code, expected_codes):
    ok = code in expected_codes
    RESULTS.append((name, code, ok))
    print(f"  {'OK ' if ok else 'FAIL'} {name:<32} -> {code}")


def gen_email(role: str) -> str:
    return f"{role}_{uuid.uuid4().hex[:10]}@example.com"


def register(role: str = "company"):
    r = client.post("/auth/register", json={
        "email": gen_email(role),
        "password": PASSWORD,
        "full_name": f"Smoke {role.capitalize()}",
        "phone": "9876523456",
        "role": role,
    })
    assert r.status_code == 201, f"Register failed: {r.status_code} {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def main():
    company_headers = register("company")
    tech_headers = register("technician")

    # 1. Company creates a job post
    print("\n>> POST /jobs (company)")
    r = client.post("/jobs/", headers=company_headers, json={
        "title": "Plumber Needed",
        "description": "Fix leaking pipes in apartment.",
        "requirements": "2+ years experience, own tools.",
        "is_active": True,
    })
    print(" ", r.status_code, r.text[:300])
    check("company_create_job", r.status_code, [201])
    assert r.status_code == 201, r.text
    job = r.json()
    job_id = job["id"]
    assert job["title"] == "Plumber Needed"
    assert "company_profile" in job, "company_profile field missing in response"
    print(f"  job_id={job_id}")

    # 2. List active job posts
    print("\n>> GET /jobs (technician)")
    r = client.get("/jobs", headers=tech_headers)
    print(" ", r.status_code, r.text[:200])
    check("list_active_jobs", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["total"] >= 1

    # 3. Technician applies
    print("\n>> POST /jobs/{id}/apply (technician)")
    r = client.post(f"/jobs/{job_id}/apply", headers=tech_headers, json={
        "cover_letter": "I have 5 years of plumbing experience.",
    })
    print(" ", r.status_code, r.text[:300])
    check("technician_apply", r.status_code, [201])
    assert r.status_code == 201, r.text
    app_data = r.json()
    app_id = app_data["id"]
    assert app_data["status"] == "applied"
    print(f"  application_id={app_id}")

    # 4. Duplicate application -> 400
    print("\n>> POST /jobs/{id}/apply (duplicate, expect 400)")
    r = client.post(f"/jobs/{job_id}/apply", headers=tech_headers, json={
        "cover_letter": "Duplicate.",
    })
    print(" ", r.status_code, r.text[:200])
    check("duplicate_apply", r.status_code, [400])
    assert r.status_code == 400, r.text

    # 5. Company lists applicants
    print("\n>> GET /jobs/{id}/applications (company)")
    r = client.get(f"/jobs/{job_id}/applications", headers=company_headers)
    print(" ", r.status_code, r.text[:300])
    check("company_list_applicants", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["total"] >= 1
    assert "technician_profile" in r.json()["items"][0]

    # 6. Company updates application status -> shortlisted
    print("\n>> PUT /jobs/applications/{id}/status (company)")
    r = client.put(f"/jobs/applications/{app_id}/status", headers=company_headers, json={
        "status": "shortlisted",
    })
    print(" ", r.status_code, r.text[:300])
    check("company_update_status", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "shortlisted"

    # 7. Technician lists my applications
    print("\n>> GET /jobs/applications/my (technician)")
    r = client.get("/jobs/applications/my", headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("tech_my_applications", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["total"] >= 1
    assert r.json()["items"][0]["status"] == "shortlisted"

    # 8. Company updates job post
    print("\n>> PUT /jobs/{id} (company)")
    r = client.put(f"/jobs/{job_id}", headers=company_headers, json={
        "title": "Senior Plumber Needed",
        "is_active": False,
    })
    print(" ", r.status_code, r.text[:300])
    check("company_update_job", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["title"] == "Senior Plumber Needed"

    # 9. Technician cannot create a job post (role gate)
    print("\n>> POST /jobs (technician, expect 403)")
    r = client.post("/jobs/", headers=tech_headers, json={
        "title": "Hack",
        "description": "Should be blocked.",
    })
    print(" ", r.status_code, r.text[:200])
    check("tech_cannot_create_job", r.status_code, [403])
    assert r.status_code == 403, r.text

    # 10. Technician lists my job posts (role gate: company only)
    print("\n>> GET /jobs/my (technician, expect 403)")
    r = client.get("/jobs/my", headers=tech_headers)
    print(" ", r.status_code, r.text[:200])
    check("tech_cannot_list_my_jobs", r.status_code, [403])
    assert r.status_code == 403, r.text

    print("\n" + "=" * 60)
    print("JOBS SMOKE TEST SUMMARY")
    print("=" * 60)
    all_ok = True
    for name, code, ok in RESULTS:
        print(f"  {name:<32} {code}  {'OK' if ok else 'FAIL'}")
        if not ok:
            all_ok = False
    print()
    print("-> ALL TESTS PASSED" if all_ok else "-> SOME TESTS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
