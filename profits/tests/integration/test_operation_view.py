import pytest

from django.urls import reverse

from rest_framework import status

from profits.models import Operation

@pytest.mark.django_db
class TestOperationViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, operation: Operation):
    #     url = reverse('operation-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_operations_when_single_operation(self, authenticated_client, operation_default):
        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_operations_when_multiple_operations(
            self, 
            authenticated_client, 
            create_operation,
            date_factory):
        create_operation()
        create_operation(date=date_factory('2024-02-01'))

        url = reverse('operation-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_operation(self, authenticated_client, operation_default, date_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == date_default.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == operation_default.type
        assert response.data['ticker'] == operation_default.ticker
        assert response.data['quantity'] == f"{operation_default.quantity:.7f}"
        assert response.data['currency'] == operation_default.currency.iso_code
        assert response.data['amount_total'] == f"{operation_default.amount_total:.7f}"
        assert response.data['exchange'] == f"{operation_default.exchange:.6f}"

    def test_create_operation(self, authenticated_client, account_default, currency_gbp, operation_default, date_factory):
        url = reverse('operation-list')
        date_create = date_factory('2024-02-01')
        data = {
            'account': account_default.id,
            'date': date_create,
            'type': operation_default.TYPE_CHOICES[0][0],
            'ticker': 'AMZN',
            'quantity': 10,
            'currency': currency_gbp.iso_code,
            'amount_total': 100,
            'exchange': 1
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == date_create.isoformat().replace('+00:00', 'Z')
        assert response.data['type'] == data['type']
        assert response.data['ticker'] == data['ticker']
        assert response.data['quantity'] == f"{data['quantity']:.7f}"
        assert response.data['currency'] == data['currency']
        assert response.data['amount_total'] == f"{data['amount_total']:.7f}"
        assert response.data['exchange'] == f"{data['exchange']:.6f}"
        assert Operation.objects.count() == 2

    def test_delete_operation_when_has_no_entities_linked(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Operation.objects.filter(id=operation_default.id).exists()

    def test_update_operation(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.put(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_partial_update_operation(self, authenticated_client, operation_default):
        url = reverse('operation-detail', args=[operation_default.id])
        response = authenticated_client.patch(url)
        
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

