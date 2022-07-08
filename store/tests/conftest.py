import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User


""" defines a reusable fixture to run pytest without having to repeatedly call the api client function in the tests """
@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticate(api_client):
    def authenticate_user(is_staff=False):
        return api_client.force_authenticate(user=User(is_staff=is_staff))
    return authenticate_user