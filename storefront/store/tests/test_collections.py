from rest_framework.test import APIClient
from rest_framework import status

class TestCreateCollection:
    def test_anonymous_user_401(self):
        client = APIClient()
        response = client.post('/store/collections/', {'title':'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
