from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker
from store.models import Collection, Order


@pytest.fixture
def collection(api_client):
    def create_collection(collection):
        return api_client.post('/store/collections/', collection)

    return create_collection


@pytest.mark.django_db
class TestCreateCollection:
    def test_anonymous_user_401(self, collection):
        response = collection({'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_user_not_Admin_403(self, api_client, collection, authenticate):
        authenticate()
        response = collection(collection={'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_invalid_data(self, api_client, collection, authenticate):
        authenticate(is_staff=True)
        response = collection({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    def test_admin_valid_data_201(self, api_client, collection, authenticate):
        authenticate(is_staff=True)
        response = collection({'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCollection:
    def test_collection_exists_200(self, api_client):
        collection = baker.make(Collection)
        response = api_client.get(f'/store/collections/{collection.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': collection.id,
            'title': collection.title,
            'products_count': 0
        }

# new Test case
@pytest.mark.django_db
class TestOrdering:
    def test_paystack_webhook(self, api_client):
        order = baker.make(Order)
        print(order.id)