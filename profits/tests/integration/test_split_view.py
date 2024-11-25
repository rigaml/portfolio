import pytest

from datetime import datetime

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware

from rest_framework.test import APIClient
from rest_framework import status

from profits.models import Split

# Gets the active User model, in our case, one defined in `core.models.User`
User = get_user_model()

date_start = make_aware(datetime.fromisoformat('2023-01-01T00:00:00'))

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def split():
    return Split.objects.create(
        date= date_start,
        ticker='TSLA',
        origin=1.0,
        target=10.0
    )

@pytest.fixture
def authenticated_client(api_client: APIClient, user: AbstractUser):
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestSplitViewSet:

    # At the moment DRF is not configured for authentication in setting.py (uncomment `REST_FRAMEWORK` section for this)
    # def test_unauthorized_access(self, api_client: APIClient, split: Split):
    #     url = reverse('split-list')
    #     response = api_client.get(url)
        
    #     assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_splits_when_single_split(self, authenticated_client: APIClient, split: Split):
        """
        'split' parameter added, even not used in code, to trigger creation in fixture.
        """        
        url = reverse('split-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_list_splits_when_multiple_splits(self, authenticated_client: APIClient, split: Split):
        """
        'split' parameter added, even not used in code, to trigger creation in fixture.
        """
        Split.objects.create(
            date= make_aware(datetime.now()),
            ticker='AMZN',
            origin=1.0,
            target=50.0
        )

        url = reverse('split-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_retrieve_split(self, authenticated_client: APIClient, split: Split):
        """
        'split' parameter added, even not used in code, to trigger creation in fixture.
        """
        url = reverse('split-detail', args=[split.id])
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['date'] == '2023-01-01'
        assert response.data['ticker'] == split.ticker
        assert response.data['origin'] == f"{split.origin:.2f}"
        assert response.data['target'] == f"{split.target:.2f}"

    def test_create_split(self, authenticated_client: APIClient, split: Split):
        url = reverse('split-list')
        data = {
            'date': '2023-01-01',
            'ticker': 'AMZN',
            'origin': 1.0,
            'target': 10.0
        }
        
        response = authenticated_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['date'] == data['date']
        assert response.data['ticker'] == data['ticker']
        assert response.data['origin'] == f"{data['origin']:.2f}"
        assert response.data['target'] == f"{data['target']:.2f}"
        assert Split.objects.count() == 2

    def test_delete_split_when_has_entities_linked(self, authenticated_client: APIClient, split: Split):
        url = reverse('split-detail', args=[split.id])
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Split.objects.filter(id=split.id).exists()
