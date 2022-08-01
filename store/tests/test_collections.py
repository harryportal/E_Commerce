from datetime import datetime

from rest_framework import status
import pytest
from model_bakery import baker

from core.models import User
from store.models import Collection, Order, Customer, OrderItem, Product


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
        data = {
            'event': 'charge.success',
            'data': {
                'id': 1923036003,
                'domain': 'test',
                'status': 'success',
                'reference': order.paystack_order_reference,
                'amount': sum([item.unit_price for item in order.items]),
                'message': None,
                'gateway_response': 'Successful',
                'paid_at': '2022-07-02T01:03:28.000Z',
                'created_at': '2022-07-02T01:03:19.000Z',
                'channel': 'card',
                'currency': 'NGN',
                'ip_address': '165.154.234.52',
                'metadata': {
                    'referrer': 'http://localhost:8080/checkout'
                },
                'fees_breakdown': None,
                'log': None, 'fees': 78940,
                'fees_split': None,
                'authorization': {
                    'authorization_code': 'AUTH_s2nz8jlm07',
                    'bin': '408408',
                    'last4': '4081',
                    'exp_month': '12',
                    'exp_year': '2030',
                    'channel': 'card',
                    'card_type': 'visa ',
                    'bank': 'TEST BANK',
                    'country_code': 'NG',
                    'brand': 'visa',
                    'reusable': True,
                    'signature': 'SIG_axLXXJBa5PhYoD4ReSax',
                    'account_name': None,
                    'receiver_bank_account_number': None,
                    'receiver_bank': None
                },
                'customer': {
                    'id': 85440699,
                    'first_name': '',
                    'last_name': '',
                    'email': 'gbovo@test.com',
                    'customer_code': 'CUS_o7rvo0x5tsctr69',
                    'phone': '',
                    'metadata': None,
                    'risk_action': 'default',
                    'international_format_phone': None
                },
                'plan': {}, 'subaccount': {},
                'split': {}, 'order_id': None,
                'paidAt': '2022-07-02T01:03:28.000Z',
                'requested_amount': 4595984,
                'pos_transaction_data': None,
                'source': {
                    'type': 'web', 'source': 'checkout', 'entry_point': 'request_inline', 'identifier': None
                }
            }
        }
        response = api_client.post(f'/orders/transaction-webhook/', data=data)
        assert response.status_code == 200
