from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
import pytest


@pytest.mark.django_db
class TestCreateCollection:

    def test_anonymous_user_401(self):
        client = APIClient()
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_Admin_403(self):
        client = APIClient()
        user = client.force_authenticate(user={})
        response = client.post('/store/collections/', {'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_invalid_data(self):
        client = APIClient()
        user = client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/', {'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_admin_valid_data_401(self):
        client = APIClient()
        user = client.force_authenticate(user=User(is_staff=True))
        response = client.post('/store/collections/',{'title':'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0

