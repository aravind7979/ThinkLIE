import requests

res = requests.post("http://ec2-16-171-37-1.eu-north-1.compute.amazonaws.com:8000/auth/login", json={"email": "testing2@example.com", "password": "password123"})
token = res.json()["access_token"]

res2 = requests.post("http://ec2-16-171-37-1.eu-north-1.compute.amazonaws.com:8000/api/chats", headers={"Authorization": f"Bearer {token}"})
print(res2.status_code, res2.text)
