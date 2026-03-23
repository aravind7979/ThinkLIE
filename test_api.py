import requests

res = requests.post("http://127.0.0.1:8001/auth/login", json={"email": "testing2@example.com", "password": "password123"})
token = res.json()["access_token"]

res2 = requests.post("http://127.0.0.1:8001/api/chats", headers={"Authorization": f"Bearer {token}"})
print(res2.status_code, res2.text)
