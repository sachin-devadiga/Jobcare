from unittest.mock import patch
from rest_framework import status

PLANS_URL = '/api/v1/payments/plans/'
CREATE_ORDER_URL = '/api/v1/payments/create-order/'
VERIFY_PAYMENT_URL = '/api/v1/payments/verify/'
SUBSCRIPTIONS_URL = '/api/v1/payments/subscriptions/'
CREATE_SUBSCRIPTION_URL = '/api/v1/payments/subscriptions/create/'


class TestSubscriptionPlans:
    def test_list_plans(self, api_client, subscription_plan):
        response = api_client.get(PLANS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert len(response.data['data']) >= 1
        assert response.data['data'][0]['name'] == 'Basic Plan'


class TestCreateOrder:
    @patch('payments.views.payment_service.create_payment_order')
    def test_create_order(self, mock_create, employer_auth_client, subscription_plan):
        mock_create.return_value = {
            'order_id': 'order_ABC123',
            'amount': 99900,
            'currency': 'INR',
            'key': 'rzp_test_key',
        }
        response = employer_auth_client.post(CREATE_ORDER_URL, {
            'plan_id': str(subscription_plan.id),
            'payment_for': 'subscription',
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['data']['order_id'] == 'order_ABC123'

    @patch('payments.views.payment_service.create_payment_order')
    def test_create_order_failure(self, mock_create, employer_auth_client, subscription_plan):
        mock_create.return_value = None
        response = employer_auth_client.post(CREATE_ORDER_URL, {
            'plan_id': str(subscription_plan.id),
            'payment_for': 'subscription',
        }, format='json')
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_create_order_employee_forbidden(self, auth_client, subscription_plan):
        response = auth_client.post(CREATE_ORDER_URL, {
            'plan_id': str(subscription_plan.id),
            'payment_for': 'subscription',
        }, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestVerifyPayment:
    @patch('payments.views.payment_service.verify_and_process_payment')
    def test_verify_payment(self, mock_verify, employer_auth_client, subscription_plan):
        mock_verify.return_value = {
            'payment_id': 'pay_XYZ789',
            'order_id': 'order_ABC123',
            'status': 'success',
            'amount': 99900,
        }
        response = employer_auth_client.post(VERIFY_PAYMENT_URL, {
            'razorpay_order_id': 'order_ABC123',
            'razorpay_payment_id': 'pay_XYZ789',
            'razorpay_signature': 'signature_value',
            'plan_id': str(subscription_plan.id),
        }, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['payment_id'] == 'pay_XYZ789'

    @patch('payments.views.payment_service.verify_and_process_payment')
    def test_verify_payment_failure(self, mock_verify, employer_auth_client):
        mock_verify.return_value = None
        response = employer_auth_client.post(VERIFY_PAYMENT_URL, {
            'razorpay_order_id': 'order_BAD',
            'razorpay_payment_id': 'pay_BAD',
            'razorpay_signature': 'bad_sig',
        }, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestSubscriptionList:
    def test_subscription_list(self, auth_client):
        response = auth_client.get(SUBSCRIPTIONS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True

    def test_subscription_list_authenticated(self, auth_client):
        response = auth_client.get(SUBSCRIPTIONS_URL)
        assert response.status_code == status.HTTP_200_OK

    def test_subscription_list_unauthenticated(self, api_client):
        response = api_client.get(SUBSCRIPTIONS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
